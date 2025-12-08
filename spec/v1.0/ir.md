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

This document defines the Phase-2 **Core IR** used by the public MIND compiler and runtime
implementations. The IR is the canonical interchange format between the surface language, the static
autodiff engine, MLIR lowering, and backend runtimes.

The specification describes only the deterministic, publicly implemented behaviour in
[`cputer/mind`](https://github.com/cputer/mind). It does not reference private infrastructure or
undocumented extensions.

## IR module model

A Core IR module is a **flat, ordered list of instructions**. Basic blocks and control-flow graphs
are out of scope for Phase-2 and MUST NOT appear in canonical modules.

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

## Instruction set and semantics

The following instructions constitute the Phase-2 surface of Core IR. Unless stated otherwise, all
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
  - Output: tensor with broadcasted shape and dtype promotion defined by the implementation.
  - `Add` and `Sub` are **commutative** for canonicalisation ordering only; semantics remain
    standard arithmetic.
  - `Div` is currently **not part of Core v1**; attempts to encode division are
    implementation-defined and SHOULD be rejected during verification.

### Reductions

- **`Sum(input, axes: [i32], keepdims: bool) -> ValueId`**
- **`Mean(input, axes: [i32], keepdims: bool) -> ValueId`**
  - Inputs: a tensor and explicit axes (may be empty). Axes semantics follow
    [Reduction rules](./shapes.md#reductions) including `keepdims` behaviour.
  - `Mean` divides by the number of elements reduced (product of reduced dimensions), not by the
    count of axes.
  - Empty `axes` denotes a full reduction consistent with the reference compiler behaviour.

### Shape manipulation

- **`Reshape(input, new_shape: [i64]) -> ValueId`**
  - Preserves element count; rank may change. Verification fails if element counts differ.
- **`Transpose(input, permutation: [i64]) -> ValueId`**
  - Permutation length MUST equal input rank and contain each axis exactly once.
- **`ExpandDims(input, axes: [i64]) -> ValueId`**
  - Inserts singleton dimensions at the specified axes. Axes MUST be within `[0, rank]` after
    prior insertions are accounted for.
- **`Squeeze(input, axes: [i64]) -> ValueId`**
  - Removes dimensions of size `1` at the specified axes. Axes MUST reference dimensions that are
    exactly `1`.

### Indexing and slicing

- **`Index(input, indices: [i64]) -> ValueId`**
  - Indexes into `input` with one index per dimension. Indices MUST be within bounds at runtime; the
    verifier enforces only that the index list length matches rank. Out-of-bounds behaviour is
    implementation-defined.
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
  - Inputs: matrices (or batched matrices) with compatible inner dimensions. Broadcasting across
    leading batch dimensions follows [broadcasting](./shapes.md#broadcasting).
- **`Conv2d(input, filter, strides: [i64], padding: Padding) -> ValueId`**
  - Input format: **NHWC**.
  - Filter format: `[H_k, W_k, C_in, C_out]` (HWCF).
  - Channels MUST satisfy `input.C == filter.C_in`.
  - Stride and padding semantics MUST match the reference implementation; unsupported padding modes
    are implementation-defined.

## Canonicalisation

Before optimisation, autodiff, or lowering, modules MUST be **canonicalised**:

- **Operand ordering**: commutative `BinOp` operands are ordered by ascending `ValueId`.
- **Constant folding**: evaluable `ConstI64`, `ConstTensor`, and `BinOp` expressions MAY be folded
  when safe. Implementations MUST NOT fold operations that would divide by zero or produce
  `i64::MIN / -1` overflow; those remain unfused.
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
   reshape element-count preservation and transpose permutation length.
4. **Conv2d constraints**:
   - Input is NHWC; filter is `[H_k, W_k, C_in, C_out]`.
   - `input.C == filter.C_in`.
   - Strides and padding conform to the implemented rules; unsupported combinations are
     implementation-defined but MUST be diagnosed if the runtime cannot execute them.

Behaviour not explicitly described is **implementation-defined** and MUST be documented by the
implementing compiler. Verification failures MUST be surfaced deterministically.
