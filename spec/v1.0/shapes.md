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

Formally, a shape is a finite sequence of positive integers:

```text
Shape = [d_0, d_1, ..., d_{n-1}]   where each d_i ∈ ℕ⁺
Rank(Shape) = n
```

Core v1 does not define symbolic or unknown dimensions in the base profile.
Implementations may extend the shape system, but conformance is defined for
fully-known shapes.

The verifier rejects tensors whose dimensions are zero or negative. Scalars
remain rank-0 tensors with an empty `[]` shape and therefore bypass the
positive-dimension rule.

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

The broadcasted shape `C` is the dimension-by-dimension result of this rule.
If any dimension fails the compatibility checks, the operator is required to
produce a **shape error** rather than silently proceeding.

### Formal broadcasting algorithm

The following algorithm defines broadcasting semantically and MUST be followed by all conforming implementations:

```
Algorithm: Broadcast(ShapeA, ShapeB) → ShapeC or Error

Inputs:
  ShapeA = [a₀, a₁, ..., aₘ₋₁]  // Shape with rank m
  ShapeB = [b₀, b₁, ..., bₙ₋₁]  // Shape with rank n

Output:
  ShapeC = [c₀, c₁, ..., cₖ₋₁]  // Broadcasted shape with rank k
  or BroadcastError             // Incompatible shapes

Procedure:
  1. Determine target rank:
       k ← max(m, n)

  2. Align shapes from the right (prepend 1s to shorter shape):
       If m < k:
         ShapeA' ← [1, 1, ..., 1︸k-m times, a₀, a₁, ..., aₘ₋₁]
       Else:
         ShapeA' ← ShapeA

       If n < k:
         ShapeB' ← [1, 1, ..., 1︸k-n times, b₀, b₁, ..., bₙ₋₁]
       Else:
         ShapeB' ← ShapeB

  3. Compute broadcasted dimensions:
       For i from 0 to k-1:
         aᵢ' ← ShapeA'[i]
         bᵢ' ← ShapeB'[i]

         If aᵢ' == bᵢ':
           cᵢ ← aᵢ'
         Else if aᵢ' == 1:
           cᵢ ← bᵢ'
         Else if bᵢ' == 1:
           cᵢ ← aᵢ'
         Else:
           Return BroadcastError(
             message: "Incompatible shapes for broadcasting",
             dimension: i,
             extent_a: aᵢ',
             extent_b: bᵢ'
           )

  4. Return ShapeC ← [c₀, c₁, ..., cₖ₋₁]
```

### Broadcasting examples

Implementations MUST produce the following results:

**Example 1: Scalar broadcast**
```
A = []        (rank-0 scalar)
B = [3, 4, 5]
Result = [3, 4, 5]

Aligned: A' = [1, 1, 1], B' = [3, 4, 5]
Broadcast: [1→3, 1→4, 1→5] = [3, 4, 5]
```

**Example 2: Leading dimension broadcast**
```
A = [1, 5]
B = [3, 5]
Result = [3, 5]

Aligned: A' = [1, 5], B' = [3, 5]
Broadcast: [1→3, 5] = [3, 5]
```

**Example 3: Multi-dimensional broadcast**
```
A = [3, 1, 5]
B = [1, 4, 5]
Result = [3, 4, 5]

Aligned: A' = [3, 1, 5], B' = [1, 4, 5]
Broadcast: [3→3, 1→4, 5] = [3, 4, 5]
```

**Example 4: Broadcast error (incompatible)**
```
A = [3, 4]
B = [3, 5]
Result = BroadcastError

Aligned: A' = [3, 4], B' = [3, 5]
Dimension 1: 4 ≠ 5 and neither is 1 → Error
```

**Example 5: Rank mismatch with broadcast**
```
A = [5]
B = [3, 4, 5]
Result = [3, 4, 5]

Aligned: A' = [1, 1, 5], B' = [3, 4, 5]
Broadcast: [1→3, 1→4, 5] = [3, 4, 5]
```

### Broadcasting invariants

Conforming implementations MUST maintain these invariants:

1. **Commutativity**: `Broadcast(A, B) = Broadcast(B, A)` for all compatible shapes
2. **Associativity**: `Broadcast(Broadcast(A, B), C) = Broadcast(A, Broadcast(B, C))` when defined
3. **Identity with rank-0**: `Broadcast(A, []) = A` for any shape A
4. **Identity with ones**: `Broadcast(A, [1, 1, ..., 1]) = A` when ranks match
5. **Determinism**: Same input shapes MUST always produce the same output or error
6. **Error precision**: Broadcast errors MUST identify the failing dimension index

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

Axis-parameterized reductions (for example, `sum` over a specific axis) are
considered an extension and must follow the same error model:

- invalid or out-of-range axes must produce a shape error;
- ambiguous axis specifications (duplicates, mismatched ranks) must not be
  silently accepted.

Axis-aware reductions, when added, will extend this chapter with a dedicated
subsection.

## Matrix multiplication

Core v1 defines a canonical **matrix multiplication** shape rule for
`tensor.matmul`:

- inputs must be **rank-2 or greater** tensors;
- the trailing two dimensions participate in the matrix multiply;
- the inner dimensions must match.

Formally:

```text
A: tensor<T>[M, K]
B: tensor<T>[K, N]
----------------------------
tensor.matmul(A, B): tensor<T>[M, N]
```

If either input has rank smaller than 2, or if `K` does not match between the
inputs, the operator must produce a shape error.

For tensors with **batch dimensions**, leading dimensions follow the
broadcasting rules described earlier. The resulting shape is therefore:
`Broadcast(batch_lhs, batch_rhs) ++ [M, N]`.

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
