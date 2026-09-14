# Mind Language Specification

[![Spec Status](https://img.shields.io/badge/Core%20v1%20spec-frozen-blue?style=flat-square)](./STATUS.md)
[![Compiler](https://img.shields.io/badge/reference%20compiler-v0.10.2-blue?style=flat-square)](https://github.com/star-ga/mind)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](./LICENSE)
[![Deterministic](https://img.shields.io/badge/deterministic-bit--identical-brightgreen?style=flat-square)](https://github.com/star-ga/mind/blob/main/docs/roadmap.md)

**MIND** is a deterministic language. Its cross-substrate CI gate verifies
bit-identical **computational outputs** for the committed integer, Q16.16 and
strict floating-point workloads on x86-AVX2 and ARM-NEON. Native machine-code
bytes may differ between ISAs. The floating-point coverage includes a strict
f32 dot product, an f32 matrix-vector product and a scalar f64 operation chain;
it is not a proof for arbitrary floating-point programs. General reductions,
transcendentals and GPU/other-substrate coverage require further implementation
and conformance evidence. [Compiler RFC 0015 §5A](https://github.com/star-ga/mind/blob/main/docs/rfcs/0015-cross-substrate-bit-identity.md#5a-conformance-evidence)
records the exact workloads, output encodings and reference hashes.

Two further precise claims, stated at their honest scope: the reference compiler's **bootstrap/front-end self-hosts** (the pure-MIND front-end reproduces the reference output byte-for-byte on the `mic@1` text, `mic@3` binary, and native-ELF gates), while full-chain Rust-independence of the whole toolchain remains roadmap. The bounded RI-D driver path has landed: `mindc build --backend native` resolves a manifest entry and its local imports, enforces export scope and entry-module ownership of `main`, and emits a native executable for the admitted scalar/control-flow subset through the pure-MIND emitter. The invoking host driver remains implemented in Rust; imported aliases, structs, and enums refuse until their source ownership can survive lowering, and native aggregate/full-language coverage remains unfinished ([compiler PR #257](https://github.com/star-ga/mind/pull/257)).

Compiled artifacts carry an **emitted, hash-anchored (tamper-evident)** evidence chain anchored on `trace_hash = SHA-256(canonical mic@3 bytes)`. Opt-in signing is implemented. The supported production profile requires **both ML-DSA-87 and SLH-DSA-SHAKE-256s**, with both public keys pinned for trusted verification. Ed25519 and the earlier Ed25519/ML-DSA-65 hybrid are retired from signing and trust verification; historical artifacts remain inspectable ([compiler PR #262](https://github.com/star-ga/mind/pull/262)). Published releases are currently unsigned.

The language evolves through an open specification process. This repository is the
authoritative source for the normative language specification (`spec/`) and the guiding design
principles (`design/`). Content here is versioned, reviewed in the open, and kept in lockstep with
the public reference implementation at [star-ga/mind](https://github.com/star-ga/mind).

## Table of contents

- [Language specification](./spec/)
  - [Core v1 overview](./spec/v1.0/overview.md)
  - [Surface language](./spec/v1.0/language.md)
  - [Core IR](./spec/v1.0/ir.md)
  - [Static autodiff](./spec/v1.0/autodiff.md)
  - [Shapes & tensor semantics](./spec/v1.0/shapes.md)
  - [Standard library](./spec/v1.0/stdlib.md) — core/math/tensor/diff/io, the pure-MIND surface (RFC 0005), and the RFC/NIST-KAT-verified crypto & protocol primitive modules (a verified **primitive library** — not a TLS client/server)
  - [MLIR lowering](./spec/v1.0/mlir-lowering.md) — downstream-interchange and exotic-chip-reach backend (non-normative self-host path; the native-ELF backend is the normative self-host target)
  - [Runtime interface](./spec/v1.0/runtime.md)
  - [IR stability + evidence chains](./spec/v1.0/ir-stability.md) — `mic@1` text + `mic@3` binary (RFC 0021), MAP epilogue (RFC 0014), and the load-bearing `trace_hash = SHA-256(canonical mic@3 bytes)` rule (RFC 0016 GAP-1; re-anchored 2026-05-31, supersedes the original `mic@1`-text rule).
  - [Future extensions](./spec/v1.0/future-extensions.md) — Language Profiles, broader accelerator-class coverage (TPU, NPU, LPU, DPU, FPGA, ASIC, Cerebras, Taalas, Tenstorrent, SambaNova, Graphcore IPU, Gaudi — available in the commercial `mind-runtime` under license; **bit-identical determinism** across them is the roadmap), Verification-as-a-Service
- [Examples](./examples/)
  - [Basic tensor operations](./examples/basics/)
  - [Autodiff](./examples/autodiff/)
  - [Linear algebra](./examples/linear_algebra/)
  - [Core IR](./examples/ir/)
  - [FFI bindings](./examples/ffi/)
- [Conformance tests](./tests/)
  - [Test corpus samples](./tests/conformance/)
- [Design documents](./design/)
  - [Design principles](./design/principles.md)
  - [RFC process](./design/rfc-process.md)

## Reading the spec

The specification is organised to mirror the reference compiler documentation in
[`star-ga/mind/docs/`](https://github.com/star-ga/mind/tree/main/docs). Each chapter notes
relationships to implementation details and links to the corresponding background materials
when informative context is helpful.

Normative sections use RFC 2119 terminology. When a document includes non-normative background or
examples it is explicitly marked as informative.

## Contributing

- **Read online:** <https://star-ga.github.io/mind-spec/>
- **Preview locally:** `npx docsify-cli serve docs`
- **Guidelines:** See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for review expectations and local setup
  instructions.

Security disclosures should follow [`SECURITY.md`](./SECURITY.md). Project status tracking lives in
[`STATUS.md`](./STATUS.md).

## Licensing

The MIND Specification is maintained by STARGA Inc. and follows an open-core
dual licensing model.

- **Community Edition (this repository)**  \
  The language and runtime specification texts in this repository are made
  available under the Apache License 2.0. See [`LICENSE`](./LICENSE).

- **Enterprise & Commercial Use**  \
  Certain proprietary extensions, compliance documents, and non-public
  materials may be offered under separate commercial terms. These are not
  covered by the Apache License and may not be present in this repository.
  See [`LICENSE-COMMERCIAL`](./LICENSE-COMMERCIAL) for the commercial license
  notice.

For commercial licensing, OEM use, or enterprise support, please contact  \
**legal@star.ga**.
