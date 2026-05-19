# Changelog

All notable changes to the MIND Language Specification are documented here.

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.5] - 2026-05-19

### Milestone: RFC 0007 (Mindcraft) sequencing gate CLEARED — documentation/sequencing only, no compiler change

`mind@a29726c` flips RFC 0007 (the pure-MIND `mindc fmt`/`lint`/`check` toolchain — "the toolchain self-hosts") from gated to **build-may-begin**. The gate was native-encoder end-to-end measurement plus numerical correctness, and the criterion benchmark publication. Both are satisfied: the native pure-MIND encoder runs end-to-end and validates against the reference encoder at cosine 0.999996 / top-5 route overlap 0.9975 (≥0.92 gate, n=160) with the cross-arch Q16.16 bit-identity invariant preserved, and the criterion benchmark publication is complete.

**No compiler/runtime version change** — this is a documentation and sequencing milestone (RFC status + roadmap), recorded here for spec-side traceability. The compiler remains at v0.6.4 (`mind@8e4b925`, tag `v0.6.4`); the gate-flip commit `a29726c` is docs-only and intentionally not tagged. Further native-encoder latency optimization continues independently and is not a Mindcraft prerequisite (the gate is measurement + numerical correctness, both met).

This entry's "RFC 0007" follows the established STATUS/changelog convention where `RFC NNNN` denotes the **compiler-repo** RFC (as with the existing "RFC 0006 mind-blas" / "RFC 0005 pure-MIND std" citations). It is distinct from the mind-spec RFC registry in `docs/rfcs/` (where RFC-0007 is the FFI Specification), which is unchanged.

### Changed

- **`STATUS.md`** — header note appended: Mindcraft (compiler-repo RFC 0007) sequencing gate cleared 2026-05-19; compiler tracking line unchanged at v0.6.4.

---

## [1.3.4] - 2026-05-19

### Milestone: mindc v0.6.4 — RFC 0006 Track B increment 2; cross-arch bit-identity gate #57 closed for the vector dot

`mind@8e4b925` + tag `v0.6.4`, CI 6/6 success. Track B increment 2 lands the **Q16.16 vector path** `dot_q16_v` — a `vector<8xi64>` widen-multiply-`shrsi 16`-accumulate `scf.for` loop + an associative `vector.reduction <add>` horizontal i64 sum + scalar tail + `trunc i64→i32`/`sext` pack. It is **byte-identical to the Track A scalar oracle `__mind_blas_dot_q16`** at every length {0,1,2,7,8,9,15,16,17,31,32,33,1024,4096,65537} — exact, not tolerance (Q16.16 integer reduction is associative, per-element arithmetic `>>16` replicated). This **closes the task #57 cross-arch bit-identity obligation for the thesis-pure vector dot-product** (single-x86-host scope, as Track A §5.2; the full Linux-x86 ↔ macOS-ARM ↔ CUDA-x86 ↔ photonic hardware contract remains the outstanding #57 portion, and `dot_l1_q16_v` is the remaining Q16.16-metric for full vector-path parity — deferred to increment 3).

Also landed: `Instr::VecStore` (symmetric vector store), `VecLoadI32`/`VecMulAddQ16`/`VecReduceAddI64` IR primitives, f32 `dot_l1_f32_v`/`dot_linf_f32_v` (L∞ via `vector.reduction <maximumf>`), and a dense-reduction-throughput bench sub-category.

### Notes

