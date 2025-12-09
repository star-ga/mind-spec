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

# Conformance (Normative)

This chapter defines how implementations claim **Core v1** conformance. Conformance is evaluated at
an **implementation** level: an implementation MAY be a compiler, runtime, or integrated system that
consumes Core v1 surface language and IR, executes the defined pipelines, and surfaces deterministic
results and errors. Individual components (for example, a parser) do not claim conformance in
isolation.

## Profiles

Core v1 defines two conformance profiles:

- **Core v1 CPU baseline** (required): an implementation MUST support the full Core v1 pipeline from
  surface language through Core IR, canonical autodiff, MLIR lowering for CPU backends, and runtime
  execution semantics for `DeviceKind::Cpu` / `BackendTarget::Cpu` as defined in the normative
  chapters of this specification.
- **Core v1 GPU profile** (optional): an implementation MAY additionally support GPU execution. This
  profile extends the CPU baseline with the GPU-specific device and backend rules in
  [`runtime.md`](./runtime.md#devices-and-backends), including `DeviceKind::Gpu`,
  `BackendTarget::Gpu`, and the backend-selection error model.

Implementations MAY claim conformance to only the CPU baseline or to both CPU baseline and GPU
profile. Claims MUST clearly state which profile(s) are implemented.

## Required behaviour

For the profile(s) an implementation claims:

- **Pipeline completeness**: implementations MUST accept verified, canonical Core IR, perform
  autodiff as defined in [`autodiff.md`](./autodiff.md), and, where applicable, lower to the
  MLIR backend following [`mlir-lowering.md`](./mlir-lowering.md) rules.
- **Runtime semantics**: runtime behaviour MUST follow [`runtime.md`](./runtime.md), including the
  deterministic execution guarantees and GPU backend-selection error model (for GPU-profile claims).
- **Deterministic diagnostics**: verification failures, unsupported features, and backend selection
  errors MUST be reported via deterministic, stable diagnostics.

## Conformance verification

Conformance is evaluated by executing the published **golden test corpus** distributed with the
reference implementation in [`cputer/mind`](https://github.com/cputer/mind). The corpus encodes the
behavioural contracts described in this specification across parsing, IR verification, autodiff,
MLIR lowering, runtime execution, and GPU backend selection. Other implementations MAY re-use or
port the corpus to verify their claimed profile(s). No specific CI or tooling is mandated; the
underlying behavioural contracts are normative, while the corpus is the public mechanism for
verifying them.
