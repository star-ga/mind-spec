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

# Surface Language (Normative)

This chapter summarises the Core v1 surface language constructs that compile down to the Core IR.
Detailed lexical and type rules continue to live in the legacy chapters ([`lexical.md`](./lexical.md),
[`types.md`](./types.md)); this document consolidates the tensor-oriented subset implemented in
[`cputer/mind`](https://github.com/cputer/mind).

## Syntax overview

- **Modules and functions**: programs are organised as modules containing functions. Functions declare
  named parameters and return values and compile to IR module inputs/outputs.
- **Expressions**: include literals, binary operators (`+`, `-`, `*`), unary operators (e.g. `-`),
  function calls, and tensor constructors.
- **Tensor literals**: may appear with explicit dtype annotations. Rank-0 literals represent scalars.
- **Control flow**: the Core v1 spec models straight-line tensor programs; high-level control flow is
  lowered away before entering the Core IR described in [Core IR](./ir.md).

## Types

The type system relevant to Core v1 consists of:

- **Scalar types**: numeric primitives supported by the compiler (e.g. `i64`, `f32`).
- **Tensor types**: parameterised by `dtype` and **shape**. Shape dimensions may be statically known
  integers or implementation-defined symbolic sizes where supported.
- **Shape descriptors**: ordered lists of dimensions. Shapes appear in type annotations and IR
  metadata. Device placements MAY be attached but are otherwise outside the Core v1 scope.

## Tensor operations

Surface syntax maps to the Core IR instruction set:

- **Arithmetic**: `+`, `-`, `*` lower to `BinOp` with broadcasting semantics from
  [Shapes](./shapes.md#broadcasting). Division is not part of Core v1 (see
  [IR spec](./ir.md#arithmetic-operations)).
- **Type checking for arithmetic**: operands MUST share a dtype; shape inference uses broadcasting
  rules so scalars implicitly extend to the non-scalar operand's shape.
- **Reductions**: `sum(x, axes, keepdims)` and `mean(x, axes, keepdims)` lower to `Sum`/`Mean`.
- **Shape ops**: `reshape`, `transpose`, `expand_dims`, and `squeeze` mirror their IR counterparts.
- **Indexing**: slicing/index expressions lower to `Index`, `Slice`, or `Gather` depending on syntax.
- **Linear algebra**: `dot`, `matmul`, and `conv2d` are available as intrinsic functions mapping to the
  IR operations described in [Core IR](./ir.md#linear-and-tensor-algebra). `matmul` requires rank-2 or
  higher operands and validates contracting dimensions before emission.

Implementations MUST reject programs that request unsupported operations or incompatible shapes
according to the verification rules in [Core IR](./ir.md).

## Relationship to Core IR

Compilation of the surface language yields canonical IR modules that obey:

- **SSA-style value production** via ordered `ValueId`s.
- **Explicit tensor metadata** for dtype and shape.
- **Deterministic lowering** enabling repeatable autodiff and MLIR generation.

### Canonical translation pipeline

Surface constructs lower to the Core IR through a deterministic, type-directed
pipeline:

1. **Symbols become inputs**: every free variable in the expression context
   materialises as an `Input` instruction that records its declared type and
   shape metadata.
2. **Literals become constants**: scalar or tensor literals emit
   `ConstTensor` instructions with dtype and shape encoded explicitly.
3. **Operators become IR instructions**: arithmetic expressions lower to `BinOp`
   (with `Add`, `Sub`, or `Mul` semantics) and other intrinsic operations map to
   the IR instruction set described in [Core IR](./ir.md).
4. **Outputs are explicit**: the last produced `ValueId` is marked as the
   module output to preserve the single-definition rule.

Implementations are expected to reuse the type system rules in
[Types](./types.md) during translation so that invalid programs are rejected
before IR is emitted.

Language features beyond this tensor core (e.g. generics, traits) are covered in the broader v1.0
specification but are not required for Core v1 conformance.
