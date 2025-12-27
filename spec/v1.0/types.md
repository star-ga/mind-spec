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

# Type System (Normative)

The MIND type system enforces static correctness and enables efficient differentiation. This chapter
formalises type formation, typing judgements, inference constraints, and trait coherence. It aligns
with the reference notes in
[`cputer/mind/docs/type-system.md`](https://github.com/cputer/mind/blob/main/docs/type-system.md).

## Type formation

The following forms are part of the core language:

- **Primitive types**: `i32`, `f64`, `bool`, `unit`.
- **Composite types**: tuples `(T1, T2, ...)`, arrays `[T; n]`, and structs defined via `struct`.
- **Function types**: `(T1, ..., Tn) -> U`.
- **Trait objects**: `dyn Trait` for traits marked as object-safe.
- **Differentiable wrappers**: `diff T` identifies values that participate in differentiation (see
  [Automatic differentiation](./autodiff.md)).

Implementations MAY extend the set of primitive types but MUST document the extensions.

## Typing judgements

Typing rules are written using natural deduction. The primary judgement `Γ ⊢ e : T` reads “under
context Γ, expression e has type T”. Implementations MUST reject programs that violate any
applicable rule. Selected core rules include:

- **Variable**: if `x : T ∈ Γ` then `Γ ⊢ x : T`.
- **Let binding**: if `Γ ⊢ e1 : T1` and `Γ, x : T1 ⊢ e2 : T2` then `Γ ⊢ let x = e1 in e2 : T2`.
- **Function abstraction**: if `Γ, x1 : T1, ..., xn : Tn ⊢ e : U` then `Γ ⊢ fn(x1 : T1, ..., xn : Tn) -> U { e } : (T1, ..., Tn) -> U`.

A comprehensive derivation catalogue is maintained in the implementation notes
([informative](https://github.com/cputer/mind/blob/main/docs/type-system.md)).

## Type inference

Implementations MUST support bidirectional type inference:

- Expressions without annotations are checked by propagating expected types from their context.
- When inference fails, diagnostics MUST include the expression span and the conflicting types.
- Generic functions MUST infer type parameters when sufficient information is available. Otherwise
  the caller MUST provide explicit type arguments.

Inference relies on unification with occurs checks. Implementations SHOULD emit informative error
messages when inference requires additional annotations.

### Core IR integration

The type checker participates directly in Core IR construction:

- **Symbol tables** feed module inputs. Each declared value is materialised as an `Input` instruction
  carrying its resolved tensor type so that the IR verifier can enforce the single-definition rule.
- **Shape validation** rejects tensors with zero or negative extents. Scalars (rank-0) are exempt and
  remain represented with an empty shape.
- **Operation typing** mirrors the IR instruction set. For arithmetic operations the operands MUST
  share a dtype; shape compatibility follows the broadcasting rules in
  [Shapes](./shapes.md#broadcasting). Scalar operands implicitly broadcast to the non-scalar
  operand's shape. Batched `MatMul` operations additionally broadcast leading dimensions and enforce
  that the contracting dimension matches.
- **Verification before emission**: translators are expected to reject programs with unknown dtypes,
  incompatible shapes, or undeclared symbols before emitting IR. This aligns the surface-language
  diagnostics with the invariants described in [Core IR](./ir.md#verification).

## Traits and generics

- Traits declare associated functions, types, and laws. Implementations MUST enforce that all
  required items are provided by conforming types.
- Trait implementations MUST be coherent: for any type and trait pair there MAY be at most one
  implementation in scope.
- Generic type parameters use an explicit `where` clause to declare trait bounds.

Trait resolution strategies are implementation-defined but MUST respect lexical scoping. The reference
implementation uses a runtime trait-based plugin architecture for backend selection.

## Differentiable types

The `diff T` wrapper marks values that participate in automatic differentiation. Implementations
MUST track primal and tangent components as described in [Automatic differentiation](./autodiff.md).
Values of type `diff T` MAY be passed where `T` is expected only when an implicit projection rule is
available; otherwise an explicit conversion is required.

## Type soundness

The canonical proof of progress and preservation is maintained alongside the reference compiler
(informative). Implementations SHOULD aim to keep diagnostic examples synced with the canonical
proof obligations.
