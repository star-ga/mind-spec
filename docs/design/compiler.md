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

# Compiler Architecture (Informative)

> **Status:** Stable
> **Last updated:** 2025-12-19
> **Specification reference:** [Core v1 Overview](../../spec/v1.0/overview.md)

This document describes the architecture of a conforming MIND compiler implementation.
It provides guidance for implementers and context for understanding the normative
specification chapters.

---

## Pipeline Overview

A MIND compiler transforms source code through several well-defined stages:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MIND Compilation Pipeline                          │
└─────────────────────────────────────────────────────────────────────────────┘

   Source Code (.mind)
         │
         ▼
   ┌─────────────┐
   │   Lexer     │  → Tokens
   │  (E1xxx)    │     Reference: grammar-lexical.ebnf
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │   Parser    │  → AST
   │             │     Reference: grammar-syntax.ebnf
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │    Type     │  → Typed AST
   │   Checker   │     Reference: language.md, types.md
   │  (E2xxx)    │
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │   Shape     │  → Shape-annotated AST
   │  Inference  │     Reference: shapes.md
   │  (E3xxx)    │
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │  IR Lowering│  → Core IR Module
   │             │     Reference: ir.md
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │ Verification│  → Verified IR
   │  (E4xxx)    │     Reference: ir.md#verification
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │Canonicalize │  → Canonical IR
   │             │     Reference: ir.md#canonicalisation
   └─────────────┘
         │
         ├───────────────────────┐
         ▼                       ▼
   ┌─────────────┐         ┌─────────────┐
   │  Autodiff   │         │    MLIR     │
   │  (E5xxx)    │         │  Lowering   │
   └─────────────┘         └─────────────┘
         │                       │
         ▼                       ▼
   Gradient Module          MLIR Module
         │                       │
         └───────────┬───────────┘
                     ▼
              ┌─────────────┐
              │   Runtime   │  → Execution
              │  (E6xxx)    │     Reference: runtime.md
              └─────────────┘
```

## Stage Details

### 1. Lexical Analysis (Lexer)

Converts source text to tokens following [`grammar-lexical.ebnf`](../../spec/v1.0/grammar-lexical.ebnf).

**Inputs:** UTF-8 source text
**Outputs:** Token stream
**Errors:** E1001-E1006 (lexical errors)

Key responsibilities:
- Unicode handling (XID_Start, XID_Continue for identifiers)
- Numeric literal parsing (decimal, binary, hex, float)
- String literal and escape sequence processing
- Comment filtering

### 2. Parsing

Builds an Abstract Syntax Tree from tokens per [`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf).

**Inputs:** Token stream
**Outputs:** Untyped AST
**Errors:** Syntax errors (parse failures)

Key responsibilities:
- Operator precedence (see [`language.md`](../../spec/v1.0/language.md))
- Expression and statement structure
- Module and function declarations

### 3. Type Checking

Validates and infers types according to the type system rules.

**Inputs:** Untyped AST
**Outputs:** Typed AST with dtype annotations
**Errors:** E2001-E2007 (type errors)

Key responsibilities:
- Dtype inference and validation
- Binary operation dtype matching
- Function call arity and type checking
- Trait bound verification

### 4. Shape Inference

Computes tensor shapes and validates shape compatibility.

**Inputs:** Typed AST
**Outputs:** Shape-annotated AST
**Errors:** E3001-E3008 (shape errors)

Key responsibilities:
- Broadcasting rule application
- Reduction shape computation
- MatMul/Conv2d dimension checking
- Reshape element count validation

### 5. IR Lowering

Translates surface language to Core IR following [`ir.md`](../../spec/v1.0/ir.md).

**Inputs:** Shape-annotated AST
**Outputs:** Core IR module

Key responsibilities:
- SSA-style value numbering
- Operator to instruction mapping
- Tensor metadata encoding

### 6. Verification

