<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Standard Library (Normative)

This chapter defines the Core v1 standard library: the set of functions, types, and modules that
conforming implementations MUST provide. The standard library provides high-level interfaces to Core
IR operations and extends them with conveniences for common patterns.

All standard library entities are available without explicit imports unless stated otherwise.

## Module organization

The standard library is organized into five modules:

1. **`core`**: Fundamental types and control flow primitives
2. **`math`**: Scalar mathematical functions (elementwise when lifted to tensors)
3. **`tensor`**: Tensor construction, manipulation, and linear algebra
4. **`diff`**: Automatic differentiation entry points
5. **`io`**: Minimal console I/O for debugging

## `core` module

### Types

- **`unit`**: The unit type `()`, representing no value
- **`bool`**: Boolean type with values `true` and `false`
- **`i32`**, **`i64`**: Signed integers (32-bit and 64-bit)
- **`f32`**, **`f64`**: IEEE 754 floating-point (single and double precision)
- **`Option<T>`**: Optional value type
  - Variants: `Some(T)`, `None`
  - Used for values that may or may not be present
- **`Result<T, E>`**: Result type for fallible operations
  - Variants: `Ok(T)`, `Err(E)`
  - Used for operations that may succeed with value T or fail with error E

### Control flow and assertions

- **`assert(condition: bool) -> unit`**
  - Aborts execution with a diagnostic if `condition` is `false`
  - Diagnostic MUST include source location (file, line, column)
  - Implementations MAY include the condition text in the diagnostic

- **`panic(message: string) -> !`**
  - Terminates execution immediately with the given message
  - Return type `!` (never) indicates this function does not return
  - Message MUST be surfaced to the user/host environment

- **`unreachable() -> !`**
  - Marks code paths that MUST NOT be reached
  - If reached, produces a panic with diagnostic "entered unreachable code"

### Pattern matching support

- **`Option<T>::is_some() -> bool`**
- **`Option<T>::is_none() -> bool`**
- **`Option<T>::unwrap() -> T`** (panics if None)
- **`Option<T>::unwrap_or(default: T) -> T`**
- **`Result<T, E>::is_ok() -> bool`**
- **`Result<T, E>::is_err() -> bool`**
- **`Result<T, E>::unwrap() -> T`** (panics if Err)
- **`Result<T, E>::unwrap_or(default: T) -> T`**

## `math` module

Scalar mathematical functions. When applied to tensors, these operate elementwise.

### Basic arithmetic

- **`abs<T: Numeric>(x: T) -> T`**
  - Absolute value: `|x|`
  - Differentiable for floating-point: `∂abs/∂x = sign(x)` (undefined at x=0, typically 0)
  - Supported dtypes: i32, i64, f32, f64

- **`neg<T: Numeric>(x: T) -> T`**
  - Negation: `-x`
  - Differentiable: `∂neg/∂x = -1`
  - Supported dtypes: i32, i64, f32, f64

- **`min<T: Ord>(a: T, b: T) -> T`**
  - Minimum of two values
  - For tensors: elementwise minimum with broadcasting
  - Not differentiable (discontinuous gradient at a=b)

- **`max<T: Ord>(a: T, b: T) -> T`**
  - Maximum of two values
  - For tensors: elementwise maximum with broadcasting
  - Not differentiable (discontinuous gradient at a=b)

### Exponential and logarithmic

- **`exp<T: Float>(x: T) -> T`**
  - Exponential function: `e^x`
  - Differentiable: `∂exp/∂x = exp(x)`
  - Supported dtypes: f32, f64
  - Semantics: matches exp() from ir.md#activation-and-elementwise-unary-operations

- **`log<T: Float>(x: T) -> Result<T, DomainError>`**
  - Natural logarithm: `ln(x)`
  - Differentiable: `∂log/∂x = 1/x`
  - Supported dtypes: f32, f64
  - Domain: x > 0; returns Err(DomainError) for x ≤ 0
  - Semantics: matches log() from ir.md#activation-and-elementwise-unary-operations

- **`log2<T: Float>(x: T) -> Result<T, DomainError>`**
  - Base-2 logarithm: `log₂(x)`
  - Differentiable: `∂log2/∂x = 1/(x ln(2))`
  - Domain: x > 0

- **`log10<T: Float>(x: T) -> Result<T, DomainError>`**
  - Base-10 logarithm: `log₁₀(x)`
  - Differentiable: `∂log10/∂x = 1/(x ln(10))`
  - Domain: x > 0

