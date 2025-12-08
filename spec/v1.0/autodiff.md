<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Static Reverse-Mode Autodiff (Normative)

This chapter specifies the **Phase-2 reverse-mode autodiff** pipeline that operates on canonical Core
IR. The rules align with the implemented behaviour in the public compiler
[`cputer/mind`](https://github.com/cputer/mind) and describe no additional proprietary features.

## Model

- Autodiff runs over verified **Core IR modules**, not over source syntax.
- Gradient construction produces a **gradient module** containing primal and gradient instructions.
  Gradients are mapped by a deterministic association: `gradients : ValueId → ValueId`.
- The engine traverses the instruction list **in reverse order**, accumulating gradient contributions
  per `ValueId`. Canonicalisation is applied to the resulting module to ensure determinism.

A conceptual result container:

- `gradient_module`: the IR module containing gradient-producing instructions (and optionally primal
  copies where needed for data dependencies).
- `gradients`: a map from each differentiated primal `ValueId` to its gradient `ValueId`.

## Error space (`AutodiffError`)

Autodiff MUST signal deterministic errors using the following categories:

- **`UnsupportedOp { op }`**: an instruction lacks a derivative rule.
- **`Verification`**: the produced gradient module fails IR verification.
- **`InvalidAxis`**: reduction axes are out of range or inconsistent with shape semantics during
  gradient construction.
- **`UnsupportedShape`**: broadcasting or reduction shapes not supported by the current engine.

Errors are surfaced per module; autodiff MUST NOT silently drop gradients.

## Options and verification

Conceptually, gradient generation accepts **GradientOptions**:

- **Canonicalise**: ALWAYS enabled; gradients are canonicalised to a stable form.
- **Verify**: enabled by default. When disabled, verification MAY be skipped for performance, but
  canonicalisation still occurs and behaviour remains deterministic for well-formed inputs.

Options are described here abstractly; concrete API surface is implementation-specific.

## Derivative rules

Autodiff implements reverse-mode rules consistent with standard tensor calculus. Highlights include:

- **Addition/Subtraction (`BinOp(Add|Sub)`)**: gradient wrt each operand is the upstream gradient
  broadcast to the operand shape.
- **Multiplication (`BinOp(Mul)`)**: applies the product rule; gradient for `lhs` multiplies upstream
  gradient by `rhs` (broadcast as needed) and vice versa.
- **Unary elementwise ops** implemented in the compiler (e.g. `Neg`) follow the standard derivative
  of the scalar function applied elementwise.
- **`Dot` / `MatMul`**: gradients follow standard matrix calculus, using transposed operands as
  required to match input shapes. Batch dimensions broadcast per the rules in [Shapes](./shapes.md).
- **`Conv2d`**: gradients are computed for input and filter using the implemented convolution backward
  rules with the same NHWC/HWCF layout assumptions.
- **`Sum` / `Mean`**: reductions distribute upstream gradients back to the unreduced shape. `Mean`
  divides the upstream gradient by the number of elements reduced.
- **Other ops**: any instruction not covered by a derivative rule MUST trigger `UnsupportedOp`.

Gradients for indexing/slicing operations propagate upstream gradients into the corresponding slices;
behaviour for out-of-bounds indices is implementation-defined but MUST be deterministic.

## Determinism

- Input IR is canonicalised and verified before autodiff.
- Generated gradient IR is canonicalised. For a fixed compiler version, identical input modules MUST
  produce **bit-for-bit identical** gradient modules.
- Error reporting is deterministic with stable categorisation as described above.
