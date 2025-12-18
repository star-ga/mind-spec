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
  - **Shape rules**: output shape is `[]` (rank-0 scalar)
  - **Dtype rules**: output dtype is always `i64`
  - **Semantics**: the output tensor contains exactly one element with value `value`
- **`ConstF32(value: f32) -> ValueId`**
  - Produces a scalar `f32` tensor (rank-0) with the literal `value`.
  - **Shape rules**: output shape is `[]` (rank-0 scalar)
  - **Dtype rules**: output dtype is always `f32`
- **`ConstF64(value: f64) -> ValueId`**
  - Produces a scalar `f64` tensor (rank-0) with the literal `value`.
  - **Shape rules**: output shape is `[]` (rank-0 scalar)
  - **Dtype rules**: output dtype is always `f64`
- **`ConstTensor(data: tensor literal, dtype: DType, shape: Shape) -> ValueId`**
  - Produces a tensor with the literal `data`. The literal encodes shape and dtype explicitly.
  - **Shape rules**: output shape is the declared `shape` attribute
  - **Dtype rules**: output dtype is the declared `dtype` attribute
  - **Verification**:
    - The literal data MUST match the declared dtype and shape
    - Element count in data MUST equal the product of shape dimensions
    - All elements MUST be valid values for the declared dtype
    - Mismatches are verification failures

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
  - Computes the sum of tensor elements along specified axes.
  - **Shape rules**:
    - If `keepdims = true`: output shape has `1` at each reduced axis position
    - If `keepdims = false`: output shape removes all reduced axes
    - Empty `axes` denotes full reduction to scalar `[]` (regardless of keepdims)
    - Example: `Sum([3, 4, 5], axes=[1], keepdims=false) → [3, 5]`
    - Example: `Sum([3, 4, 5], axes=[1], keepdims=true) → [3, 1, 5]`
  - **Dtype rules**: output dtype equals input dtype; sum preserves dtype (may overflow for integers)
  - **Verification**:
    - All axis indices MUST be in range `[0, rank)`
    - Duplicate axes are verification failures
    - Negative axis indices MAY be supported but are implementation-defined
- **`Mean(input, axes: [i32], keepdims: bool) -> ValueId`**
  - Computes the arithmetic mean of tensor elements along specified axes.
  - **Shape rules**: same as `Sum` (see above)
  - **Dtype rules**: output dtype equals input dtype
  - **Semantics**:
    - Divides by the number of elements reduced (product of reduced dimension extents)
    - NOT by the count of axes
    - Example: `Mean([2, 3, 4], axes=[1,2]) divides by 3*4=12`
  - **Verification**: same as `Sum`

### Shape manipulation

- **`Reshape(input, new_shape: [i64]) -> ValueId`**
  - Reshapes a tensor to a new shape while preserving element count and order.
  - **Shape rules**: output shape is `new_shape`
  - **Dtype rules**: output dtype equals input dtype (reshape does not change dtype)
  - **Verification**:
    - Element count MUST be preserved: `product(input.shape) == product(new_shape)`
    - All dimensions in `new_shape` MUST be positive integers
    - Exactly one dimension MAY be `-1` (inferred from element count); if present, it is computed
      as `product(input.shape) / product(other_dimensions)`
    - Element count mismatch is a verification failure
- **`Transpose(input, permutation: [i64]) -> ValueId`**
  - Permutes the dimensions of a tensor according to the given permutation.
  - **Shape rules**: `output.shape[i] = input.shape[permutation[i]]` for all i
  - **Dtype rules**: output dtype equals input dtype
  - **Verification**:
    - Permutation length MUST equal input rank
    - Permutation MUST contain each axis index in `[0, rank)` exactly once
    - Duplicate or out-of-range indices are verification failures
  - **Example**: `Transpose([2, 3, 4], perm=[2, 0, 1]) → [4, 2, 3]`
