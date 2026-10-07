# The Determinism Contract

> Status legend — **✅ shipped** (implemented and gated in CI) · **🔄 strict-path
> bit-identical, cross-ISA verified** (scalar IEEE-754 `f64`/`f32` on the strict
> deterministic path — run-to-run bit-identical and verified byte-identical on
> x86_64 (AVX2) + ARM64 (NEON) real hardware) · **📋 specified**
> (the rule is fixed by this contract; enforcement is in progress).

## Definition

MIND is **deterministic**: the same source code, the same inputs, the same
compiler/runtime version, and the same target settings produce the same output —
every time, on every conforming implementation.

This is not a claim that every mathematical question has one truth. It is a claim
that the **language defines one exact behaviour** for every operation and never
leaves the result to accident — to undefined behaviour, backend quirks, hidden
global state, race conditions, or the order in which a parallel runtime happens to
execute.

Every questionable operation falls into exactly one of three buckets:

| Bucket | Meaning |
|--------|---------|
| **define** | The spec picks one rule. The operation always produces that result. |
| **reject** | The operation is a compile error or a defined domain error. |
| **mark non-deterministic** | The operation is explicitly opted into a `fast` / unordered mode that the spec labels non-deterministic. |

The forbidden fourth bucket — *"sometimes 1, sometimes 0, sometimes NaN, depending
on backend / GPU / optimization level"* — does not exist in MIND.

### Determinism is verifiable, not promised

Determinism in MIND is **checkable**. Each compiled artifact embeds an evidence
chain whose `trace_hash = SHA-256` of the canonical `mic@3` bytes. Identical
(source, inputs, version, target) ⇒ identical `trace_hash`. `mindc verify ./artifact`
confirms it without trusting the build host. No other toolchain ships a verifiable
determinism contract. ✅

The verifier also re-derives the artifact's **floating-point contract mode**
(`strict` / `relaxed`) directly from the hashed body — so `mindc verify
--require-strict-fp ./artifact` fails closed unless the artifact was lowered on
the strict path (no FMA-contraction, no `f32` reduction reassociation). Because
the mode is a pure function of bytes the `trace_hash` already attests, this is
build-host-independent and adds no wire-format surface. ✅

---

## 1. Integer semantics — ✅ shipped (v0.10.0)

Integer arithmetic is fully deterministic and byte-identical across substrates.

