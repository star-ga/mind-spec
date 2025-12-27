<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Implemented RFCs

> **Status:** Stable
> **Last updated:** 2025-12-19

This page lists RFCs that have been accepted and merged into the Core v1
specification. Each entry links to the relevant specification chapter.

---

## Core v1.0 RFCs

The following RFCs were implemented as part of the initial Core v1.0 release:

### RFC-0001: Core IR Instruction Set

**Specification:** [ir.md](../../spec/v1.0/ir.md)

Defines the Core IR instruction set including:
- Constants (ConstI64, ConstF32, ConstF64, ConstTensor)
- Binary operations (Add, Sub, Mul)
- Reductions (Sum, Mean)
- Shape manipulation (Reshape, Transpose, ExpandDims, Squeeze)
- Indexing (Index, Slice, Gather)
- Linear algebra (Dot, MatMul, Conv2d)
- Activations (Relu, Neg, Exp, Log)

---

### RFC-0002: Broadcasting Semantics

**Specification:** [shapes.md](../../spec/v1.0/shapes.md)

Defines tensor broadcasting rules:
- Shape alignment from trailing dimensions
- Dimension extension for size-1 dimensions
- Broadcasting failure conditions (E3001)
- Interaction with reductions and MatMul

---

### RFC-0003: Reverse-Mode Autodiff

**Specification:** [autodiff.md](../../spec/v1.0/autodiff.md)

Defines automatic differentiation:
- VJP (Vector-Jacobian Product) as primitive
- Gradient rules for all Core IR operations
- Broadcasting gradient handling
- Error conditions (E5xxx)

---

### RFC-0004: Error Code Catalog

**Specification:** [errors.md](../../spec/v1.0/errors.md)

Defines structured error reporting:
- Error categories (E1xxx-E6xxx)
- Required diagnostic context
- Error message format
- Stable error codes across versions

---

### RFC-0005: Standard Library

**Specification:** [stdlib.md](../../spec/v1.0/stdlib.md)

Defines the standard library modules:
- `core` — Fundamental types and assertions
- `math` — Scalar mathematical functions
- `tensor` — Tensor construction and manipulation
- `diff` — Autodiff entry points
- `io` — Console I/O for debugging

---

### RFC-0006: Conformance Testing

**Specification:** [conformance.md](../../spec/v1.0/conformance.md)

Defines conformance verification:
- CPU baseline and GPU profile
- Test corpus structure (YAML format)
- Coverage requirements
- Pass criteria (100% required)

---

### RFC-0007: FFI Specification

**Specification:** [ffi.md](../../spec/v1.0/ffi.md)

Defines foreign function interface:
- C ABI compatibility
- Python, C++, Rust bindings
- Memory management across language boundaries
- Tensor data sharing (zero-copy where possible)

---

### RFC-0008: Versioning Policy

**Specification:** [versioning.md](../../spec/v1.0/versioning.md)

Defines versioning and stability:
- Semantic Versioning 2.0.0
- Stability levels (Stable, Evolving, Unstable)
- Deprecation policy
- Compatibility guarantees

---

## Summary

| RFC | Title | Spec Chapter | Key Features |
|-----|-------|--------------|--------------|
| 0001 | Core IR | ir.md | 20+ instructions, SSA model |
| 0002 | Broadcasting | shapes.md | NumPy-compatible rules |
| 0003 | Autodiff | autodiff.md | Reverse-mode, VJP |
| 0004 | Errors | errors.md | 40+ error codes |
| 0005 | Stdlib | stdlib.md | 5 modules, 50+ functions |
| 0006 | Conformance | conformance.md | Test format, profiles |
| 0007 | FFI | ffi.md | C/Python/Rust bindings |
| 0008 | Versioning | versioning.md | SemVer, deprecation |

---

## Core v1.1 RFCs

The following RFCs were implemented as part of Core v1.1:

### RFC-0001: MindIR Compact (MIC)

**Specification:** [0001-mindir-compact.md](../../design/rfcs/0001-mindir-compact.md)

Defines token-efficient IR serialization for AI agents:
- Line-oriented format (one node per line)
- 4x token reduction vs JSON
- Deterministic canonicalization
- Security limits (input size, node count, shape dims)
- Thread-safe string interning with bounded capacity
- Lossless roundtrip: `parse(emit(ir)) == ir`

---

### RFC-0002: Mind AI Protocol (MAP)

**Specification:** [0002-ai-protocol.md](../../design/rfcs/0002-ai-protocol.md)

Defines compiler-in-the-loop protocol for AI agents:
- Request-response protocol over stdin/stdout/TCP
- Structured diagnostics with fix suggestions
- Incremental patching (insert, delete, replace)
- Security modes (no_io, no_unsafe, pure_only)
- Poison-safe session management

---

## Summary

| RFC | Title | Spec Chapter | Key Features |
|-----|-------|--------------|--------------|
| 0001 | Core IR | ir.md | 20+ instructions, SSA model |
| 0002 | Broadcasting | shapes.md | NumPy-compatible rules |
| 0003 | Autodiff | autodiff.md | Reverse-mode, VJP |
| 0004 | Errors | errors.md | 40+ error codes |
| 0005 | Stdlib | stdlib.md | 5 modules, 50+ functions |
| 0006 | Conformance | conformance.md | Test format, profiles |
| 0007 | FFI | ffi.md | C/Python/Rust bindings |
| 0008 | Versioning | versioning.md | SemVer, deprecation |
| **MIC** | MindIR Compact | design/rfcs/0001 | Token-efficient IR format |
| **MAP** | Mind AI Protocol | design/rfcs/0002 | Compiler-in-the-loop |

---

[Back to RFC Index](./index.md) | [Active Proposals](./active.md)
