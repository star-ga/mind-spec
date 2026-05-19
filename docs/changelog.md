# Changelog

All notable changes to the MIND Language Specification are documented here.

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.4] - 2026-05-18

### Milestone: mindc v0.5.1 — Phase 6.5 Stage 1 PASS (pure-MIND lexer cdylib byte-identical)

The reference implementation ships **first concrete bootstrap evidence on the self-host ladder**. The pure-MIND lexer (`examples/lexer/main.mind`, ~290 LOC tail-recursive `.mind` source authored by humans) was compiled via mindc-Rust's `--emit-shared` to `libmindc_lexer.so` (25,704 bytes; std-surface symbols + a runtime-support archive statically bundled), `dlopen`'d via Python ctypes, and `lex()` ran to completion producing a `Vec<i64>` stride-3 token stream **byte-identical to the documented spec contract** (32 of 32 tokens). This is the first time MIND has produced observational evidence that its self-host design is correct, not just type-checkable.

### Changed

- **`STATUS.md`** — Compiler entry bumped to v0.5.1; IR Stability row records the new control-flow primitives ratified by v0.5.1: `Instr::If` with `scf.if`-style branch lowering, bitwise BinOps (`BitAnd`/`BitOr`/`BitXor`/`Shl`/`Shr` → `arith.andi`/`ori`/`xori`/`shli`/`shrsi`), branch-binding scope threading via `branch_bindings` field on `Instr::If`, and cdylib `--emit-shared` static-linking of std-surface modules + a tiny runtime-support archive so resulting `.so` files are self-contained at `dlopen` time. All gated under `std-surface`; default-build hot path byte-identical.

### Notes

- The cdylib linker bundling resolves the symbol resolution layer of self-host: each `.so` produced by mindc now ships with the seven `__mind_*` intrinsics (alloc/realloc/free/load_i64/store_i64/read/write) wired through a C runtime-support archive, plus statically-linked `std.vec` / `std.string` / `std.map` / `std.io` from the pure-MIND module tree.
- Phase 6.5 sub-stages 2 (parser), 3 (typecheck), 4 (emit_ir) follow the same pattern proven by Stage 1. Stage 5 = APEX combines all four into `libmindc_mind.so` with a driver fn that takes source bytes and produces IR text byte-identical to mindc-Rust on the same input.

---

## [1.2.3] - 2026-05-18

### Milestone: mindc v0.5.0 — RFC 0005 Phase 6.2b (three compiler gaps closed)

The compiler-side closure of Phase 6.2b lands at mindc v0.5.0. The
informative "Self-host smoke" subsection in `spec/v1.0/stdlib.md` is
updated to reflect that the surface-grammar growth ratified by
mindc 0.5.0 unblocks Phase 6.5 (fixed-point bootstrap apex). No
normative change — Phase 6.2b grammar growth lands under the
`std-surface` feature gate so the default-build hot path stays
byte-identical to v0.4.4. Bench-gate cap held (+7% vs
`.bench-baseline-2026-05-18-rfc0005.txt`): small_matmul -0.7%,
medium_mlp -1.5%, large_network +3.5%.

### Changed

- **`STATUS.md`** — Compiler entry bumped to v0.5.0; IR Stability row
  notes the three Phase 6.2b grammar additions: `while` statement
  form, `[T; N]` fixed-size array types + `[expr, …]` array literals,
  and unsigned-i64 literal reinterpret-cast (range
  `[i64::MAX+1, u64::MAX]` accepted via bit-pattern cast, preserving
  the signed-i64 ABI surface).

### Notes

- Phase 6.5 (fixed-point bootstrap) is the only remaining sub-step of
  the self-host ladder. The mindc surface grammar now expresses
  everything the pure-MIND lexer + parser + type-checker + emitter
  needs to compile mindc-in-MIND. The bootstrap exercise lifts a
  `libmindc_mind.so` from mindc-Rust and verifies its IR output is
  byte-identical to mindc-Rust's compilation of the same input.
- The three closed gaps were each surfaced by real production work
  (Phase 6.1 lexer surfaced Gap 1; Phase 6.3 type-checker surfaced
  Gap 3; mind-nerve A1.1 LUT family surfaced Gap 2). All three closed
  with sub-+7% bench-gate impact under module-level cfg gating.