- **Bootstrap fixed-point unchanged**: 10,889 bytes / 206 SSA (bootstrap sources use no vector ops). Same clean no-shift discipline as v0.6.2/v0.6.3.
- **Bench-gate 0.0%**: the default-feature `mindc` binary built at clean `c130db3` vs increment-2 HEAD is **byte-identical** (sha256 `9a9edf429e8971a089f93dfe8725dc47d49527a7e3ca5b1bbf99b00ee8a16717` both) — all increment-2 code is `#[cfg(feature = "std-surface")]`-gated and absent from the binary the `compiler` bench measures. CI Bench gate: success.
- 519 std-surface tests; clippy (both feature sets) + `cargo fmt --check` + rustdoc `-D warnings` clean. Track A `blas_smoke` 12/12 + inc-1 `blas_vec_smoke` 3/3 green. One pre-existing inc-1 test-harness temp-`.so` self-race fixed (OnceLock single-build); inc-1 code paths untouched.
- **Increment 3 honestly deferred** (RFC 0006 §9.3): `dot_l1_q16_v`, real `@target("simd-x86"|"simd-arm")` per-call annotation (needs MLIR target-attr plumbing, explicitly not shipped as an inert token), vectorised `matmul_rmajor_f32` inner loop, cross-module `use std.blas` vector inlining.

### Changed

- **`STATUS.md`** — compiler entry bumped to v0.6.4; #57 marked closed for the vector dot.

---

## [1.3.3] - 2026-05-19

### Milestone: mindc v0.6.3 — RFC 0006 mind-blas Track B increment 1 (native MLIR vector dialect)

`mind@c130db3` + tag `v0.6.3`. Track A (runtime-support AVX2 C bridge, v0.6.x) is joined by **Track B increment 1**: a pure-mindc vectorisation path. New `std-surface`-gated IR primitives — `Instr::VecLoad`, `Instr::VecFma`, `Instr::VecReduceAdd` (+ a `VectorF32` value kind) — lower to the MLIR `vector` dialect (`vector.load`, `vector.fma`, `vector.reduction <add>`), legalised to target SIMD by LLVM. `dot_f32` now has a fused 8-lane FMA loop + horizontal reduction + scalar tail emitted by the compiler itself, with no C-shim / clang / `-fPIC` dependency (so no Windows-MSVC packaging problem). Track A's `__mind_blas_dot_f32` extern path is untouched and still registered — Track B is strictly additive.

### Notes

