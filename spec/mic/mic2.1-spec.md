# MIC 2.1 — Metadata Attachment Partner (MAP) Extension

**Version:** 2.1
**Status:** Draft
**Date:** 2026-05-25
**Parent:** [mic2-spec.md](./mic2-spec.md), [micb-spec.md](./micb-spec.md)

## 1. Motivation

mic@2 today has no extension surface. Its text grammar is closed
(`header | symbol | type | value | output | comment | empty`); comments are
stripped on canonicalization (mic2-spec.md §"Canonicalization Rules", rule 6);
and the binary partner MIC-B v2 (micb-spec.md) is a fixed five-table layout
with no provision for sidecar metadata.

A growing set of downstream RFCs needs to attach *normative*,
canonicalization-stable, sign-able metadata to a compiled IR binary without
breaking byte-identity for existing producers:

- **RFC 0016** (task #288, evidence-chain emission) — per-graph
  `evidence_chain` carrying trace hash, substrate identifier, parent pointer.
- **RFC 0014** (per-substrate lowering) — canonical lowering-tier name attached
  to the artifact, not just the build log.
- **RFC 0017** (cross-substrate verify) — hashes of cross-target certificates
  embedded in the artifact so verifiers need no separate sidecar.
- **RFC 0019** (task #294, deterministic agent substrate) — agent-trace
  identifiers linkable to the IR that produced them.

mic@2.1 is the smallest possible additive change that unlocks all four RFCs
simultaneously: a **Metadata Attachment Partner (MAP)** section — an ordered,
typed, canonically-serialised key/value table — that lives alongside the
existing graph sections.

Non-goals: no change to graph opcodes, types, or value semantics; no new
dtype, no new opcode; no change to the byte layout of existing mic@2 producers
when MAP is empty (the common case during rollout).

## 2. Compatibility contract

mic@2.1 is a backward-compatible minor revision of mic@2:

1. **Every valid mic@2 binary is a valid mic@2.1 binary** with an empty MAP
   section. Existing producers keep emitting mic@2; existing consumers keep
   reading them.
2. **The mic@2.1 parser reads mic@2 binaries unchanged.** "No MAP section" is
   detected structurally (absence of the section marker), not versioned — the
   version header stays `mic@2` for text, the magic byte stays `0x02` for
   binary.
3. **The mic@2.1 emitter omits the MAP section entirely when empty**, so the
   round-trip mic@2 → parse → re-emit is byte-identical to the original mic@2
   bytes. No version flag flips by upgrading the parser.
4. **Producers and consumers negotiate via the existing version header.** A
   consumer that does not understand MAP either ignores it (lenient) or refuses
   the artifact (strict).
5. **Unknown MAP keys are preserved on round-trip** unless the consumer
   explicitly drops them. Strict consumers MAY reject unknown keys under known
   reserved namespaces (§4); they MUST NOT silently rewrite them.

Rationale for the original 2.0 → 2.1 bump (NOT 3.0): the binary delta is one
optional section, the text delta is one optional block, the canonicalisation
delta is one ordering clause — all additive. A major bump would force every
tool to update detection logic for no behavioural benefit.

> **Note (post-RFC 0021, 2026-05-27).** The `mic@3` name was later allocated to
> a different artifact — a canonical *binary serialisation of the `IRModule`
> data shape* (the same shape `mic@1` text serialises), shipped in mindc 0.7.x
> via `mind/src/ir/compact/v3/` and reachable through `mindc --emit-mic3`. The
> evidence-chain MAP attaches to that `mic@3` form too, via the `0x4D`-sentinel
> epilogue, with the same key/value vocabulary defined here. See
> `mind/docs/rfcs/0021-canonical-ir-unification.md` for the unification plan
> (steps 1–3 shipped, 4–6 in flight) and `spec/v1.0/ir-stability.md` for the
> stability surface.

## 3. Wire format

The MAP section is defined for both the text format (mic@2) and the binary
partner (MIC-B v2). The two encodings round-trip losslessly.

### 3.1 Placement (normative)

The MAP section is placed **after `O` (output)** in both formats — at the very
end of the artifact, immediately following the output line/varint.

Justification for end-placement:
- The mic@2 grammar declares `output ::= "O" WS value_id` as the terminal
  production with no trailing newline. Adding MAP before `O` would relocate an
  already-stable terminal. Adding it *after* `O` frames MAP as a bounded
  epilogue and preserves "the graph proper ends at `O`".
- MIC-B v2 places output as the last varint with no terminator; a trailing MAP
  section preserves the property that a mic@2 consumer streaming until output
  is satisfied produces a structurally complete graph before encountering any
  MAP bytes. This enables the empty-MAP byte-identity in §2(3): a producer that
  emits no MAP terminates exactly where mic@2 said, no trailing marker.
- Tooling that strips MAP (for diff, unsigned diagnostic output, downgrade)
  truncates the trailing section — a one-line operation.

### 3.2 Text grammar (mic@2.1 extension)

```ebnf
mic2.1      ::= mic2 (map_block)?
map_block   ::= "map" WS "{" LF map_entry* "}" LF?
map_entry   ::= WS* map_key WS* "=" WS* map_value LF
map_key     ::= ident ("." ident)*
ident       ::= [A-Za-z_][A-Za-z0-9_]*
map_value   ::= map_string | map_int | map_bytes | map_nested
map_string  ::= "\"" string_char* "\""
map_int     ::= "-"? [0-9]+
map_bytes   ::= "bytes" "(" "0x" [0-9a-f]+ ")"
map_nested  ::= "{" LF map_entry* WS* "}"
```

`mic2` is the production from mic2-spec.md. `string_char` is any UTF-8
codepoint except `"`, `\`, `\n`, escaped with JSON string rules. `map_bytes`
is lowercase hex, even-length, `0x` prefix mandatory. `map_int` is decimal,
signed 64-bit range. Nesting is bounded (§3.5).

### 3.3 Text example

```
mic@2
T0 f16 128 128
T1 f16 128
a X T0
p W T0
p b T1
m 0 1
+ 3 2
r 4
+ 5 0
O 6
map {
  evidence_chain.parent = bytes(0xcafef00d)
  evidence_chain.substrate = "x86_avx2"
  evidence_chain.trace_hash = bytes(0xdeadbeef0123456789abcdef)
  target.canonical_name = "cpu_avx2"
}
```

### 3.4 Binary grammar (MIC-B v2.1 extension)

An OPTIONAL trailing section after the output varint:

```
uleb128   map_marker      # 0x4D = 'M' (sentinel; absent if no MAP)
uleb128   count           # number of top-level entries
repeat count:
  uleb128 key_str_idx     # index into the existing string table (interned dotted key)
  u8      value_tag       # 0=string, 1=int, 2=bytes, 3=nested
  match value_tag:
    0: uleb128 str_idx          # string-table index
    1: sleb128 int              # zigzag signed 64-bit
    2: uleb128 byte_len; bytes  # then byte_len raw bytes
    3: uleb128 nested_count; .. # then nested_count entries (recursive)
```

**Detection rule:** after consuming the output varint, attempt one more byte
read. EOF = "no MAP". A byte equal to `0x4D` ('M') = MAP section follows. Any
other byte = parse error. This sentinel lets a mic@2.0 producer's output
(ending exactly at the output varint) be a valid mic@2.1 binary with empty MAP.

**Reusing the string table** for keys is deliberate: dotted MAP keys repeat
across a build; the existing interning machinery handles them. New strings
discovered during MAP encoding append in first-seen order, after the existing
four string orderings.

### 3.5 Limits (strict consumers SHOULD enforce)

Max MAP key length 256 bytes; max key depth (dotted segments) 8; max nesting
depth 4; max entry count (recursively summed) 4096; max `bytes()` value 1 MiB;
max `string` value 64 KiB. Advisory ceilings — reject at boundary, never
silently truncate.

## 4. Reserved MAP keys

| Namespace          | Owner RFC | Purpose                                          |
| ------------------ | --------- | ------------------------------------------------ |
| `evidence_chain.*` | RFC 0016  | Trace-hash, substrate, parent — emission         |
| `target.*`         | RFC 0014  | Per-substrate lowering-tier metadata             |
| `verify.*`         | RFC 0017  | Cross-substrate verification certificate hashes  |
| `agent.*`          | RFC 0019  | Deterministic agent-substrate trace links        |
| `signature.*`      | this spec | Detached signing (§6)                            |

Key structure within each namespace is defined by the owning RFC, not here.

**Forward-compatibility:** unknown keys (including unknown keys inside a
reserved namespace) are preserved on round-trip by default. Strict consumers
MAY reject; lenient consumers MUST preserve.

**Duplicate keys** at the same nesting level are a hard parse error — no
last-write-wins. The §5 canonicalisation rules make duplicate emission a
producer bug, not a wire-format ambiguity.

Non-reserved keys are permitted under any non-colliding namespace; producers
SHOULD domain-prefix application keys (`org.example.*`).

## 5. Canonicalisation

Extends the mic@2 canonicalisation rules with:

7. **MAP section comes last** — after `O`.
8. **Top-level MAP entries sort lexicographically by full dotted key**,
   byte-wise on the UTF-8 encoding (string content is the sort key, not the
   string-table index).
9. **Nested MAP entries follow the same rule recursively.**
10. **Empty MAP section is omitted entirely** — there is no canonical
    "empty map" marker; an empty MAP is the absence of the section. Enforces §2(3).
11. **Bytes values emit as lowercase hex.**
12. **String values use minimum-length escapes** (`\"`, `\\`, `\n`, `\t`,
    `\uXXXX` for non-ASCII-printable). No redundant escaping.
13. **Integer values: no leading zeros, no `+`, `-0` → `0`.**
14. **Nested-map serialisation order is keys-sorted-per-rule-8, recursive.**

Byte-identity guarantees:
- **Text:** `emit(parse(emit(G))) == emit(G)` byte-for-byte.
- **Binary:** `emit_micb(parse_micb(emit_micb(G))) == emit_micb(G)` — the
  string-table interning order is deterministic from graph + sorted MAP entries.
- **mic@2 backward:** `emit_mic2.1(parse_mic2.1(emit_mic2(G))) == emit_mic2(G)`
  — round-trip of an old-emitter artifact through the new parser yields the same
  bytes because MAP is empty (rule 10).

## 6. Signing surface

mic@2.1 reuses the Ed25519 primitive from
`mind-mem/src/mind_mem/model_signing.py` (`sign_manifest` / `verify_manifest`).
The signature is itself a MAP key:

- `signature.ed25519` — `bytes(...)` length 64. The signature.
- `signature.pubkey` — `bytes(...)` length 32. OPTIONAL; if absent the verifier
  resolves the pubkey out-of-band (key registry / CI publisher key).
- `signature.algo` — `"ed25519"`. OPTIONAL, RECOMMENDED for forward-compat.

### 6.1 Bytes-to-sign rule (normative)

The signature is computed over the **canonical mic@2.1 binary encoding of the
artifact with the `signature.*` namespace removed**:

1. Take graph G and MAP `m`.
2. `m_signed = { k: v for k, v in m if not k.startswith("signature.") }`.
3. `B = emit_micb(G, m_signed)` per §3.4 + §5.
4. `sig = ed25519_sign(B, private_key)` — same primitive as
   `mind_mem.model_signing.sign_manifest` but byte-oriented (expose the
   bytes-form helper directly; do not UTF-8 round-trip).
5. Set `m["signature.ed25519"] = sig` (+ optional pubkey/algo).
6. Re-emit with populated `m`.

Verification runs steps 1–3 against MAP-minus-`signature.*`, then
`ed25519_verify(sig, B, pubkey)`.

Why the binary form: it is deterministic-by-construction (interning, varint, no
whitespace ambiguity) — the same discipline `model_signing` uses for its
byte-canonical `MODEL_MANIFEST.txt`. Why omit the whole `signature.*` namespace:
a signature cannot sign itself, and omitting the namespace lets a verifier
attach its own `signature.pubkey` after-the-fact without invalidating.

### 6.2 Reuse, do not duplicate

Implementations MUST call into `mind_mem.model_signing` (or an exact
byte-equivalent — same library, same RFC 8032 parameters) rather than
re-implementing Ed25519. Per the #288 ecosystem-fit decision: one signing
primitive across mind-mem, mic@2.1, and any future signed surface.

## 7. Open questions for follow-up

1. **MAP-only delta format** — RFC 0019 may want to update agent-trace links
   after the IR is otherwise frozen, without rewriting the whole binary. Defer
   until RFC 0019's update-frequency profile is known.
2. **Compression for large MAP sections** — defer until a real `evidence_chain.*`
   profile exceeds ~100 KiB compressed; the §3.5 ceilings keep this off the
   critical path.
3. **Backwards-incompatible MAP keys** — the first new value-tag (e.g. a Q16.16
   fixed-point numeric tag) is a `mic@2.2` change (additive tag, old parsers
   reject), not `mic@3`. Until then, encode novel numeric metadata as `bytes()`.
4. **Cross-artifact MAP references** — RFC 0017 may want to reference another
   artifact by hash; `bytes()` suffices today, a typed `ref(hash)` is deferred.
5. **Streaming-aware MAP placement** — end-placement means a streaming consumer
   can't validate signed metadata until the whole graph is read. Correct for an
   epilogue; a `pre_map` section is deferred until a real use-case lands.

## 8. Compatibility matrix

| Reader \ Writer | mic@1 | mic@2 | mic@2.1 (empty MAP) | mic@2.1 (with MAP) |
| --------------- | ----- | ----- | ------------------- | ------------------ |
| mic@1 reader    | OK    | err: bad header | err: bad header | err: bad header |
| mic@2 reader    | err   | OK    | OK (identical bytes) | err: trailing bytes after `O` |
| mic@2.1 reader  | err   | OK (empty MAP) | OK (empty MAP) | OK (full MAP) |

**Downgrade** mic@2.1 → mic@2 is lossy (MAP discarded). A downgrader MUST drop
the MAP section, not encode keys as comments (stripped on mic@2 canon). A
downgrader MUST NOT silently downgrade a *signed* artifact (destroys the
verification chain) without explicit operator consent.

**Upgrade** mic@2 → mic@2.1 is lossless and a byte-level no-op (empty MAP =
absent section). Version header and binary magic unchanged.

**Forward compat (mic@2.1 reader, mic@2.2 emit):** an unknown `value_tag` byte
fails at the boundary with the tag named — the correct behaviour; the
value-tag space is small and any extension is a real change.

## 9. References

- [mic2-spec.md](./mic2-spec.md) — parent text format
- [micb-spec.md](./micb-spec.md) — parent binary format
- `mind/src/ir/compact/v2/` — reference Rust impl (emit/parse/binary/types/varint)
- `mind/src/ir/compact/v3/` — `mic@3` binary `IRModule` codec + MAP epilogue
  (RFC 0021 steps 1–3)
- RFC 0016 — evidence-chain emission (task #288, `evidence_chain.*`)
- RFC 0014 — per-substrate lowering (`target.*`)
- RFC 0017 — cross-substrate verify (`verify.*`)
- RFC 0021 — canonical IR unification (the long-term home of the MAP carrier
  on the `IRModule` data shape; `mic@3` binary + `mic@2.x` → `mind-model@2`
  demotion)
- RFC 0019 — deterministic agent substrate (task #294, `agent.*`)
- `mind-mem/src/mind_mem/model_signing.py` — Ed25519 primitive reused by §6
- RFC 8032 — EdDSA, §5.1 Ed25519 parameters
