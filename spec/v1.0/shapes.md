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

# Shapes and Tensor Semantics (Normative)

This chapter captures the tensor shape, dtype, and broadcasting semantics used by the Core IR and
its lowering pipelines. It mirrors the behaviour implemented in
[`cputer/mind`](https://github.com/cputer/mind) and avoids prescribing runtime-specific layouts.

## Tensor shapes and dtypes

- Tensors carry an explicit **shape** (ordered list of dimension sizes) and **dtype** (numeric element
  type). Devices MAY be specified when required by the runtime, but device placement is otherwise
  out of scope for the Core v1 spec.
- Scalars are represented as rank-0 tensors.

## Broadcasting

Binary elementwise operations (e.g. `BinOp`, elementwise unary ops) use **right-aligned broadcasting**
matching NumPy/PyTorch semantics:

1. Shapes are aligned from the **trailing dimensions**.
2. For each aligned axis, dimensions must be equal or one of them MUST be `1`.
3. The resulting dimension is the maximum of the two aligned sizes.
4. Leading unmatched dimensions are copied from the longer shape.

Broadcasting preserves dtype promotion rules from the implementation; unsupported promotions are
implementation-defined and MUST be diagnosed.

## Reductions

`Sum` and `Mean` reduce explicit `axes: [i32]` with optional `keepdims: bool`:

- **Axis handling**: axes refer to zero-based dimensions. Duplicate axes are invalid. Empty `axes`
  denotes reduction across all dimensions.
- **Output shape**:
  - If `keepdims = true`, reduced axes become size `1`.
  - If `keepdims = false`, reduced axes are removed.
- **`Mean` scaling**: divides by the total element count of the reduced dimensions, not by the number
  of axes listed.

Axis values outside the rank are verification failures during IR validation. Behaviour for runtime
out-of-bounds is implementation-defined.

## Index, slice, and gather

- **`Index`**: consumes one index per dimension and returns a scalar (or lower-rank tensor when
  indexing into higher-rank tails). The result shape is the suffix of the input shape after removing
  indexed dimensions.
- **`Slice`**: each dimension uses `(start, end, step)`. The resulting size per dimension is
  `ceil((end-start)/step)` for positive steps; negative steps are implementation-defined. Start/end
  pairs are verifier-checked for rank alignment; runtime bounds handling is implementation-defined.
- **`Gather`**: for input shape `[D0, D1, ... Dn]` and indices shape `[I0, ... Ik]`, the result shape
  is `[I0, ... Ik, D1, ... Dn]` when gathering along the leading dimension. Alternate axis selections
  are implementation-defined in this version.

## Convolution shape inference

`Conv2d` uses NHWC input tensors and HWCF filters:

- **Input shape**: `[N, H, W, C_in]`.
- **Filter shape**: `[H_k, W_k, C_in, C_out]`.
- **Strides/Padding**: follow the implementation’s conventions (e.g. `SAME`/`VALID`). Unsupported
  padding modes are implementation-defined and SHOULD be rejected during verification.
- **Output shape**: `[N, H_out, W_out, C_out]` where `H_out` and `W_out` are derived from input size,
  kernel, stride, and padding according to the chosen padding rule.

Channel compatibility (`input.C == filter.C_in`) is mandatory; violations MUST fail verification.

## Relationship to Phase-1 semantics

These rules extend the Phase-1 tensor semantics already present in the public compiler. Any
behaviour not explicitly captured here remains implementation-defined but MUST NOT contradict the
Phase-1 behaviours shipped in current releases.