---

## [1.2.2] - 2026-05-18

### Milestone: RFC 0005 Phase 6.3 + 6.4 shipped (type-checker + MLIR emit in pure MIND)

Two further sub-steps of the self-host ladder land in the reference
implementation. The spec's informative "Self-host smoke" subsection in
`spec/v1.0/stdlib.md` is updated to reflect that **four of the six**
Phase 6 sub-steps are now shipped (6.1 lexer, 6.2a parser, 6.3
type-checker, 6.4 MLIR emit). No normative change — Phase 6 remains
informative.

### Changed

- **`spec/v1.0/stdlib.md` §Self-host smoke** — 6.3 entry now records
  shipped status with the frozen seven-tag type system
  (`ty_unknown=0`, `ty_i64=1`, `ty_f64=2`, `ty_bool=3`, `ty_vec=4`,
  `ty_string=5`, `ty_unit=6`) and the documented Phase-6.3b stub list
  (call-site signature matching, `let`-init mismatch diagnostics,
  cross-fn name hoisting, struct/enum type-name resolution,
  `Result`-shaped diagnostic node). 6.4 entry now records shipped
  status as `examples/emit_ir/` under STARGA/mind.

### Notes

- Phase 6.2b (mindc grammar growth — `while` statement, array literals,
  unsigned-i64 literals + cdylib const-blob linkage) remains the only
  open *optional ergonomic* path. Phase 6.5 (fixed-point bootstrap)
  remains open and is the apex of the self-host thesis.

---

## [1.2.1] - 2026-05-18

### Milestone: RFC 0005 Phase D — mindc 0.4.3 + 0.4.4 (env-var override + diagnostic fidelity)

Two follow-on patch tags refine the RFC 0005 surface ratified in 1.2.0.
The spec gains an informative override clause (Phase D₁) and a diagnostic
fidelity clause (Phase D₂a). Both surface in `spec/v1.0/stdlib.md` only;
no normative ABI or syntax change.

### Added

- **`spec/v1.0/stdlib.md`** — New "Environment override" subsection
  formalising `MIND_STDLIB_PATH` as an informative override for the
  bundled pure-MIND modules. Spec stays implementation-neutral
  (implementations MAY honour it); reference impl ships it from
  mindc 0.4.3 onwards (RFC 0005 Phase D₁) behind the
  `cross-module-imports` feature.
- **`spec/v1.0/stdlib.md`** — New "Diagnostic fidelity for imported
  `pub fn`s" subsection (informative): SHOULD preserve Named struct
  parameter names in error messages (e.g. "expects Vec (heap-record
  i64 addr), got tensor&lt;f32[3]&gt;") rather than collapsing to the
  lowered ABI surface. Diagnostic-only contract — the underlying
  compatibility check stays permissive under the Option-C heap-record
  ABI. Reference impl ships it from mindc 0.4.4 onwards (Phase D₂a).

### Changed

- **`spec/v1.0/stdlib.md` §Compile-speed guarantee** — Updated the
  +5% → +7% regression cap notation to reflect the reference-impl
  threshold loosening at mindc 0.4.3 (GitHub-hosted-runner variance
  on microbenches); the bench-gate workflow comment records the
  rationale.

- **STATUS.md** — Now tracks compiler 0.4.4; IR Stability row
  records the Phase D₁ env-var override and Phase D₂a diagnostic
  ratifications; MIND Compiler reference entry bumped to v0.4.4
  with the +7% bench-gate cap.

---

## [1.2.0] - 2026-05-18

### Milestone: RFC 0005 — Pure-MIND Standard Surface (ratified by mindc 0.4.2)

The standard library chapter gains a normative "Pure-MIND standard surface"
section formalising the four collection / I/O modules that mindc now ships
as in-tree `.mind` source. The previous five high-level modules (`core`,
`math`, `tensor`, `diff`, `io`) remain authoritative for the math+tensor
surface; the new section sits next to them as additive surface area.

### Added