- **`ExpandDims(input, axes: [i64]) -> ValueId`**
  - Inserts singleton dimensions (size `1`) at the specified axis positions.
  - **Shape rules**: output rank is `input.rank + len(axes)`; new dimensions have size `1`
  - **Dtype rules**: output dtype equals input dtype
  - **Semantics**:
    - Axes are inserted sequentially in ascending order of axis value
    - Each insertion shifts subsequent axis positions
    - After all insertions, output has size `1` at each specified axis
  - **Verification**:
    - Each axis MUST be in range `[0, current_rank]` at insertion time
    - Duplicate axes MAY be allowed if they refer to different positions after prior insertions
    - Out-of-range axes are verification failures
  - **Example**: `ExpandDims([3, 4], axes=[0, 2]) → [1, 3, 1, 4]`
- **`Squeeze(input, axes: [i64]) -> ValueId`**
  - Removes dimensions of size `1` at the specified axis positions.
  - **Shape rules**: output rank is `input.rank - len(axes)`; specified dimensions are removed
  - **Dtype rules**: output dtype equals input dtype
  - **Verification**:
    - All specified axes MUST reference dimensions with size exactly `1`
    - Axis indices MUST be in range `[0, rank)`
    - Duplicate axes are verification failures
    - Squeezing a dimension with size ≠ 1 is a verification failure
  - **Example**: `Squeeze([1, 3, 1, 4], axes=[0, 2]) → [3, 4]`

### Indexing and slicing

- **`Index(input, indices: [i64]) -> ValueId`**
  - Extracts a single element from the input tensor at the specified multi-dimensional index.
  - **Shape rules**: output is a rank-0 scalar `[]`
  - **Dtype rules**: output dtype equals input dtype
  - **Semantics**: `Index(input, [i₀, i₁, ..., iₙ₋₁])` returns `input[i₀, i₁, ..., iₙ₋₁]`
  - **Verification**:
    - Index list length MUST equal input rank
    - Length mismatch is a verification failure
  - **Runtime behaviour**: bounds checking is a runtime responsibility
    - Out-of-bounds indices MAY produce an error, undefined value, or backend-specific handling
    - Implementations SHOULD document their out-of-bounds behaviour
- **`Slice(input, starts: [i64], ends: [i64], steps: [i64]) -> ValueId`**
  - Extracts a sub-tensor using range-based slicing along each dimension.
  - **Shape rules**: `output.shape[i] = ceil((ends[i] - starts[i]) / steps[i])` for each dimension i
  - **Dtype rules**: output dtype equals input dtype
  - **Semantics**: slices along dimension `i` from `starts[i]` (inclusive) to `ends[i]` (exclusive)
    with stride `steps[i]`
  - **Verification**:
    - Lengths of `starts`, `ends`, and `steps` MUST all equal input rank
    - All `steps[i]` MUST be non-zero
    - Length mismatch or zero steps are verification failures
  - **Runtime behaviour**:
    - Negative `starts`/`ends` MAY be interpreted as offsets from the end (implementation-defined)
    - Negative `steps` (reverse slicing) MAY be supported (implementation-defined)
    - Empty slices (where `ends[i] ≤ starts[i]` for positive step) produce size-0 dimensions
- **`Gather(input, indices: tensor<i32|i64>) -> ValueId`**
  - Gathers elements from input using an index tensor.
  - **Shape rules**:
    - If `indices` has shape `[I₀, I₁, ..., Iₖ]` and `input` has shape `[D₀, D₁, ..., Dₘ]`
    - Output shape is `[I₀, I₁, ..., Iₖ, D₁, D₂, ..., Dₘ]`
    - Indices tensor indexes into the first dimension of input
  - **Dtype rules**:
    - Indices tensor MUST have dtype `i32` or `i64`
    - Output tensor has the same dtype as input
  - **Semantics**: `output[i₀, ..., iₖ, d₁, ..., dₘ] = input[indices[i₀, ..., iₖ], d₁, ..., dₘ]`
  - **Verification**:
    - Indices tensor MUST have integer dtype (i32 or i64)
    - Non-integer indices dtype is a verification failure
  - **Runtime behaviour**:
    - Index validity is checked at runtime
    - Out-of-range indices MAY produce an error or backend-specific handling

### Linear and tensor algebra

