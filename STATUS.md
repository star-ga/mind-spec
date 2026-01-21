# Documentation Status

This status page provides a quick view of the readiness of key documentation areas within the MIND specification. Use it to coordinate work, plan reviews, and spot sections that still need expansion.

## Core v1 Specification

The formal Core v1 specification documents are located in `spec/v1.0/`. See [`overview.md`](spec/v1.0/overview.md) for the complete structure.

| Chapter | File | Status | Notes |
| ------- | ---- | ------ | ----- |
| 1. Surface Language | `spec/v1.0/language.md` | ✅ Stable | Syntax and tensor-centric constructs. |
| 2. Core IR | `spec/v1.0/ir.md` | ✅ Stable | SSA-style tensor instruction set. |
| 3. Static Autodiff | `spec/v1.0/autodiff.md` | ✅ Stable | Reverse-mode differentiation rules. |
| 4. Shapes & Tensor Semantics | `spec/v1.0/shapes.md` | ✅ Stable | Broadcasting, reduction, indexing. |
| 5. Standard Library | `spec/v1.0/stdlib.md` | ✅ Stable | core, math, tensor, diff, io modules. |
| 6. Error Catalog | `spec/v1.0/errors.md` | ✅ Stable | Error codes E1xxx–E6xxx. |
| 7. Conformance | `spec/v1.0/conformance.md` | ✅ Stable | Test corpus and compliance procedures. |
| 8. Versioning & Stability | `spec/v1.0/versioning.md` | ✅ Stable | Semantic versioning policy. |
| 9. MLIR Lowering | `spec/v1.0/mlir-lowering.md` | ✅ Stable | Feature-gated MLIR backend. |
| 10. Runtime Interface | `spec/v1.0/runtime.md` | ✅ Stable | CPU and GPU profile contracts. |
| 11. Security & Safety | `spec/v1.0/security.md` | ✅ Stable | Memory safety, determinism, supply chain. |
| 12. Performance & Benchmarks | `spec/v1.0/performance.md` | ✅ Stable | Targets and methodology (informative). |
| 13. Foreign Function Interface | `spec/v1.0/ffi.md` | ✅ Stable | C/C++/Python/Rust bindings. |
| 14. Future Extensions | `spec/v1.0/future-extensions.md` | ✅ Stable | BCI/neuro, embedded AI, safety-critical systems roadmap (informative). |

## Documentation Areas

| Area | Scope | Status | Notes |
| ---- | ----- | ------ | ----- |
| Core language spec | `docs/spec/` | ✅ Stable | Content mirrors the latest compiler implementation. Minor clarifications welcome. |
| Standard library | `docs/spec/stdlib.md` | ✅ Stable | Aligned with Core v1 spec and `star-ga/mind-runtime`. |
| RFCs | `docs/rfcs/` | ✅ Stable | 10 implemented RFCs (Core v1 + MIC/MAP). New proposals accepted via pull requests. |
| Design notes | `docs/design/` | ✅ Stable | Architecture diagrams and autodiff design complete. |
| Examples | `examples/` | ✅ Stable | Standalone examples for basics, autodiff, linear algebra, FFI, and IR. |
| Conformance tests | `tests/` | ✅ Stable | Sample test corpus with YAML format per conformance.md. |
| Changelog | `docs/changelog.md` | ✅ Up to date | Released alongside each tagged compiler/runtime version. |

## Reference Implementations

| Implementation | Repo | Status | Notes |
| -------------- | ---- | ------ | ----- |
| MIND Compiler | [`star-ga/mind`](https://github.com/star-ga/mind) | ✅ Complete | 175+ tests passing, LLVM 18, 0 Clippy warnings, FFI safety docs. |
| MIND Runtime | [`star-ga/mind-runtime`](https://github.com/star-ga/mind-runtime) | ✅ Complete | 136 tests, GPU docs, package management, distributed training, model serving. |

_Status legend_: ✅ Stable • ⚠️ Needs updates • 🚧 Under active development • 📝 Drafts in progress.

If you are planning a contribution, please update this table as part of your pull request so downstream readers know what to expect from each section.
