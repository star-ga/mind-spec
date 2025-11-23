<!--
Copyright (c) 2025 STARGA Inc.
MIND Language Specification — Community Edition
Licensed under the MIT License. See LICENSE-MIT.
-->

# Design Principles (Informative)

These principles guide the evolution of the MIND language and inform the normative requirements in
[`spec/v1.0`](../spec/v1.0/overview.md). They are intended to remain stable across specification
revisions. References to supporting discussion in the compiler repository are included for context.

## Clarity first

Language features SHOULD prioritise clarity of expression for both human readers and tooling. Syntax
that introduces ambiguity or relies on implicit behaviour is discouraged unless accompanied by
comprehensive diagnostics and formatter support. See the implementation commentary in
[`cputer/mind/docs/style`](https://github.com/cputer/mind/tree/main/docs/style).

## Differentiation as a first-class concern

Automatic differentiation is central to MIND. Language features MUST preserve differentiability where
possible and provide explicit escape hatches when not. Compiler passes SHOULD surface derivative
information for inspection and debugging. See [`cputer/mind/docs/autodiff`](https://github.com/cputer/mind/tree/main/docs/autodiff).

## Predictable performance

Program performance SHOULD be predictable from surface-level constructs. Optimisations MAY reorder
expressions but MUST respect observable semantics and differentiation invariants. Guidance on
performance tuning lives in [`cputer/mind/docs/perf`](https://github.com/cputer/mind/tree/main/docs/perf).

## Stability with room for evolution

Specification revisions SHOULD be backwards compatible whenever possible. When breaking changes are
necessary, they MUST be introduced through the RFC process described in
[`design/rfc-process.md`](./rfc-process.md) and accompanied by migration guidance.

## Open ecosystem

The specification and reference implementation evolve in the open. Tooling authors SHOULD be able to
consume the canonical IR and participate in the RFC process without proprietary constraints.