- **`spec/v1.0/stdlib.md`** — New normative section "Pure-MIND standard
  surface (RFC 0005, normative)" documenting:
  - The seven `__mind_*` intrinsics (`alloc`, `realloc`, `free`,
    `load_i64`, `store_i64`, `read`, `write`) and their `i64` ABI.
  - The four bundled modules: `std.vec`, `std.string`, `std.map`, `std.io`.
  - `use std.<name>` resolution rules (bundled-first, last-write-wins
    shadowing, per-arg signature matching, Phase-A fall-through).
  - Compile-speed guarantee (module-level feature gates,
    `parse_typecheck_ir` workloads must not regress by more than 5%).

### Changed

- **STATUS.md** — Now tracks compiler 0.4.2; Standard Library row notes
  the pure-MIND surface; IR Stability row notes the `__mind_*` ABI
  ratification; MIND Compiler reference entry bumped to v0.4.2 with the
  RFC 0005 bench floor (2.80–17.10 µs).

- **`spec/v1.0/ir-stability.md`** — Status preamble now records the
  RFC 0005 extension to the runtime contract surface.

---

## [1.1.3] - 2026-02-17

### Milestone: v0.2.1 Audit Hardening & Security Specification Update

Updated specification to reflect the deep research audit remediation across compiler and runtime.

### Changed

- **Security spec** - Added comprehensive audit hardening section:
  - Compiler findings C1-C7: Conv2d verifier, string interning DoS, IR determinism, constant folding bounds, SSA scope enforcement
  - Runtime findings R2-R6: Deallocate safety, stride validation, padding correctness, determinism verification
  - Supply chain findings S1-S6, A1: cargo-deny CI enforcement with explicit license allowlist

- **Performance spec** - Updated for v0.2.1:
  - Added v0.2.1 to version history (338K compilations/sec, audit-hardened)
  - Updated compilation table to reflect sub-5µs compilation
  - Updated all framework comparisons from v0.1.7 to v0.2.1 numbers
  - Documented -2.6% performance cost of audit hardening (347K → 338K)

- **STATUS.md** - Updated reference implementations:
  - Compiler: v0.1.8 → v0.2.1, 175+ → 220 tests, audit-hardened
  - Runtime: 136 → 53 tests (corrected count for no-default-features), audit-hardened

---

## [1.1.2] - 2026-02-07

### Milestone: v0.2.0 Performance Specification Update (15× parser speedup)

Updated performance benchmarks to reflect v0.2.0 hand-written recursive descent parser.

### Changed

- **Performance benchmarks** - Updated with v0.2.0 criterion results:
  - scalar_math: 1.77 µs (was 26 µs, **14.7× faster**)
  - matmul operations: 2.8-2.9 µs (was 45-46 µs, **15.6× faster**)
  - New benchmarks: tensor_ops (4.75 µs), reductions (2.92 µs), reshape_ops (2.80 µs)
  - Added compilations/sec column: 347,000+ compilations per second

- **Version history table** - Added v0.2.0 entry:
  - v0.2.0: 1.77-2.84 µs, 347,000 compilations/sec (hand-written recursive descent)

- **Framework comparisons** - Updated all speedup calculations:
  - vs PyTorch 2.10 GPU (full pipeline): ~35,000-176,000× faster (frontend vs full pipeline)
  - vs Mojo 0.26.1: ~135,000-458,000× faster

---

## [1.1.1] - 2026-02-04

### Milestone: Performance Specification Update (v0.1.7)

Updated performance benchmarks and compiler targets to reflect production v0.1.7 measurements.

### Changed

- **Performance benchmarks** - Updated with v0.1.7 verified results:
  - scalar_math: 26 µs (was 25 µs)
  - matmul operations: 45-46 µs (was 52-55 µs, **-18% improvement**)
  - Parser optimization: Reordered `choice()` combinator for faster parsing

- **Version history table** - New section documenting benchmark progression:
  - Baseline (Dec 2025): 21-37 µs (minimal parser)
  - v0.1.6: 26-55 µs (full typed tensors)
  - v0.1.7: 26-46 µs (parser optimization)

- **Framework comparisons** - Updated all speedup calculations:
  - vs PyTorch 2.0: ~77,000-122,000× faster
  - vs Mojo 0.25.7: ~20,000-35,000× faster
  - vs JAX/XLA/TVM: ~220-3,850× faster

### Notes

The ~22% overhead vs baseline is the cost of production features (typed tensors, imports, function lowering). v0.1.7's parser optimization recovers ~18% of matmul overhead.

---

