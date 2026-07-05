<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# RFC-0022: Float-Determinism Enforcement via `fp.tier`

| Status | Accepted |
|--------|----------|
| Author | STARGA AI Engineering |
| Created | 2026-07-05 |
| Updated | 2026-07-05 |
| Target | mind-spec v1.0, mindc 0.7.x |
| Depends | RFC-0016 (evidence chain), RFC-0021 (`mic@3` canonical binary), RFC-0017 (`mindc verify`) |

## Summary

This RFC makes MIND's floating-point determinism contract **enforceable and
self-attesting** rather than merely promised. It introduces one normative
mechanism:

1. A per-operation **`fp.tier` IR attribute** (`strict` | `fast`) carried on
   every floating-point op inside the canonical `IRModule`, so an operation's
   determinism tier is part of the hashed IR — not build-host configuration.
2. A **verifier invariant** — `mind verify --require-strict-fp ./artifact` — that
   re-derives the artifact's floating-point contract mode **purely from the
   hashed `mic@3` body** and fails closed unless every FP op carries
   `fp.tier=strict`.

The load-bearing property is that determinism is **derived, not asserted**:
because `trace_hash = SHA-256(canonical mic@3 bytes)` (RFC-0016 GAP-1, re-anchored
2026-05-31; see [`ir-stability.md`](../../spec/v1.0/ir-stability.md) §"Evidence-chain
attestation") and `fp.tier` lives inside those bytes, the strict-FP guarantee is a
pure function of the same bytes the `trace_hash` already commits to. No new
wire-format surface, no side channel, no trust in the build host.

## Motivation

[`determinism.md`](../../determinism.md) §"Determinism is verifiable, not promised"
already states that the verifier re-derives an artifact's floating-point contract
mode (`strict` / `relaxed`) from the hashed body. That guarantee was documented but
not grounded in a normative IR representation: nothing in the spec said **where in
the IR** the tier lives, or **how** a conforming verifier recovers it without
trusting the compiler that produced the artifact.

Absent a hashed, per-op representation, "strict FP" is a build flag — a promise the
consumer cannot check. A consumer receiving an artifact cannot distinguish an
image lowered with `-ffp-contract=off` on the strict path from one that silently
contracted a multiply-add, unless the tier is committed *inside* the bytes the
`trace_hash` covers. This RFC closes that gap by pinning the tier to the IR and the
check to the hash.

This matters most for the strict scalar path that is already shipping:
[`determinism.md`](../../determinism.md) §2.1 records scalar `f64` (with the integer
and Q16.16 tiers) as bit-identical across x86 and ARM CPUs, **verified 2026-07-05**;
scalar `f32` is run-to-run bit-identical on the strict path with cross-ISA
confirmation still in progress. `fp.tier` is the representation that lets a
downstream consumer *check* that an artifact was in fact lowered on that strict
path.

## Specification

### 1. The `fp.tier` attribute

Every floating-point operation in a canonical `IRModule` MUST carry an `fp.tier`
attribute with exactly one value:

| Value | Meaning |
|-------|---------|
| `strict` | The op is on the strict deterministic path: plain `arith.addf`/`arith.mulf`/`arith.divf`/`arith.sqrt`, **no** FMA-contraction, **no** fast-math, **no** reassociation, fixed source order (per [`determinism.md`](../../determinism.md) §2, §5). |
| `fast` | The op is explicitly opted into the fast tier the contract labels **non-deterministic** (per [`determinism.md`](../../determinism.md) §3, §4). |

Rules:

- **Total coverage.** A conforming lowering MUST assign an `fp.tier` to every FP op;
  there is no unmarked/default-implicit tier. An FP op without `fp.tier` is a
  verification error.
- **Canonical serialisation.** `fp.tier` is part of the `IRModule` data shape and
  therefore serialises into `mic@1` text, `mic@2.x` compact, and — normatively for
  attestation — the canonical `mic@3` binary form
  ([`ir-stability.md`](../../spec/v1.0/ir-stability.md)). It is thus committed by
  `trace_hash`.
- **No host escape hatch.** The tier is a property of the IR, not of a compiler
  command-line flag. Two artifacts with the same `trace_hash` have identical
  `fp.tier` assignments by construction.

### 2. The verifier invariant

`mind verify --require-strict-fp ./artifact` (RFC-0017 verify surface) MUST:

1. Recompute `trace_hash = SHA-256(canonical mic@3 bytes)` and confirm it matches
   the embedded evidence-chain `trace_hash`
   ([`conformance.md`](../../spec/v1.0/conformance.md) §"Evidence-chain conformance").
2. Re-derive the artifact's floating-point contract mode by scanning the `fp.tier`
   attribute of every FP op **in the hashed body**.
3. **Fail closed** — exit non-zero — unless every FP op carries `fp.tier=strict`.

Because step 2 reads only bytes that step 1 has already hash-verified, the check is
**self-attesting**: it does not trust the build host, the compiler version string,
or any out-of-band claim. A tampered or fast-tier artifact cannot pass, and a
strict-tier artifact cannot be forged without producing a different `trace_hash`.

This invariant adds **no wire-format surface**: `fp.tier` rides inside the existing
`IRModule`, and the check consumes the existing `mic@3` bytes and existing
`trace_hash`. It is a pure reader of already-committed state.

### 3. Determinism is derived

The contract's central claim — *identical (source, inputs, version, target) ⇒
identical bytes* — becomes a **derivation** rather than a promise for the strict FP
tier:

```
fp.tier ⊆ canonical mic@3 bytes
trace_hash = SHA-256(canonical mic@3 bytes)
∴  (all fp.tier = strict)  is a pure function of trace_hash-committed state
∴  --require-strict-fp is decidable from the artifact alone
```

A verifier therefore *proves* the strict-FP property of an artifact offline, with
no access to the build environment.

## Scope and non-goals

- **In scope:** the open-source `mindc` CPU strict path — scalar `f64`/`f32`
  `+ − × ÷ √` (per [`determinism.md`](../../determinism.md) §2.1) and the integer /
  Q16.16 tiers already gated by `cross_substrate`.
- **Out of scope (roadmap):** `f32`/`f64` **vector reductions** and
  **correctly-rounded transcendentals** remain frontier work and are **not** on the
  strict tier; a `fast`-marked reduction is honestly non-deterministic under this
  RFC, not silently promoted. GPU / accelerator float determinism is provided by
  the commercial `mind-runtime` and is outside the open-source `mindc` verifier
  surface this RFC governs (see [`determinism.md`](../../determinism.md) §3).
- **No signing dependency.** This RFC governs the emitted, hash-anchored surface
  only. Ed25519 signing of the evidence chain (RFC-0016 Phase C / RFC-0017 signature
  mode) is a separate, later milestone; `--require-strict-fp` does **not** imply a
  signed chain.

## References

- [`determinism.md`](../../determinism.md) — the Determinism Contract (§2.1 strict
  scalar path, verified 2026-07-05; §"Determinism is verifiable, not promised").
- [`spec/v1.0/ir-stability.md`](../../spec/v1.0/ir-stability.md) — `IRModule`
  canon, `mic@3` binary form, and the `trace_hash = SHA-256(canonical mic@3 bytes)`
  anchor.
- [`spec/v1.0/conformance.md`](../../spec/v1.0/conformance.md) — evidence-chain
  conformance and the `mic@3` hashing rule.
- RFC-0016 — evidence-chain emission and the GAP-1 `trace_hash` anchor.
- RFC-0021 — `mic@3` canonical binary serialisation of the `IRModule` data shape.
- RFC-0017 — `mindc verify` surface (`--require-strict-fp` mode).
