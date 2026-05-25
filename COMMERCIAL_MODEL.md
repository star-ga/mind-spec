# STARGA Commercial-Open Model

## Principle

Contract is OPEN (auditable, bit-identity verifiable). Optimized implementations of
commodity substrates are OPEN — the wedge claim must be publicly reproducible by any
third party. Protected layer captures ONLY the unbounded-future-IP layer that
competitors structurally cannot replicate: agent OS internals, non-commodity-substrate
optimization, and the governed runtime kernel.

Substrate-business shape parallels:
- LLVM — open IR + open base lowering; commercial target-specific passes protected.
- Rust — open language + std; paid per-customer toolchain tuning and support.
- Anthropic — open API patterns and prompt formats; protected model weights.

STARGA's wedge is bit-identity-first cross-substrate. That claim has no commercial
weight if it cannot be independently verified. Therefore the commodity-substrate
implementations that prove the wedge are always open.

---

## Open Layer

Every repo listed here is public and remains open indefinitely.

| Repo | Role | Why open | Canonical location |
|---|---|---|---|
| `mind-spec` | Language specification and RFC track | Spec must be auditable; wedge claim starts here | `star-ga/mind-spec` |
| `mind` (compiler + std) | `mindc` compiler; `mind/std/` stdlib including `mind/std/blas.mind`, AVX2 register-tiled Q16.16 GEMM, NEON dots, reference CUDA | Commodity-substrate impls prove the wedge; reproducibility is the proof | `star-ga/mind` |
| `mind-nerve` | Python binding + MCP wire layer | Commodity integration surface; drives adoption | `star-ga/mind-nerve` |
| `rfn-mind` | Recursive-function-network runtime | Wedge property: Q16.16 bit-identity gate across microarch | `star-ga/rfn-mind` |
| `mind-inference` | MIND-native LLM inference pipeline | Wedge property: deterministic inference on open substrates | `star-ga/mind-inference` |
| `mind-mem` Python API | 84 MCP tools + `.mind` config-dialect surface + Python client | Commodity API surface; open to prove governed-write moat exists | `star-ga/mind-mem` (API layer) |
| `mindlang.dev` | Language website and public documentation | Spec/doc; must be public | `star-ga/mindlang.dev` |

---

## Protected Layer

Every surface listed here is closed-source commercial IP.

| Surface | Role | Why protected |
|---|---|---|
| `mind-runtime` backends for non-commodity substrates | Optimized kernels for Cerebras CS-3, future neuromorphic, optical, and customer ASICs | Unbounded-future-IP; replication requires the exact customer hardware — structurally non-reproducible by a competitor without the same chips |
| `mind-mem` fully-protected runtime kernel `.so` | Anti-debug (ptrace / IsDebuggerPresent / PT_DENY_ATTACH) + VM bytecode interpreter + encrypted strings + triple-redundant state + watchdog loop + binary integrity checks | The runtime kernel is the product; obfuscation enforces the governed-write contract at the binary layer |
| naestro-OS internals | The AGI/ASI agent substrate — orchestration, cognitive kernel, soul-layer | The actual product; 9-LLM orchestration architecture and session memory substrate are the core differentiator |
| NikolaChess protected build | Chess engine with `mind-runtime` protection applied | IP-layered: engine open (public `star-ga/NikolaChess`); protection binaries closed (`nikolachess-source` private) |
| Enterprise certified pipelines | Customer-specific deployment work, SLA attestation chains, regulated-industry governance profiles | Customer-specific; per-contract IP |

Note on `mind/std/blas`: AVX2 register-tiled Q16.16 GEMM and NEON dots live in the
open `mind` repo and stay there. Replicable by a competent team in months. The wedge
requires public verifiability. Future `mind-runtime/blas/<arch>/` tiers may be
protected if and only if they target non-commodity hardware (Cerebras / neuromorphic /
optical / customer ASICs). The commodity tier is never protected.

---

## Wedge Properties that Compose the Unbounded Moat

- **Cross-substrate bit-identity as a type property.** CUDA hash == AVX2 hash == NEON
  hash for the same workload, enforced at the type level by `mindc`. Not a runtime
  assertion — a compilation guarantee.

- **Composable determinism.** RFC 0012 Phase C checks (determinism call-graph +
  target-name validity + q16-dtype rules) compose across the full pipeline. Each layer
  that adopts the Q16.16 dtype inherits the guarantee without re-proving it.

- **Evidence-chain unification (RFC 0016 + RFC 0019).** The three existing governance
  pipelines (512-mind Hash256/Hash512, mind-mem Ed25519 model\_signing, RFC 0011
  ReplayScheduler hash) converge onto a single mic@2.1 + MAP-key vocabulary. No
  competitor can claim this chain without reproducing the full RFC history.

