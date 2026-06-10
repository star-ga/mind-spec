# Mind Language Specification

[![Spec Status](https://img.shields.io/badge/Core%20v1%20spec-frozen-blue)](./STATUS.md)
[![Compiler](https://img.shields.io/badge/reference%20compiler-v0.7.1-blue)](https://github.com/star-ga/mind)
[![Runtime](https://img.shields.io/badge/runtime-CPU%20backend%3B%20GPU%20roadmap-lightgrey)](https://github.com/star-ga/mind-runtime)

The **MIND** language evolves through an open specification process. This repository is the
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
  - [MLIR lowering](./spec/v1.0/mlir-lowering.md)
  - [Runtime interface](./spec/v1.0/runtime.md)
  - [IR stability + evidence chains](./spec/v1.0/ir-stability.md) — `mic@1` text + `mic@3` binary (RFC 0021), MAP epilogue (RFC 0014), and the load-bearing `trace_hash = SHA-256(canonical mic@3 bytes)` rule (RFC 0016 GAP-1; re-anchored 2026-05-31, supersedes the original `mic@1`-text rule).
  - [Future extensions](./spec/v1.0/future-extensions.md) — Language Profiles, roadmap for broader accelerator-class coverage (TPU, NPU, LPU, DPU, FPGA, ASIC, Cerebras, Taalas, Tenstorrent, SambaNova, Graphcore IPU, Gaudi — research/roadmap, not shipped), Verification-as-a-Service
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
