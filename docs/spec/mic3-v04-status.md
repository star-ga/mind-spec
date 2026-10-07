<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# MIC@3 `0x04` implementation status

**Status: unreleased implementation draft.** The reference implementation landed
on compiler `main` through [PR #256](https://github.com/star-ga/mind/pull/256) at
[`66f43a6b`](https://github.com/star-ga/mind/commit/66f43a6bed42709047682b28cef6bd8e27118c7b).
This page is an informative cross-reference rather than a
versioned or normative wire specification; the v04 wire contract, shared
golden vectors, and release status remain unfrozen.

The proposed first stage carries canonical scalar IR together with owner-
qualified record schemas, fixed or dynamic array descriptors, function
identities and signatures, resolved call targets, and function-scoped semantic
value types. It is intended to preserve logical identity supplied by the
compiler. It does not authorize a physical record ABI or infer identity from
host paths, source order, or scalar handles.

The reference implementation provides checked v04 admission and decoder validation. It
bounds input size, nesting, allocation, and semantic descriptors, stages
declarations before cumulative validation, and rejects malformed or unsupported
content. Its checked evidence path applies the size limit to the complete body
plus MAP artifact before publication. These are implementation checks for the
draft format and do not establish a released wire contract.

The opt-in `compile_source_to_canonical_ir` Rust library API, introduced in
[compiler PR #259](https://github.com/star-ga/mind/pull/259), binds a source
snapshot to captured project scope. It preserves resolved function ownership
and call identities, carries scalar producer facts from the existing type
checker, and checks every canonical return in its defining function scope.
Missing facts, changed snapshots, and unsupported source forms are refused.
This bounded path requires `cross-module-imports`; it returns verified IR
before optimization or backend execution.

The canonical source slice excludes unit functions, functions without explicit
return annotations, and bare returns without values. Those restrictions do not
change ordinary compilation's inferred-return or evaluator unit-placeholder
behavior. This API supplies neither a standalone MIND driver nor native record
and array execution.

The proposal is limited to a scalar instruction subset. Standard-surface and
tensor instructions, source-to-native aggregate execution, pure-MIND codec
parity, cross-profile or cross-substrate identity, a frozen protocol, and
promotion remain separate work. A successful scalar-stage transport result is
not evidence that those dependencies are complete.

## Draft intrinsic contract alignment

The following table records the ten-row intrinsic registry implemented by
[compiler PR #261](https://github.com/star-ga/mind/pull/261), merged on compiler
`main` at
[`a334ead4`](https://github.com/star-ga/mind/commit/a334ead49cfe9e98501c4345d9ec64d6ce2db3b2).
This remains a draft alignment note and does not make v04 a released wire
contract. A canonical declaration using the reserved owner `__mind_intrinsic`
must use one of these exact logical names, physical symbols, arities, and
signatures. The registry has no generic or variadic intrinsic form.

| Logical name | Physical symbol | Wire signature | Effect metadata | Profiles metadata | Result-use metadata |
|---|---|---|---|---|---|
| `argc` | `__mind_argc` | `() -> i64` | argument count | `FrozenNative` | value |
| `argv` | `__mind_argv` | `(i64) -> i64` | argument vector | `FrozenNative` | value |
| `alloc` | `__mind_alloc` | `(i64) -> i64` | arena allocation | `FrozenNative`, `RustMlir` | value |
| `load_i64` | `__mind_load_i64` | `(i64) -> i64` | 8-byte memory read | `FrozenNative`, `RustMlir` | value |
| `load8` | `__mind_load_i8` | `(i64) -> i64` | 1-byte memory read | `FrozenNative`, `RustMlir` | value |
| `open` | `__mind_open` | `(i64) -> i64` | read-only open | `FrozenNative`, `RustMlir` | value |
| `read` | `__mind_read` | `(i64, i64, i64, i64) -> i64` | file-descriptor read; offset is `-1` and ignored | `FrozenNative`, `RustMlir` | value |
| `store_i64` | `__mind_store_i64` | `(i64, i64) -> i64` | 8-byte memory write | `FrozenNative`, `RustMlir` | `DiscardOnly` in `FrozenNative` |
| `store8` | `__mind_store_i8` | `(i64, i64) -> i64` | 1-byte memory write | `FrozenNative`, `RustMlir` | `DiscardOnly` in `FrozenNative` |
| `write` | `__mind_write` | `(i64, i64, i64, i64) -> i64` | file-descriptor write; offset is `-1` and ignored | `FrozenNative`, `RustMlir` | value |

Effect, profile, and result-use columns are registry metadata, not additional
fields in the encoded function signature. In particular,
`DiscardOnly` describes how a FrozenNative emitter may use a store result; it
does not change the historical `i64` wire return, and it does not grant native
admission or prove memory provenance. The offset rule for `read` and `write`
also leaves all four `i64` parameters in the wire signature. Unknown names,
wrong owners, wrong arities, wrong scalar types, and generic identities remain
structured refusals.

## Experimental body mirror and resource limits

The experimental pure-MIND mirror began as a decoder for a declared prefix:
the header, string table, schemas, and function declarations with their
signature descriptors. Compiler commits [`70434b42`](https://github.com/star-ga/mind/commit/70434b42f31e91c21cd25235f862a61c3c4c06f8), [`f788ec90`](https://github.com/star-ga/mind/commit/f788ec900aaf1e4116e435f0b5ded1c45a27521c),
[`335bbf9c`](https://github.com/star-ga/mind/commit/335bbf9c7fb4abe4d8f546a685bc150f3d850ae7), and [`bb53942b`](https://github.com/star-ga/mind/commit/bb53942bc2e15a7fced560626b56a49fb63eb337), which are part of
[compiler PR #264](https://github.com/star-ga/mind/pull/264), extend it through
the complete core body. The mirror now decodes:

- the module `next_id`;
- the export list, which must be strictly increasing, with every reference in
  bounds;
- the instruction list: `ConstI64`, `ConstF64` (eight raw little-endian bytes),
  `BinOp` over the eleven core operator tags, `Output`, `Return`, `Param`, `Call`
  with its resolved callee, and nested `FnDef` with its parameters, optional
  return ID, optional reap threshold, nested body, reserved legacy table,
  resolved identity, and its own scoped value rows;
- the four reserved compatibility counts, each of which must be zero; and
- the module semantic value rows, which must be strictly sorted by `ValueId`.

Opcodes outside the core scalar subset are refused (exit 37) rather than skipped,
and a binary-operator tag outside the core set is refused. The mirror re-emits
the decoded body through its own canonical encoder and compares the result with
the bytes it consumed. Exit 0 means the body decoded, passed the checks listed
in this section, and re-emitted byte for byte with nothing after it; it does not
mean full canonical validation. Its native artifact is tested against reference
decoder outcomes and exact positive-fixture re-emission. This is a
review candidate, not a released protocol or the production decoder.

Wire-format acceptance is not full semantic validation. The mirror applies the
checks below on every run. Their vectors form a separate corpus,
`SEMANTIC_MANIFEST.tsv`, run by `mirror_gate.py --semantic`, and the compiler
test suite checks the Rust reference decoder's verdicts on controls for these
rules (`tests/v04_value_id_boundary.rs`). The mirror now refuses:

- a module `next_id` below a module-scope `ValueId`, a `FnDef` whose return
  metadata or name disagrees with its resolved declaration, and a `FnDef` whose
  parameter count disagrees with it ([`1eefe191`](https://github.com/star-ga/mind/commit/1eefe19119cb43dd7315ccb42ed8d2873f3a32ab));
- a `FnDef` over an external or intrinsic declaration ([`50f8c123`](https://github.com/star-ga/mind/commit/50f8c123c6105160453faccdb0e645f6585de468));
- a declaration defined by two `FnDef` bodies, counted module-wide so that
  sibling and nested definitions are both refused ([`94cacfb3`](https://github.com/star-ga/mind/commit/94cacfb3a9bf50c1518c780aba3c54092b0ddf4d));
- a `Return` outside any function body when the module carries semantic
  authority, and a body with no semantic authority, meaning no schema, no
  function declaration, and no module semantic row ([`5c04641d`](https://github.com/star-ga/mind/commit/5c04641df20a8279ae54aa0c91a501587cbec713));
- a `FnDef` parameter that has no type in the function's own scoped rows (a type
  present only at module scope does not count), or whose scoped type differs
  from the declared descriptor at that position ([`8fd5f27d`](https://github.com/star-ga/mind/commit/8fd5f27dac797c145e84c0f8341795ed4cbf49f3));
- semantic rows that type a value their own scope does not define, with a nested
  `FnDef` treated as opaque to the enclosing scope ([`e96cde52`](https://github.com/star-ga/mind/commit/e96cde520d75909efffd4058aa7ed1be4bf1d342), with the
  membership lookup bounded by [`e85e0b5f`](https://github.com/star-ga/mind/commit/e85e0b5f2c5348618ff23b206a3cf21b59e96aea)); and
- a function's scoped rows above `2^40` elements, counted per function so that
  siblings and nested functions do not share an allowance ([`3923608a`](https://github.com/star-ga/mind/commit/3923608a036b7be46e130dc224500c64f88939d1)).

Module semantic rows are charged to the same cumulative element scope as every
declaration signature ([`86b72913`](https://github.com/star-ga/mind/commit/86b7291326850abc4b6498db01ba9fa8eba8907f)); a function's own scoped rows are not.

At compiler [`7831998b`](https://github.com/star-ga/mind/commit/7831998b07a23d3c973d56505aa761a696ea8df9) the corpus is 72 wire vectors in `MANIFEST.tsv` and 29
semantic vectors in `SEMANTIC_MANIFEST.tsv`. `tests/v04_mirror_vector_dump.rs`
assigns each wire vector its expected mirror exit code and checks each vector's
accept-or-refuse polarity against the reference decoder, which accepts 22
vectors and refuses 50. The mirror is expected to exit 0 on 21 of the 22. The
other is a complete body followed by one trailing byte: the reference's body
parser accepts it up to the body boundary, and the mirror refuses the trailing
content with exit 20. The semantic corpus has 10 positive and 19 negative
vectors. For every vector named `pos_`, the gate also compares the bytes the
mirror re-emits with the vector's own bytes outside the mirror process.

Still open as explicit parity obligations are parameter names; typed call
relationships (argument count, argument types and result type against the
callee's declaration); the type of a `Return` inside a function body (the
reference refuses a missing value when the declaration has a return type, a
value when it has none, and a value whose scoped type differs from the declared
return type, while the mirror checks only the `FnDef` return ID); the rule that
every local declaration is defined by a `FnDef` body (the mirror refuses a
second definition but not a missing one); string-table minimality (the
reference rebuilds the table from the strings a body actually references, while
the mirror re-emits the table it was given); and first-refusal parity: a body
that breaks several rules can be refused here for a different cause than the
reference decoder reports first, so diagnostic-order parity is not claimed. A
passing mirror result does not authorize native execution of the represented
program.

The candidate's implementation limits are:

| Resource | Draft mirror limit | Failure behavior |
|---|---:|---|
| Admitted input | 10,485,760 bytes (`10 MiB`) | refuse before decoding when larger |
| Temporary read buffer | admitted limit plus 2 bytes | bounded probe for oversize detection; the extra bytes are never admitted |
| Re-emitted core body | 65,536 bytes | refuse when the body exceeds the mirror limit |
| ULEB value | `2^62 - 1` (`4,611,686,018,427,387,903`) | refuse larger values without wrapping |
| Type-descriptor nesting | 64 | refuse deeper declared type descriptors |
| Instruction depth | less than 256, with root depth 0 | refuse depth 256 |
| Allocation budget | `min(128 MiB, 1 MiB + 32 × input bytes)` | refuse when checked charges exceed the budget |
| Implemented descriptor scopes | `2^40` elements | check each descriptor, the schema-field total, and the shared total over every declaration signature plus module semantic rows (`2^40` admitted, `2^40 + 1` refused); each function's own scoped rows have a separate `2^40` allowance, counted per function |

The input cap, body cap, and budget are implementation limits for this
unreleased draft. They do not establish complete v04 reader/writer parity
or native aggregate execution. The ULEB limit is a declared narrowing. The
reference decoder reads ULEB values over the full `u64` range, while the mirror
refuses any ULEB field above `2^62 - 1` (exit 17, or exit 14 past nine bytes).
On a 64-bit host, bodies the reference accepts are therefore refused here when
they carry a `next_id` from `2^62` to `2^64 - 2` (the reference itself refuses
only `usize::MAX`), a `ConstI64` value of `2^61` or more or below `-2^61`
(including `i64::MAX` and `i64::MIN`, whose zigzag encodings exceed the limit),
or a `ValueId` or `Param` index of `2^62` or more. The reference
allocation accounting charges each instruction twice (640 logical bytes total);
this is an admission budget, not a measured heap allocation. The mirror applies
the reference's per-item charges but not its final whole-body re-emission
charge, so a body at the edge of the budget can be admitted here and refused by
the reference.

None of the commits cited in this section modifies `src/`, so the Rust reference
decoder in `src/ir/compact/v3` is unchanged by them. Existing `mic@3` versions,
including their `0x03` compatibility behavior, remain unchanged. This status
page establishes no normative v04 byte contract, shared
vectors, reader/writer contract, or Core v1 requirement. Any future v04
specification must be accepted separately and must define its own strict
version, malformed-input, resource, canonicality, and backward-compatibility
rules before publication.

[Back to Spec Index](./index.md) | [Project status](../../STATUS.md)
