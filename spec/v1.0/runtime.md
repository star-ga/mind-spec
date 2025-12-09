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

A conforming runtime provides an abstraction capable of:

- Allocating tensors from a **tensor descriptor** containing shape, dtype, and optional device.
- Executing named **operations** matching the Core IR instruction set by providing a mechanism that
  consumes inputs and produces outputs deterministically.
- Synchronising device/stream state where relevant.

The interface is intentionally language-agnostic; concrete API surfaces MAY differ by implementation
but MUST provide equivalent capabilities.

## Devices and backends

- A **device** is an abstract execution resource identified by a **device kind**:
  - `Cpu`: normative Core v1 execution target. All conforming runtimes MUST support `Cpu`.
  - `Gpu`: experimental accelerator target. Support for `Gpu` is OPTIONAL in Core v1 and MAY change
    between versions.
- A **backend target** represents the compilation + execution target used by the compiler/runtime
  pipeline. The reference implementation exposes enums named `DeviceKind` and `BackendTarget` with
  variants such as `Cpu` and `Gpu` to mirror this contract.
- Normative requirements:
  - All Core v1 semantics and conformance requirements are defined with respect to `Cpu` execution.
  - Runtimes MUST execute verified Core IR deterministically on `Cpu` as described elsewhere in this
    document.

### Experimental GPU backends (non-normative)

- Some implementations MAY provide GPU backends that map Core IR to accelerator-specific runtimes.
- GPU backends are **experimental** in Core v1:
  - Availability is implementation-defined.
  - Supported device kinds, memory models, and kernel scheduling strategies MAY evolve without Core
    v1 conformance impact.
- Implementations SHOULD:
  - Preserve Core IR semantics modulo floating-point and backend-specific numeric differences.
  - Surface failures as structured runtime errors (e.g. “backend not available”, “device out of
    memory”).
- For an overview of the public runtime surface in the reference implementation, see the GPU backend
  contract in [`cputer/mind`](https://github.com/cputer/mind/blob/main/docs/gpu.md).

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

## Error model

- **Backend selection errors**: runtimes MUST surface structured errors when a requested backend
  target (e.g. `BackendTarget::Gpu`) is unavailable or feature-gated, particularly for experimental
  GPU backends.