- **`sqrt<T: Float>(x: T) -> Result<T, DomainError>`**
  - Square root: `√x`
  - Differentiable: `∂sqrt/∂x = 1/(2√x)`
  - Supported dtypes: f32, f64
  - Domain: x ≥ 0; returns Err(DomainError) for x < 0

- **`pow<T: Float>(base: T, exponent: T) -> T`**
  - Power function: `base^exponent`
  - Differentiable: `∂pow/∂base = exponent · base^(exponent-1)`
  - Special cases: `pow(0, 0) = 1`, `pow(x, 0) = 1`

### Trigonometric

- **`sin<T: Float>(x: T) -> T`**
  - Sine function (radians)
  - Differentiable: `∂sin/∂x = cos(x)`
  - Supported dtypes: f32, f64

- **`cos<T: Float>(x: T) -> T`**
  - Cosine function (radians)
  - Differentiable: `∂cos/∂x = -sin(x)`
  - Supported dtypes: f32, f64

- **`tan<T: Float>(x: T) -> T`**
  - Tangent function (radians)
  - Differentiable: `∂tan/∂x = sec²(x) = 1/cos²(x)`
  - Supported dtypes: f32, f64

- **`asin<T: Float>(x: T) -> Result<T, DomainError>`**
  - Arcsine (radians)
  - Differentiable: `∂asin/∂x = 1/√(1-x²)`
  - Domain: -1 ≤ x ≤ 1

- **`acos<T: Float>(x: T) -> Result<T, DomainError>`**
  - Arccosine (radians)
  - Differentiable: `∂acos/∂x = -1/√(1-x²)`
  - Domain: -1 ≤ x ≤ 1

- **`atan<T: Float>(x: T) -> T`**
  - Arctangent (radians)
  - Differentiable: `∂atan/∂x = 1/(1+x²)`
  - Supported dtypes: f32, f64

- **`atan2<T: Float>(y: T, x: T) -> T`**
  - Two-argument arctangent: `atan2(y, x) = atan(y/x)` with correct quadrant
  - Range: (-π, π]
  - Differentiable with respect to both arguments

### Hyperbolic

- **`sinh<T: Float>(x: T) -> T`**
  - Hyperbolic sine: `(e^x - e^(-x)) / 2`
  - Differentiable: `∂sinh/∂x = cosh(x)`

- **`cosh<T: Float>(x: T) -> T`**
  - Hyperbolic cosine: `(e^x + e^(-x)) / 2`
  - Differentiable: `∂cosh/∂x = sinh(x)`

- **`tanh<T: Float>(x: T) -> T`**
  - Hyperbolic tangent: `sinh(x) / cosh(x)`
  - Differentiable: `∂tanh/∂x = 1 - tanh²(x)`
  - Common activation function in neural networks

### Rounding

- **`floor<T: Float>(x: T) -> T`**
  - Floor function: largest integer ≤ x
  - Not differentiable (discontinuous)

- **`ceil<T: Float>(x: T) -> T`**
  - Ceiling function: smallest integer ≥ x
  - Not differentiable (discontinuous)

- **`round<T: Float>(x: T) -> T`**
  - Round to nearest integer (ties round to even)
  - Not differentiable (discontinuous)

## `tensor` module

Tensor construction, manipulation, and linear algebra operations.

### Construction

- **`zeros(shape: [i64], dtype: DType = f32) -> Tensor<dtype>`**
  - Creates tensor filled with zeros
  - Shape dimensions MUST be positive integers
  - Example: `zeros([2, 3])` produces rank-2 tensor with shape [2, 3]

- **`ones(shape: [i64], dtype: DType = f32) -> Tensor<dtype>`**
  - Creates tensor filled with ones
  - Shape dimensions MUST be positive integers

- **`full(shape: [i64], value: T, dtype: DType = infer) -> Tensor<dtype>`**
  - Creates tensor filled with constant `value`
  - Dtype inferred from value if not specified

