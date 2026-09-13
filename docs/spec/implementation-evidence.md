<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0.
-->

# Implementation evidence

This page records how a public implementation claim can be checked. A source
reference establishes a contract or code path; it does not establish that a
particular binary was built, that a feature was enabled, or that a benchmark
was reproduced. Those facts require a receipt with the fields below.

## Reference under review

The source reference used for the current compiler observations is
[`star-ga/mind@45846292638920a7865085fd0f3019c74d876bfb`](https://github.com/star-ga/mind/tree/45846292638920a7865085fd0f3019c74d876bfb),
observed 2026-09-12. No release artifact digest, host/target substrate, or
command receipt is attached to this source-only review; those fields remain
**UNKNOWN** until recorded with the artifact.

| Field | Value |
| --- | --- |
| Source SHA | `45846292638920a7865085fd0f3019c74d876bfb` |
| Features | **UNKNOWN** for an installed binary. The documented full working build uses `mlir-build std-surface cross-module-imports`; see [`docs/cli.md`](https://github.com/star-ga/mind/blob/45846292638920a7865085fd0f3019c74d876bfb/docs/cli.md#L39-L58). |
| Artifact SHA / filename | **UNKNOWN** |
| Command, host/target substrate, timestamp | **UNKNOWN** |

## Hard release gates

These are pass/fail contract checks. A row marked source-verified is not a
claim that a release artifact passed it.

| Gate | Public source contract | Source status | Receipt status and boundary |
| --- | --- | --- | --- |
| Native executable target | `--backend native` is a separate build path; the native bridge accepts `binary` emission and rejects library/object emission because the frozen backend emits static ET_EXEC. [`src/bin/mindc.rs`](https://github.com/star-ga/mind/blob/45846292638920a7865085fd0f3019c74d876bfb/src/bin/mindc.rs#L87-L98) dispatches it; [`src/build/native_bridge.rs`](https://github.com/star-ga/mind/blob/45846292638920a7865085fd0f3019c74d876bfb/src/build/native_bridge.rs#L62-L79) enforces the emission boundary. | Verified from source. The bridge’s final output fence checks ELF magic and minimum length; an independent ET_EXEC header receipt is still required for a binary release claim. | Artifact and command receipt **UNKNOWN**. The opt-in boundary is `mindc build --backend native --emit binary`; library emission belongs to the MLIR path. |
| Cross-module imports | `cross-module-imports` is an optional feature and depends on `std-surface`; it is not a blanket assertion that the resolver is absent. [`Cargo.toml`](https://github.com/star-ga/mind/blob/45846292638920a7865085fd0f3019c74d876bfb/Cargo.toml#L335-L376) and the resolver’s feature gates define this boundary. | Verified from source. | A project-resolution receipt using `--features cross-module-imports` is **UNKNOWN**. A default/no-feature build cannot be used as evidence for the opt-in path. |
| CLI capability metadata | `mindc --version` prints the package version and only the components compiled under the enabled feature gates; `mindc --stability` prints the public stability model. [`src/bin/mindc.rs`](https://github.com/star-ga/mind/blob/45846292638920a7865085fd0f3019c74d876bfb/src/bin/mindc.rs#L1690-L1720) | Verified from source. | The output is partial capability metadata, not binary/source identity. Artifact SHA and feature manifest remain **UNKNOWN** until captured. |
| Tensor surface versus exports | [`std/tensor.md`](../../std/tensor.md) is specification text and describes the normative tensor surface. The compiler’s bundled `std/*.mind` export inventory is a separate implementation fact; at this reference it does not contain `std/tensor.mind`. | Separation verified from the two public trees. | A compiled `std::tensor` export and runnable tensor artifact require their own feature, command, and test receipts; status is **UNKNOWN** here. |

## Comparative performance claims

Historical numbers in `STATUS.md` and the benchmark documents are retained as
historical reports. A new comparison is publishable only when both sides use
the same source/configuration reference, input vectors, optimization settings,
substrate, warm-up and measurement protocol. Record the exact artifact SHA and
command for each side. A source SHA by itself cannot reproduce a performance
number, so new values without those fields are **UNKNOWN**.

| Required field | Required value |
| --- | --- |
| Source and artifact | Full source SHA plus artifact filename and digest for every side |
| Features/configuration | Exact compiler features, optimization flags, runtime/library versions |
| Workload | Fixture/input digest, shape, precision, and correctness result |
| Measurement | Command, host/target substrate, warm-up, repetitions, statistic, timestamp |

## Migration inventory

The #306 byte-store migration is closed at the source level for the named
modules. The current sources use byte stores for byte-buffer sites while keeping
aligned `__mind_store_i64` writes for words and record fields; the migration
commit is [`a664a71e`](https://github.com/star-ga/mind/commit/a664a71e), and the
source is present at the reference SHA above. This does not substitute for a
fresh executable or cross-substrate receipt.

| Item | Current public evidence | Remaining evidence |
| --- | --- | --- |
| `std.string` byte writes | `__mind_store_i8` at byte-buffer call sites | Runnable and artifact receipt **UNKNOWN** |
| `std.sha256` byte-buffer writes | `__mind_store_i8` for message/output byte positions; aligned state words remain i64 | KAT and artifact receipt **UNKNOWN** |
| `std.toml` byte writes | `__mind_store_i8` for byte copy/append; aligned headers/handles remain i64 | Parser/runtime receipt **UNKNOWN** |

## Evidence record

Use one record per gate, benchmark side, or migration verification:

```text
source_sha      = <full public commit>
features        = <exact feature set, or none>
artifact        = <filename and SHA-256, or UNKNOWN>
command         = <complete command>
substrate       = <host/target and relevant runtime/tool versions>
timestamp       = <UTC>
input           = <fixture/vector digest, if applicable>
expected        = <contract>
observed        = <result and exit status>
verdict         = PASS | FAIL | UNKNOWN
limits          = <scope, skipped checks, or configuration differences>
```

Do not promote **UNKNOWN** to PASS from a constructor, help string, source
listing, or capability advertisement alone.
