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

# Core v1 Specification Overview

This overview enumerates the **Core v1** documents that together define the public behaviour
implemented by [`cputer/mind`](https://github.com/cputer/mind) and its reference runtime. The scope is
intentionally limited to public, deterministic semantics; private infrastructure and experimental
features are out of scope.

## Structure

Core v1 is organised into the following pillars:

1. **Surface Language** ([`language.md`](./language.md)) — syntax and tensor-centric constructs that
   lower into the Core IR.
2. **Core IR** ([`ir.md`](./ir.md)) — SSA-style tensor instruction set, canonicalisation, and
   verification rules.
3. **Static Autodiff** ([`autodiff.md`](./autodiff.md)) — reverse-mode differentiation on verified IR,
   producing canonical gradient modules.
4. **Shapes & Tensor Semantics** ([`shapes.md`](./shapes.md)) — broadcasting, reduction, indexing, and
   convolution shape rules shared by IR and lowering pipelines.
5. **Standard Library** ([`stdlib.md`](./stdlib.md)) — normative specifications for core, math, tensor,
   diff, and io modules with function signatures and semantics.
6. **Error Catalog** ([`errors.md`](./errors.md)) — comprehensive error codes (E1xxx–E6xxx), diagnostic
   requirements, and error recovery semantics.
7. **Conformance** ([`conformance.md`](./conformance.md)) — test corpus structure, coverage requirements,
   and compliance claim procedures for CPU and GPU profiles.
8. **Versioning & Stability** ([`versioning.md`](./versioning.md)) — semantic versioning policy,
   stability guarantees, breaking vs non-breaking changes, and deprecation procedures.
9. **MLIR Lowering** ([`mlir-lowering.md`](./mlir-lowering.md)) — deterministic lowering patterns for
   the feature-gated MLIR backend.
10. **Runtime Interface** ([`runtime.md`](./runtime.md)) — abstract contract for executing canonical IR
    semantics across CPU and the optional GPU profile.
11. **Security & Safety** ([`security.md`](./security.md)) — memory safety guarantees, determinism
    requirements, supply chain security, and threat model considerations.
12. **Performance & Benchmarks** ([`performance.md`](./performance.md)) — performance targets, benchmark
    methodology, optimization strategies, and profiling guidance (informative).
13. **Foreign Function Interface** ([`ffi.md`](./ffi.md)) — C ABI, Python/C++/Rust bindings, memory
    management, and cross-language interoperability.

Legacy chapters such as [`lexical.md`](./lexical.md) and [`types.md`](./types.md) remain available for
background on the broader language but are not required for Core v1 conformance.

## Conformance and determinism

Implementations claiming Core v1 compliance MUST:

- Accept only verified and canonicalised IR modules.
- Emit deterministic results for IR transformation pipelines (autodiff, MLIR lowering, runtime
  execution) given identical inputs.
- Surface verification failures and unsupported features using deterministic diagnostics.

Reference implementations in `cputer/mind` and `cputer/mind-runtime` are expected to follow these
rules; this repository is the normative source of truth for the semantics above.

## Related documents

- [Runtime: Devices and backends](./runtime.md#devices-and-backends) — device kinds, backend targets,
  and the CPU/GPU runtime profiles.

Core v1 defines two runtime **profiles**:

- **CPU profile**: requires the CPU runtime interface and execution model; this is the baseline
  that every conforming implementation MUST support.
- **GPU profile**: extends the CPU profile with device and backend semantics for GPUs as described
  in `runtime.md`. Runtimes that implement this profile MUST expose `DeviceKind::Gpu` and
  `BackendTarget::Gpu` together with well-defined backend-selection errors.

Profiles allow the specification to keep the CPU pipeline minimal while still providing a stable
contract for GPU-capable runtimes.

## Conformance levels

Core v1 conformance is defined in [`conformance.md`](./conformance.md) and evaluated at the
implementation level. Implementations MAY claim either the baseline CPU conformance or the optional
GPU profile conformance (which inherits the CPU baseline). Conformance is validated against the
public golden test corpus published with [`cputer/mind`](https://github.com/cputer/mind), which
codifies the behaviours described across the Core v1 chapters.
