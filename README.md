# Mind Language Specification

The **MIND** language evolves through an open specification process. This repository is the
authoritative source for the normative language specification (`spec/`) and the guiding design
principles (`design/`). Content here is versioned, reviewed in the open, and kept in lockstep with
the public reference implementation at [cputer/mind](https://github.com/cputer/mind).

## Table of contents

- [Language specification](./spec/)
  - [Core v1 overview](./spec/v1.0/overview.md)
  - [Surface language](./spec/v1.0/language.md)
  - [Core IR](./spec/v1.0/ir.md)
  - [Static autodiff](./spec/v1.0/autodiff.md)
  - [Shapes & tensor semantics](./spec/v1.0/shapes.md)
  - [MLIR lowering](./spec/v1.0/mlir-lowering.md)
  - [Runtime interface](./spec/v1.0/runtime.md)
- [Design documents](./design/)
  - [Design principles](./design/principles.md)
  - [RFC process](./design/rfc-process.md)

## Reading the spec

The specification is organised to mirror the reference compiler documentation in
[`cputer/mind/docs/`](https://github.com/cputer/mind/tree/main/docs). Each chapter notes
relationships to implementation details and links to the corresponding background materials
when informative context is helpful.

Normative sections use RFC 2119 terminology. When a document includes non-normative background or
examples it is explicitly marked as informative.

## Contributing

- **Read online:** <https://cputer.github.io/mind-spec/>
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
