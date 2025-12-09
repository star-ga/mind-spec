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

This overview enumerates the **Core v1** documents that together define the Phase-2 public behaviour
implemented by [`cputer/mind`](https://github.com/cputer/mind) and its reference runtime. The scope is
intentionally limited to public, deterministic semantics; private infrastructure and experimental
features are out of scope.
(Phase-2 refers to the second major milestone in the MIND project, focusing on deterministic,
public-facing semantics; see the project roadmap for more context.)

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
5. **MLIR Lowering** ([`mlir-lowering.md`](./mlir-lowering.md)) — deterministic lowering patterns for
   the feature-gated MLIR backend.
6. **Runtime Interface** ([`runtime.md`](./runtime.md)) — abstract contract for executing canonical IR
   semantics. Core v1 assumes a normative CPU execution model; GPU and accelerator backends are
   experimental extensions documented separately.

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
  and experimental GPU notes.
