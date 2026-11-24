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

# RFC Index

Requests for Comments (RFCs) are the mechanism for proposing significant changes
to the MIND language specification. This index tracks all RFCs by status.

## RFC Process

See [RFC Process](../../design/rfc-process.md) for the full procedure.

**Lifecycle:**
1. **Draft** — Initial proposal, open for discussion
2. **Active** — Under active consideration, gathering feedback
3. **Accepted** — Approved for implementation
4. **Implemented** — Merged into specification
5. **Rejected** — Not accepted (with rationale)
6. **Withdrawn** — Author withdrew proposal

## Active Proposals

RFCs currently under discussion. See [Active Proposals](./active.md) for details.

| RFC | Title | Status | Champion |
|-----|-------|--------|----------|
| [RFC 0023](../../design/rfcs/0023-type-parameters-on-user-types.md) | Type parameters on `struct`, `enum`, `trait` and `type`, and type arguments on user types | Draft | — |
| [RFC 0024](../../design/rfcs/0024-impl-forms.md) | `trait` and `impl` blocks: an implementation of a type, of a trait for a type, and associated items | Draft | — |
| [RFC 0025](../../design/rfcs/0025-patterns.md) | Patterns, guards and the record literal | Draft | — |
| [RFC 0026](../../design/rfcs/0026-module-items.md) | Module items: `module`, `export`, import alias, version attribute | Draft | — |
| [RFC 0027](../../design/rfcs/0027-function-generics.md) | Function generics: several type parameters, bounds, supertraits, `where`, explicit type arguments | Draft | — |

## Implemented RFCs

RFCs that have been accepted and merged into the Core v1 specification.
See [Implemented RFCs](./implemented.md) for details.

| RFC | Title | Spec Version | Implementation |
|-----|-------|--------------|----------------|
| RFC-0001 | Core IR Instruction Set | Core v1.0 | ir.md |
| RFC-0002 | Broadcasting Semantics | Core v1.0 | shapes.md |
| RFC-0003 | Reverse-Mode Autodiff | Core v1.0 | autodiff.md |
| RFC-0004 | Error Code Catalog | Core v1.0 | errors.md |
| RFC-0005 | Standard Library | Core v1.0 | stdlib.md |
| RFC-0006 | Conformance Testing | Core v1.0 | conformance.md |
| RFC-0007 | FFI Specification | Core v1.0 | ffi.md |
| RFC-0008 | Versioning Policy | Core v1.0 | versioning.md |

## Proposing an RFC

To propose a new RFC:

1. **Check existing proposals** — Ensure your idea isn't already covered
2. **Open a discussion** — File a GitHub issue to gauge interest
3. **Write the RFC** — Use the template in `design/rfc-process.md`
4. **Submit a PR** — Create a pull request with your RFC document
5. **Gather feedback** — Respond to reviewer comments
6. **Reach consensus** — RFC is accepted when maintainers approve

## RFC Template

```markdown
# RFC-XXXX: Title

> **Status:** Draft
> **Author:** Your Name
> **Created:** YYYY-MM-DD
> **Target Version:** Core vX.Y

## Summary

One-paragraph description of the proposal.

## Motivation

Why is this change needed? What problem does it solve?

## Detailed Design

Technical specification of the proposed change.

## Alternatives Considered

Other approaches that were evaluated.

## Compatibility

Impact on existing code and migration path.

## Open Questions

Unresolved issues requiring discussion.
```

---

[Back to Docs Index](../README.md) | [Design Notes](../design/index.md)