## [1.1.0] - 2025-12-27

### Milestone: Production GPU Backends & AI Protocol

This release brings production-grade GPU backends and AI-native tooling for seamless
integration with modern AI development workflows.

### Added

- **MindIR Compact (MIC) Format** - RFC-0001:
  - Token-efficient IR serialization (4x reduction vs JSON)
  - Line-oriented format for Git-friendly diffs
  - Deterministic canonicalization with roundtrip guarantee
  - Security limits (input size, node count, shape dims, interner capacity)
  - Thread-safe string interning with bounded memory

- **Mind AI Protocol (MAP)** - RFC-0002:
  - Compiler-in-the-loop protocol for AI agents
  - Structured diagnostics with fix suggestions
  - Incremental patching (insert, delete, replace, batch)
  - Security modes (no_io, no_unsafe, pure_only)
  - Poison-safe session management

- **Production GPU Backends** (mind-runtime):
  - Metal backend with full trait implementations
  - ROCm/HIP backend for AMD GPUs
  - WebGPU backend for cross-platform support
  - CUDA backend with production parity
  - Features: poison-safe locking, defragmentation, context recovery, stream sync

### Changed

- Updated STATUS.md to reflect 10 implemented RFCs
- Updated implemented.md with MIC and MAP entries
- GPU backends now production-ready (previously MockGpuBackend)

---

## [1.0.0] - 2025-12-19

### Milestone: 100% Specification Complete

The Core v1 specification is now stable and complete, with all reference implementations
verified and passing.

### Added

- **14 specification chapters** - All marked stable:
  - Surface Language, Core IR, Static Autodiff, Shapes & Tensor Semantics
  - Standard Library, Error Catalog, Conformance, Versioning & Stability
  - MLIR Lowering, Runtime Interface, Security & Safety
  - Performance & Benchmarks, Foreign Function Interface, Future Extensions

- **3 EBNF grammar files** - Complete formal grammar:
  - `grammar-lexical.ebnf` - Lexical structure
  - `grammar-syntax.ebnf` - Surface language syntax
  - `grammar-ir.ebnf` - Core IR textual format

- **13 example files** - Comprehensive examples:
  - Basics (3): hello_tensor, broadcasting, reductions
  - Autodiff (2): simple_grad, mlp_backward
  - Linear Algebra (2): matmul, conv2d
  - FFI (2): c_bindings.mind, python_embed.py
  - IR (4): simple_module, autodiff_output, matmul_module, reduction_module

- **Reference implementation sync**:
  - `star-ga/mind` compiler: 69 tests passing, LLVM 18, 0 Clippy warnings
  - `star-ga/mind-runtime`: 33+ tests, GPU docs, release workflow

### Changed

- Updated `STATUS.md` with reference implementation status
- Updated `docs/README.md` to reflect v1.0 stable status
- Added status badges to main `README.md`

---

## [0.9.0] - 2025-11-07

### Added

- Initial draft of Core v1 specification chapters
- RFC process documentation
- Design principles

---

[Back to Spec Index](./spec/index.md)

## [1.1.4] - 2026-04-10

### Milestone: v0.2.3 Clean Core Release

Aligned specification with compiler v0.2.3 and runtime v0.1.9 releases.

### Changed

- **Compiler v0.2.3** — Removed XRM/ASIC target dialect from compiler core
  - ASIC backend moved to mind-runtime where all hardware backends belong
  - Added `use` keyword parser support (alias for `import`)
  - Clean separation: compiler generates IR, runtime executes on target hardware

- **Runtime v0.1.9** — Added ASIC backend, struct/enum parser stripping
  - `src/backend/asic/` — XRM-SSD ASIC target dialect (from compiler v0.2.2)
  - `strip_mind_syntax` handles struct/enum blocks for multi-module programs
  - `mind_main` symbol exported for compiled program entry

### Architecture Clarification

The MIND ecosystem has three layers:
1. **mind** (compiler) — Parser, type checker, IR, autodiff, MLIR lowering. No hardware backends.
2. **mind-runtime** — Hardware backends (cuda, metal, rocm, webgpu, webnn, asic), eval engine, FFI.
3. **mind-spec** — Language specification, design documents, conformance tests.

Backend code belongs in mind-runtime, not in the compiler.
