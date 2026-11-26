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

Formally, a shape is a finite sequence of integers that are not negative. A dimension of size 0 is valid (an
empty slice gives one); a negative dimension MUST be refused at check time with
[`E3006`](./errors.md#e3006-negative-dimension), and a negative dimension that is known only at run time makes
the defined stop, whose diagnostic names `E3006` ([Index bounds](./ir.md#index-bounds)):

```text
Shape = [d_0, d_1, ..., d_{n-1}]   where each d_i ∈ ℕ (0 included)
Rank(Shape) = n
```

Core v1 has no symbolic or unknown dimension: every dimension of a type is known at check time
([The tensor type](#the-tensor-type)). A dimension that a program computes at run time (for example an
argument of a constructor function) is a value, not a dimension of a type.

The verifier rejects tensors with a negative dimension; a negative dimension that
is known only at run time makes the defined stop. Scalars remain
rank-0 tensors with an empty `[]` shape and therefore have no dimension to
check.

## The tensor type

`Tensor` is a predeclared generic type name. Its argument list holds a dtype and a shape, and both are required:
`Tensor<f32, [2, 3]>` is the type of a tensor of `f32` elements with the shape `[2, 3]`. The grammar has no rule of its
own for the tensor type: `IdentifierType` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) takes the type arguments,
and a `TypeArgument` is a type or a `Shape`.

- **Dtype.** The dtype MUST be a dtype of the profile; in Core v1 the dtypes are `i32`, `i64`, `f32` and `f64`. Another
  type MUST be refused at check time with [`E2005`](./errors.md#e2005-invalid-dtype-for-operation), and the message
  names the set: `Tensor<bool, [2]>` is refused.
- **Both arguments.** `Tensor<f32>` (no shape) MUST be refused at check time. `tensor<f32[2]>` is not a type: the
  message of [`E1105`](./errors.md#e1105-form-that-mind-writes-another-way) gives `Tensor<f32, [2]>`.
- **Dimensions.** A dimension is an integer literal or an identifier (`Dimension`). An identifier MUST name a `const`
  of the type `i64` in scope; another name MUST be refused at check time with
  [`E3013`](./errors.md#e3013-unknown-dimension-name). `?` is not a dimension and MUST be refused with
  [`E1105`](./errors.md#e1105-form-that-mind-writes-another-way). A negative dimension is refused with
  [`E3006`](./errors.md#e3006-negative-dimension).
- **Size.** Each dimension, and the count of elements of the shape (the product of its dimensions), MUST be at most
  2^63 - 1; a larger one MUST be refused at check time with [`E3012`](./errors.md#e3012-shape-too-large).
- **Rank 0.** `Tensor<D, []>` is the type `D`: a rank-0 tensor and a scalar of the dtype `D` are one type.

```mind
const N: i64 = 3;

fn scale(x: Tensor<f32, [N]>, k: f32) -> Tensor<f32, [N]> {
    return x * k;
}

fn first(t: Tensor<f32, []>) -> f32 {
    return t;
}
```

The parameter `x` has the shape `[3]`; `k` is a scalar and extends to that shape
([Elementwise binary](#elementwise-binary)); `t` has the type `f32`.

## Tensor literals

An array literal whose expected type is `Tensor<D, S>` is a tensor literal. Its nesting depth is the rank, and the
lengths of its nested lists are the dimensions; they MUST equal the shape `S`, else the literal MUST be refused at
check time with [`E3010`](./errors.md#e3010-invalid-shape-in-literal). A ragged literal, whose nested lists at one
depth have different lengths, MUST be refused with `E3010` as well. A cast to a tensor type, written with a type name
(`e as V` after `type V = Tensor<f32, [2]>;`), MUST be refused with [`E2016`](./errors.md#e2016-invalid-cast); the type
of a cast has no type-argument list, so `e as Tensor<f32, [2]>` has no derivation ([Casts](./language.md#casts)). The
tensor constructor `tensor(e, dtype: D)` ([Tensor operations](./language.md#tensor-operations)) converts the dtype.

```mind
let m: Tensor<f32, [2, 3]> = [[1.0, 2.0, 3.0],
                              [4.0, 5.0, 6.0]];
```

`let t: Tensor<f32, [2]> = [1.0, 2.0, 3.0];` (three elements for the dimension 2) and
`let r: Tensor<f32, [2, 2]> = [[1.0], [2.0, 3.0]];` (a ragged literal) are refused with `E3010`.

## Indexing a tensor

An index of a tensor holds one item for each leading axis, separated by `,` (`IndexOperator` and `IndexItem` of
[`grammar-syntax.ebnf`](./grammar-syntax.ebnf)): `t[i, j]`. It holds at most rank items; a source with more MUST be
refused at check time with [`E3014`](./errors.md#e3014-too-many-index-items). The axes after the last item are taken
whole. An item that is a scalar index drops its axis, and an item that is a slice (`s:e:k` and its forms with omitted
parts, [Tuple index](./language.md#tuple-index)) keeps it. An index of an array `[T; n]` holds one item.

```mind
fn pick(t: Tensor<f32, [4, 3]>) -> Tensor<f32, [4]> {
    return t[:, 1];
}
```

`t[2]` has the shape `[3]`, `t[2, 1]` is an `f32`, `t[:, 1]` has the shape `[4]` and `t[1:3, :]` has the shape
`[2, 3]`. `t[0, 1, 2]` on this rank-2 tensor is refused with `E3014`.

## Comparison of tensors

`==` and `!=` on two tensors of one dtype and one shape compare the whole values and give one `bool`; there is no
broadcast. `<`, `<=`, `>` and `>=` with a tensor operand MUST be refused at check time with
[`E2008`](./errors.md#e2008-operator-not-defined-for-tensor-operands).

## Broadcasting

Broadcasting is the rule by which the dotted operators `.+`, `.-`, `.*`, `./` and `.%` and the batch dimensions of
`matmul` extend the shapes of two operands to one shape ([Elementwise binary](#elementwise-binary)). The plain
operators do not broadcast. The rule aligns the two shapes from the right and extends a dimension of size 1.

Given two shapes `A` and `B`, broadcasting proceeds as:

1. Align shapes from the **right** by inserting leading dimensions of size `1`
   to the shorter shape as needed.
2. For each dimension (from right to left):
   - if the extents are equal (`a_i == b_i`), the result extent is that value;
   - if one of the extents is `1`, the result extent is the other value;
   - otherwise broadcasting fails.

Formally, let `A'` and `B'` be the aligned shapes of the same rank `k`. Then
for each i ∈ {0, ..., k-1}:

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

A binary elementwise operation has two source forms, and the form says whether the shapes broadcast
([Tensor operators and broadcasting](./language.md#tensor-operators-and-broadcasting)):

- **Plain operators** `+`, `-`, `*`, `/` and `%` on two tensors need one dtype and one shape; the output has that
  shape. A scalar operand extends to the shape of the tensor operand. A plain operator on two tensors of different
  shapes MUST be refused at check time with [`E3015`](./errors.md#e3015-plain-operator-on-two-shapes), and the fix
  is the dotted operator.
- **Dotted operators** `.+`, `.-`, `.*`, `./` and `.%` broadcast. The operands share a dtype, and the output shape is
  the broadcasted shape of the two inputs:

  ```text
  Shape_out = Broadcast(Shape_lhs, Shape_rhs)
  ```

  If broadcasting fails (as defined above), the source MUST be refused with
  [`E3001`](./errors.md#e3001-broadcasting-failure). A dotted operator that expands no operand (two tensors of one
  shape, a scalar operand, or no tensor operand) MUST be refused at check time with
  [`E3016`](./errors.md#e3016-dotted-operator-with-no-expansion), and the fix is the plain operator. A dotted operator
  has the precedence of its plain operator.

Two operands of different dtypes MUST be refused with
[`E2004`](./errors.md#e2004-dtype-mismatch-in-binary-operation) in both forms. So every expansion of a shape is
written in the source, and one search for the dotted operators finds every one.

```mind
fn outer_sum(col: Tensor<f32, [3, 1]>, row: Tensor<f32, [1, 4]>) -> Tensor<f32, [3, 4]> {
    return col .+ row;
}

fn add(a: Tensor<f32, [3, 4]>, b: Tensor<f32, [3, 4]>) -> Tensor<f32, [3, 4]> {
    return a + b;
}
```

`col + row` (a plain operator on the shapes `[3, 1]` and `[1, 4]`) is refused with `E3015`, and the fix is
`col .+ row`. `a .+ b` on two tensors of the shape `[3, 4]`, `t .* 2.0` and `a .+ b` on two `i64` scalars are refused
with `E3016`, and the fix is the plain operator. The IR operations of both forms are the operations of
[Core IR](./ir.md#binary-operations); the Core v1 conformance suite holds rows for both forms and for a failing
broadcast.

## Reductions

Core v1 defines two forms of reduction:

- **full reductions** that reduce all axes to a scalar (rank-0);
- **axis-aware reductions** that reduce along specified axes, preserving the
  remaining dimensions.

Both forms are part of Core v1. The `Sum` and `Mean` instructions support both
modes via the `axes` and `keepdims` parameters (see `ir.md` for the full
instruction specification and `conformance.md` for required test coverage).

### Full reductions

A full reduction (`axes = []`, i.e. empty axes list) reduces all dimensions:

```text
Input:  Tensor<f32, [d_0, d_1, ..., d_{n-1}]>
Output: Tensor<f32, []>    (rank-0 scalar, the type f32)
```

If the input is already a scalar (`[]`), the output is also a scalar of the
same shape. Implementations must not silently change the rank (for example, to
`[1]`); the scalar representation is part of the contract.

### Axis-aware reductions

Axis-parameterized reductions (for example, `Sum(input, axes=[1], keepdims=false)`)
reduce along the specified axes:

- If `keepdims = false`: the reduced axes are removed from the output shape.
  Example: `Sum([3, 4, 5], axes=[1], keepdims=false)` produces shape `[3, 5]`.
- If `keepdims = true`: the reduced axes are replaced with size `1`.
  Example: `Sum([3, 4, 5], axes=[1], keepdims=true)` produces shape `[3, 1, 5]`.

The following error model applies to axis-aware reductions:

- invalid or out-of-range axes must produce a shape error;
- duplicate axis indices must produce a shape error;
- negative axis indices are supported and normalized via `axis = axis + rank`
  when `axis < 0`.

## Matrix multiplication

Core v1 defines a canonical **matrix multiplication** shape rule for
`tensor.matmul`:

- inputs must be **rank-2 or greater** tensors;
- the trailing two dimensions participate in the matrix multiply;
- the inner dimensions must match.

Formally:

```text
A: Tensor<T, [M, K]>
B: Tensor<T, [K, N]>
----------------------------
matmul(A, B): Tensor<T, [M, N]>
```

If either input has rank smaller than 2, or if `K` does not match between the
inputs, the operator must produce a shape error.

The source form of the matrix product is the call `matmul(a, b)`. The token `@` has no production: `a @ b` MUST be
refused with [`E1105`](./errors.md#e1105-form-that-mind-writes-another-way), and the message gives `matmul(a, b)`
([Tokens](./lexical.md#tokens)).

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
implement. The reference implementation in `star-ga/mind` exposes a small shape
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
