from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Sequence

from .core_ir import CoreIR


@dataclass(frozen=True)
class TensorType:
    dtype: str
    shape: tuple[int, ...] = ()

    def __str__(self) -> str:  # pragma: no cover - simple representation
        shape_suffix = f"[{', '.join(map(str, self.shape))}]" if self.shape else "[]"
        return f"tensor<{self.dtype}{shape_suffix}>"

    def is_scalar(self) -> bool:
        return not self.shape

    @property
    def rank(self) -> int:
        return len(self.shape)


class TypeSystem:
    """Minimal type environment for static validation.

    The prototype models a small subset of the specification: scalar and tensor
    types with shape metadata. It enforces dtype compatibility, positive
    dimensions, broadcasting for elementwise operations, and batched matmul
    validation. Inputs are materialised directly into the Core IR module to keep
    value numbering deterministic.
    """

    def __init__(self, known_dtypes: Iterable[str] | None = None) -> None:
        self.known_dtypes = set(known_dtypes or {"i32", "i64", "f32", "f64"})
        self.symbols: Dict[str, TensorType] = {}
        self._materialized_symbols: Dict[str, int] = {}

    def ensure_known_dtype(self, dtype: str) -> None:
        if dtype not in self.known_dtypes:
            raise TypeError(f"Unknown dtype '{dtype}'")

    def validate_shape(self, shape: Sequence[int]) -> None:
        if any(d <= 0 for d in shape):
            raise ValueError("Shape dimensions must be positive integers")

    def validate_tensor(self, tensor: TensorType) -> TensorType:
        self.ensure_known_dtype(tensor.dtype)
        self.validate_shape(tensor.shape)
        return tensor

    def add_symbol(self, name: str, tensor_type: TensorType) -> None:
        self.symbols[name] = self.validate_tensor(tensor_type)

    def resolve_symbol(self, name: str) -> TensorType:
        try:
            return self.symbols[name]
        except KeyError as exc:
            raise TypeError(f"Symbol '{name}' is not declared") from exc

    def materialize_symbol(self, ir: CoreIR, name: str, tensor_type: TensorType) -> int:
        if name not in self._materialized_symbols:
            value_id = ir.declare_input(name, result_type=str(tensor_type))
            self._materialized_symbols[name] = value_id
        return self._materialized_symbols[name]

    def broadcast_shapes(self, lhs: Sequence[int], rhs: Sequence[int]) -> tuple[int, ...]:
        lhs_rev = list(reversed(lhs))
        rhs_rev = list(reversed(rhs))
        result: list[int] = []

        for i in range(max(len(lhs_rev), len(rhs_rev))):
            ldim = lhs_rev[i] if i < len(lhs_rev) else 1
            rdim = rhs_rev[i] if i < len(rhs_rev) else 1

            if ldim == rdim:
                result.append(ldim)
            elif ldim == 1:
                result.append(rdim)
            elif rdim == 1:
                result.append(ldim)
            else:
                raise ValueError(f"Shapes are not broadcastable: {tuple(lhs)} vs {tuple(rhs)}")

        return tuple(reversed(result))

    def validate_binop(self, op: str, lhs: TensorType, rhs: TensorType) -> TensorType:
        lhs = self.validate_tensor(lhs)
        rhs = self.validate_tensor(rhs)

        if lhs.dtype != rhs.dtype:
            raise TypeError(f"cannot mix dtypes `{lhs.dtype}` and `{rhs.dtype}` in binary op {op}")

        broadcast_shape = self.broadcast_shapes(lhs.shape, rhs.shape)
        return TensorType(lhs.dtype, broadcast_shape)

    def validate_matmul(self, lhs: TensorType, rhs: TensorType) -> TensorType:
        lhs = self.validate_tensor(lhs)
        rhs = self.validate_tensor(rhs)

        if lhs.rank < 2 or rhs.rank < 2:
            raise ValueError("MatMul requires tensors of rank 2 or greater")

        if lhs.shape[-1] != rhs.shape[-2]:
            raise ValueError(f"Matmul dimension mismatch: {lhs.shape[-1]} != {rhs.shape[-2]}")

        batch_shape = self.broadcast_shapes(lhs.shape[:-2], rhs.shape[:-2])
        return TensorType(lhs.dtype, batch_shape + (lhs.shape[-2], rhs.shape[-1]))

    def validate_program(self) -> None:
        for name, tensor_type in self.symbols.items():
            self.validate_tensor(tensor_type)

