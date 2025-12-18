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

# Core Intermediate Representation (Normative)

This document defines the **Core IR** used by the public MIND compiler and runtime implementations.
The IR is the canonical interchange format between the surface language, the static autodiff engine,
MLIR lowering, and backend runtimes.

The specification describes only the deterministic, publicly implemented behaviour in
[`cputer/mind`](https://github.com/cputer/mind). It does not reference private infrastructure or
undocumented extensions.

## IR module model

A Core IR module is a **flat, ordered list of instructions**. Basic blocks and control-flow graphs
are out of scope for Core v1 and MUST NOT appear in canonical modules.

### Values and `ValueId`

- Each instruction may produce zero or more **values** identified by abstract `ValueId`s.
- `ValueId`s form a **totally ordered** set; the order reflects creation order and is used for
  canonicalisation. The ordering is abstract and does not expose internal fields.
- **Single-definition invariant**: every `ValueId` is defined exactly once.
- A conceptual **freshness** rule assigns the next available `ValueId` when an instruction produces
  outputs. Implementations MAY allocate identifiers differently, but MUST preserve ordering for
  equivalent programs.

### Module contents

A module declares:

- **Inputs/Outputs**: distinguished values marking the externally visible interface of the module.
- **Instruction list**: the ordered instructions that produce all internal and output values.

Modules MUST be serialisable to a stable textual form. Canonicalisation (below) establishes the
canonical ordering expected by downstream pipelines.

### `CoreOperation` structure

The reference tooling models each instruction as a `CoreOperation` record:

```text
CoreOperation ::= {
    value_id: int,
    opcode: str,
    operands: [int],
    attributes: Dict[str, Any],
    result_type: str
}
```

`value_id`s follow the freshness rule described above to maintain SSA-style ordering. Attributes are
kept generic so verifier-visible metadata (for example, tensor shape and dtype) can be attached
deterministically. The textual encoding below renders this record in a stable order suitable for
round-tripping in tests and debugging tools.

### Reference encoding

The reference compiler exposes a minimal textual encoding to aid debugging and unit testing. The
encoding follows the ordered instruction list model described above:

- **Inputs**: each module input materialises as an `Input` instruction carrying a `name` attribute
  and the declared tensor type (dtype plus shape). Inputs appear first and receive the lowest
  `ValueId`s.
- **Operations**: instructions render as `%<id> = <Opcode> (<operands>) {attrs} : <type>`. Attribute
  braces are omitted when empty and operand lists are comma-separated. Result types record the
  verifier-visible tensor type.
- **Outputs**: the module records output value identifiers explicitly to satisfy the interface
  contract. When serialised, outputs appear as a trailing `outputs: %<id>, ...` list.

This encoding is intentionally small and lossless so that translators from the surface language can
round-trip canonical modules during conformance testing.

### Surface language lowering

The reference translation pipeline from surface expressions to Core IR is deterministic:

1. **Inputs**: free variables materialise as `Input` instructions with explicit tensor metadata.
2. **Literals**: scalar and tensor literals emit `ConstTensor` instructions that embed dtype and shape
   in attributes.
3. **Operations**: language operators lower directly to the Core IR instruction set, applying
   type-directed validation (broadcasting, dtype equality, matmul dimension checks) before emission.
4. **Outputs**: the final produced `ValueId` is recorded as a module output to satisfy the
   single-definition invariant.

This lowering process reuses the type system rules in [Types](./types.md) so that invalid programs are
rejected before IR is emitted.

## Instruction set and semantics

The following instructions constitute the Core v1 surface of Core IR. Unless stated otherwise, all
instructions operate on tensors with explicit **dtype** and **shape** metadata. Dtypes and shape
rules are defined in [Shapes and Tensor Semantics](./shapes.md).

For each instruction, inputs MUST reference existing values and outputs MUST respect the shape/dtype
constraints described here. Behaviour outside these rules is **verification failure** unless marked
as implementation-defined.

### Constants

- **`ConstI64(value: i64) -> ValueId`**
  - Produces a scalar `i64` tensor (rank-0) with the literal `value`.
- **`ConstTensor(data: tensor literal) -> ValueId`**
  - Produces a tensor with the literal `data`. The literal encodes shape and dtype explicitly.
  - The literal MUST match the declared dtype and shape; mismatches are verification failures.

### Binary operations

- **`BinOp(op: Add|Sub|Mul, lhs, rhs) -> ValueId`**
  - Inputs: two tensors broadcastable under the rules in [Shapes](./shapes.md#broadcasting).
  - Dtypes: operands MUST share a dtype; mixing dtypes is a verification failure.
  - Output: tensor with broadcasted shape as defined in [Shapes](./shapes.md#broadcasting).
  - For canonicalisation ordering, operands of **commutative** `BinOp`s (such as `Add`, `Mul`) are
    ordered by ascending `ValueId`. Only `Add` (and other truly commutative operations) are treated
    as commutative; `Sub` and `Div` are **not** commutative, and their operand order MUST be
    preserved.
  - `Div` is currently **not part of Core v1**; attempts to encode division are implementation-defined
    and SHOULD be rejected during verification.

### Reductions

- **`Sum(input, axes: [i32], keepdims: bool) -> ValueId`**
- **`Mean(input, axes: [i32], keepdims: bool) -> ValueId`**
  - Inputs: a tensor and explicit axes (may be empty). Axes semantics follow
    [Reduction rules](./shapes.md#reductions) including `keepdims` behaviour.
  - `Mean` divides by the number of elements reduced (product of reduced dimensions), not by the
    count of axes.
  - Empty `axes` denotes a full reduction consistent with the reference compiler behaviour.
  - Specifically, passing `axes: []` reduces across **all** dimensions (a full reduction), not a
    no-op.

### Shape manipulation

- **`Reshape(input, new_shape: [i64]) -> ValueId`**
  - Preserves element count; rank may change. The verifier enforces that element counts match; if they
    differ, verification fails.
- **`Transpose(input, permutation: [i64]) -> ValueId`**
  - Permutation length MUST equal input rank and contain each axis exactly once.
- **`ExpandDims(input, axes: [i64]) -> ValueId`**
  - Inserts singleton dimensions at the specified axes.
  - When multiple axes are provided, insertions are performed sequentially in ascending order of axis
    value; each insertion shifts the positions of subsequent axes.
  - Each axis MUST be within `[0, rank]` at the time of its respective insertion.
- **`Squeeze(input, axes: [i64]) -> ValueId`**
  - Removes dimensions of size `1` at the specified axes. Axes MUST reference dimensions that are
    exactly `1`.

### Indexing and slicing

- **`Index(input, indices: [i64]) -> ValueId`**
  - Indexes into `input` with one index per dimension.
  - The verifier enforces only that the index list length matches the tensor rank.
  - Bounds checking of indices is a runtime responsibility. If any index is out of bounds, the
    behaviour is implementation-defined (e.g. may result in an error, undefined value, or other
    backend-specific handling).
- **`Slice(input, starts: [i64], ends: [i64], steps: [i64]) -> ValueId`**
  - Produces a view with range semantics per dimension. Start/end/step lengths MUST match rank.
    Negative steps and bounds that would create empty slices are implementation-defined.
- **`Gather(input, indices: tensor) -> ValueId`**
  - Gathers elements according to the leading dimensions of `indices`. Result shape follows the
    [Gather shape rules](./shapes.md#index-slice-and-gather). Index validity is checked per backend
    and may be implementation-defined for out-of-range indices.

### Linear and tensor algebra

- **`Dot(lhs, rhs) -> ValueId`**
  - Inputs: rank-1 or rank-2 tensors with compatible inner dimensions.
  - Output: tensor following standard dot-product broadcasting (implementation-aligned).
- **`MatMul(lhs, rhs) -> ValueId`**
  - Inputs: matrices (or batched matrices) with compatible inner dimensions. Inputs MUST each have
    rank ≥ 2; leading batch dimensions broadcast following [broadcasting](./shapes.md#broadcasting).
- **`Conv2d(input, filter, strides: [i64], padding: Padding) -> ValueId`**
  - Input format: **NHWC**.
  - Filter format: `[H_k, W_k, C_in, C_out]` (HWCF).
  - Channels MUST satisfy `input.shape[3] == filter.shape[2]`.
  - Stride and padding semantics MUST match the reference implementation; unsupported padding modes
    are implementation-defined.

## Canonicalisation

Before optimisation, autodiff, or lowering, modules MUST be **canonicalised**:
- **Operand ordering**: operands of commutative `BinOp`s (`Add`, `Mul`, etc.) are ordered by
  ascending `ValueId`. Non-commutative operations such as `Sub` and `Div` MUST NOT have their
  operands reordered.
- **Constant folding**: evaluable `ConstI64`, `ConstTensor`, and `BinOp` expressions MAY be folded
  when safe. Implementations MUST NOT fold operations that would result in unsafe or undefined
  behaviour; those remain unfused.
- **Dead instruction pruning**: instructions whose outputs are unused and are not declared module
  outputs or referenced by gradient outputs MAY be removed.

All downstream pipelines (autodiff, MLIR lowering, runtime execution) assume inputs are verified and
canonical.

## Verification

A verifier MUST reject IR modules that violate the following rules:

1. **Definition/Use discipline**: every operand references a previously defined `ValueId`; each
   `ValueId` is defined exactly once.
2. **Interface validity**: all declared outputs reference existing values.
3. **Shape and dtype consistency**: instructions follow the constraints described above, including
   reshape element-count preservation, transpose permutation length, positive tensor dimensions, and
   broadcast/matmul rules from [Shapes](./shapes.md).
4. **Conv2d constraints**:
   - Input is NHWC; filter is `[H_k, W_k, C_in, C_out]`.
   - `input.shape[3] == filter.shape[2]`.
   - Strides and padding conform to the implemented rules; unsupported combinations are
     implementation-defined but MUST be diagnosed if the runtime cannot execute them.

Behaviour not explicitly described is **implementation-defined** and MUST be documented by the
implementing compiler. Verification failures MUST be surfaced deterministically.