| Case | Rule |
|------|------|
| `x / 0` | `= 0` (defined; no trap, no UB) |
| `x % 0` | `= 0` (defined) |
| `INT_MIN / -1` | `= INT_MIN` (defined; no overflow trap) |
| Integer overflow | wraps two's-complement (defined; identical on x86 and ARM) |
| Declared narrow width (`i8`, `u8`, `i16`, `u16`, `i32`, `u32`) | a value wraps at the declared width where it is materialised (binding, assignment, argument, return, struct field): two's-complement for signed widths, modulo 2^N for unsigned widths. An 8- or 16-bit arithmetic intermediate (`+ - * / %` and shifts) is re-wrapped to the widest 8- or 16-bit operand width; an operand that is a wider variable, or a cast to a wider type, leaves it unwrapped. ✅ on the MLIR build path for the 8- and 16-bit widths since v0.10.2 (not v0.10.0); the wider-operand rule is on compiler main since `732edb0f` (pending release), and v0.10.2 re-wrapped such an intermediate to the narrow width (`i64` 1000 + `u8` 1 gave 233). The native backend is not covered by this evidence. |
| Integer type the implementation does not compute at its written width (e.g. `i128`, `u128`, `i256`) | never computed at a narrower width: it is either computed at its written width as a documented extension, or refused at check time. 📋 The reference compiler refuses `iN`/`uN` with N > 64 at check time on compiler main (`4fd65cfb`, pending release); v0.10.2 accepted them outside extern function signatures, and a `let` binding of one was computed in 64 bits. Widths of 64 or less that it does not recognise (e.g. `i24`) are not covered by this check (see [types.md](spec/v1.0/types.md#type-formation)). |
| Oversized shift (`count ≥ bit-width`) | given a defined result (never UB) |
| Condition truthiness (`if c`) | tests `c != 0` — the whole value, not the low bit |

The narrow-integer call ABI (`i32`/`u32` across call boundaries) and struct
narrow-field ABI are sound. Gated by the keystone and `cross_substrate` suites.

The declared-width row describes compiled output of the default (`std-surface`)
build on the MLIR build path. On compiler main the `mindc test` evaluator applies the same widths for the
covered cases (`97c0d273`, `74004786`, `2575c1e9`, `a7f9520a`; pending release).
The gaps, where agreement with compiled output is not claimed, are listed in
[`spec/v1.0/conformance.md`](spec/v1.0/conformance.md).

---

## 2. Floating-point semantics

MIND follows **IEEE 754** and pins every edge case. Scalar `f64`/`f32` follow the
IEEE rules below and now run on the **strict deterministic path** — plain
`arith.addf` / `arith.mulf`, no FMA-contraction, no fast-math, no reassociation,
fixed source order — so scalar `+`, `-`, `*`, `/`, `sqrt` are bit-exact,
**run-to-run bit-identical**, and **verified byte-identical across the proven CPU
substrates (x86_64 + ARM64) on real hardware** today (see §2.1). The **Q16.16
fixed-point** tier is fully deterministic and byte-identical across those same
substrates (x86 == ARM) today.

| Case | Rule | Status |
|------|------|--------|
| Scalar `+ − × ÷ √` (`f64`/`f32`) | bit-exact IEEE-754 on the strict path; no FMA-contraction, no reassociation, fixed source order | 🔄 |
| `1.0 / 0.0` | `+Inf` (IEEE) | 🔄 |
| `-1.0 / 0.0` | `-Inf` (IEEE) | 🔄 |
| `0.0 / 0.0` | `NaN` (IEEE) | 🔄 |
| `sqrt(-1.0)` | `NaN` (IEEE); `strict_domain` → defined domain error | 🔄 (`strict_domain` error 📋) |
| `pow(0.0, 0.0)` | `1.0` — IEEE `pow`: `x^0 == 1` for **all** `x` (including `0` and `NaN`) | 📋 (transcendental) |
| `powr(0.0, 0.0)` | `NaN` — IEEE `powr` (= `exp(0·log 0)`), the strict real-power form | 📋 (transcendental) |
| `limit_form(0^0)` | indeterminate — symbolic/calculus context, not a number | 📋 |
| Float comparisons (NaN operand, signed zero) | `<`, `<=`, `>`, `>=`, `==` are `false` and `!=` is `true`; `-0.0 == +0.0` is `true` | 📋 compiled MLIR path on compiler main since `2597ee9c` (the v0.10.2 release lowered `!=` as ordered, so `NaN != NaN` was `false` there); native x86-64 `f64` since `ccbb00b8` (pending release; the native backend refuses `f32`); the `mindc test` evaluator has an open `f64` comparison defect |
| `min` / `max` / `sort` with NaN | use a defined total order (NaN sorts last) so results are deterministic | 📋 |
| Rounding | round-to-nearest-even (IEEE default), fixed | 🔄 |
| Q16.16 fixed-point | fully deterministic, byte-identical x86 == ARM | ✅ |

### `0^0` — worked example

`0^0` is the canonical "vague" case. MIND removes the vagueness by choosing the
function, not the mood:

```mind
pow(0, 0)        // 1     — integer / exact arithmetic, deterministic
pow(0.0, 0.0)    // 1.0   — IEEE pow, deterministic (x^0 == 1 for all x)
powr(0.0, 0.0)   // NaN   — IEEE powr (real power), deterministic
limit_form(0^0)  //        indeterminate — symbolic/calculus, not a runtime number
```

`pow(0,0) = 1` matches the empty-product convention and every mainstream language,
and keeps polynomial / tensor `x^0` well-behaved. `powr` is the honestly-NaN real
power. Both are deterministic — you pick which one. Mathematically honest **and**
never an accident.

### 2.1 Scalar IEEE-754 strict path — run-to-run and cross-ISA bit-identical 🔄

Scalar `f64` and `f32` arithmetic (`+`, `-`, `*`, `/`, `sqrt`) now compiles and
runs on the **strict deterministic path**: the backend emits plain `arith.addf` /
`arith.mulf` / `arith.divf` / `arith.sqrt` with **no FMA-contraction, no
fast-math, no reassociation, and fixed source order**. Because IEEE-754 fixes the
correctly-rounded result of each of these scalar operations, the output is
bit-exact and **identical run-to-run**. This is verified end-to-end: a
loop-carried `f64` integrator (an explicit-Euler Lorenz solver) compiles, runs,
and reproduces a reference computation bit-for-bit, and reruns produce the exact
same bytes.

Cross-substrate bit-identity is **verified on hardware for the CPU↔GPU pair**:
the same `f64` Lorenz solver produces results identical to the last bit on an
x86 CPU and on an NVIDIA GPU (CUDA, `sm_86`), because the same no-FMA-contraction
contract (`-ffp-contract=off` on the CPU, `--fmad=false` on the GPU) forbids the
fused multiply-add both would otherwise apply — with contraction enabled the
chaotic trajectory diverges, worse the longer it runs. Because scalar
`+ − × ÷ √` are correctly-rounded IEEE-754 operations, the same holds in
principle on any conforming FPU; further substrate coverage is added as it is
verified on hardware. This scalar strict path is now **verified byte-identical
across x86_64 (AVX2) and ARM64 (NEON) CPUs on real hardware**: the `cross_substrate`
gate's canary workloads — including the scalar-`f64` arithmetic chain
(`scalar-float-f64`; the gate's Lorenz workload, `lorenz-q16`, is integer Q16.16, not
`f64`) — produce byte-identical outputs on a `ubuntu-24.04`-class ARM64
runner (LLVM 20.1.8, `MIND_BENCH_REQUIRE=1`) matching the pinned x86-verified
references. The honest claim is therefore *scalar IEEE-754 `float64`/`f32` on the
strict path, verified byte-identical across x86_64 (AVX2) and ARM64 (NEON)
CPUs on real hardware.* The claim is computational **output** identity for the
covered workloads on those two tested substrates — at compiler `7831998b`, 35
workload manifests in the `cross_substrate` gate, with `scalar-float-f64`,
`dot-f32-v-4093` and `matmul-f32-v-64x64` carrying committed matching AVX2 and
NEON output hashes, and ten scalar-`f64` quantitative-finance workloads described
below — not native-binary identity, and not a universal floating-point, CPU or GPU
claim. The no-FMA-contraction contract is designed
to extend to GPU substrates, but GPU coverage is a roadmap proof obligation
until it is verified on hardware. (The integer / Q16.16 path already **is**
cross-substrate byte-identical on the proven x86 + ARM set; see §1 and the
`cross_substrate` gate.)

The **f32 vector BLAS reductions** — the `dot` / `L1` / `matmul` `*_v` kernels —
are now on the strict tier: their per-lane FMA is unfused to separate
`mulf`+`addf` and the horizontal sum is a pinned fixed-order fold, so they emit
no `vector.fma` / `vector.reduction <add>` and are bit-exact (run-to-run
bit-identical, `objdump`-verified free of fused FMA on x86; the `dot-f32-v-4093`
and `matmul-f32-v-64x64` workloads carry committed matching AVX2 and NEON output
hashes in the `cross_substrate` gate).

Ten scalar-`f64` quantitative-finance workloads (option pricing, implied
volatility, binomial lattices, Monte Carlo, bond curve and portfolio risk programs
under `examples/quant`) were added to the gate after v0.10.2 (`545ed80c`,
`82e34947`; pending release). Each hashes one exported MIND kernel over eight fixed
inputs. The kernels' floating-point arithmetic is `+ - * /` and `sqrt` in fixed
source order (some kernels also use comparisons, `max`, integer loop counts, and in
the Monte Carlo kernel an integer LCG with integer-to-`f64` conversion), with `exp`,
`log` and `erfc` re-derived in MIND, and each has committed AVX2 and NEON
hashes that are equal; the maintainers record the NEON values as verified on
aarch64 hardware. The identity test binary has 26 base tests plus ten quant
reproducibility gates and two quant consistency tests, one of which runs on x86_64
only. This is evidence for those programs only, on the compiled MLIR path only; it
is not evidence for compiler-provided transcendentals.

What remains on the roadmap — deliberately **not** yet deterministic — is the
frontier of §4/§5: broader `f32`/`f64` **vector reductions** (tensor `sum`,
`f64` — still a documented relative tolerance, pending canonical reduction trees
/ superaccumulators), **correctly-rounded transcendentals** (`sin`/`exp`/…
pending a vendored correctly-rounded libm rather than the host libm), and **GPU
float** (pending fixed-tree / Ozaki-scheme reductions; Metal/WebGPU have no
hardware `f64`).

---

## 3. Backend must not change meaning

Two execution tiers; the contract is **bit-identity**, never "within tolerance"
(tolerance-equal is a correctness-testing notion, not a determinism guarantee).

- **Strict tier (default).** Integer and Q16.16 results are byte-identical across
  substrates (x86 == ARM), gated by `cross_substrate` (see §2.1 for the workload set). ✅ Scalar `f64`/`f32`
  arithmetic (`+ − × ÷ √`) runs on the strict path bit-exact and run-to-run
  bit-identical, and is verified byte-identical across substrates (x86_64 + ARM64)
  on real hardware by the same `cross_substrate` gate. 🔄 For `f32`/`f64`
  **vector reductions**, the strict tier will fix the reduction order (canonical
  reduction tree) and pin one correctly-rounded transcendental implementation to
  yield bit-identical results across substrates — this is roadmap. 📋
- **Fast tier (opt-in).** Explicitly labelled non-deterministic; results may differ
  by substrate. You opt **into** it — you never get it by accident.

GPU and accelerator execution (CUDA, Metal, ROCm, WebGPU) ships in the commercial
`mind-runtime`; bit-identical determinism across those substrates is on the roadmap.
The open-source `mindc` in this repo emits for the CPU.

---

## 4. Parallel execution must not randomise results

For floating-point, `(a + b) + c != a + (b + c)`. A parallel runtime that reorders
a reduction can change the result. MIND's rule:

- **Strict is the default.** Reductions use a defined reduction order (or a stable
  kernel) and are reproducible regardless of thread/lane count.
- **Fast is opt-in and labelled non-deterministic.**

```mind
sum(x)                 // strict: defined reduction order, reproducible
sum(x, mode = "fast")  // explicitly non-deterministic
```

Fixed-reduction-order kernels are the active work (Phase 13.6). 📋

---

## 5. Compiler optimizations cannot change observable behaviour

MIND separates two math modes:

- **`strict_math` (default).** The compiler may not rewrite floating-point in ways
  that change the observable result: **no** `x * 0 → 0` (because `NaN * 0 = NaN`,
  `Inf * 0 = NaN`), **no** reassociation, **no** FMA-contraction. NaN, Inf, and
  rounding are preserved exactly.
- **`fast_math` (opt-in).** Permits those rewrites; the spec labels the result
  non-deterministic.

The native-ELF backend emits an image that is a **pure function of the source image it
is given** (the user sources plus the fixed seed standard library) — there
is no external toolchain whose `-ffast-math` can leak in. ✅ The `strict_math` /
`fast_math` surface is being finalised. 📋

A call to a MIND function runs that function's body. An implementation MUST NOT
replace a user-defined function, or a call to it, with a host library routine or a
host-folded constant because its name matches a C library routine (`pow`, `sin`,
`exp`, `log`, `cos`, ...).

Reference status (pending release): on the MLIR build path the reference compiler
marks every function definition `nobuiltin` before LLVM sees it (`9c231f50`), so
LLVM does not treat a MIND function as the library routine its name matches.
`--emit-mlir` text is unchanged, the feature-gated `mlir-exec`, `mlir-jit` and
`mlir-gpu` execution modes of the `mind` binary do not apply it, and the native ELF
path has no external toolchain to apply such a rewrite. The evidence is one runtime test with three probe names
(`pow`, `sin`, `exp`), not an audit of every libm symbol. This does not make the
`std.math` transcendentals correctly rounded or identical across substrates; that
remains on the roadmap (§2.1). It does not change the published v0.10.2 artifact.

---

## 6. Randomness must be explicit

There is no implicit `rand()` reading hidden global state. Randomness is always
seeded and explicit:

```mind
let rng = Random(seed = 42)
let x   = rng.normal(shape = [1024])   // same seed ⇒ same tensor, every run
```

The generator is **counter-based** (Philox / Threefry), keyed by
`(seed, element_index)`. Because each element's draw is a stateless function of its
index, parallel generation is reproducible regardless of execution order, and the
result is identical across substrates. This is the basis of MIND's
reproducible-across-hardware `randn` (Phase 11 deterministic intrinsic). 📋

### Determinism is enforced; non-determinism never leaks untraced

MIND programs are **deterministic by default** — but as a systems language MIND
can compile *anything*, including a genuinely non-deterministic operation (an
unseeded PRNG draw `random` / `rand_uniform`, or a wall-clock / stdin read `now` /
`read_line`). Such a program is neither silently accepted nor silently rejected;
non-determinism is a **traced, attested opt-in** across three layers:

1. **Build gate.** Producing a runnable or attested artifact from a program that
   calls such a builtin is **rejected fail-loud**, naming the offender and pointing
   at the seeded `Random(seed = 42)` API — *unless* the build passes
   `--allow-nondeterministic`. Hidden non-determinism cannot reach a shipped
   artifact by accident.
2. **Honest attestation.** With that flag the program compiles, and its
   `evidence_chain.determinism` field — *derived from the IR* — declares
   `nondeterministic`. Every deterministic module (including seeded
   `randn(shape, seed)`) declares `deterministic`. The flag authorises the
   *build*, never the *label*.
3. **Verify re-derivation (tamper-proof).** The `determinism` field is a MAP-epilogue
   key, outside the `trace_hash` anchor, so on an unsigned artifact it would be
   forgeable. `mindc verify` **re-derives** the mode from the hashed body (exactly as
   it re-derives the floating-point contract mode), reports that authoritative
   value, and **fails closed** if the stored field disagrees — a forged
   `deterministic` label cannot pass. `mindc verify --require-deterministic` fails
   closed for a consumer that requires reproducibility.

The attestation can never lie, and non-determinism is always **opt-in and
labelled, never by accident**. ✅

---

## Summary

> MIND does not depend on undefined behaviour, backend quirks, hidden randomness,
> race conditions, or accidental execution order. Every questionable case is either
> precisely **defined**, explicitly **rejected**, or explicitly **marked
> non-deterministic** — and the result is **verifiable** through the artifact's
> `trace_hash`.