- **`eye(n: i64, dtype: DType = f32) -> Tensor<dtype>`**
  - Creates n×n identity matrix
  - Output shape: [n, n]
  - Example: `eye(3)` produces [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

- **`arange(start: T, end: T, step: T = 1) -> Tensor<T>`**
  - Creates 1D tensor with evenly spaced values in range [start, end)
  - Output shape: [ceil((end - start) / step)]
  - Example: `arange(0, 5, 2)` produces [0, 2, 4]

- **`linspace(start: T, end: T, num: i64) -> Tensor<T>`**
  - Creates 1D tensor with `num` evenly spaced values in range [start, end]
  - Output shape: [num]
  - Includes both endpoints

### Shape operations

These functions map directly to IR operations from ir.md#shape-manipulation:

- **`reshape(input: Tensor<T>, new_shape: [i64]) -> Tensor<T>`**
  - Semantics: ir.md#shape-manipulation Reshape
  - Element count MUST be preserved
  - Exactly one dimension MAY be -1 (inferred)

- **`transpose(input: Tensor<T>, axes: [i64] = infer) -> Tensor<T>`**
  - Semantics: ir.md#shape-manipulation Transpose
  - Default (no axes): reverses all axes
  - With axes: permutes according to specified order

- **`expand_dims(input: Tensor<T>, axes: [i64]) -> Tensor<T>`**
  - Semantics: ir.md#shape-manipulation ExpandDims
  - Inserts singleton dimensions at specified positions

- **`squeeze(input: Tensor<T>, axes: [i64] = all) -> Tensor<T>`**
  - Semantics: ir.md#shape-manipulation Squeeze
  - Default: removes all dimensions of size 1
  - With axes: removes only specified dimensions (MUST have size 1)

- **`flatten(input: Tensor<T>) -> Tensor<T>`**
  - Convenience: `reshape(input, [-1])`
  - Flattens to 1D tensor

### Indexing and slicing

- **`index(input: Tensor<T>, indices: [i64]) -> T`**
  - Semantics: ir.md#indexing-and-slicing Index
  - Extracts single element (returns rank-0 scalar)

- **`slice(input: Tensor<T>, starts: [i64], ends: [i64], steps: [i64] = all_ones) -> Tensor<T>`**
  - Semantics: ir.md#indexing-and-slicing Slice
  - Default steps: [1, 1, ...]

- **`gather(input: Tensor<T>, indices: Tensor<i32|i64>) -> Tensor<T>`**
  - Semantics: ir.md#indexing-and-slicing Gather

- **`concat(tensors: [Tensor<T>], axis: i64) -> Tensor<T>`**
  - Concatenates tensors along specified axis
  - All tensors MUST have same shape except along concat axis
  - Output shape: sum of extents at concat axis, other dims unchanged

- **`stack(tensors: [Tensor<T>], axis: i64 = 0) -> Tensor<T>`**
  - Stacks tensors along new axis
  - All tensors MUST have identical shapes
  - Output rank: input_rank + 1

### Reductions

- **`sum(input: Tensor<T>, axes: [i64] = all, keepdims: bool = false) -> Tensor<T>`**
  - Semantics: ir.md#reductions Sum
  - Default: sum over all axes (produces scalar)
  - With axes: sum over specified axes

- **`mean(input: Tensor<T>, axes: [i64] = all, keepdims: bool = false) -> Tensor<T>`**
  - Semantics: ir.md#reductions Mean
  - Divides by product of reduced dimension extents

- **`max(input: Tensor<T>, axes: [i64] = all, keepdims: bool = false) -> Tensor<T>`**
  - Element-wise maximum over specified axes
  - Not differentiable (use softmax for differentiable approximation)

- **`min(input: Tensor<T>, axes: [i64] = all, keepdims: bool = false) -> Tensor<T>`**
  - Element-wise minimum over specified axes
  - Not differentiable

- **`prod(input: Tensor<T>, axes: [i64] = all, keepdims: bool = false) -> Tensor<T>`**
  - Product of elements over specified axes
  - Differentiable: gradient computed via quotient rule

### Linear algebra

- **`dot(lhs: Tensor<T>, rhs: Tensor<T>) -> Tensor<T>`**
  - Semantics: ir.md#linear-and-tensor-algebra Dot
  - Supports all rank combinations from ir.md

- **`matmul(lhs: Tensor<T>, rhs: Tensor<T>) -> Tensor<T>`**
  - Semantics: ir.md#linear-and-tensor-algebra MatMul
  - Batched matrix multiplication with broadcasting
  - Both inputs MUST have rank ≥ 2

- **`conv2d(input: Tensor<T>, filter: Tensor<T>, strides: [i64] = [1, 1], padding: Padding = Valid) -> Tensor<T>`**
  - Semantics: ir.md#linear-and-tensor-algebra Conv2d
  - Input format: NHWC
  - Filter format: HWCF
  - Padding: Valid, Same, or Custom

### Activation functions

- **`relu(input: Tensor<T>) -> Tensor<T>`**
  - Semantics: ir.md#activation-and-elementwise-unary-operations Relu
  - Rectified linear unit: `max(0, x)`
  - Differentiable: gradient is 1 for x>0, 0 otherwise

- **`sigmoid(input: Tensor<T>) -> Tensor<T>`**
  - Sigmoid function: `σ(x) = 1 / (1 + e^(-x))`
  - Differentiable: `∂σ/∂x = σ(x)(1 - σ(x))`
  - Output range: (0, 1)

- **`softmax(input: Tensor<T>, axis: i64 = -1) -> Tensor<T>`**
  - Softmax function: `softmax(x)ᵢ = exp(xᵢ) / Σⱼ exp(xⱼ)`
  - Normalizes to probability distribution (sums to 1 along axis)
  - Differentiable: Jacobian computed via `∂softmax/∂x = diag(softmax) - softmax ⊗ softmax`

## `diff` module

Automatic differentiation entry points.

- **`grad<T, U>(f: fn(T) -> U, x: T) -> T'`**
  - Computes gradient of scalar-valued function f at point x
  - U MUST be scalar (rank-0 tensor or f32/f64)
  - Returns gradient with same shape as x
  - Semantics: reverse-mode autodiff from autodiff.md

- **`jacobian<T, U>(f: fn(T) -> U, x: T) -> Tensor`**
  - Computes Jacobian matrix of f at x
  - If f: ℝⁿ → ℝᵐ, Jacobian has shape [m, n]
  - Each row i contains gradient of fᵢ with respect to x

- **`vjp<T, U>(f: fn(T) -> U, x: T) -> (U, fn(U') -> T')`**
  - Vector-Jacobian product (reverse-mode AD)
  - Returns: (forward output, backward function)
  - Backward function maps cotangent of output to cotangent of input

- **`jvp<T, U>(f: fn(T) -> U, x: T, v: T') -> (U, U')`**
  - Jacobian-vector product (forward-mode AD)
  - Returns: (forward output, directional derivative along v)

- **`value_and_grad<T, U>(f: fn(T) -> U, x: T) -> (U, T')`**
  - Convenience: returns both function value and gradient
  - More efficient than calling f and grad separately

## `io` module

Minimal console I/O for debugging.

- **`print<T: Display>(value: T) -> unit`**
  - Writes value to stdout without trailing newline
  - Formatting determined by Display trait

- **`println<T: Display>(value: T) -> unit`**
  - Writes value to stdout with trailing newline

- **`eprint<T: Display>(value: T) -> unit`**
  - Writes value to stderr without trailing newline

- **`eprintln<T: Display>(value: T) -> unit`**
  - Writes value to stderr with trailing newline

- **`debug<T: Debug>(value: T) -> unit`**
  - Writes debug representation to stdout
  - Shows internal structure (tensors show shape, dtype, and values)

## Implementation requirements

Conforming implementations MUST:

1. **Provide all functions listed**: No omissions permitted for Core v1 conformance
2. **Match semantics**: Behavior MUST align with referenced IR operations and autodiff rules
3. **Report errors consistently**: Use error codes from errors.md where applicable
4. **Preserve determinism**: Same inputs MUST produce same outputs (within numeric tolerance)
5. **Document extensions**: Any additional functions MUST be clearly marked as extensions

Implementations MAY:

- Provide additional convenience functions beyond this list
- Offer performance-optimized variants (e.g., fused operations)
- Support additional dtypes as extensions (e.g., f16, bf16)

## Numeric precision

- **f32 operations**: Error MUST be within 1e-6 relative tolerance or 1e-9 absolute
- **f64 operations**: Error MUST be within 1e-12 relative tolerance or 1e-15 absolute
- **Integer operations**: Exact (no approximation)
  - Overflow behavior: implementation-defined (MAY wrap, saturate, or error)

## Versioning

Standard library functions are versioned with the specification:

- Core v1.0 includes all functions listed above
- Minor versions (v1.1, v1.2) MAY add new functions, MUST NOT remove or change signatures
- Deprecations MUST be marked for at least one minor version before removal in major version
- Breaking changes require major version bump (v2.0)