Validates IR well-formedness per [`ir.md#verification`](../../spec/v1.0/ir.md#verification).

**Inputs:** Core IR module
**Outputs:** Verified IR (unchanged if valid)
**Errors:** E4001-E4006 (verification errors)

Key responsibilities:
- Def-use chain validation
- Shape/dtype constraint checking
- Operation-specific verification

### 7. Canonicalization

Normalizes IR to canonical form for reproducible downstream processing.

**Inputs:** Verified IR
**Outputs:** Canonical IR

Key responsibilities:
- Operand ordering for commutative operations
- Optional constant folding
- Dead code elimination

### 8. Autodiff

Generates gradient modules per [`autodiff.md`](../../spec/v1.0/autodiff.md).

**Inputs:** Canonical IR
**Outputs:** Forward + gradient IR modules
**Errors:** E5001-E5004 (autodiff errors)

Key responsibilities:
- Reverse-mode differentiation
- Gradient rule application
- VJP computation

### 9. MLIR Lowering (Optional)

Lowers to MLIR dialects per [`mlir-lowering.md`](../../spec/v1.0/mlir-lowering.md).

**Inputs:** Canonical IR
**Outputs:** MLIR module

### 10. Runtime Execution

Executes IR on CPU or GPU per [`runtime.md`](../../spec/v1.0/runtime.md).

**Inputs:** Canonical IR or lowered representation
**Outputs:** Tensor results
**Errors:** E6001-E6008 (runtime errors)

## Data Flow Diagram

```
                    ┌─────────────────────────────────────────┐
                    │              Core IR Module             │
                    │  ┌───────────────────────────────────┐  │
                    │  │ Inputs: %0, %1, ...               │  │
                    │  │ Instructions: [CoreOperation, ...]│  │
                    │  │ Outputs: %n, ...                  │  │
                    │  └───────────────────────────────────┘  │
                    └─────────────────────────────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           │                            │                            │
           ▼                            ▼                            ▼
   ┌───────────────┐           ┌───────────────┐           ┌───────────────┐
   │   Autodiff    │           │ Optimization  │           │ Serialization │
   │   Transform   │           │    Passes     │           │   (textual)   │
   └───────────────┘           └───────────────┘           └───────────────┘
           │                            │                            │
           ▼                            ▼                            ▼
   Gradient Module            Optimized Module              .ir file
```

## Error Handling Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Error Handling Flow                                │
└─────────────────────────────────────────────────────────────────────────────┘

   Compiler Stage                    Error Detection              Error Code
   ─────────────                    ───────────────              ──────────
   Lexer          ───────────────▶  Invalid UTF-8, tokens   ───▶  E1xxx
   Parser         ───────────────▶  Syntax violations       ───▶  (parse err)
   Type Checker   ───────────────▶  Type mismatches         ───▶  E2xxx
   Shape Checker  ───────────────▶  Shape incompatibility   ───▶  E3xxx
   IR Verifier    ───────────────▶  IR malformation         ───▶  E4xxx
   Autodiff       ───────────────▶  Undifferentiable ops    ───▶  E5xxx
   Runtime        ───────────────▶  Execution failures      ───▶  E6xxx

   All errors include:
   - Error code (stable, versioned)
   - Source location (line, column)
   - Contextual message (unstable text)
   - Suggested fix (where applicable)
```

## Implementation Guidelines

### Determinism

All compiler stages MUST be deterministic:
- Same input → same output (IR, errors, diagnostics)
- No dependence on environment, time, or random state
- Reproducible across runs and machines

### Incremental Compilation

Implementations MAY support incremental compilation by:
- Caching intermediate representations
- Tracking file dependencies
- Invalidating affected modules on change

### Parallel Compilation

Stages MAY be parallelized where data dependencies allow:
- Lexing/parsing of independent modules
- Type checking within non-dependent scopes
- Shape inference for independent operations

### Memory Management

Core IR uses a linear value numbering scheme. Implementations SHOULD:
- Avoid copying IR unnecessarily
- Use arena allocation for AST/IR nodes
- Release intermediate representations after use

---

[Back to Design Index](./index.md) | [Spec Index](../spec/index.md)
