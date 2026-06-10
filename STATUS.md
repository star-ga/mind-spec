# Documentation Status

> **Last Updated:** 2026-06-02 · spec v1.0 · tracking compiler **v0.7.1 (released) — the high-level execution surface now EXECUTES on the shipped compiler and `std-surface` is the shipped default.** Ten desugaring "bricks", each keystone-verified 7/7 across substrates, lower the high-level surface onto the existing low-level pipeline: integer/literal match, enum-discriminant match, `Option`/payload match, string literals, struct field-write, nested-struct + borrow field access, method-as-field accessors (`s.len()`), and method-with-args UFCS (`v.push(x)` → `vec_push(v, x)`, with unresolved methods failing loud). The Cargo feature set now defaults to `["std-surface"]`, so the high-level surface is live on every shipped binary; cross-substrate Q16.16 byte-identity is preserved (keystone 7/7 across the flip). Constructs that have **not** been promoted (by-value tuple/aggregate returns, `region { }`) are re-gated behind `std-surface-experimental` and **fail loud by default** — never a silent miscompile. Generics have no syntax yet (parser-rejected). `--no-default-features` restores the low-level-only subset (byte-identical to the pre-flip default build). Prior v0.7.0 work still holds: Mindcraft RFC 0007 fully shipped; RFC 0008 all 7/7 phases (KEYSTONE: cargo retired from pure-MIND compile loop); RFC 0010 Phases A/B/C + J-A/J-B shipped (extern "C" + SysV + Win64 ABI; region { } region-interior + GenRef region-exterior memory tiers), G1 dropped vestigial deps; RFC 0011 Phase A (std.async Scheduler-injection + ReplayScheduler); RFC 0012 tensor-native syntax Phases A (shape-typed Tensor<dtype,[dims]>) + B (`@`/`.*`/`.T`/reductions → std.blas) shipped, Phase C annotation checks shipped on the single canonical `#[name]` attribute form (C.0 threading + C.1 enforced `determinism::unknown_target`/`float_in_q16_fn`/`nondeterministic_in_deterministic` + C.2 implicit dtype-suffix determinism + `module { }` descent); 13 stdlib modules; mindc doc; standalone binary release. See [`star-ga/mind CHANGELOG`](https://github.com/star-ga/mind/blob/main/CHANGELOG.md) for the full per-version record.

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
| 16. IR Stability | `spec/v1.0/ir-stability.md` | ✅ Stable | `mic@1` textual form as the runtime contract. Ratified by mindc 0.2.5 (Pratt + stable IR API); pure-MIND `__mind_*` intrinsic ABI ratified by mindc 0.4.2 (RFC 0005). `MIND_STDLIB_PATH` env-var override added by mindc 0.4.3 (Phase D₁); Named-struct parameter names preserved in error diagnostics by mindc 0.4.4 (Phase D₂a). Phase 6.2b grammar growth ratified by mindc 0.5.0: `while` statement form, `[T; N]` fixed-size array types + `[expr, …]` array literals, and unsigned-i64 literal reinterpret-cast. mindc 0.5.1 adds: `Instr::If` IR primitive with `scf.if`-style branch lowering, bitwise BinOps (`BitAnd`/`BitOr`/`BitXor`/`Shl`/`Shr` → `arith.andi`/`ori`/`xori`/`shli`/`shrsi`), branch-binding scope threading, and cdylib `--emit-shared` static-links the std-surface modules + a tiny runtime-support archive so the resulting `.so` is self-contained at `dlopen` time. All gated under `std-surface`; default-build hot path byte-identical (the `std-surface` gate was on by default as of mindc 0.7.1, so this opt-in byte-identity invariant now attaches to the `--no-default-features` low-level subset; cross-substrate Q16.16 byte-identity is preserved across the flip). **mindc 0.7.x** extends the surface with three new IR-canon layers, all anchored on the same `mic@1` `IRModule` shape: (a) `mic@2.1` MAP-extension carrier in compact IR (RFC 0014, the silent prereq for evidence chains), (b) compile-time evidence-chain emission (RFC 0016 Phase A inert + Phase B verifier), and (c) `mic@3` binary `IRModule` codec + evidence MAP epilogue + `mindc --emit-mic3` / `--emit-evidence` CLI flags (RFC 0021 steps 1–3). The `trace_hash` carried by the chain is **`SHA-256(canonical mic@3 bytes)`** — the full-fidelity binary `IRModule` (RFC 0016 GAP-1, `db5cb76`; re-anchored 2026-05-31 after a collision audit found `mic@1` text can drop function-body semantics, supersedes the original `mic@1`-text rule), making `mic@3` the load-bearing anchor for the whole attestation surface — `mic@1`-text and `mic@2.x`-anchored hashing is non-conformant. RFC 0021 steps 4–6 (`mindc verify` CLI, `mic@2.x` → `mind-model@2` demotion, oracle + CI gate) remain in progress. |

## Documentation Areas

| Area | Scope | Status | Notes |
| ---- | ----- | ------ | ----- |
| Core language spec | `docs/spec/` | ✅ Stable | Content mirrors the latest compiler implementation. Minor clarifications welcome. |
| Standard library | `docs/spec/stdlib.md` | ✅ Stable | Aligned with Core v1 spec and `star-ga/mind-runtime`. As of v0.7.1 the `std-surface` high-level layer is the shipped default (see the Compile-speed guarantee note in `spec/v1.0/stdlib.md`). |
| RFCs | `docs/rfcs/` | ✅ Stable | RFCs 0001–0021 authored in `star-ga/mind`; implemented set covers Core v1, MIC/MAP, toolchain, evidence chains. New proposals accepted via pull requests. |
| Design notes | `docs/design/` | ✅ Stable | Architecture diagrams and autodiff design complete. |
| Examples | `examples/` | ✅ Stable | Standalone examples for basics, autodiff, linear algebra, FFI, and IR. |
| Conformance tests | `tests/` | ✅ Stable | Sample test corpus with YAML format per conformance.md. |
| Changelog | `docs/changelog.md` | ✅ Up to date | Released alongside each tagged compiler/runtime version. |

## Reference Implementations

| Implementation | Repo | Status | Notes |
| -------------- | ---- | ------ | ----- |
| MIND Compiler | [`star-ga/mind`](https://github.com/star-ga/mind) | 🟢 Reference compiler v0.7.1 | **v0.7.1 — high-level execution surface EXECUTES on the shipped compiler; `std-surface` promoted to the shipped default (`default = ["std-surface"]`).** Ten desugaring "bricks" lower the high-level surface onto the existing low-level pipeline, each keystone-verified 7/7 across substrates: integer/literal match, enum-discriminant match, `Option`/payload match, string literals, struct field-write, nested-struct + borrow field access, method-as-field accessors (`s.len()`), and method-with-args UFCS (`v.push(x)` → `vec_push(v, x)`; an unresolved method fails loud rather than miscompiling). With the feature on by default, the high-level surface runs on every shipped binary while cross-substrate Q16.16 byte-identity is preserved (keystone 7/7 across the flip). Unpromoted constructs (by-value tuple/aggregate returns, `region { }`) are re-gated behind `std-surface-experimental` and **fail loud by default**. Generics have no syntax yet (parser-rejected). `--no-default-features` restores the low-level-only subset, byte-identical to the pre-flip default build. **v0.7.0 — credibility-ladder rung 3 graduation. Mindcraft RFC 0007 fully shipped (all 6 phases + MINDCRAFT-001 keystone); RFC 0008 all 7/7 phases shipped (KEYSTONE: cargo retired from pure-MIND compile loop); RFC 0010 Phases A/B/C shipped + E/F scaffolded; 13 stdlib modules; mindc doc; standalone binary releases.** Six-step Phase 2A sequence landed: trivia layer (`4cfe7b9`), formatter walker (`bfeffbe`), stability tests (`434da71`), CLI subcommand (`696027a`), criterion bench (`d1f10f6`), normative docs (current). `mindc fmt [PATHS...] [--check] [--diff] [--stdin]` rewrites `.mind` files to canonical form deterministically; `--check` is the CI gate. Config: `[mindcraft.format]` in `Mind.toml` (indent_width/max_line_length/trailing_comma). All Phase 2A formatter rules operational: indentation, top-level spacing, trailing comma, whitespace normalisation, string passthrough, blank-line collapse, comment attachment, idempotence. Normative reference at `docs/mindcraft/fmt.md`; RFC 0007 status updated. Phase 2B (soft line-wrap) deferred. Full test suite passes, bench-gate held: `vec.mind` ~45us, `mindc_mind/main.mind` ~1.8ms, synthetic 1000-LOC ~446us on commodity x86 CPU. **v0.6.7 — RFC 0006 mind-blas alignment hardening (`mind@e921ed6`, tag `v0.6.7`).** Every std-surface `llvm.load → vector<…>` (dot_f32_v/dot_q16_v/dot_l1_q16_v/f32 L1·L∞/`VecLoad`·`VecLoadI32`) now emits explicit `{alignment = 4 : i64}` → `vmovups`, matching the inc-3b matmul fix; pre-empts the `vmovaps` GP-fault when the #230 encode rewire passes interior catalog-row pointers to `dot_q16_v`. Contract-neutral (changes the move, never the bytes): #57 byte-identity re-verified **exact** for dot_q16_v+dot_l1_q16_v, dot_f32_v 1e-4 intact; default release byte-identical + bootstrap fixed-point byte-identical (next_id 206) → bench-gate 0.0%. **v0.6.6 — RFC 0006 mind-blas Track B increment 3b (`mind@2dd896d`, tag `v0.6.6`).** Native vectorised row-major `matmul_rmajor_f32_v`: outer `scf.for` over rows + inlined inc-1 `dot_f32` 8-lane reduction + scalar tail, returns 0 like the Track A oracle; same 1e-4 f64 contract as `dot_f32_v`; verified `(1,1)`…`(128,384)` incl the `(2,17)` regression case. Root-caused+fixed a `vector<8xf32>` `llvm.load` natural-32B-alignment GP-fault (→ `{alignment = 4}` / `vmovups`); confirmed **not** a nested-`scf.for` lowering defect (valid MLIR, independently audited). default release binary byte-identical + bootstrap fixed-point byte-identical (next_id 206) → bench-gate 0.0%; `blas_vec_q16_smoke` 6/6. Direct latency lever for the mind-nerve native-encode GEMMs. **v0.6.5 — RFC 0006 mind-blas Track B increment 3a (`mind@38611f2`, tag `v0.6.5`, CI success).** Native Q16.16 **L1** vector path `dot_l1_q16_v` (`vector<8xi64>` widen → signed-subtract → arith-only `maxsi(d,0-d)` abs → i64-lane accumulate → associative `vector.reduction <add>` → scalar tail), byte-identical to the Track A scalar oracle `__mind_blas_dot_l1_q16` at all RFC lengths — **cross-arch bit-identity gate #57 now CLOSED for BOTH the thesis-pure vector dot and vector L1** (single-x86-host scope). No new IR variants (additive-only, like `dot_q16_v`); all `std-surface`-gated; default release binary byte-identical base↔inc-3a (reproducible) and bootstrap IR byte-identical (next_id 206) → bench-gate 0.0%; `blas_vec_q16_smoke` 5/5. **v0.6.4 — RFC 0006 mind-blas Track B increment 2 (`mind@8e4b925`, tag `v0.6.4`, CI 6/6 green).** Q16.16 vector path `dot_q16_v` byte-identical to the Track A scalar oracle at all lengths — **cross-arch bit-identity gate #57 CLOSED for the thesis-pure vector dot** (single-x86-host scope). Adds `Instr::VecStore`, `VecLoadI32`, `VecMulAddQ16`, `VecReduceAddI64`, and f32 `dot_l1_f32_v`/`dot_linf_f32_v`. v0.6.3 first landed Track B inc 1 (native vector-dialect `dot_f32`). Bootstrap fixed-point byte-identical (10,889 / 206 SSA, bootstrap uses no vector ops); bench-gate 0.0% (default binary byte-identical c130db3↔8e4b925); 519 std-surface tests; Track A `blas_smoke` 12/12 + inc-1 `blas_vec_smoke` 3/3 intact. Increment 3a (`dot_l1_q16_v`) shipped v0.6.5 and 3b (vectorised `matmul_rmajor_f32_v`) shipped v0.6.6, both above. Deferred to a later increment (RFC §9.3c): `@target(...)` per-call substrate annotation, cross-module `use std.blas` inlining, defensive `{alignment=4}` on the other `dot_*_v` kernels. **v0.6.2 — negative-literal correctness fix (bug #11) on the Bootstrap fixed-point.** v0.6.2 (`mind@969c2da`, tag `v0.6.2`) adds the missing `Node::Neg` arm in IR lowering: bare negative integer/float literals and any unary-minus expression were silently lowered to `const 0` (the catch-all path) — surfaced by the pure-MIND lookup-table work whose generated `-65536`/`-524288` entries were being zeroed. 519 tests pass; bench-gate improved (small_matmul −1.2 %, medium_mlp −1.8 %, large_network −0.2 %); the v0.6.1 fixed-point oracle is unchanged (bootstrap sources contain zero negative literals). Cumulative compiler bugs surfaced + closed by the pure-MIND self-host / end-to-end discipline: **11** (10 from the ladder + fixed-point, +1 negative-literal). **v0.6.1 — Bootstrap fixed-point REACHED.** The pure-MIND mindc — `examples/mindc_mind/main.mind` (1,084 LOC of `.mind` source merging the lexer + parser + type-checker + MLIR-text emitter, with helpers deduplicated) — compiled via `mindc --emit-shared` to a 78,488-byte cdylib, then fed its own source as input: the returned 10,889 bytes of MLIR text (206 SSA values) is **byte-identical to mindc-Rust's `--emit-ir` output on the same source**. v0.6.0 first proved self-host on a small fixture (148-byte MLIR byte-identical); v0.6.1 closes the loop. The Rust implementation is now decorative — only required for the initial bootstrap. Fixed-point closure surfaced + fixed two narrow emitter gaps (`UseDecl` stub emission + `StructDef` parsing + stub emission) at `e29b734`. Cumulative compiler bugs surfaced + closed by the self-host ladder + fixed-point: 0 (lexer) + 3 (parser) + 3 (typecheck) + 1 (emit_ir) + 0 (apex) + 3 (fixed-point: 1 UseDecl, 1 StructDef parse, 1 StructDef emit) = **10**. Frontend floor 2.80–17.10 µs (post-RFC-0005 baseline, +7% gate, preserved through every addition). |
| MIND Runtime | [`star-ga/mind-runtime`](https://github.com/star-ga/mind-runtime) | 🟢 CPU backend shipped (open-core) | v0.2.x, 17-symbol C ABI under `--features ffi,eval,serving`, audit-hardened, cargo-deny supply chain audit. CPU backend is shipped; GPU + accelerator backends are available under the commercial license (open-core). **Cross-substrate bit-identical determinism across CPU/GPU/accelerators is the roadmap, not a shipped guarantee.** |

## Toolchain Features (mindc v0.7.1)

| Feature | RFC | Status | Version | Canonical Spec |
| ------- | --- | ------ | ------- | -------------- |
| Self-hosted compiler (bootstrap fixed-point) | — | ✅ Complete | v0.6.1 | `examples/mindc_mind/` in `star-ga/mind` |
| mind-blas dense-vector surface (Track A + B) | RFC 0006 | ✅ Complete | v0.6.3–v0.6.7 | [`docs/rfcs/0006-mind-blas.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0006-mind-blas.md) |
| Mindcraft: `mindc fmt` | RFC 0007 Phase 2A | ✅ Shipped | v0.6.8 (`6e36fa3`) | [`docs/rfcs/0007-mindcraft.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0007-mindcraft.md) |
| Mindcraft: lint rule infrastructure | RFC 0007 Phase 3 | ✅ Shipped | v0.6.8 (`ccbaba9`) | [`docs/rfcs/0007-mindcraft.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0007-mindcraft.md) |
| Mindcraft: 5 named lint rules | RFC 0007 Phase 4 | ✅ Shipped | v0.6.8 (`5ff5367`) | [`docs/rfcs/0007-mindcraft.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0007-mindcraft.md) |
| Mindcraft: `mindc check` project driver | RFC 0007 Phase 5 | ✅ Shipped | v0.6.8 (`1442a31`) | [`docs/rfcs/0007-mindcraft.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0007-mindcraft.md) |
| Mindcraft: `--fix`, CI workflow, LSP reporter | RFC 0007 Phase 6 | ✅ Shipped | v0.6.8 (`15f9960`) | [`docs/rfcs/0007-mindcraft.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0007-mindcraft.md) |
| MINDCRAFT-001: `pub` keyword AST + formatter | RFC 0007 keystone | ✅ Shipped | v0.6.8 (`1d988bd`) | [`docs/rfcs/0007-mindcraft.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0007-mindcraft.md) |
| RFC 0008 spec (`mindc build` / `mindc test`) | RFC 0008 | ✅ Spec complete | v0.6.8 (`20c3c1c`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| `mindc build` single-crate orchestrator | RFC 0008 Phase A | ✅ Shipped | v0.6.8 (`d5bb605`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| `mindc test` discovery + parallel runner | RFC 0008 Phase B | ✅ Shipped | v0.6.8 (`9c8fb6f`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| Workspace support (`[workspace] members`) | RFC 0008 Phase C | ✅ Shipped | v0.6.8 (`267a9a6`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| External path deps + content-hash drift | RFC 0008 Phase D | ✅ Shipped | v0.6.8 (`7117b2a`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| Git deps + `Mind.lock` mandatory enforcement | RFC 0008 Phase E | ✅ Shipped | v0.6.8 (`f27789f`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| Incremental compilation cache | RFC 0008 Phase F | ✅ Shipped | v0.7.0 (`01fc039`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| Bootstrap `mind` with `mindc build` (KEYSTONE) | RFC 0008 Phase G | ✅ Shipped | v0.7.0 (`faa6027`) | [`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md) |
| extern "C" + SysV/Win64 ABI | RFC 0010 Phase A/B/C | ✅ Shipped | v0.7.0 | [`docs/rfcs/0010-memory-safety-and-c-abi.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0010-memory-safety-and-c-abi.md) |
| Three-tier memory model: `region { }` + `GenRef` (as of v0.7.1 the `region { }` interior is re-gated behind `std-surface-experimental` and fails loud under the default feature set; `GenRef` remains in the shipped surface) | RFC 0010 Phase J-A/J-B | ✅ Shipped | v0.7.0 (`region { }` experimental v0.7.1) | [`docs/rfcs/0010-memory-safety-and-c-abi.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0010-memory-safety-and-c-abi.md) |
| std.mlir + std.llvm C API scaffolds | RFC 0010 Phase E/F | ✅ Scaffolded | v0.7.0 | [`docs/rfcs/0010-memory-safety-and-c-abi.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0010-memory-safety-and-c-abi.md) |
| 13 stdlib modules (vec/string/map/io/blas/toml/json/regex/net/fs/process/mlir/llvm) | RFC 0005 + RFC 0006 + v0.7.0 | ✅ Complete | v0.7.0 | `std/` in `star-ga/mind` |
| High-level execution surface — 10 desugaring "bricks" (literal/enum/`Option`/string/struct-write/nested-borrow/method-as-field/method-args-UFCS), each keystone 7/7 across substrates | RFC 0005 + RFC 0012 | ✅ Executes on shipped compiler | v0.7.1 | `std/` + desugar pipeline in `star-ga/mind` |
| `std-surface` promoted to shipped default (`default = ["std-surface"]`); cross-substrate Q16.16 byte-identity preserved (keystone 7/7); `--no-default-features` restores low-level-only subset | RFC 0005 | ✅ Shipped (default) | v0.7.1 | `Cargo.toml` + `std/` in `star-ga/mind` |
| Unpromoted constructs (by-value tuple/aggregate returns, `region { }` interior) re-gated behind `std-surface-experimental`, **fail loud by default** | RFC 0005 + RFC 0010 | ✅ Shipped (fail-loud) | v0.7.1 | `Cargo.toml` + frontend in `star-ga/mind` |
| `mindc doc` HTML documentation generator | — | ✅ Phase 1 shipped | v0.7.0 | `src/doc/` in `star-ga/mind` |
| Standalone binary release (linux x64/arm64, macos x64/arm64, windows x64) | — | ✅ Complete | v0.7.0 | `.github/workflows/release.yml` + `scripts/install.sh` |
| RFC 0009 federation-first package layer (spec) | RFC 0009 | ✅ Spec complete | v0.7.0 | [`docs/rfcs/0009-federation-package-layer.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0009-federation-package-layer.md) |
| RFC 0011 async + structured concurrency (spec) | RFC 0011 | ✅ Spec complete | v0.7.0 | [`docs/rfcs/0011-async-and-structured-concurrency.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0011-async-and-structured-concurrency.md) |
| RFC 0010 G1: drop vestigial melior/inkwell deps | RFC 0010 Phase G1 | ✅ Shipped | v0.7.0 | [`docs/mindcraft/rfc0010-phase-ghi-migration-plan.md`](https://github.com/star-ga/mind/blob/main/docs/mindcraft/rfc0010-phase-ghi-migration-plan.md) |
| `mic@2.1` MAP-extension carrier (compact IR) | RFC 0014 | ✅ Shipped | v0.7.x (post-tag) | `spec/mic/mic2.1-spec.md` + `mind/src/ir/compact/v2/` |
| Compile-time evidence-chain emission (Phase A inert + Phase B verifier) | RFC 0016 | ✅ Shipped | v0.7.x (post-tag, mind@`e7c8c28`/`cadca87`) | [`docs/rfcs/0016-…`](https://github.com/star-ga/mind/blob/main/docs/rfcs/) |
| Evidence `trace_hash` anchored on canonical `mic@3` bytes | RFC 0016 GAP-1 (re-anchored 2026-05-31) | ✅ Shipped | v0.7.x (post-tag, mind@`db5cb76`) | `mind/src/ir/evidence.rs` |
| `mic@3` binary `IRModule` codec (additive) | RFC 0021 step 1 | ✅ Shipped | v0.7.x (post-tag) | `mind/src/ir/compact/v3/` |
| Evidence MAP epilogue on `mic@3` | RFC 0021 step 2 | ✅ Shipped | v0.7.x (post-tag) | `mind/src/ir/compact/v3/evidence.rs` |
| `mindc --emit-mic3` / `--emit-evidence` CLI flags | RFC 0021 step 3 | ✅ Shipped | v0.7.x (post-tag) | `mind/src/bin/mindc.rs` |
| `mindc verify` CLI + `mic@2.x` → `mind-model@2` demotion + CI oracle gate | RFC 0021 steps 4–6 + RFC 0017 | 🚧 In progress | targets v0.7.1+ | [`docs/rfcs/0021-canonical-ir-unification.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0021-canonical-ir-unification.md) · [`docs/rfcs/0017-mindc-verify.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0017-mindc-verify.md) |
| `__mind_load_i8` / `__mind_store_i8` byte-precise intrinsics (additive) | RFC 0005 Phase 1.6 (#306 path-B) | ✅ Shipped | v0.7.x (post-tag, mind@`0e7dd6c`) | `mind/runtime-support/mind_intrinsics.c` |
| `std.string` / `std.sha256` / `std.toml` site migration to byte-precise stores | #306 keystone re-bless | 🚧 Pending fresh-context session | targets v0.7.1 | [`mind/docs/byte-store-migration.md`](https://github.com/star-ga/mind/blob/main/docs/byte-store-migration.md) |
| Cross-substrate bit-identity CI gate (AVX2 + NEON hash comparison, `MIND_BENCH_REQUIRE` hard-fail) | RFC 0015 | ✅ Shipped | v0.7.x (post-tag, mind@`3037c04`) | [`docs/rfcs/0015-cross-substrate-bit-identity.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0015-cross-substrate-bit-identity.md) |
| `mindc verify` artifact verification surface (hash-equality + Ed25519 modes) | RFC 0017 | 📝 Draft (authored 2026-05-29, task #290) | targets v0.7.1 | [`docs/rfcs/0017-mindc-verify.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0017-mindc-verify.md) |
| Bare-metal substrate lowering tier (no-OS, static-memory, RFC 0015 determinism obligations) | RFC 0018 | 📝 Draft (authored 2026-05-29) | targets post-v0.7.1 | [`docs/rfcs/0018-bare-metal-substrate.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0018-bare-metal-substrate.md) |
| Deterministic agent substrate (`agent.*` MAP namespace, RFC 0016 §3.3 trace-hash fold) | RFC 0019 | 📝 Draft (authored 2026-05-29, task #294) | targets post-v0.7.1 | [`docs/rfcs/0019-deterministic-agent-substrate.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0019-deterministic-agent-substrate.md) |
| mind-bench reproducibility harness (`wedge-score`, `agent-state-replay-*` workloads) | RFC 0020 | 📝 Draft | targets v0.7.1+ | [`docs/rfcs/0020-mind-bench-reproducibility-harness.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0020-mind-bench-reproducibility-harness.md) |
| Rust edition | — | ✅ 2024 | v0.6.8 | `Cargo.toml` |

## Mindcraft (RFC 0007) — Fully Shipped

All six phases and the MINDCRAFT-001 keystone landed in mindc v0.6.8.
The toolchain self-hosting credibility ladder is now complete: the
language self-hosts (v0.6.0 apex), the compiler self-hosts (v0.6.1
fixed-point), and the toolchain self-hosts (v0.6.8 Mindcraft).

- Phase 1: `MindcraftConfig` manifest types in `Mind.toml` (`6526029`)
- Phase 2A: `mindc fmt` with `--check` / `--diff` / `--stdin` / `--fix` (`6e36fa3`)
- Phase 3: Lint rule infrastructure + glob `overrides` + `RuleRegistry` (`ccbaba9`)
- Phase 4: 5 named lint rules (`q16_overflow`, `unused_import`, `naming_convention`, `shadowing`, `trailing_whitespace`) (`5ff5367`)
- Phase 5: `mindc check` project driver — VCS-aware, JSON + LSP reporters (`1442a31`)
- Phase 6: `--fix` pipeline + CI integration + `.github/workflows/mindcraft.yml` (`15f9960`)
- MINDCRAFT-001 keystone: `pub` keyword preserved through AST and formatter (`1d988bd`)

Canonical spec: [`docs/rfcs/0007-mindcraft.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0007-mindcraft.md) in `star-ga/mind`.

## RFC 0008 (`mindc build` / `mindc test`) — 5/7 Phases Shipped

The cargo retirement track. 850-line spec at
[`docs/rfcs/0008-mindc-build.md`](https://github.com/star-ga/mind/blob/main/docs/rfcs/0008-mindc-build.md)
in `star-ga/mind`.

| Phase | Description | Commit | Status |
| ----- | ----------- | ------ | ------ |
| Spec | 850-line RFC | `20c3c1c` | ✅ Complete |
| A | `mindc build` single-crate orchestrator | `d5bb605` | ✅ Shipped |
| B | `mindc test` discovery + parallel runner | `9c8fb6f` | ✅ Shipped |
| C | Workspace support, topo sort, cycle detection | `267a9a6` | ✅ Shipped |
| D | External path deps + content-hash drift detection | `7117b2a` | ✅ Shipped |
| E | Git deps + `~/.mindenv/cache` + `Mind.lock` mandatory enforcement | `f27789f` | ✅ Shipped |
| F | Incremental compilation cache | `01fc039` | ✅ Shipped |
| G | KEYSTONE — bootstrap `mind` with `mindc build`, Cargo retirement | `faa6027` | ✅ Shipped |

Phase G landed in v0.7.0: `mindc build` compiles the entire MIND compiler and standard
library without Cargo on the critical path. Cargo remains in the repo only to host
the `mindc` binary itself until RFC 0010 delivers a pure-MIND libMLIR FFI (Phase G of
RFC 0010).

## Toolchain Features (mindc v0.7.1 compiler reference)

See the `star-ga/mind` [Reference Implementations](#reference-implementations) row for
the full feature delta.

_Status legend_: ✅ Stable • ⚠️ Needs updates • 🚧 Under active development • 📝 Drafts in progress.

If you are planning a contribution, please update this table as part of your pull request so downstream readers know what to expect from each section.
