# Documentation Status

> **Last Updated:** 2026-05-18 · spec v1.0 · tracking compiler **0.6.1 — Bootstrap fixed-point REACHED**. The pure-MIND mindc `libmindc_mind.so` compiles its own 1,084-LOC `.mind` source byte-identically (10,889 bytes of MLIR text, 206 SSA values) to mindc-Rust on the same input. The Rust implementation is now decorative — required only for the initial bootstrap. v0.6.0 first proved the self-host thesis on a small fixture (148-byte MLIR byte-identical); v0.6.1 closes the loop on the compiler's own source.

This status page provides a quick view of the readiness of key documentation areas within the MIND specification. Use it to coordinate work, plan reviews, and spot sections that still need expansion.

## Core v1 Specification

The formal Core v1 specification documents are located in `spec/v1.0/`. See [`overview.md`](spec/v1.0/overview.md) for the complete structure.

| Chapter | File | Status | Notes |
| ------- | ---- | ------ | ----- |
| 1. Surface Language | `spec/v1.0/language.md` | ✅ Stable | Syntax and tensor-centric constructs. |
| 2. Core IR | `spec/v1.0/ir.md` | ✅ Stable | SSA-style tensor instruction set. |
| 3. Static Autodiff | `spec/v1.0/autodiff.md` | ✅ Stable | Reverse-mode differentiation rules. |
| 4. Shapes & Tensor Semantics | `spec/v1.0/shapes.md` | ✅ Stable | Broadcasting, reduction, indexing. |
| 5. Standard Library | `spec/v1.0/stdlib.md` | ✅ Stable | core, math, tensor, diff, io modules + RFC 0005 pure-MIND surface (std.vec/string/map/io on seven `__mind_*` intrinsics). |
| 6. Error Catalog | `spec/v1.0/errors.md` | ✅ Stable | Error codes E1xxx–E6xxx. |
| 7. Conformance | `spec/v1.0/conformance.md` | ✅ Stable | Test corpus and compliance procedures. |
| 8. Versioning & Stability | `spec/v1.0/versioning.md` | ✅ Stable | Semantic versioning policy. |
| 9. MLIR Lowering | `spec/v1.0/mlir-lowering.md` | ✅ Stable | Feature-gated MLIR backend. |
| 10. Runtime Interface | `spec/v1.0/runtime.md` | ✅ Stable | CPU and GPU profile contracts. |
| 11. Security & Safety | `spec/v1.0/security.md` | ✅ Stable | Memory safety, determinism, supply chain. |
| 12. Performance & Benchmarks | `spec/v1.0/performance.md` | ✅ Stable | Targets and methodology (informative). |
| 13. Foreign Function Interface | `spec/v1.0/ffi.md` | ✅ Stable | C/C++/Python/Rust bindings. |
| 14. Future Extensions | `spec/v1.0/future-extensions.md` | ✅ Stable | BCI/neuro, systems programming, embedded AI, safety-critical systems roadmap (informative). |
| 15. Package Management | `spec/v1.0/package.md` | ✅ Stable | PubGrub resolver, lockfile format, SBOM, SLSA provenance, registry protocol. |
| 16. IR Stability | `spec/v1.0/ir-stability.md` | ✅ Stable | `mic@1` textual form as the runtime contract. Ratified by mindc 0.2.5 (Pratt + stable IR API); pure-MIND `__mind_*` intrinsic ABI ratified by mindc 0.4.2 (RFC 0005). `MIND_STDLIB_PATH` env-var override added by mindc 0.4.3 (Phase D₁); Named-struct parameter names preserved in error diagnostics by mindc 0.4.4 (Phase D₂a). Phase 6.2b grammar growth ratified by mindc 0.5.0: `while` statement form, `[T; N]` fixed-size array types + `[expr, …]` array literals, and unsigned-i64 literal reinterpret-cast. mindc 0.5.1 adds: `Instr::If` IR primitive with `scf.if`-style branch lowering, bitwise BinOps (`BitAnd`/`BitOr`/`BitXor`/`Shl`/`Shr` → `arith.andi`/`ori`/`xori`/`shli`/`shrsi`), branch-binding scope threading, and cdylib `--emit-shared` static-links the std-surface modules + a tiny runtime-support archive so the resulting `.so` is self-contained at `dlopen` time. All gated under `std-surface`; default-build hot path byte-identical. |

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
| MIND Compiler | [`star-ga/mind`](https://github.com/star-ga/mind) | ✅ Complete | **v0.6.1 — Bootstrap fixed-point REACHED.** The pure-MIND mindc — `examples/mindc_mind/main.mind` (1,084 LOC of `.mind` source merging the lexer + parser + type-checker + MLIR-text emitter, with helpers deduplicated) — compiled via `mindc --emit-shared` to a 78,488-byte cdylib, then fed its own source as input: the returned 10,889 bytes of MLIR text (206 SSA values) is **byte-identical to mindc-Rust's `--emit-ir` output on the same source**. v0.6.0 first proved self-host on a small fixture (148-byte MLIR byte-identical); v0.6.1 closes the loop. The Rust implementation is now decorative — only required for the initial bootstrap. Fixed-point closure surfaced + fixed two narrow emitter gaps (`UseDecl` stub emission + `StructDef` parsing + stub emission) at `e29b734`. Cumulative compiler bugs surfaced + closed by the self-host ladder + fixed-point: 0 (lexer) + 3 (parser) + 3 (typecheck) + 1 (emit_ir) + 0 (apex) + 3 (fixed-point: 1 UseDecl, 1 StructDef parse, 1 StructDef emit) = **10**. Frontend floor 2.80–17.10 µs (post-RFC-0005 baseline, +7% gate, preserved through every addition). |
| MIND Runtime | [`star-ga/mind-runtime`](https://github.com/star-ga/mind-runtime) | ✅ Complete | v0.2.x, 17-symbol C ABI under `--features ffi,eval,serving`, GPU docs, audit-hardened, cargo-deny supply chain audit. |

_Status legend_: ✅ Stable • ⚠️ Needs updates • 🚧 Under active development • 📝 Drafts in progress.

If you are planning a contribution, please update this table as part of your pull request so downstream readers know what to expect from each section.
