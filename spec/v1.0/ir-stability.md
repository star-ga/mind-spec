# IR Stability — `mic@1` Textual Form

> **Status:** stable (mind-spec v1.0, ratified by mindc 0.2.5; extended with the
> pure-MIND `__mind_*` intrinsic ABI in mindc 0.4.2, RFC 0005; evidence-chain
> attestation in mindc 0.7.x, RFC 0016; binary IRModule + MAP epilogue in
> mindc 0.7.x, RFC 0021 steps 1–3).
> **Surface:** `mic@1` text format + `IRModule` data shape (the canonical
> data shape both `mic@2/2.1` compact and `mic@3` binary serialise).
> **Reference implementation:** `mind/src/ir/mod.rs` and `mind/src/ir/compact/`.

## Why this is normative

mindc 0.2.5 promotes the public IR layer to the **stable runtime contract**
between the surface compiler and downstream consumers. Before 0.2.5,
runtimes (notably `mind-runtime`) re-parsed embedded MIND source on every
invocation, which made the surface parser a runtime hot path across the
12+ planned backends (CPU, CUDA, Metal, ROCm, WebGPU, WebNN, ARM, TPU,
NPU, LPU, DPU, FPGA, Quantum). The IR layer breaks that coupling.

## Implementations MUST provide

Any implementation claiming mind-spec v1.0 conformance MUST:

1. Accept `mic@1` text input through a `load(bytes) -> IRModule` entry
   point semantically equivalent to `libmind::ir::load`.
2. Emit `mic@1` text output through a deterministic `save(module) -> String`
   entry point semantically equivalent to `libmind::ir::save`. The
   `save → load → save` round-trip MUST be a fixed point.
3. Honour the `IRModule.instrs` ordering as significant (no implicit
   reordering before verification).

## Format detection

`mic@1` is the canonical text format with explicit node IDs.  The compact
and binary forms are alternative serialisations standardised separately
under `spec/v1.0/mic/` and `spec/mic/`:

| Form     | Header bytes | Data shape       | Stability surface                                       |
|----------|--------------|------------------|---------------------------------------------------------|
| `mic@1`  | `mic@1\n`    | `IRModule`       | this document                                           |
| `mic@2`  | `mic@2\n`    | `Graph` (compat) | `spec/mic/mic2-spec.md`, deferred per RFC 0021          |
| `mic@2.1`| `mic@2.1\n`  | `Graph` + MAP    | `spec/mic/mic2.1-spec.md` (RFC 0014 — MAP carrier)      |
| `mic@3`  | `MIC3` magic | `IRModule` (binary) | `spec/mic/mic2.1-spec.md` §3 + RFC 0021 (steps 1–3 shipped, 4–6 in flight) |

Per RFC 0021, `mic@3` is the **canonical binary serialisation of the
`IRModule` data shape** that `mic@1` text serialises today; the two are
round-trip equivalent.  `mic@2.x` is preserved as a back-compat lane and
will be demoted to `mind-model@2` (a separate model-graph artifact, not
an IR contract) once RFC 0021 step 5 lands.

The header `mic@1\n` MUST appear as the first non-whitespace bytes of any
`mic@1` document.

## Evidence-chain attestation (mindc 0.7.x, RFC 0016 + RFC 0021 step 2)

An `IRModule` may carry an **evidence-chain attestation** — a Metadata-
Attachment-Pair (MAP) epilogue with the keys `evidence_chain.determinism`,
`evidence_chain.substrate`, `evidence_chain.toolchain`, `evidence_chain.trace_hash`,
and optionally `evidence_chain.parent`.  The MAP attaches to `mic@2.1`
compact IR via the MAP-carrier extension (RFC 0014) and to `mic@3` binary
IR via the trailing `0x4D` sentinel epilogue (RFC 0021 step 2).

The `trace_hash` is `trace_hash = SHA-256(canonical mic@3 bytes)` — the
**full-fidelity binary `IRModule`** (RFC 0016 GAP-1, mindc commit `db5cb76`;
re-anchored 2026-05-31 after a collision audit found `mic@1` text can drop
function-body semantics, two semantically-different programs could share a
`mic@1`-text hash — `mic@3` binary commits the full `IRModule`; this
supersedes the original GAP-1 `mic@1`-text rule).  This makes `mic@3` the
load-bearing anchor for the entire attestation surface.  Implementations
claiming evidence-chain emission MUST honour this `mic@3` anchor; hashing on
the `mic@1` textual form or the `mic@2.x` binary form is non-conformant.

## Bench-gate discipline

mindc enforces a **+2% mean regression cap** on the
`small_matmul / medium_mlp / large_network` pipeline benchmarks
relative to the frozen baseline at `.bench-baseline-2026-04-28-pratt.txt`.
Implementations are encouraged (but not required) to maintain equivalent
discipline; the rationale is that any drift in the surface compiler hot
path compounds across the runtime hot paths of all downstream backends.

## See also

- `mind/docs/ir-stability.md` — implementation-side contract.
- `spec/v1.0/versioning.md` — overall stability policy.
- `spec/v1.0/conformance.md` — test corpus.
- `spec/mic/mic2-spec.md`, `spec/mic/mic2.1-spec.md`, `spec/mic/micb-spec.md`
  — the alternative compact / binary serialisations.
- `mind/docs/rfcs/0016-…` — evidence-chain emission Phase A/B.
- `mind/docs/rfcs/0021-canonical-ir-unification.md` — the mic@3 design
  decision + mic@2.x → mind-model@2 demotion plan.