- **naestro-OS itself.** The agent substrate is not a feature — it is the product. It
  is protected not because it is secret but because it is the product of a multi-year
  architecture; a competitor cannot clone an agent OS by copying a single repo.

- **Unified governance vocabulary.** 512-mind + mind-mem + ReplayScheduler share a
  common proof-chain vocabulary. This vocabulary is load-bearing for regulated-industry
  buyers (right-of-integrity, chain-of-title, provable-original attestation). No one
  else has this vocabulary.

- **Multi-year mindc + std + spec coherence.** The specification, compiler, stdlib, and
  runtime are co-designed. Each RFC closes a loop between layers. This coherence is
  harder to replicate than any individual component.

---

## Classification Rule for New Repos

Every new STARGA repo is classified open or protected at creation. Apply the following
rule in order:

| Condition | Classification |
|---|---|
| (a) It proves a wedge property (bit-identity, determinism, evidence-chain) | **Open** |
| (b) It is a commodity-substrate implementation (AVX2, NEON, standard CUDA) | **Open** |
| (c) It is documentation, specification, or RFC text | **Open** |
| (d) It is the agent substrate itself (naestro-OS layer or cognitive kernel) | **Protected** |
| (e) It captures optimization for non-commodity hardware (Cerebras / neuromorphic / optical / customer ASIC) | **Protected** |
| (f) It is customer-specific deployment or certified-pipeline work | **Protected** |

When a repo satisfies both (a) and (d), the agent-substrate clause (d) wins for the
internals; but any spec or protocol the substrate implements that satisfies (a) or (c)
is extracted and published separately.

---

## Open / Protected Boundary at `mind/std/blas` (Decision 2026-05-24)

**Stays fully open.**

Rationale:
- AVX2 register-tiled Q16.16 GEMM and NEON dots are replicable by a motivated team in
  months. Bounded IP is not worth the friction of a split repo.
- The wedge claim — CUDA hash == AVX2 hash == NEON hash — requires that third parties
  can run the commodity-substrate implementations and verify the claim themselves. A
  closed blas layer breaks the verifiability of the wedge.
- The moat is not in the commodity kernel. It is in the type-system guarantee that the
  hash identity is a compilation property, and in the non-commodity-substrate backends
  that are structurally hard to replicate.

Future path: if a `mind-runtime/blas/<arch>/` tier targets a non-commodity substrate
(Cerebras CS-3, a customer ASIC, a future neuromorphic chip), it may be protected under
rule (e) above. The commodity AVX2/NEON/reference-CUDA tier remains open regardless.

---

## Anti-Fragmentation Principle

Three governance pipelines exist today:

| Pipeline | Source | Hash / signing scheme |
|---|---|---|
| 512-mind proof chain | `512-mind/src/proof_chain.mind` | Hash256 / Hash512 sealed-preimage |
| mind-mem model signing | mind-mem runtime kernel | Ed25519 model\_signing |
| RFC 0011 ReplayScheduler | `mind` RFC track | ReplayScheduler hash |

RFC 0016 (task #288) MUST unify these three onto a single `mic@2.1` + MAP-key
vocabulary, citing `512-mind/src/proof_chain.mind` as the parent vocabulary anchor.

**Never add a fourth governance pipeline.** Any new hash or signing scheme proposed for
a STARGA repo is either unified into the RFC 0016 track at design time, or it is
rejected. Fragmentation of the evidence chain destroys the unified-governance
value proposition.

---

## Commit Author and Leak Discipline

- All commits: `STARGA Inc <noreply@star.ga>`. No co-author lines. No AI attribution.
- Forbidden strings in any public STARGA surface: `FORTRESS`, `naestro-bot`,
  `weavemind`, `sentrux`, `biome`, `nikolachess-source`.
- Forbidden in public: competitor evaluation paragraphs, prior-art survey text,
  multi-LLM round transcripts, autoresearch reports. These land in `mind-internal/`
  only.
- Per-repo leak audit at every push. If a forbidden string appears in staging, the
  commit does not land.

---

## Cross-References

Memory records (mind-mem):
- `project_starga_session_checkpoint_2026_05_25`
- `project_starga_four_pillar_strategy_2026_05_24`
- `feedback_mind_wedge_vs_credibility_lane`

Related specs:
- RFC 0016 — evidence-chain unification (mic@2.1 + MAP key)
- RFC 0019 — governance vocabulary alignment
- RFC 0011 — ReplayScheduler hash (source pipeline for unification)
- `512-mind/src/proof_chain.mind` — parent vocabulary anchor
