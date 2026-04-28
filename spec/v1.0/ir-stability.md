# IR Stability — `mic@1` Textual Form

> **Status:** stable (mind-spec v1.0, ratified by mindc 0.2.5).
> **Surface:** `mic@1` text format + `IRModule` data shape.
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

`mic@1` is the legacy text format with explicit node IDs. `mic@2` and
`MIC-B` (binary) are alternative compact forms standardised separately
in `spec/v1.0/mic/` — they produce a different `Graph` data shape and
fall under their own stability surface.

The header `mic@1\n` MUST appear as the first non-whitespace bytes of any
`mic@1` document.

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
