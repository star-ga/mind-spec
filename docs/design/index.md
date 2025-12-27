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

# Design Notes

This section contains informative design documents that provide context for the
normative specification. These documents explain the rationale behind design
decisions and offer guidance for implementers.

## Contents

| Document | Description | Status |
|----------|-------------|--------|
| [Compiler Architecture](./compiler.md) | Pipeline stages, data flow, error handling | ✅ Stable |
| [Autodiff Design](./autodiff.md) | Differentiation strategy and implementation | ✅ Stable |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MIND System Architecture                            │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────┐
    │                        User-Facing Layer                              │
    ├───────────────┬───────────────┬───────────────┬──────────────────────┤
    │  .mind files  │   Python API  │   C/C++ API   │   Rust API           │
    │  (source)     │   (bindings)  │   (bindings)  │   (bindings)         │
    └───────┬───────┴───────┬───────┴───────┬───────┴──────────┬───────────┘
            │               │               │                  │
            ▼               ▼               ▼                  ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │                         Compiler Frontend                             │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
    │  │  Lexer  │─▶│ Parser  │─▶│  Type   │─▶│  Shape  │─▶│   IR    │    │
    │  │         │  │         │  │ Checker │  │ Checker │  │ Builder │    │
    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
    └──────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │                            Core IR                                    │
    │  • SSA-style ordered instructions                                    │
    │  • Tensor type metadata (dtype, shape)                               │
    │  • Deterministic textual encoding                                    │
    └──────────────────────────────────────────────────────────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            ▼                           ▼                           ▼
    ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
    │   Autodiff    │          │   Optimizer   │          │     MLIR      │
    │   Engine      │          │   Passes      │          │   Lowering    │
    └───────────────┘          └───────────────┘          └───────────────┘
            │                           │                           │
            └───────────────────────────┼───────────────────────────┘
                                        ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │                            Runtime                                    │
    │  ┌─────────────────────────┐    ┌─────────────────────────┐         │
    │  │     CPU Backend         │    │     GPU Backend         │         │
    │  │  (DeviceKind::Cpu)      │    │  (DeviceKind::Gpu)      │         │
    │  └─────────────────────────┘    └─────────────────────────┘         │
    └──────────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

See [Design Principles](../../design/principles.md) for the full list.

1. **Clarity First** — Syntax prioritizes readability
2. **Differentiation as First-Class** — Autodiff is core, not bolted on
3. **Predictable Performance** — No surprising optimization behaviors
4. **Stability with Evolution** — Backwards compatibility by default
5. **Open Ecosystem** — Spec and IR are public and consumable

## Relationship to Specification

| Design Document | Related Spec Chapters |
|-----------------|----------------------|
| Compiler Architecture | ir.md, language.md, errors.md |
| Autodiff Design | autodiff.md, ir.md |

Design documents are **informative** — they explain but do not define behavior.
The normative specification in `spec/v1.0/` is the authoritative source.

---

[Back to Docs Index](../README.md) | [RFC Index](../rfcs/index.md)
