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

# MLIR Lowering (Normative)

This chapter specifies the deterministic lowering of canonical Core IR into MLIR for the feature-gate
that ships with the public compiler. The rules cover only the stable, publicly implemented subset.

## Scope and prerequisites

- Lowering is **feature-gated** (e.g. via an `mlir-lowering` feature flag in the compiler).
- The input module MUST be **verified and canonicalised** per [Core IR](./ir.md).
- Lowering produces deterministic **MLIR textual IR** suitable for snapshot testing. Minor changes may
  occur between MIND versions but are stable within a release.

## Lowering patterns

### Constants

- Scalars and tensors lower to `arith.constant` with explicit MLIR tensor types.

### Tensor allocation and fill

- Zero-initialised tensors are represented using `tensor.empty` followed by `linalg.fill` fed by a
  separate `arith.constant` for the fill value.

### Matrix multiplication

- `MatMul` lowers to `linalg.matmul` in **destination-passing style**:
  - A `tensor.empty` destination is created with the inferred result shape.
  - The destination is passed via `outs` and the filled tensor is the operation result.

### Convolution

- `Conv2d` lowers to `linalg.conv_2d_nhwc_hwcf` with **NHWC** input and **HWCF** filter.
- Destination-passing mirrors matmul: allocate with `tensor.empty`, feed through `outs`.
- Verification ensures input and filter channels match before lowering.

### Elementwise and reductions

- Elementwise `BinOp` instructions lower to MLIR arithmetic ops on broadcasted tensors using MLIR
  canonical broadcasting utilities.
- `Sum` and `Mean` lower to reduction patterns that preserve `keepdims` semantics; `Mean` divides by
  the reduced element count explicitly.

## Determinism and stability

- Given canonical IR, the emitted MLIR text is **deterministic**. Ordering follows IR instruction
  order and canonical operand ordering rules.
- The textual form is stable **within a compiler release**. Future releases MAY evolve op selections
  or attributes but MUST preserve semantics for the defined Core v1 operations.
