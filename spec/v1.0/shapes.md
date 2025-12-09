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

# Shapes and dtypes

This chapter describes the shape and dtype lattice for Core v1 programs and the
rules used by the Core v1 shape engine for elementwise operations, reductions
and matrix multiplication.

Shapes and dtypes are **device-agnostic**: the same rules apply to the CPU baseline and the optional GPU profile.

## Tensor ranks and shapes

- A *tensor* has a **rank** (number of dimensions) and a **shape** (an ordered
  list of extents, one per dimension).
- Scalars are treated as **rank-0** tensors with an empty shape `[]`.
- Vectors and matrices are rank-1 and rank-2 respectively.

Formally, a shape is a finite sequence of non-negative integers:

```text
Shape = [d_0, d_1, ..., d_{n-1}]   where each d_i ∈ ℕ
Rank(Shape) = n
```

Core v1 does not define symbolic or unknown dimensions in the base profile.
Implementations may extend the shape system, but conformance is defined for
fully-known shapes.

## Broadcasting

Many Core v1 operators are **elementwise** and support broadcasting of their
inputs. Broadcasting follows the standard "numpy-style" rules.

Given two shapes `A` and `B`, broadcasting proceeds as:

1. Align shapes from the **right** by inserting leading dimensions of size `1`
   to the shorter shape as needed.
2. For each dimension (from right to left):
   - if the extents are equal (`a_i == b_i`), the result extent is that value;
   - if one of the extents is `1`, the result extent is the other value;
   - otherwise broadcasting fails.

Formally, let `A'` and `B'` be the aligned shapes of the same rank `k`. Then
for each `i ∈ {0, ..., k-1}`:

```text
if A'[i] == B'[i]      → C[i] = A'[i]
else if A'[i] == 1     → C[i] = B'[i]
else if B'[i] == 1     → C[i] = A'[i]
else                   → error (incompatible shapes)
```

The broadcasted shape `C` is the elementwise result of this rule. If any
dimension fails the rule, the operator is required to produce a **shape error**
rather than silently proceeding.

### Elementwise unary

For **unary elementwise** operators (for example, `tensor.relu`, `tensor.neg`,
`tensor.exp`, `tensor.log`) no broadcasting is required. The output shape is
exactly the input shape:

```text
Shape_out = Shape_in
```

Shape errors occur only if the operator is applied to a rank or dtype outside
its defined domain (for example, applying a floating-point-only op to an
integer tensor where the implementation does not support it).

### Elementwise binary

For **binary elementwise** operators (for example, `tensor.add`, `tensor.sub`,
`tensor.mul`, `tensor.div`) the output shape is the broadcasted shape of the
two inputs:

```text
Shape_out = Broadcast(Shape_lhs, Shape_rhs)
```

If broadcasting fails (as defined above), the compiler or runtime must report a
shape error. The Core v1 conformance suite is expected to include examples of
both successful and failing broadcasts.

## Reductions

Core v1 distinguishes between:

- **full reductions** that reduce all axes to a scalar (rank-0);
- **axis-aware reductions** (future extension), which remain out of scope for
  the Core v1 baseline.

The operator `tensor.sum_all` is a **full reduction**:

```text
Input:  tensor<f32>[d_0, d_1, ..., d_{n-1}]
Output: tensor<f32>[]    (rank-0 scalar)
```

If the input is already a scalar (`[]`), the output is also a scalar of the
same shape. Implementations must not silently change the rank (for example, to
`[1]`); the scalar representation is part of the contract.

Axis-parameterised reductions (for example, `sum` over a specific axis) are
considered an extension and must follow the same error model:

- invalid or out-of-range axes must produce a shape error;
- ambiguous axis specifications (duplicates, mismatched ranks) must not be
  silently accepted.

Axis-aware reductions, when added, will extend this chapter with a dedicated
subsection.

## Matrix multiplication

Core v1 defines a canonical **2D matrix multiplication** shape rule for
`tensor.matmul`:

- both inputs must be **rank-2** tensors;
- the inner dimensions must match.

Formally:

```text
A: tensor<T>[M, K]
B: tensor<T>[K, N]
----------------------------
tensor.matmul(A, B): tensor<T>[M, N]
```

If either input has rank different from 2, or if `K` does not match between the
inputs, the operator must produce a shape error.

Higher-rank batched matrix multiplication and other generalisations are
considered future extensions and will be specified separately. Implementations
may support them as non-Core v1 extensions, but must not claim Core v1
conformance based on those rules.

## Relationship to dtypes

This chapter focuses on shapes. Dtype rules (for example, which element types
are accepted by each operator) are specified alongside the operator registry
and runtime semantics. Implementations must ensure that shape and dtype checks
are consistent:

- an operator may reject an input for dtype reasons even when shapes are
  compatible;
- the resulting error must still be deterministic and follow the general error
  model.

## Reference shape engine

The Core v1 shape rules in this chapter are intended to be straightforward to
implement. The reference implementation in `cputer/mind` exposes a small shape
engine (`mind::shapes::engine`) that:

- encodes the high-level rule category for each Core v1 operator
  (unary/binary elementwise, full reduction, 2D matmul);
- implements broadcasting as defined above; and
- provides helpers to infer output shapes or report structured shape errors.

Other implementations are not required to use this engine, but they are
expected to produce the same outcomes (shapes or shape errors) for the same
operator and input shapes when claiming Core v1 conformance.

## Device independence

Core v1 defines:

- a CPU baseline which provides a stable, device-agnostic Core v1 execution
  environment; and
- a GPU profile that extends the CPU baseline with device/backend semantics.

Shape and dtype semantics are **device-agnostic**: a conforming implementation
MUST apply the same rules regardless of the chosen device kind.
