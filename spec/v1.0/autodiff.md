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

This chapter specifies the **Core v1 reverse-mode autodiff** pipeline that operates on canonical Core
IR. The rules align with the implemented behaviour in the public compiler
[`cputer/mind`](https://github.com/cputer/mind) and describe no additional proprietary features.

## Model

- Autodiff runs over verified **Core IR modules**, not over source syntax.
- Gradient construction produces a **gradient module** containing primal and gradient instructions.
  Gradients are mapped by a deterministic association: `gradients : ValueId → ValueId` (i.e., a map
  from each differentiated primal `ValueId` to its gradient `ValueId`).
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

Autodiff implements reverse-mode rules consistent with standard tensor calculus. The following sections
provide complete mathematical formulations for each Core v1 operation.

### Notation

- `∇_y L`: upstream gradient (gradient of loss L with respect to output y)
- `∂y/∂x`: local derivative (derivative of output y with respect to input x)
- `∇_x L = ∇_y L · ∂y/∂x`: downstream gradient via chain rule
- `⊙`: elementwise (Hadamard) product
- `shape(x)`: shape of tensor x
- `ReduceSum(g, axes)`: sum gradient g along specified axes to restore original shape
- `Broadcast(g, shape_target, shape_original)`: reduce gradient from broadcasted shape back to original

### Constants

- **`ConstI64(value)`, `ConstF32(value)`, `ConstF64(value)`, `ConstTensor(...)`**
  - Constants have no inputs and do not participate in differentiation
  - Gradient: none (constants are not differentiated)

### Binary operations

- **`Add: y = x₁ + x₂`**
  - Forward: `y = x₁ + x₂` (with broadcasting)
  - Gradient for `x₁`: `∇_{x₁} L = ReduceSum(∇_y L, broadcast_axes(shape(x₁), shape(y)))`
  - Gradient for `x₂`: `∇_{x₂} L = ReduceSum(∇_y L, broadcast_axes(shape(x₂), shape(y)))`
  - If no broadcasting occurred for an operand, gradient passes through unchanged
  - Example: `x₁=[2,1], x₂=[2,3] → y=[2,3]`, then `∇_{x₁}` sums gradient over axis 1

- **`Sub: y = x₁ - x₂`**
  - Forward: `y = x₁ - x₂` (with broadcasting)
  - Gradient for `x₁`: `∇_{x₁} L = ReduceSum(∇_y L, broadcast_axes(shape(x₁), shape(y)))`
  - Gradient for `x₂`: `∇_{x₂} L = -ReduceSum(∇_y L, broadcast_axes(shape(x₂), shape(y)))`
  - Note the negation for the right operand (∂y/∂x₂ = -1)

- **`Mul: y = x₁ * x₂`**
  - Forward: `y = x₁ ⊙ x₂` (elementwise with broadcasting)
  - Local derivatives: `∂y/∂x₁ = x₂`, `∂y/∂x₂ = x₁`
  - Gradient for `x₁`: `∇_{x₁} L = ReduceSum(∇_y L ⊙ Broadcast(x₂, shape(y)), broadcast_axes(shape(x₁), shape(y)))`
  - Gradient for `x₂`: `∇_{x₂} L = ReduceSum(∇_y L ⊙ Broadcast(x₁, shape(y)), broadcast_axes(shape(x₂), shape(y)))`
  - Product rule: each operand's gradient is upstream gradient times the other operand

### Reductions

- **`Sum: y = Sum(x, axes, keepdims)`**
  - Forward: `y = Σ_{i ∈ axes} x_i`
  - Local derivative: `∂y/∂x_j = 1` for all j
  - Gradient: `∇_x L = ExpandToOriginalShape(∇_y L, shape(x), axes, keepdims)`
  - If `keepdims=true`: gradient has same rank as input with 1s at reduced axes; broadcast to restore
  - If `keepdims=false`: gradient has lower rank; insert 1s at reduced axes then broadcast
  - Implementation: uses `ExpandDims` if keepdims=false, then broadcasts gradient to input shape

- **`Mean: y = Mean(x, axes, keepdims)`**
  - Forward: `y = (1/N) Σ_{i ∈ axes} x_i` where `N = ∏_{axis ∈ axes} shape(x)[axis]`
  - Local derivative: `∂y/∂x_j = 1/N` for all j
  - Gradient: `∇_x L = (1/N) · ExpandToOriginalShape(∇_y L, shape(x), axes, keepdims)`
  - Same expansion as Sum, but scaled by reciprocal of reduced element count

### Shape manipulation

- **`Reshape: y = Reshape(x, new_shape)`**
  - Forward: reinterprets tensor storage in new shape
  - Gradient: `∇_x L = Reshape(∇_y L, shape(x))`
  - Reshape gradient back to original input shape

- **`Transpose: y = Transpose(x, permutation)`**
  - Forward: permutes axes according to permutation `perm`
  - Gradient: `∇_x L = Transpose(∇_y L, inverse_perm)`
  - Inverse permutation undoes the original transpose
  - If `perm = [2, 0, 1]`, then `inverse_perm = [1, 2, 0]`

- **`ExpandDims: y = ExpandDims(x, axes)`**
  - Forward: inserts singleton dimensions at specified axes
  - Gradient: `∇_x L = Squeeze(∇_y L, axes)`
  - Removes inserted dimensions to restore original shape

- **`Squeeze: y = Squeeze(x, axes)`**
  - Forward: removes singleton dimensions at specified axes
  - Gradient: `∇_x L = ExpandDims(∇_y L, axes)`
  - Reinserts squeezed dimensions

### Indexing and slicing

- **`Index: y = Index(x, indices)`**
  - Forward: extracts single element at multi-dimensional index
  - Gradient: `∇_x L = ZeroTensor(shape(x))` with `∇_y L` placed at `indices` position
  - Scatter gradient back to indexed position; all other elements receive zero gradient

- **`Slice: y = Slice(x, starts, ends, steps)`**
  - Forward: extracts sub-tensor
  - Gradient: `∇_x L = ZeroTensor(shape(x))` with `∇_y L` scattered to sliced region
  - Pad zeros outside sliced region; place upstream gradient in corresponding slice

- **`Gather: y = Gather(x, indices)`**
  - Forward: gathers elements using index tensor
  - Gradient: `∇_x L = ScatterAdd(ZeroTensor(shape(x)), indices, ∇_y L)`
  - Scatter gradient values back to gathered positions; duplicate indices accumulate gradients

### Linear and tensor algebra

- **`Dot: y = Dot(x₁, x₂)`**
  - **Rank-1 × Rank-1** (inner product): `y = Σᵢ x₁[i] · x₂[i]`
    - `∇_{x₁} L = ∇_y L · x₂`
    - `∇_{x₂} L = ∇_y L · x₁`
  - **Rank-2 × Rank-1** (matrix-vector): `y[i] = Σⱼ x₁[i,j] · x₂[j]`
    - `∇_{x₁} L = ∇_y L ⊗ x₂ᵀ` (outer product)
    - `∇_{x₂} L = x₁ᵀ · ∇_y L`
  - **Rank-1 × Rank-2** (vector-matrix): `y[j] = Σᵢ x₁[i] · x₂[i,j]`
    - `∇_{x₁} L = ∇_y L · x₂ᵀ`
    - `∇_{x₂} L = x₁ᵀ ⊗ ∇_y L` (outer product)

- **`MatMul: y = MatMul(x₁, x₂)`** where `x₁: [..., M, K]`, `x₂: [..., K, N]`, `y: [..., M, N]`
  - Forward: batched matrix multiplication
  - Gradient for `x₁`: `∇_{x₁} L = MatMul(∇_y L, Transpose(x₂, last_two_axes))`
    - `∇_{x₁}[..., i, k] = Σⱼ ∇_y L[..., i, j] · x₂[..., k, j]`
    - If batch dimensions were broadcast, reduce gradient appropriately
  - Gradient for `x₂`: `∇_{x₂} L = MatMul(Transpose(x₁, last_two_axes), ∇_y L)`
    - `∇_{x₂}[..., k, j] = Σᵢ x₁[..., i, k] · ∇_y L[..., i, j]`
    - If batch dimensions were broadcast, reduce gradient appropriately

- **`Conv2d: y = Conv2d(input, filter, strides, padding)`**
  - Forward: 2D convolution NHWC format
  - Gradient for `input`:
    - `∇_{input} L = Conv2dBackwardInput(∇_y L, filter, input_shape, strides, padding)`
    - Convolves gradient with flipped filter to distribute gradients back to input positions
  - Gradient for `filter`:
    - `∇_{filter} L = Conv2dBackwardFilter(input, ∇_y L, filter_shape, strides, padding)`
    - Convolves input with gradient to accumulate filter gradients
  - Implementation uses standard convolution backward formulas maintaining NHWC/HWCF layouts

### Activation and elementwise unary operations

- **`Relu: y = Relu(x) = max(0, x)`**
  - Forward: `y[i] = x[i] if x[i] > 0 else 0`
  - Local derivative: `∂y/∂x = 1 if x > 0 else 0` (undefined at x=0; implementations typically use 0)
  - Gradient: `∇_x L = ∇_y L ⊙ (x > 0)`
  - Multiply upstream gradient by indicator function of positive inputs

- **`Neg: y = -x`**
  - Forward: `y = -x`
  - Local derivative: `∂y/∂x = -1`
  - Gradient: `∇_x L = -∇_y L`

- **`Exp: y = exp(x)`**
  - Forward: `y = eˣ`
  - Local derivative: `∂y/∂x = eˣ = y`
  - Gradient: `∇_x L = ∇_y L ⊙ y`
  - Multiply upstream gradient by forward output (efficient: reuse forward result)

- **`Log: y = log(x)`**
  - Forward: `y = ln(x)`
  - Local derivative: `∂y/∂x = 1/x`
  - Gradient: `∇_x L = ∇_y L ⊙ (1/x)`
  - Multiply upstream gradient by reciprocal of input

### Unsupported operations

The following operations trigger `AutodiffError::UnsupportedOp` (E5001):

- **`Div`**: Division autodiff is NOT implemented. Use `Mul` with reciprocal if differentiable division
  is required.
- **`Conv2d`**: Convolution backward passes are NOT implemented in Core v1. Forward-only Conv2d is
  supported; attempting autodiff through Conv2d returns `UnsupportedOp`.

Any other instruction not listed above MUST also trigger `AutodiffError::UnsupportedOp`. Implementations
extending Core v1 with additional operations MUST document their derivative rules or explicitly mark
them as non-differentiable.

## Determinism

- Input IR is canonicalised and verified before autodiff.
- Generated gradient IR is canonicalised. For a fixed compiler version, identical input modules MUST
  produce **bit-for-bit identical** gradient modules.
- Error reporting is deterministic with stable categorisation as described above.
