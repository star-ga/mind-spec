from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class CoreOperation:
    """A minimal Core IR instruction.

    Each operation owns its output ``value_id`` and records operands, opcode,
    and result type metadata for deterministic compilation. Attributes are kept
    generic so tests can attach shape information when available.
    """

    value_id: int
    opcode: str
    operands: List[int] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    result_type: Optional[str] = None

    def format(self) -> str:
        attr_items = [f"{k}={v}" for k, v in sorted(self.attributes.items())]
        attr_suffix = f" {{{', '.join(attr_items)}}}" if attr_items else ""
        operand_suffix = f" ({', '.join(f'%{op}' for op in self.operands)})" if self.operands else ""
        result_suffix = f" : {self.result_type}" if self.result_type else ""
        return f"%{self.value_id} = {self.opcode}{operand_suffix}{attr_suffix}{result_suffix}"


class CoreIR:
    """In-memory representation of the Core IR module model.

    The module is intentionally simple: a flat list of ``CoreOperation``
    objects with deterministic ``value_id`` assignment. Inputs are encoded as
    `Input` operations to keep ordering canonical with the specification's
    single-definition rule.
    """

    def __init__(self) -> None:
        self.operations: List[CoreOperation] = []
        self.outputs: List[int] = []
        self._next_value_id: int = 0

    def _fresh_value(self) -> int:
        value_id = self._next_value_id
        self._next_value_id += 1
        return value_id

    def declare_input(self, name: str, result_type: Optional[str] = None) -> int:
        value_id = self._fresh_value()
        self.operations.append(
            CoreOperation(
                value_id=value_id,
                opcode="Input",
                attributes={"name": name},
                result_type=result_type,
            )
        )
        return value_id

    def add_operation(
        self,
        opcode: str,
        operands: Optional[Sequence[int]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        result_type: Optional[str] = None,
    ) -> int:
        value_id = self._fresh_value()
        op = CoreOperation(
            value_id=value_id,
            opcode=opcode,
            operands=list(operands or []),
            attributes=attributes or {},
            result_type=result_type,
        )
        self.operations.append(op)
        return value_id

    def mark_output(self, value_id: int) -> None:
        self.outputs.append(value_id)

    def compile(self) -> str:
        output_section = "" if not self.outputs else "\noutputs: " + ", ".join(f"%{oid}" for oid in self.outputs)
        return "\n".join(op.format() for op in self.operations) + output_section
