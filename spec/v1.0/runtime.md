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

# Runtime Interface (Normative)

This chapter defines the abstract runtime contract expected by Core v1. It mirrors the behaviour
implemented by public runtimes without prescribing internal threading or device strategies.

## Runtime model

A conforming runtime provides a **MindRuntime-like abstraction** capable of:

- Allocating tensors from a **tensor descriptor** containing shape, dtype, and optional device.
- Executing named **operations** matching the Core IR instruction set via a `run_op`-style entry point
  that consumes inputs and produces outputs deterministically.
- Synchronising device/stream state where relevant.

The interface is intentionally language-agnostic; concrete API surfaces MAY differ by implementation
but MUST provide equivalent capabilities.

## Responsibilities

- **Semantic fidelity**: runtime implementations MUST execute operations in accordance with the IR
  semantics defined in [Core IR](./ir.md) and [Shapes](./shapes.md).
- **Determinism**: given canonical IR and identical inputs, runtimes MUST produce identical outputs
  within numeric precision guarantees of the dtype.
- **Unsupported operations**: when an operation is not implemented, the runtime MUST return a
  well-defined error (e.g. “unsupported operation”) rather than exhibiting undefined behaviour.
- **Resource management**: allocation and deallocation semantics are implementation-defined but MUST
  not violate the deterministic execution model.

Performance considerations (threading, SIMD usage, accelerator integration) are **out of scope** for
this specification. Implementations MAY optimise freely provided they preserve the semantics above.
