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

# Active Proposals

> **Status:** Stable
> **Last updated:** 2026-11-24

This page tracks RFCs that are currently under active discussion. Once an RFC
reaches consensus, it moves to [Implemented RFCs](./implemented.md).

---

## Current Proposals

| RFC | Title | State |
|-----|-------|-------|
| [RFC 0023](../../design/rfcs/0023-type-parameters-on-user-types.md) | Type parameters on `struct`, `enum`, `trait` and `type`, and type arguments on user types | Draft |
| [RFC 0024](../../design/rfcs/0024-impl-forms.md) | `trait` and `impl` blocks: an implementation of a type, of a trait for a type, and associated items | Draft |
| [RFC 0025](../../design/rfcs/0025-patterns.md) | Patterns, guards and the record literal | Draft |
| [RFC 0026](../../design/rfcs/0026-module-items.md) | Module items: `module`, `export`, import alias, attributes, version attribute | Draft |
| [RFC 0027](../../design/rfcs/0027-function-generics.md) | Function generics: several type parameters, bounds, predeclared numeric bounds, supertraits, `where`, explicit type arguments | Draft |

The specification owner decided the questions of these drafts on 2026-11-24; each draft lists the decided
questions and the points that stay open. RFC 0023, RFC 0024 and RFC 0027 belong to one edition, Core v1.1. The
[decision notes](../../design/rfcs/decision-notes.md) record the decisions on the points that the specification
text did not decide. The numbers are provisional.

New proposals are welcome! See the [RFC Process](../../design/rfc-process.md)
for how to submit a proposal.

---

## Recently Discussed

The following topics have been discussed but not yet formalized as RFCs:

### Potential Future RFCs

| Topic | Discussion | Notes |
|-------|------------|-------|
| Forward-mode autodiff | — | JVP for efficient scalar→many-output gradients |
| Control flow in IR | — | Loops and conditionals for dynamic computation |
| Additional dtypes | — | f16, bf16, complex32, complex64 |
| Sparse tensor support | — | CSR/CSC/COO formats |
| Quantization | — | int8/int4 inference support |

To champion any of these topics, open a GitHub issue to start discussion.

---

## How to Participate

1. **Comment on existing proposals** — Provide feedback on open PRs
2. **Propose alternatives** — Suggest different approaches
3. **Prototype implementations** — Test feasibility in star-ga/mind
4. **Write documentation** — Help clarify proposals

---

[Back to RFC Index](./index.md) | [Implemented RFCs](./implemented.md)
