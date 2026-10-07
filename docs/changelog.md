# Changelog

All notable changes to the MIND Language Specification are documented here.

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed — owner rulings of 2026-10-07 (targeted for specification 1.7.0)

- Import paths separate their segments with `.` in the grammar (`ImportPath`). The earlier `::` spelling was never accepted for `import` by a released reference compiler; the reference `use` still accepts `::` as an extension.
- Added the normative [Module-qualified references](../spec/v1.0/language.md#module-qualified-references) rule: an import qualifier selects the member exported by the module that import names, and an unexported member is refused with `E2002`. The reference does not yet conform for functions: two imported modules that export the same function check without a diagnostic but fail to link.
- The compile-speed bound in [Standard Library](../spec/v1.0/stdlib.md) is now 10%, matching what the reference gate enforces (it previously stated 7%). It is to be tightened only when measured run-to-run noise is well below the tighter value.
- A verifier MUST name a retired signature scheme's tag as legacy and non-compliant, so a retired signature is never mistaken for corruption, and MUST NOT silently downgrade verification. The reference's wording is a pending compiler change.

### Fixed — status accuracy

- Qualified the ML-DSA-87 + SLH-DSA-SHAKE-256s signing profile as implemented on compiler main after v0.10.2 (pending release; v0.10.2 contains neither scheme) and replaced the legacy-format sentence that implied retired signatures could still be accepted.
- Described the native-ELF image as a pure function of the source image it is given (user sources plus the fixed seed standard library) everywhere, not of "the IR".
- RFC 0001: replaced the unmeasured `mic@3` ratio, which came from a reference-model encoder rather than `mindc --emit-mic3`, with the measured canonical size of the same network (87 bytes at compiler `83ed6a11`). No JSON encoding of that IR exists, so no ratio is stated.
- Removed vendor attribution from the MHS profile and roadmap pages and from STATUS.

### Added — E2036 and E2037 type-check refusals

- Added pending catalog entries `E2036` (a proven non-integer or opaque-handle value stored into an `i8`/`u8`/`i16`/`u16` element; compiler `0a8b34a5`, merged with PR #263 at `1833f095`) and `E2037` (a function name used as a value; compiler `1def5dde`). Both are additive Core v1 catalog changes targeted for specification 1.7.0; they do not declare that release or promote an unreleased compiler artifact.
- Clarified that `E2002` covers bare-headed `Enum::Variant` paths whose enum is unimported, exported by several imports, or lacks the variant. The compiler integrations remain pending and unpromoted.

### Documentation alignment: type-checking refusals and record arrays

- Recorded pending reference coverage for `[i64; N]` struct-literal field cardinality and element checks under `E2001` (compiler `c4c7b034`) without extending the normative let/const cardinality rule.
- Clarified that an unsupported integer width must be refused rather than computed at another width; the reference refuses annotations wider than 64 bits (compiler `4fd65cfb`).
- Documented bare-headed imported enum variants, resolved through the module's imports or refused with `E2002` (compiler `1def5dde`, `cross-module-imports`).
- Linked `E2036` from record-field array coverage and narrowed the pure-MIND native record-array statement to a read-only emitter slice (`c4c7b034`, `9b23e3fe`) that the standalone compiler and canonical trace paths still refuse (`fe912396`, `a80b67ea`). The compiler integrations remain pending and unpromoted.

### Documentation alignment: surface-language status

- Clarified that `f32`/`f64` comparison operators are IEEE 754 comparisons (with a NaN operand all are false except `!=`) and recorded reference status: unordered MLIR `!=` since compiler `2597ee9c`, native x86-64 `f64` since `ccbb00b8`, and an open `mindc test` defect for `f64` comparisons.
- Added the parenthesised `assert(cond, "message")` form to the grammar as an additive form targeted for specification 1.7.0 (compiler `487dd5c7`).
- Recorded informative reference status for range-`for` loop-variable re-declaration (`fe9854ec`), the `E2037` function-as-value refusal (`1def5dde`), and import aliases and `::` member references (`f2fc890d`, `cd150ae7`). The import-path separator and the qualifier rule are covered by the owner-ruling entry above.
- Fixed the Core IR link for binary operations. The compiler integrations remain pending and unpromoted.

### Documentation alignment: source test evaluation

- Required source test runners to evaluate integers at the same declared widths as compiled artifacts and to refuse values they cannot materialise at a narrow width; recorded the reference evaluator's coverage and gaps (compiler `97c0d273`, `74004786`, `2575c1e9`, `a7f9520a`).
- Recorded path-spelled imported calls and constants under `mindc test` (`953d7233`) and failure reporting for `assert(cond, "message")` (`487dd5c7`), and noted the open `mindc test` defect for `f64` comparisons. The compiler integrations remain pending and unpromoted; this entry does not represent a compiler-version change.

### Documentation alignment: assertion message form and reduction evidence

- Added `assert(condition, message)` with a string-literal message to the `core` module as an additive form targeted for specification 1.7.0 (compiler `487dd5c7`, pending release).
- Noted that the fixed-order strict `f32` dot (length 4093) and 64x64 matrix-vector kernels carry committed matching AVX2 and NEON output hashes (compiler `c8efcf9a`), without removing the vector-reduction tolerance allowance.

### Documentation alignment: determinism and evidence verification

- Clarified that a retired-scheme evidence signature verifies as `retired`, never valid or absent, and that retired or malformed signing seeds are refused without an artifact (compiler PR #262: `83bebf39`, `2b8d5e2e`, `9881cb91`). This supersedes the 'pending retirement' wording in the bounded native project builds entry; releases remain unsigned.
- Recorded declared-width integer wrapping, refusal of integer widths above 64 bits (`4fd65cfb`), per-backend status of IEEE NaN comparisons (`2597ee9c`, `ccbb00b8`), and the rule that a user-defined function is never replaced by a host library routine (`9c231f50`).
- Qualified vector-reduction wording with the two committed strict `f32` kernels (`c8efcf9a`) and updated the cross-substrate inventory to 35 workloads, including ten scalar-`f64` quant workloads (`545ed80c`, `82e34947`). The compiler changes remain pending release.

### Documentation alignment: MLIR build path and native backend location

- Recorded that the reference build driver marks every MLIR function definition `nobuiltin` before the LLVM toolchain runs, leaving `--emit-mlir` text unchanged (compiler `9c231f50`, pending release).
- Replaced the removed `src/native` path with the pure-MIND emitter in `examples/mindc_mind` (removed in compiler `776facc8`) and repaired the runtime GPU-backends link.

### Documentation alignment: implementation evidence reference

- Moved the implementation-evidence source reference to compiler `7831998b` and re-verified its source anchors.
- Recorded the native first-fence changes (IEEE-ordered `f64` comparisons, `ccbb00b8`; named refusal of `f32`/`f16`/`bf16` types, `a1b0b5f5`, `f6541e21`), the formatter write guard and check drift reporting (`eb872eaf`, `f2fc890d`, `6f9ac5eb`), early-failure reporter output (`fbb08821`) and the LLVM/MLIR 20 toolchain requirement (`3f9b80df`). Artifact and command receipts remain UNKNOWN; none of these is a release claim.

### Documentation alignment: mic@3 0x04 mirror status

- Updated the experimental pure-MIND mirror status: complete core body decoding with canonical re-emission (compiler `70434b42` to `bb53942b`) and a separate semantic gate covering ValueId coverage, function identity, parameter agreement, duplicate definitions, authority presence, scope membership and per-function element allowances (`1eefe191` to `3923608a`). Parameter names, typed call relationships, string-table minimality and refusal-order parity remain open. The mirror remains a review candidate; no v04 wire contract or Core v1 requirement is established.

### Documentation alignment: checked canonical source lowering

- Recorded the opt-in source-to-canonical-IR API from [compiler PR #259](https://github.com/star-ga/mind/pull/259), including captured ownership, checked scalar producer facts, and validation of returns in each function scope.
- Distinguished canonical source restrictions from ordinary compiler compatibility and kept native aggregate execution, pure-MIND codec parity, and the standalone MIND driver open.

### Documentation alignment: bounded native project builds

- Recorded the native project-build path landed in [compiler PR #257](https://github.com/star-ga/mind/pull/257): manifest entry and local-import resolution, export visibility, and entry-module ownership of `main` for the admitted scalar/control-flow subset.
- Kept Rust host-driver dependence and aggregate/full-language native coverage explicit. Unsupported owned aliases, structs, and enums are refused.
- Clarified the supported production signing profile, ML-DSA-87 **and** SLH-DSA-SHAKE-256s, and that published releases are currently unsigned. Ed25519 and the Ed25519/ML-DSA-65 hybrid have since been retired from signing and trust verification (see the determinism and evidence verification entry above).

### Added — E6009 compiler materialization refusal

- Reserved `E6009` for deterministic compiler-side materialization refusal,
  while preserving `E6002` as Backend unavailable. This is an additive Core v1
  catalog change targeted for specification 1.7.0; it does not declare that
  release or promote an unreleased compiler artifact.
- Required a non-zero refusal and no partial runnable artifact. Accepted source
  may still be refused when an aggregate shape has no runnable lowering
  representation, so `E6009` is not classified as a type error.

### Added — E6010 invalid manifest export

- Assigned `E6010` to invalid `Mind.toml [exports] c_abi` entries after the
  catalog scan confirmed that Core v1 `E6001` is already the out-of-bounds index
  code. This keeps the manifest validation diagnostic outside the capability
  cause namespace and is additive for the planned 1.7.0 specification update.

### Documentation alignment: pending compiler contracts

- Publish the versioned specification with the documentation site. Pages now
  uploads the generated artifact containing the canonical chapters, so language
  and conformance navigation reaches the same files maintained in the repository.
- Specified source-test discovery, exact imported module ownership, exported
  type validation, dependency standard-library capture, and isolated lexical
  globals. Distinguished interpreter digest verification from native execution,
  signature verification and compiler promotion. Compiler reference: `eedcfb2c`.
- Clarified inferred struct-literal bindings, same-struct reassignment and
  preservation of declared integer widths. Documented the confident numeric
  scalar replacement refusal (`E2026`) and retained genuine scalar narrowing
  errors. Shared-library regression evidence does not promote native-ELF
  coverage or full structural inference.
- Added the pending `std-surface` `array<T>`-to-`&[T]` / `&mut [T]` call
  boundary to the normative type and error chapters, including the Option-C
  `[addr, len, cap]` handle, supported operations, and E2032/E2033 split.
- Clarified that slice capability flow is checked through implemented branch
  and loop joins, while general lifetime and mutable-alias exclusivity analysis
  remain future work.
- Documented manifest-owned qualified imported types, including export and
  import visibility, owner-preserving aliases, and `E2002` refusal. Inline
  module names remain parser-only syntax and do not establish semantic
  ownership; project ownership comes from the enclosing source file.
- Added the pending `E2300` and `E2301` check/build refusal contracts. Both
  require structured user errors and no artifact, while preserving valid
  owner-rebinding collection updates and final catch-all patterns.
- Distinguished the owned-array `push` replacement-handle contract from the
  scalar status returned by `set`, and retained the borrowed-slice capability
  boundary.
- The corresponding compiler integrations remain pending and unpromoted; this
  entry does not represent a shipped compiler artifact or compiler-version
  change.

## [1.6.0] - 2026-08-14

### Aligned: mindc v0.10.2 (corr2 correctness batch) + Rust-independence (RI) track

- **Compiler reference bumped to mindc v0.10.2.** v0.10.2 is a correctness-hardening
  batch (`corr2`): the signedness/width-erasure family (`u8`/`u16` intermediate-op
  wrap, `u64` signed `compare`/`div`/`rem`/`shr`, `x as bool`), bounds/arity checks,
  bare enum-payload patterns resolved against the scrutinee enum (`corr2/#287-F3`), a
  `continue`-in-match-arm forward-phi fix, and the `Mind.toml` version-parity keystone
  gate. Cardinal invariant held: **0 wrong-bytes** on every gate.
- **Rust-independence (RI) track documented in STATUS.md.** The native-ELF backend is
  the pure-MIND emitter (no `src/native`). Closed: mic@3 canonicality (RI-A),
  native-ELF float + tensor/SIMD emit with zero MLIR/LLVM (RI-B), the pure-MIND host
  driver (RI-C), and the native-ELF self-host **reproduction fixed point** (RI-E1).
  Near-term milestone **RI-D**: `mindc build --backend native` producing a runnable ELF
  with zero `mlir-opt`/`mlir-translate`/`clang` for the covered scalar subset,
  fail-closed (no MLIR fallback). **Honest scope:** the default build still uses the
  Rust + MLIR-text → `clang` pipeline; full-language native coverage, register
  allocation, and the default-backend flip remain roadmap.

---

## [1.5.0] - 2026-06-25

### Milestone: mindc v0.10.0 — native-ELF self-host fixed point closed; backend architecture pivot

This spec cut documents two related changes that land together in the v0.10.0 window:

#### Backend architecture pivot (2026-06-24)

The normative self-host target is now the **native-ELF backend** (`src/native`), not the MLIR-text
backend. Rationale: the native-ELF output is a pure function of the IR (determinism-by-construction),
making it the correct anchor for the self-host convergence proof. The MLIR-text backend is demoted to
**downstream-interchange and exotic-chip-reach** status — it remains fully supported for LLVM/MLIR
ecosystem interoperability and for reaching accelerator targets (TPU, NPU, custom silicon) available
in the commercial `mind-runtime` under license. "Target any chip" is implemented via a pluggable
backend trait; the choice of normative self-host path does not affect that reach.

#### Native-ELF self-host fixed point (verified 2026-06-25)

The pure-MIND compiler front-end (`examples/mindc_mind/main.mind`) now reproduces the Rust reference
byte-for-byte across all three self-host gates:

- **(a) mic@1 IR-text bootstrap fixed point** — the textual IR of `main.mind` compiled by the
  pure-MIND front-end matches the Rust oracle byte-for-byte.
- **(b) mic@3 canonical-binary-IR flip** — the binary `IRModule` matches the Rust reference
  byte-for-byte (CI gate `mic3_flip_smoke.py` 7/7).
- **(c) Native x86-64/ELF emit of the entire seeded module** — the native ELF produced by the
  pure-MIND compiler for the full module (21 stdlib modules + `main.mind`, 1 055 777 B) is
  byte-identical to the Rust reference. The native-ELF self-host fixed point is closed.

**What remains:**
- The 32-byte `ir_trace_hash` PT_NOTE embedded in the ELF is still fed from the Rust oracle; a
  pure-MIND SHA-256 is implemented but not yet wired to the pruned-combined mic@3 emit.
- The Rust `src/native` backend is not yet deleted.
Correct framing: the pure-MIND native backend reproduces the full self-host module byte-for-byte
(the core of the front-end self-host fixed point — full-chain toolchain Rust-independence stays
roadmap); the final trace-hash note emit and the Rust-backend removal remain.

### Spec changes in this 1.5.0 cut

- **`STATUS.md`** — Last-Updated 2026-06-25; header rewritten to state the backend pivot, the
  three self-host gates, and the two remaining items precisely.
- **`spec/v1.0/mlir-lowering.md`** — Added a "Backend role" preamble block noting that MLIR-text
  is the downstream-interchange backend, not the normative self-host target; the native-ELF backend
  holds that role. The chapter's normative lowering rules are unchanged.
- **`docs/design/compiler.md`** — Last-Updated 2026-06-25; added a backend note in the header;
  pipeline diagram updated to show native-ELF as the normative self-host exit alongside the MLIR
  interchange exit; stage 9 split into 9 (native-ELF, normative) and 9b (MLIR, downstream).
- **`README.md`** — MLIR lowering TOC entry annotated as downstream-interchange / non-normative
  self-host path.

---

## [1.4.0] - 2026-05-28

### Milestone: mindc v0.7.x — RFC 0007 / 0008 / 0010 / 0011 / 0012 / 0013 Tier 1 ship + IR-canon unification (RFC 0014 / 0016 / 0021)

The credibility-ladder rung 3 graduation: Mindcraft (RFC 0007) and the
cargo-retirement track (RFC 0008) shipped in mindc v0.6.8 and v0.7.0,
followed by the post-tag IR-canon unification work in v0.7.x. Headline
ratifications since `v0.6.7` (the v1.3.8 entry below):

- **RFC 0007 Mindcraft — fully shipped (v0.6.8).** All six phases plus the
  MINDCRAFT-001 keystone: `mindc fmt`, lint-rule infrastructure, 5 named
  lint rules, `mindc check` project driver, `--fix` + CI workflow + LSP
  reporter, and `pub` keyword AST + formatter round-trip preservation.
- **RFC 0008 `mindc build` / `mindc test` — all 7 phases shipped (v0.6.8 →
  v0.7.0), Phase G is the KEYSTONE.** `mindc build` produces
  `libmindc_mind.so` byte-identical to the v0.6.1 fixed-point oracle, driven
  entirely by the pure-MIND build orchestrator. Cargo is no longer
  load-bearing for the pure-MIND compile loop.
- **RFC 0010 memory safety + C ABI — Phases A/B/C + J-A/J-B shipped (v0.7.0).**
  `extern "C"` + SysV/Win64 ABI; the three-tier memory model with
  `region { }` (region-interior) and `GenRef` (region-exterior, generation-
  checked references that return `None` on stale-handle deref instead of
  use-after-free UB). Phase G1 dropped vestigial `melior`/`inkwell` deps.
- **RFC 0011 async + structured concurrency — Phase A shipped (v0.7.0).**
  `std.async` as the 12th gated stdlib module: explicit-Scheduler API,
  Sender/Receiver composition, and a deterministic `ReplayScheduler` with a
  byte-stable FNV-1a `trace_hash`. Phases B/C/D remain.
- **RFC 0012 tensor-native surface syntax — Phases A + B + C shipped (post-tag).**
  Shape-typed `Tensor<dtype,[dims]>` with compile-time diagnostics; the `@` /
  `.+` / `.-` / `.*` / `./` / `.T` / reduction operator surface desugaring
  to `std.blas` (byte-identity-gated); `#[deterministic]` / `#[target(...)]`
  / `#[q16]` annotation checks. Attributes unified on `#[name]` (§5 hard-cut).
- **RFC 0013 Tier 1 — agent-grade std surface (post-tag).** `std.cli`,
  `std.io` ANSI/TTY, `std.string` helpers, `std.tui` (Box / Text /
  terminal-size), and **`std.sha256`** (pure-MIND FIPS 180-4 — the hash
  primitive the evidence chain anchors on). Tiers 2–6 remain.
- **RFC 0014 `mic@2.1` MAP-extension carrier — shipped (post-tag).** The
  Metadata-Attachment-Pair epilogue on `mic@2`/`MIC-B`. Documented in
  `spec/mic/mic2.1-spec.md`. Back-compatible by omission.
- **RFC 0016 evidence-chain emission — Phase A + Phase B shipped (post-tag).**
  Compile-time provenance attestation. Phase A: inert MAP-epilogue emission
  (`determinism / substrate / toolchain / trace_hash` + optional `parent`).
  Phase B: `verify_evidence_chain` verifier core. **GAP-1 (closed,
  `mind@db5cb76`)** originally anchored the `trace_hash` on the canonical
  `mic@1` textual serialisation. **Re-anchored 2026-05-31** to
  `SHA-256(canonical mic@3 bytes)` — the full-fidelity binary `IRModule` —
  after a collision audit found `mic@1` text can drop function-body
  semantics (two semantically-different programs could share a `mic@1`-text
  hash); this supersedes the original GAP-1 `mic@1`-text rule. Implementations
  claiming evidence-chain emission MUST honour the `mic@3` anchor.
- **RFC 0021 canonical IR unification — steps 1–3 shipped (post-tag).**
  Resolves the two-IR divergence. Step 1: `mic@3` binary `IRModule` codec
  (`mind/src/ir/compact/v3/`, magic `MIC3`, additive). Step 2: evidence MAP
  epilogue on `mic@3` via the `0x4D` sentinel. Step 3: `mindc --emit-mic3`
  / `--emit-evidence` CLI flags. Steps 4–6 (`mindc verify`, `mic@2.x` →
  `mind-model@2` demotion, oracle + CI gate) remain in flight. The earlier
  `mic@1e` proposal was superseded by `mic@3` once `mic@2/2.1` shipped.
- **mindc v0.7.1 — high-level execution surface now EXECUTES on the shipped
  compiler; `std-surface` promoted to the shipped default.** Ten desugaring
  "bricks" lower the high-level surface onto the existing low-level pipeline,
  each keystone-verified 7/7 across substrates: integer/literal match,
  enum-discriminant match, `Option`/payload match, string literals, struct
  field-write, nested-struct + borrow field access, method-as-field accessors
  (`s.len()`), and method-with-args UFCS (`v.push(x)` → `vec_push(v, x)`, with
  unresolved methods failing loud). The reference implementation's Cargo
  feature set now defaults to `["std-surface"]`, so the high-level surface
  runs on every shipped binary; cross-substrate Q16.16 byte-identity is
  preserved across the flip (keystone 7/7). Unpromoted constructs (by-value
  tuple/aggregate returns, `region { }` interiors) are re-gated behind
  `std-surface-experimental` and fail loud by default — never a silent
  miscompile. Generics have no syntax yet (parser-rejected).
  `--no-default-features` restores the low-level-only subset, byte-identical
  to the pre-flip default build. Reflected in `STATUS.md` and the
  Compile-speed guarantee note in `spec/v1.0/stdlib.md`.

### Spec changes in this 1.4.0 cut

- **`spec/v1.0/ir-stability.md`** — Format-detection table covering `mic@1` /
  `mic@2` / `mic@2.1` / `mic@3`; new "Evidence-chain attestation" section
  documenting the MAP keys, both carriers, and the GAP-1 anchor rule (the
  rule was re-anchored 2026-05-31 to `SHA-256(canonical mic@3 bytes)`,
  superseding the original `mic@1`-text form).
- **`spec/mic/mic2.1-spec.md`** — note that `mic@3` was later allocated to
  RFC 0021's binary `IRModule` form; References section gains the RFC 0021 +
  `mind/src/ir/compact/v3/` pointers.
- **`design/rfcs/0001-mindir-compact.md`** — accepted RFC body unchanged;
  adds a "Subsequent RFCs (post-acceptance evolution)" forward-reference to
  RFC 0014 / RFC 0016 / RFC 0021.
- **`STATUS.md`** — Last-Updated 2026-05-28; IR-Stability row gains the
  mindc-0.7.x paragraph; 9 new toolchain-features rows.

### Notes

- The mind implementation-side docs (`mind/docs/ir-stability.md`,
  `mind/docs/versioning.md`) and the public site (`mindlang.dev/docs/mic`,
  `/docs/stability`, `/docs/ir`, `/roadmap`, `/docs/mic/v2`, `/docs/mic/binary`)
  all rewrote the prior "`mic@1e` epilogue" framing to the actual shipped
  `mic@3` design (steps 1–3) + steps 4–6 in flight.
- The earlier `1.3.x` entries below remain authoritative for the mindc
  v0.4.x – v0.6.7 surface; v1.4.0 covers the v0.6.8 → v0.7.x window.

---

## [1.3.8] - 2026-05-19

### Milestone: mindc v0.6.7 — RFC 0006 mind-blas vector-load alignment hardening

`mind@e921ed6` + tag `v0.6.7`. Every `llvm.load … -> vector<…>` the std-surface lowering emits now carries an explicit `{alignment = 4 : i64}`: `emit_vec_dot_f32`, `emit_vec_dot_q16`, `emit_vec_dot_l1_q16`, `emit_vec_dot_metric_f32` (f32 L1/L∞), and the `Instr::VecLoad` / `Instr::VecLoadI32` primitive lowerings (10 sites; the inc-3b matmul's 2 already had it). Without it MLIR defaults to the loaded type's natural 32-byte alignment, which the x86 backend lowers to `vmovaps` (alignment-required) — a GP-fault on any non-32-byte-aligned (interior) pointer, exactly the inc-3b matmul bug. These kernels are only ever called on allocation-base (over-aligned) pointers today so they did not fault, but the task #230 mind-nerve native-encode rewire will pass interior catalog-row pointers to `dot_q16_v` and would have hit the identical fault — this is pre-emptive hardening that de-risks #230.

### Notes

- **Contract-neutral**: an alignment attribute changes the emitted machine move (`vmovaps`→`vmovups`) but never the loaded bytes. Re-verified, not assumed: the cross-arch bit-identity gate **#57 still holds exactly** for `dot_q16_v` and `dot_l1_q16_v` (`blas_vec_q16_smoke` byte-identity tests pass unchanged, 6/6), and the `dot_f32_v` below-one-lane byte-identity + 1e-4 contracts are intact (`blas_vec_smoke` 3/3).
- **Bench-gate 0.0%**: default-feature release `mindc` byte-identical base-vs-change; bootstrap fixed-point IR byte-identical (`next_id = 206`). All changes `#[cfg(feature = "std-surface")]`-gated. `cargo fmt --check` clean; only the pre-existing `src/project/mod.rs:303` clippy advisory.

### Changed

- **`STATUS.md`** — compiler tracking bumped to v0.6.7; alignment hardening noted on the reference-implementation entry.

---

## [1.3.7] - 2026-05-19

### Milestone: mindc v0.6.6 — RFC 0006 Track B increment 3b; native vectorised `matmul_rmajor_f32_v`

`mind@2dd896d` + tag `v0.6.6`. Track B increment 3b lands the **vectorised row-major f32 matmul** `matmul_rmajor_f32_v`: the compiler emits an outer `scf.for` over the output rows (no `iter_args` — it stores directly to `y[r]`), each row inlining the proven increment-1 `dot_f32` reduction (8-lane `vector.fma` accumulate + `vector.reduction <add>` + scalar tail), and returns `0 : i64` exactly like the Track A C oracle `__mind_blas_matmul_rmajor_f32`. Every output row equals `dot_f32(W + r·cols, x, cols)` — the identical per-row reduction the Track A oracle performs — so it holds the **same documented 1e-4 relative f64-oracle contract** as `dot_f32_v` (f32 reduction re-association is not bit-exact; the established f32 contract, distinct from the bit-exact Q16.16 paths). Verified within 1e-4 at `(1,1) (1,8) (2,8) (3,8) (1,9) (1,17) (2,17) (5,17) (33,1025) (128,384)`.

### Notes

- **Root-cause record (an earlier mis-diagnosis corrected).** A first cut SIGSEGV'd for *rows ≥ 2 with a non-empty scalar tail* (`(2,17)` crashed; `(1,17)` passed). This was **not** a triple-nested-`scf.for` lowering defect — that nested sibling-`iter_args` pattern is valid MLIR and lowers correctly under the pinned LLVM (independently confirmed by a research audit). The actual cause: `llvm.load` of `vector<8xf32>` with no alignment attribute defaults to the type's natural 32-byte alignment, which LLVM's x86 backend lowers to `vmovaps` (alignment-required). Row-base pointers `W + r·cols·4` are only 4-byte (f32) aligned — row 0 is malloc-base-over-aligned (works), but row ≥ 1 with `cols` not a multiple of 8 is mis-aligned → general-protection fault. Fix: emit `{alignment = 4 : i64}` on the vector `llvm.load`s → `vmovups` (unaligned), correct for every row.
- **Bench-gate 0.0%**: the default-feature `mindc` **release** binary is byte-identical base-vs-increment-3b (verified, reproducible release build); the criterion compiler bench measures that identical binary so its µs figures are unchanged (1.8–17.1 µs frontend band; any per-run delta is criterion sampling noise, not code). Bootstrap fixed-point IR byte-identical (`next_id = 206`). All increment-3b code is `#[cfg(feature = "std-surface")]`-gated.
- `blas_vec_q16_smoke` 6/6 including the new `vec_matmul_rmajor_f32_within_1e4_rel_of_f64_oracle`; `cargo fmt --check` clean; the single pre-existing `src/project/mod.rs:303` clippy advisory is unrelated and predates this work; CI remains green as for v0.6.4/v0.6.5.
- **Deferred to a later increment** (RFC 0006 §9.3c): `@target(...)` per-call substrate annotation; cross-module `use std.blas` inlining; defensive `{alignment = 4}` on the other `dot_*_v` kernels (not a regression in current use — they are only ever called on allocation-base/over-aligned pointers).

### Changed

- **`STATUS.md`** — compiler tracking bumped to v0.6.6; matmul `matmul_rmajor_f32_v` added to the reference-implementation entry.

---

## [1.3.6] - 2026-05-19

### Milestone: mindc v0.6.5 — RFC 0006 Track B increment 3a; cross-arch bit-identity gate #57 closed for the vector L1 too

`mind@38611f2` + tag `v0.6.5`, CI success. Track B increment 3a lands the **Q16.16 L1 vector path** `dot_l1_q16_v` — the compiler emits a native MLIR `vector<8xi64>` widen → signed-subtract → arith-only absolute value (`maxsi(d, 0 - d)`, mirroring the Track A C oracle's `if (d<0) d=-d`) → i64-lane accumulate → associative `vector.reduction <add>` → scalar tail → `trunci`/`extsi` pack. No new IR variants (the emitter writes MLIR text directly, exactly as `dot_q16_v` does), so the additive-only envelope holds; no C shim, no clang, no `-fPIC`.

It is **byte-identical to the Track A scalar oracle `__mind_blas_dot_l1_q16`** at every RFC length {0,1,2,7,8,9,15,16,17,31,32,33,1024,4096,65537} — exact, not a tolerance (integer add is associative; per-element `|sext64(a) - sext64(b)|` is exact). This **closes the task #57 cross-arch bit-identity obligation for the full thesis-pure vector-path metric set**: both the vector dot (`dot_q16_v`, inc 2) and the vector L1 (`dot_l1_q16_v`, inc 3a) now hold the gate (single-x86-host scope, as Track A §5.2; the full Linux-x86 ↔ macOS-ARM ↔ CUDA-x86 ↔ photonic hardware contract remains the outstanding #57 portion).

### Notes

- **Bootstrap fixed-point unchanged**: `next_id = 206`, bootstrap IR byte-identical base-vs-inc-3a (the bootstrap source uses no vector ops). Same clean no-shift discipline as v0.6.2–v0.6.4.
- **Bench-gate 0.0%**: the default-feature `mindc` **release** binary is byte-identical base-vs-increment-3a (verified with a reproducible release build; the debug binary is rustc-metadata-nondeterministic and is not a valid byte-identity oracle). All increment-3a code is `#[cfg(feature = "std-surface")]`-gated and absent from the binary the `compiler` bench measures.
- 519 std-surface tests; `blas_vec_q16_smoke` 5/5 including the new `vec_dot_l1_q16_byte_identical_to_scalar_oracle_all_lengths`; `cargo fmt --check` clean. (One pre-existing clippy advisory at `src/project/mod.rs:303` predates this increment and is unrelated; CI remains green, as it was for v0.6.4.)
- **Increment 3b honestly deferred** (RFC 0006 §9.3b): `@target("simd-x86"|"simd-arm"|…)` per-call substrate annotation (needs real MLIR target-attr plumbing parser→AST→type-checker→`Instr::Call`→lowering), a vectorised `matmul_rmajor_f32` inner loop, and cross-module `use std.blas` vector inlining.

### Changed

- **`STATUS.md`** — compiler tracking bumped to v0.6.5; #57 marked closed for both the vector dot and the vector L1.

---

## [1.3.5] - 2026-05-19

### Milestone: RFC 0007 (Mindcraft) sequencing gate CLEARED — documentation/sequencing only, no compiler change

`mind@a29726c` flips RFC 0007 (the pure-MIND `mindc fmt`/`lint`/`check` developer tooling — the fmt/lint/check tools themselves written in MIND; not toolchain-wide self-hosting, which remains roadmap) from gated to **build-may-begin**. The gate was native-encoder end-to-end measurement plus numerical correctness, and the criterion benchmark publication. Both are satisfied: the native pure-MIND encoder runs end-to-end and validates against the reference encoder at cosine 0.999996 / top-5 route overlap 0.9975 (≥0.92 gate, n=160) with the cross-arch Q16.16 bit-identity invariant preserved, and the criterion benchmark publication is complete.

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
- GPU backend scaffolding landed (previously MockGpuBackend)

> **Historical / roadmap note (re-anchored 2026-06):** the "production-grade
> GPU backends" framing in this 2025-12 entry was aspirational. The shipped
> open-core reality: `mind-runtime` ships the **CPU backend**; GPU and
> accelerator backends are available under the **commercial license**
> (open-core). **Bit-identical determinism across CPU, GPU, and accelerators
> is the roadmap, not a shipped guarantee.** See [`STATUS.md`](../STATUS.md)
> and the root [`README.md`](../README.md) for the current version-pinned
> status.

---

## [1.0.0] - 2025-12-19

### Milestone: Core v1 Specification Frozen

The Core v1 **specification** is frozen and stable. "Complete" here refers to
the specification text — the 14 normative chapters and formal grammar — not to
end-to-end implementation coverage. Reference-implementation maturity is tracked
separately and version-pinned in [`STATUS.md`](../STATUS.md) and the root
[`README.md`](../README.md) (reference compiler `v0.7.1`; `mind-runtime` CPU
backend shipped, GPU + accelerators under commercial license).

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
