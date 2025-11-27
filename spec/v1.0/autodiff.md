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

# Automatic Differentiation (Normative)

This chapter specifies the semantics for differentiable computation in MIND. Implementations that
claim Differentiable or Full conformance (see [Overview](./overview.md)) MUST adhere to these rules.
Background material and worked examples are recorded in
[`cputer/mind/docs/autodiff`](https://github.com/cputer/mind/tree/main/docs/autodiff).

## Differentiable values

A differentiable value is represented as a pair `(primal, tangent)` encapsulated by the `diff T`
wrapper. Implementations MUST ensure:

- The primal component has type `T`.
- The tangent component has type `T'` determined by the tangent functor defined in the reference
  documentation.
- Projecting a `diff T` to `T` drops the tangent component and is only permitted when the projection
  is explicitly requested or implied by a rule in this chapter.

## Differentiable functions

A function `f : (diff T1, ..., diff Tn) -> diff U` induces a derivative `Df` with the same arity.
Implementations MUST produce derivatives using forward-mode automatic differentiation unless a
future specification revision defines additional modes.

- Function bodies execute on primal values while tangents are propagated alongside each operation.
- Higher-order functions MUST propagate derivatives by differentiating the function arguments.
- Closures capture tangents for captured differentiable variables.

## Operator rules

The following rules are normative:

- **Arithmetic**: addition, subtraction, and multiplication propagate tangents using the standard
  product rule. Division MUST signal a runtime error when the primal denominator is zero; tangent
  propagation follows the quotient rule otherwise.
- **Control flow**: differentiable branches are resolved on the primal value. Both branches MUST be
  type-checked, and tangents follow the executed branch.
- **Loops**: tangents accumulate per iteration. Implementations MUST guarantee convergence of the
  tangent sequence for finite loops; divergent loops have undefined derivative.
- **Trait methods**: when a trait specifies differentiable behaviour, implementations MUST provide
  tangent propagation consistent with the trait law definitions.

Informative derivations are available in the compiler documentation under
[`cputer/mind/docs/autodiff`](https://github.com/cputer/mind/tree/main/docs/autodiff#rules).

## Differentiation built-ins

The standard library exposes the following built-ins:

- `diff::derivative(f, x)` computes the derivative of single-variable function `f` at `x`.
- `diff::jacobian(f, x)` produces the Jacobian matrix for a multivariate function `f` at `x`.

Implementations MUST provide these built-ins for types that satisfy the differentiable trait bounds
and MAY extend them to additional numeric types.

## Error handling

If differentiation fails due to unsupported operations (such as non-differentiable primitives), the
implementation MUST emit a diagnostic referencing both the primal expression and the unsupported
operation. Implementations SHOULD suggest possible workarounds, such as inserting explicit
`primal()` projections.
