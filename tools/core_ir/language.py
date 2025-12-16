from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .core_ir import CoreIR
from .type_system import TensorType, TypeSystem


class Expression:
    """Base class for surface language expressions."""

    def emit(self, ir: CoreIR, type_system: TypeSystem) -> int:  # pragma: no cover - abstract
        raise NotImplementedError

    def infer_type(self, type_system: TypeSystem) -> TensorType:  # pragma: no cover - abstract
        raise NotImplementedError


@dataclass
class Literal(Expression):
    value: object
    dtype: str
    shape: tuple[int, ...] = ()

    def infer_type(self, type_system: TypeSystem) -> TensorType:
        tensor_type = TensorType(self.dtype, self.shape)
        return type_system.validate_tensor(tensor_type)

    def emit(self, ir: CoreIR, type_system: TypeSystem) -> int:
        result_type = str(self.infer_type(type_system))
        return ir.add_operation(
            "ConstTensor",
            operands=[],
            attributes={"value": self.value, "shape": self.shape, "dtype": self.dtype},
            result_type=result_type,
        )


@dataclass
class Variable(Expression):
    name: str

    def infer_type(self, type_system: TypeSystem) -> TensorType:
        return type_system.resolve_symbol(self.name)

    def emit(self, ir: CoreIR, type_system: TypeSystem) -> int:
        symbol_type = self.infer_type(type_system)
        return type_system.materialize_symbol(ir, self.name, symbol_type)


@dataclass
class BinaryOperation(Expression):
    op: str
    lhs: Expression
    rhs: Expression

    def infer_type(self, type_system: TypeSystem) -> TensorType:
        lhs_type = self.lhs.infer_type(type_system)
        rhs_type = self.rhs.infer_type(type_system)
        if self.op == "MatMul":
            return type_system.validate_matmul(lhs_type, rhs_type)
        return type_system.validate_binop(self.op, lhs_type, rhs_type)

    def emit(self, ir: CoreIR, type_system: TypeSystem) -> int:
        lhs_id = self.lhs.emit(ir, type_system)
        rhs_id = self.rhs.emit(ir, type_system)
        result_type = str(self.infer_type(type_system))
        return ir.add_operation(self.op, operands=[lhs_id, rhs_id], result_type=result_type)


class LanguageConstruct:
    """Entry point for compiling expressions to the Core IR prototype."""

    def __init__(self, expression: Expression, type_system: Optional[TypeSystem] = None) -> None:
        self.expression = expression
        self.type_system = type_system or TypeSystem()

    def to_ir(self) -> CoreIR:
        self.type_system.validate_program()

        ir = CoreIR()
        result_value = self.expression.emit(ir, self.type_system)
        ir.mark_output(result_value)
        return ir