- **`Dot(lhs, rhs) -> ValueId`**
  - Inputs: rank-1 or rank-2 tensors with compatible inner dimensions.
  - **Shape rules**:
    - Rank-1 × Rank-1: `[n] · [n] → []` (scalar inner product)
    - Rank-2 × Rank-1: `[m, n] · [n] → [m]` (matrix-vector product)
    - Rank-1 × Rank-2: `[m] · [m, n] → [n]` (vector-matrix product)
    - Rank-2 × Rank-2: delegates to MatMul
  - **Dtype rules**: both operands MUST have the same dtype; output has the same dtype.
  - **Verification**: inner dimensions MUST match; mismatches are verification failures.
- **`MatMul(lhs, rhs) -> ValueId`**
  - Inputs: matrices (or batched matrices) with compatible inner dimensions. Inputs MUST each have
    rank ≥ 2; leading batch dimensions broadcast following [broadcasting](./shapes.md#broadcasting).
  - **Shape rules**:
    - `lhs: [...batch_lhs, M, K]`
    - `rhs: [...batch_rhs, K, N]`
    - `output: [...Broadcast(batch_lhs, batch_rhs), M, N]`
  - **Dtype rules**: both operands MUST have the same dtype; output has the same dtype.
  - **Verification**:
    - Both inputs MUST have rank ≥ 2
    - Contracting dimension K MUST match: `lhs.shape[-1] == rhs.shape[-2]`
    - Batch dimensions MUST be broadcast-compatible
    - Rank < 2 or K mismatch are verification failures
- **`Conv2d(input, filter, strides: [i64], padding: Padding) -> ValueId`**
  - Input format: **NHWC** `[batch, height, width, channels_in]`
  - Filter format: **HWCF** `[kernel_height, kernel_width, channels_in, channels_out]`
  - **Shape rules**:
    - Input: `[N, H_in, W_in, C_in]`
    - Filter: `[H_k, W_k, C_in, C_out]`
    - Output: `[N, H_out, W_out, C_out]`
    - `H_out = floor((H_in + 2*pad_h - H_k) / stride_h) + 1`
    - `W_out = floor((W_in + 2*pad_w - W_k) / stride_w) + 1`
  - **Dtype rules**: input and filter MUST have the same dtype; output has the same dtype.
  - **Verification**:
    - Input MUST have rank 4
    - Filter MUST have rank 4
    - Channels MUST match: `input.shape[3] == filter.shape[2]`
    - Strides MUST have length 2 with positive values
    - Padding MUST be Valid, Same, or Custom with 2 pairs of non-negative integers
    - Channel mismatch or invalid strides/padding are verification failures

### Activation and elementwise unary operations

- **`Relu(input) -> ValueId`**
  - Computes rectified linear unit: `max(0, x)` elementwise
  - **Shape rules**: output shape equals input shape (no broadcasting)
  - **Dtype rules**: input MUST be a floating-point dtype (f32 or f64); output has the same dtype.
    Integer dtypes MAY be supported as an extension but are not required for Core v1 conformance.
  - **Semantics**: `Relu(x)[i] = x[i] if x[i] > 0 else 0` for all indices i
- **`Neg(input) -> ValueId`**
  - Computes elementwise negation: `-x`
  - **Shape rules**: output shape equals input shape
  - **Dtype rules**: input MUST be a numeric dtype; output has the same dtype
  - **Semantics**: `Neg(x)[i] = -x[i]` for all indices i
- **`Exp(input) -> ValueId`**
  - Computes elementwise exponential: `e^x`
  - **Shape rules**: output shape equals input shape
  - **Dtype rules**: input MUST be a floating-point dtype; output has the same dtype
  - **Semantics**: `Exp(x)[i] = e^(x[i])` for all indices i
- **`Log(input) -> ValueId`**
  - Computes elementwise natural logarithm: `ln(x)`
  - **Shape rules**: output shape equals input shape
  - **Dtype rules**: input MUST be a floating-point dtype; output has the same dtype
  - **Semantics**: `Log(x)[i] = ln(x[i])` for all indices i
  - **Runtime behaviour**: `Log(x)` where `x ≤ 0` is implementation-defined (may produce NaN or error)

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