- **Bootstrap fixed-point unchanged**: `libmindc_mind.so` still compiles its own source byte-identically (10,889 bytes / 206 SSA). Bootstrap sources use no vector ops, so the oracle does not shift — clean no-shift case, same discipline as v0.6.2.
- **Bench-gate ≤ +7%**: small_matmul −0.5%, medium_mlp +0.1%, large_network +3.0% (inside the documented large_network jitter band). Default-build hot path byte-identical — all Track B IR/lowering is `#[cfg(feature = "std-surface")]`-gated and absent from `parse_typecheck_ir`. The 2.80–17.10 µs frontend floor is preserved.
- **Numerical equivalence**: emitted vector `dot_f32` is within 1e-4 relative of an f64 oracle at 1,024 and 1,000,000 elements (measured ~3e-7 and ~6e-6); byte-identical to the sequential scalar reference at sub-lane lengths; ragged lengths verified. Track A Q16.16 byte-identity gate (#57) still 12/12 green, unchanged.
- 519 `std-surface` tests pass; clippy (both feature sets) + `cargo fmt --check` + rustdoc `-D warnings` clean; CI board green.
- **Deferred to Track B increment 2** (honestly scoped in RFC 0006 §9): Q16.16 vector path + its cross-arch bit-identity gate, `VecStore`, vector lowering for `dot_l1`/`dot_linf`/`matmul_rmajor`, per-call `@target(...)` substrate annotation, cross-module std-wrapper inlining, dense-reduction-throughput bench sub-category.

### Changed

- **`STATUS.md`** — compiler entry bumped to v0.6.3 with RFC 0006 Track B increment 1 framing.

---

## [1.3.2] - 2026-05-19

### Milestone: mindc v0.6.2 — negative-literal correctness fix (compiler bug #11)

`mind@969c2da` + tag `v0.6.2`. The IR-lowering function `lower_expr` had no arm for the unary-minus AST node, so **every bare negative integer/float literal — and any unary-minus expression — fell through to the catch-all and was silently lowered to `const 0`**. `let a: i64 = -65536; return a;` emitted `0`; the binary form `(0 - 65536)` was always correct (separate `Sub` arm). The fix adds a `Node::Neg` arm: integer literal → `ConstI64(n.wrapping_neg())` (`-INT64_MIN` well-defined, matching two's-complement `0 - INT64_MIN`), float literal → `ConstF64(-f)`, any other operand → `0 - operand` via `Sub` (selecting `arith.subi`/`arith.subf` exactly as the hand-written subtraction form).

Surfaced by the pure-MIND lookup-table work in the routing pipeline: generated tables with entries like `-524288` / `-65536` were silently zeroed at lowering time — invisible until the C shim that had masked the pure-MIND path was removed.

### Notes

- 519 reference-implementation tests pass (10 new negative-literal regression cases). Bench-gate **improved**, not merely held: small_matmul −1.2 %, medium_mlp −1.8 %, large_network −0.2 % vs the post-RFC-0005 baseline; the 2.80–17.10 µs frontend floor is preserved.
- The v0.6.1 **bootstrap fixed-point is unchanged**: `libmindc_mind.so` still compiles its own source byte-identically (10,889 bytes / 206 SSA values). The oracle did not shift because the pure-MIND bootstrap sources contain zero negative literals — a `Node::Neg`-only change cannot affect them. Clean "no legitimate shift" case.
- Cumulative compiler bugs surfaced + closed by the pure-MIND self-host / end-to-end discipline: **11** (0 lexer + 3 parser + 3 typecheck + 1 emit_ir + 0 apex + 3 fixed-point + 1 negative-literal). Each a true correctness fix the pure-MIND path forced into the open.

### Changed

- **`STATUS.md`** — Compiler entry bumped to v0.6.2; cumulative bug count 10 → 11.

---

## [1.3.1] - 2026-05-18

### Milestone: mindc v0.6.1 — Bootstrap fixed-point REACHED

`libmindc_mind.so` (the pure-MIND mindc, the 78,488-byte combined cdylib that shipped in v0.6.0) was fed its own 1,084-LOC `.mind` source as input. The returned MLIR text — **10,889 bytes, 206 SSA values** — is **byte-identical to mindc-Rust's `--emit-ir` output on the same source**. The bootstrap fixed-point is reached: the Rust implementation is now decorative, required only for the initial bootstrap.

**Closure (`mind@e29b734` + tag `v0.6.1`):** the FIRST-DIVERGENCE diagnosis flagged 6 missing SSA values. Two narrow emitter gaps + one parser gap closed the loop:

- `emit_program_items` skipped `UseDecl` items (kind 7) — fix: emit one `const.i64 0` / `output` stub per `ast_use()` item.
- `emit_program_items` skipped `StructDef` items (kind 13) — but more importantly, the pure-MIND parser didn't recognize `struct` as an item-starting keyword, so each struct body token became a separate ident item. Fix required two parts: (a) add `parse_struct_def` to the parser so it consumes the whole `struct Name { ... }` and returns a single `ast_struct_def` (kind 13) leaf node; (b) emit one stub for `ast_struct_def()` items in `emit_program_items`.
- `lower_program` had one spurious leading stub with no oracle counterpart — removed.

Net: −1 + 4 (UseDecl) + 3 (StructDef parse + emit) = +6 — exactly the gap. Pre-closure: 195 SSA values, 97% byte-identical. Post-closure: 206 SSA values, **100% byte-identical**.

### What this proves

The self-host loop closes on its own source. The pure-MIND mindc can compile MIND programs — including its own implementation — and produce IR text the reference compiler would produce. From here, the Rust implementation can be retired from any new feature work; v0.6.1 and forward, all new compiler features can land in `examples/mindc_mind/main.mind` and round-trip through itself.

### Changed

- **`STATUS.md`** — Compiler entry bumped to v0.6.1 with "Bootstrap fixed-point REACHED" framing.

### Notes

- Cumulative compiler bugs surfaced + closed by the self-host ladder + fixed-point: 0 (lexer) + 3 (parser) + 3 (typecheck) + 1 (emit_ir) + 0 (apex) + 3 (fixed-point) = **10**. Each was a true correctness fix.
- Default-build hot path remained byte-identical through the closure. Bench-gate +7% cap held: 2.80–17.10 µs frontend floor preserved across v0.4.4 → v0.6.1.
- The mind-nerve A1.5 native-encoder p95 measurement against v0.6.1 surfaced a separate, expected substrate gap: pure-MIND tail-recursive scalar matmul on an 11,922-row catalog is 14.4 ms p50 vs 0.38 ms p50 for numpy+BLAS. mind-blas (a MIND-native SIMD/vector backend, two tracks: runtime-support C bridge + RFC 0006 native MLIR vector dialect) is queued as the follow-on substrate work.

---

## [1.3.0] - 2026-05-18

### Milestone: mindc v0.6.0 — Phase 6.5 APEX REACHED (self-host thesis proven)

The reference implementation has reached the **apex of the Phase 6 self-host ladder**. The pure-MIND mindc — a 1,084-LOC `.mind` driver merging the lexer + parser + type-checker + MLIR-text emitter at `examples/mindc_mind/main.mind` — was compiled via mindc-Rust's `--emit-shared` to a 78,488-byte cdylib. A Python ctypes harness calls `mindc_compile(src_addr, src_len)` on `examples/mindc_mind/fixture.mind` and the returned 148-byte MLIR text is **byte-identical to mindc-Rust's `--emit-ir` output on the same input**.

**All five stages of the self-host ladder PASS:**

| Stage | Pure-MIND surface | Output | Bytes verified |
|---|---|---|---:|
| 1 | `examples/lexer/main.mind` | 32-token stream | byte-identical (v0.5.1) |
| 2 | `examples/parser/main.mind` | 42 AST nodes | byte-identical (v0.5.2) |
| 3 | `examples/typecheck/main.mind` | 127-byte type-check report | byte-identical (v0.5.3) |
| 4 | `examples/emit_ir/main.mind` | 148-byte MLIR text | byte-identical (v0.5.4) |
| **5 = APEX** | `examples/mindc_mind/main.mind` (combined) | 148-byte MLIR text | **byte-identical to mindc-Rust** (v0.6.0) |

This is the credibility milestone any new language must cross. The MIND language is now demonstrably expressive enough to host its own compiler, and the integrated pipeline produces the reference compiler's exact output byte-for-byte.

### Notes

- The self-host ladder surfaced and closed **seven latent compiler bugs** across IR control-flow lowering, subprocess plumbing, std-surface C stubs, Python harness decoding, and POSIX I/O contract — bugs that had been correct-looking under all prior tests because no other input had exercised those code paths. Each was a true correctness fix.
- Default-build hot path remained byte-identical through every addition. Bench-gate +7% cap held: 2.80–17.10 µs frontend floor preserved across v0.4.4 → v0.6.0 (six tagged versions in one day).
- The second-order goal (`libmindc_mind.so` compiles its own source byte-identically — bootstrap fixed-point) is now reachable: a follow-on round-trip exercise on top of v0.6.0. After fixed-point, the Rust implementation is decorative — only required for the initial bootstrap.
- The combined `examples/mindc_mind/main.mind` uses a deliberate textual merge of the four sub-components with deduplicated helpers, rather than multi-file `use`, because mindc v0.5.4's `use`-resolver covers only `std.*`. Extending the resolver to user-defined modules is tracked as a follow-on item but is not on the apex path.

### Changed

- **`STATUS.md`** — Compiler entry bumped to v0.6.0 with APEX REACHED framing.

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
