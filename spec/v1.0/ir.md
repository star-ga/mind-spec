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

# Intermediate Representation (Normative)

This chapter defines the canonical compiler intermediate representation (IR) for MIND. The IR serves
as the interchange format between the front-end, optimisation passes, and code generators.
Implementation notes live in [`cputer/mind/docs/ir`](https://github.com/cputer/mind/tree/main/docs/ir).

## Goals

The IR MUST provide:

- **Structural fidelity**: it preserves the high-level structure required for differentiation and type
  checking.
- **Deterministic semantics**: equivalent source programs produce alpha-equivalent IR modules.
- **Verification hooks**: each transformation pass MUST be able to assert invariants using the schema
  defined below.

## Module structure

An IR module consists of:

- A list of imports referencing other modules.
- Type declarations mirroring surface-level structs and traits.
- Function definitions with explicit control-flow graphs.
- Metadata blocks for optimisation hints (informative by default).

Modules MUST be serialisable to a canonical textual representation to support incremental
compilation caches.

## Control-flow graph

- Functions are partitioned into basic blocks with single entry and exit points.
- Each block ends with a terminator instruction (`branch`, `return`, `switch`, or `unreachable`).
- Terminator operands reference successor blocks. Implementations MUST validate that successors exist
  and that phi-nodes receive a value for each predecessor.

Further discussion of graph construction is documented in
[`cputer/mind/docs/ir/control-flow`](https://github.com/cputer/mind/tree/main/docs/ir/control-flow)
(informative).

## Instructions

Core instruction categories include:

- **Value operations**: arithmetic, logical, and call instructions.
- **Memory operations**: allocate, load, store, and reference-count primitives.
- **Differentiation primitives**: tangent extraction and accumulation instructions that correspond to
  the rules in [Automatic differentiation](./autodiff.md).

Each instruction specifies operand types and result types explicitly. Implementations MUST reject IR
that violates typing rules.

## Verification

Compilers MUST run IR verification after each transformation pass. Verification ensures:

- All references are well-formed and point to declared entities.
- Types match across instructions and phi-nodes.
- Differentiation primitives appear only in functions marked as differentiable.

Verification procedures SHOULD emit actionable diagnostics that reference both the IR location and
source span when available.

## Serialization

The canonical textual format uses S-expressions. Implementations MAY provide binary encodings for
performance but MUST support round-tripping through the textual form without loss of information.

A reference encoder/decoder exists in
[`cputer/mind/docs/ir/serialization`](https://github.com/cputer/mind/tree/main/docs/ir/serialization)
(informative).
