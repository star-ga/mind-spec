<!--
Copyright (c) 2025 STARGA Inc.
MIND Language Specification — Community Edition
Licensed under the MIT License. See LICENSE-MIT.
-->

# Mind Specification v1.0 Overview

This document describes the scope and organisation of the normative MIND language specification.
It introduces the terminology used across the specification suite, outlines the available
conformance levels, and records references to the reference implementation and design background.

## Structure of the v1.0 specification

The language specification is segmented to align with the major implementation guides in
[`cputer/mind/docs`](https://github.com/cputer/mind/tree/main/docs):

- [Lexical structure](./lexical.md) — tokenisation, layout rules, and source text conventions.
- [Type system](./types.md) — typing rules, inference constraints, and generics.
- [Automatic differentiation](./autodiff.md) — operator semantics for differentiable programs.
- [Intermediate representation](./ir.md) — the canonical compiler IR and verification invariants.

Each chapter is normative unless explicitly marked as informative. Informative callouts reference
supporting materials or implementation notes in the compiler repository.

## Conformance levels

The specification defines three conformance levels:

1. **Core**: Implementations MUST support programs that only depend on the core syntax and typing
   rules defined in this specification. Behaviour outside the core is implementation-defined.
2. **Differentiable**: Implementations claiming differentiable support MUST satisfy all Core
   requirements and MUST implement the automatic differentiation semantics described in
   [Automatic differentiation](./autodiff.md).
3. **Full**: Implementations claiming full conformance MUST satisfy all Core and Differentiable
   requirements, and MUST emit or consume the canonical IR defined in [Intermediate representation](./ir.md).

Conformance claims are made per released compiler. Compilers MAY provide feature gates for
experimental functionality provided that the default configuration remains conformant.

## Notation and terminology

The specification uses the following conventions:

- **Grammar** fragments are described using extended Backus–Naur form (EBNF).
- **Judgements** in the type system are written in natural deduction style, following the notation
  used in [`cputer/mind/docs/type-system`](https://github.com/cputer/mind/tree/main/docs/type-system).
- **Differentiation rules** reference implementation notes in
  [`cputer/mind/docs/autodiff`](https://github.com/cputer/mind/tree/main/docs/autodiff) for worked
  examples (informative).
- **IR invariants** reuse the terminology defined in
  [`cputer/mind/docs/ir`](https://github.com/cputer/mind/tree/main/docs/ir).

RFC 2119 keywords such as MUST, SHOULD, and MAY are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## Relationship to other documents

The design documents under [`design/`](../../design/) record the principles that inform the
normative requirements here. RFCs proposing changes to v1.0 MUST include an impact statement that
links back to the relevant sections of this overview.
