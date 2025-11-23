<!--
Copyright (c) 2025 STARGA Inc.
MIND Language Specification — Community Edition
Licensed under the MIT License. See LICENSE-MIT.
-->
                                                                                                                                ﻿
# Standard Library (Core APIs)

> **Status:** Draft
> **Last updated:** 2025-11-07
> **MIND Spec Section:** Standard library overview

The MIND standard library defines the foundational modules shipped with every toolchain. This page
summarises the stable surface area exposed to user programs, focusing on the Core and
Differentiable conformance profiles. Each module listed here is available without additional
imports unless otherwise noted.

---

## Module map

| Module | Purpose | Example entry points |
| ------ | ------- | -------------------- |
| `core` | Primitive types, assertions, and option/result helpers. | `assert`, `panic`, `Option`, `Result` |
| `math` | Scalar math over integers and floats with differentiable overloads. | `abs`, `sqrt`, `sin`, `cos`, `exp`, `log` |
| `tensor` | Dense tensor construction and algebra. | `zeros`, `ones`, `eye`, `matmul`, `transpose` |
| `diff` | Differentiation entry points backed by the language’s AD semantics. | `derivative`, `jacobian`, `with_tangent` |
| `io` | Minimal console I/O for debugging and examples. | `print`, `println`, `eprint`, `eprintln` |

The reference implementation keeps these modules in [`cputer/mind-runtime`](https://github.com/cputer/mind-runtime)
(informative). Implementations MAY add extension modules provided they do not shadow or alter the
behaviour of the core set.

---

## Core utilities

### Assertions and failure

| Symbol | Signature | Notes |
| ------ | --------- | ----- |
| `assert(cond: bool)` | `()->` | Aborts evaluation with a diagnostic if `cond` is `false`. Diagnostics SHOULD include the source span. |
| `panic(msg: string)` | `()->` | Terminates execution immediately. Implementations SHOULD surface the panic message to the host environment. |

### Optional and error-aware types

`Option<T>` and `Result<T, E>` mirror the semantics found in other ML-family languages:

- `Option::some(value)` wraps a present value; `Option::none()` represents absence.
- `Result::ok(value)` and `Result::err(error)` model success and failure respectively.
- Pattern matching on these variants MUST be exhaustive. Unhandled cases SHOULD trigger a static
  type error during exhaustiveness checking.

`Result` interoperates with the language’s error propagation operator (`?`). When applied to a
`Result::err`, the operator short-circuits evaluation, propagating the error to the caller.

---

## Math

The `math` module exposes scalar operations over `i32`, `i64`, `f32`, and `f64`. Functions MUST
signal domain errors using `Result` rather than panicking (e.g., `sqrt(-1.0)` returns an error).
Where applicable, implementations SHOULD provide differentiable overloads that match the rules in
[Automatic Differentiation](../../spec/v1.0/autodiff.md).

| Function | Signature | Behaviour |
| -------- | --------- | --------- |
| `abs(x)` | `(i32 | i64 | f32 | f64) -> same` | Returns the absolute value of `x`. Differentiable for floating-point inputs. |
| `sqrt(x)` | `(f32 | f64) -> Result<same, DomainError>` | Computes the principal square root. Domain errors occur for `x < 0`. |
| `sin(x)` / `cos(x)` | `(f32 | f64) -> same` | Trigonometric functions operating on radians. |
| `exp(x)` | `(f32 | f64) -> same` | Exponential function. |
| `log(x)` | `(f32 | f64) -> Result<same, DomainError>` | Natural logarithm; domain errors occur for `x <= 0`. |

Implementations MAY extend `math` with additional functions (e.g., `tanh`, `atan2`) provided their
semantics are well-defined and documented.

---

## Tensor

Tensor operations build on the language’s dense array representation. Implementations MUST maintain
row-major layout compatibility with the reference runtime when exchanging data across FFI
boundaries.

| Function | Signature | Behaviour |
| -------- | --------- | --------- |
| `zeros(shape: [i64])` | `-> Tensor` | Allocates a tensor of the given shape initialised with zeros. |
| `ones(shape: [i64])` | `-> Tensor` | Allocates a tensor initialised with ones. |
| `eye(n: i64)` | `-> Tensor` | Constructs an `n x n` identity matrix. |
| `matmul(a: Tensor, b: Tensor)` | `-> Tensor` | Matrix multiplication. Dimension mismatches MUST raise a runtime error. |
| `transpose(x: Tensor)` | `-> Tensor` | Transposes the last two dimensions. |

Shape inference SHOULD validate dimensions statically where possible. Differentiable backends MUST
propagate tangents through `matmul` and `transpose` according to the rules in the autodiff
specification.

---

## Differentiation helpers

The `diff` module is the stable entry point for user-invoked differentiation. These functions are
thin wrappers over the language-level AD semantics defined in [Automatic
Differentiation](../../spec/v1.0/autodiff.md).

| Function | Signature | Behaviour |
| -------- | --------- | --------- |
| `derivative(f, x)` | `(fn(T)->U, T) -> U'` | Computes the derivative of a single-variable function at `x`. |
| `jacobian(f, x)` | `(fn(Vec<T>)->Vec<U>, Vec<T>) -> Tensor` | Produces the Jacobian matrix for multi-variable functions. |
| `with_tangent(x, t)` | `(T, T') -> diff T` | Attaches an explicit tangent `t` to the primal `x`. Useful for custom sensitivity analysis. |

Errors arising from non-differentiable operations MUST surface as diagnostics that include both the
primal expression and the offending operation.

---

## I/O (minimal)

Console I/O is intentionally minimal to keep the core runtime lightweight. These functions are
synchronous and intended for debugging or small utilities.

| Function | Signature | Behaviour |
| -------- | --------- | --------- |
| `print(x)` | `(any) ->` | Writes `x` to standard output without a trailing newline. |
| `println(x)` | `(any) ->` | Writes `x` followed by a newline to standard output. |
| `eprint(x)` | `(any) ->` | Writes to standard error without a trailing newline. |
| `eprintln(x)` | `(any) ->` | Writes to standard error with a trailing newline. |

Implementations MAY provide buffered or asynchronous variants as extensions, but these are outside
the scope of the core standard library.

---

## Compatibility and versioning

- Functions listed here form the compatibility baseline for `mind-2025a` toolchains.
- Backwards-incompatible changes MUST be preceded by a deprecation cycle documented in the
  changelog.
- Implementations SHOULD keep APIs deterministic across CPU and GPU backends. Where numeric drift is
  unavoidable (e.g., reduced precision on specialised accelerators), this SHOULD be documented in
  release notes.

---

[ Back to Spec Index](index.md)
