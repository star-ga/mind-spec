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

# Conformance (Normative)

This chapter defines how implementations claim **Core v1** conformance. Conformance is evaluated at
an **implementation** level: an implementation MAY be a compiler, runtime, or integrated system that
consumes Core v1 surface language and IR, executes the defined pipelines, and surfaces deterministic
results and errors. Individual components (for example, a parser) do not claim conformance in
isolation.

## Profiles

Core v1 defines two conformance profiles:

- **Core v1 CPU baseline** (required): an implementation MUST support the full Core v1 pipeline from
  surface language through Core IR, canonical autodiff, MLIR lowering for CPU backends, and runtime
  execution semantics for `DeviceKind::Cpu` / `BackendTarget::Cpu` as defined in the normative
  chapters of this specification.
- **Core v1 GPU profile** (optional): an implementation MAY additionally support GPU execution. This
  profile extends the CPU baseline with the GPU-specific device and backend rules in
  [`runtime.md`](./runtime.md#devices-and-backends), including `DeviceKind::Gpu`,
  `BackendTarget::Gpu`, and the backend-selection error model.

Implementations MAY claim conformance to only the CPU baseline or to both CPU baseline and GPU
profile. Claims MUST clearly state which profile(s) are implemented.

## Required behaviour

For the profile(s) an implementation claims:

- **Pipeline completeness**: implementations MUST accept verified, canonical Core IR, perform
  autodiff as defined in [`autodiff.md`](./autodiff.md), and, where applicable, lower to the
  MLIR backend following [`mlir-lowering.md`](./mlir-lowering.md) rules.
- **Runtime semantics**: runtime behaviour MUST follow [`runtime.md`](./runtime.md), including the
  deterministic execution guarantees and GPU backend-selection error model (for GPU-profile claims).
- **Deterministic diagnostics**: verification failures, unsupported features, and backend selection
  errors MUST be reported via deterministic, stable diagnostics.

## Conformance verification

Conformance is evaluated by executing the published **golden test corpus** distributed with the
reference implementation in [`cputer/mind`](https://github.com/cputer/mind). The corpus encodes the
behavioural contracts described in this specification across parsing, IR verification, autodiff,
MLIR lowering, runtime execution, and GPU backend selection. Other implementations MAY re-use or
port the corpus to verify their claimed profile(s). No specific CI or tooling is mandated; the
underlying behavioural contracts are normative, while the corpus is the public mechanism for
verifying them.

### Test corpus structure

The golden test corpus is organized into categories corresponding to specification chapters:

1. **Lexical tests** (`tests/lexical/`)
   - Valid and invalid tokens, identifiers, literals, comments
   - UTF-8 handling, escape sequences, numeric literal formats
   - Expected: lexer produces correct token stream or emits E1xxx errors

2. **Type checking tests** (`tests/type_checker/`)
   - Type inference, dtype compatibility, trait bounds
   - Function signatures, generic instantiation
   - Expected: type checker accepts valid programs, rejects with E2xxx errors

3. **Shape inference tests** (`tests/shapes/`)
   - Broadcasting examples (compatible and incompatible shapes)
   - Reduction shape rules, MatMul batch broadcasting, Conv2d output shapes
   - Expected: shape checker computes correct output shapes or emits E3xxx errors

4. **IR verification tests** (`tests/ir_verification/`)
   - SSA property validation, operand def-use checks
   - Instruction-specific verification (permutation validity, element counts, channel matches)
   - Expected: verifier accepts valid IR, rejects with E4xxx errors

5. **Autodiff tests** (`tests/autodiff/`)
   - Gradient computation for all differentiable operations
   - Broadcasting in gradients, reduction gradient expansion, matmul/conv2d gradients
   - Expected: autodiff produces correct gradient modules or emits E5xxx errors
   - Validation: numerical gradient checking where applicable

6. **Runtime execution tests** (`tests/runtime/`)
   - Forward execution for all Core v1 operations
   - Numeric correctness (within floating-point tolerances)
   - Edge cases: rank-0 scalars, large tensors, boundary conditions
   - Expected: runtime produces correct output values

7. **Backend selection tests** (`tests/backend/`)
   - CPU backend availability (always succeeds for CPU profile)
   - GPU backend availability and graceful failure (for GPU profile claims)
   - Expected: correct backend or E6002 error with diagnostic

### Test format

Each conformance test is a structured file containing:

```yaml
# test_name.yaml
description: "Human-readable test description"
category: "lexical" | "type_checker" | "shapes" | "ir_verification" | "autodiff" | "runtime" | "backend"
profile: "cpu" | "gpu"  # Minimum profile required

input:
  source: |
    # MIND source code or IR text
  # OR
  ir_module: |
    # Pre-constructed IR module

expected:
  status: "success" | "error"

  # For success cases:
  output:
    ir: |
      # Expected canonical IR (for compilation tests)
    # OR
    gradient_module: |
      # Expected gradient IR (for autodiff tests)
    # OR
    result:
      dtype: "f32"
      shape: [2, 3]
      values: [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
      tolerance: 1e-6  # Optional per-test tolerance (MUST NOT exceed global maximum tolerance)

  # For error cases:
  error:
    code: "E3001"  # Error code from errors.md
    message_contains: "Broadcasting failed"  # Substring that MUST appear
    location:
      line: 10
      column: 15
```

Implementations MAY use alternative test formats internally but MUST be able to demonstrate
conformance on tests semantically equivalent to the reference corpus.

### Coverage requirements

For **CPU baseline** conformance, implementations MUST pass tests covering:

- All Core v1 operations from ir.md:
  * Constants: ConstI64, ConstF32, ConstF64, ConstTensor
  * Binary ops: Add, Sub, Mul
  * Reductions: Sum, Mean (with all keepdims and axes combinations)
  * Shape ops: Reshape, Transpose, ExpandDims, Squeeze
  * Indexing: Index, Slice, Gather
  * Linear algebra: Dot (all rank combinations), MatMul (batched), Conv2d (NHWC)
  * Activations: Relu, Neg, Exp, Log

- Broadcasting rules: scalar, leading dimension, multi-dimensional, rank mismatches, error cases

- Autodiff gradients: forward and backward for all differentiable operations

- Error codes: at least one test per E-code from E1001-E6008 in errors.md

- Edge cases: rank-0 scalars, empty axes (full reduction), single-element tensors

For **GPU profile** conformance, implementations additionally MUST pass:

- All CPU baseline tests executed on GPU backend
- Backend selection tests demonstrating E6002 error when GPU unavailable
- GPU-specific numeric precision tests (if GPU numerics differ from CPU)

### Test execution

Conformance test runners MUST:

1. **Parse test files**: load test description, input, and expected output
2. **Execute pipeline**: run the implementation on the test input
3. **Compare results**:
   - For success cases: verify output matches expected (IR text match, numeric values within tolerance)
   - For error cases: verify error code matches and message contains expected substring
4. **Report**: produce pass/fail per test with diff for failures

Implementations MAY skip tests for unimplemented optional features (e.g., MLIR lowering) but MUST
clearly document skipped tests and rationale. Skipped tests do NOT count toward pass rate.

### Pass criteria

An implementation conforms to a profile if:

- **100% pass rate** on all non-skipped tests for that profile
- No crashes, hangs, or undefined behavior during test execution
- Deterministic results: running the same test multiple times produces identical results
- Error messages include required context from errors.md

Partial conformance (e.g., 95% pass rate) is NOT recognized. Implementations MAY publish their
pass rate during development but MUST NOT claim conformance until reaching 100%.

### Golden test corpus versioning

The golden test corpus is versioned with the specification:

- **Specification version**: Core v1.0, Core v1.1, etc.
- **Corpus version**: Matches specification version
- Corpus MAY add new tests in minor versions (v1.0 → v1.1) without removing tests
- Corpus MUST NOT change expected outputs for existing tests in minor versions
- Major versions (v1.x → v2.0) MAY change or remove tests

Implementations claiming "Core v1 conformance" MUST specify which corpus version they tested against
(e.g., "Core v1.0 conformance per corpus v1.0.5").

## Compliance claims

Implementations claiming conformance MUST publish:

1. **Profile(s)**: CPU baseline, GPU profile, or both
2. **Corpus version**: Exact version of golden test corpus used (e.g., v1.0.5)
3. **Test results**: Pass/fail report for all tests (or link to public CI)
4. **Skipped tests**: List of skipped tests with rationale (if any)
5. **Deviations**: Any known deviations from specification (SHOULD be zero for conformance claim)
6. **Numeric precision**: Floating-point tolerance used (MUST be ≤ 1e-6 for f32, ≤ 1e-12 for f64)

### Compliance statement template

```text
[Implementation Name] claims Core v1 [CPU baseline | GPU profile] conformance.

- Specification version: Core v1.0
- Test corpus version: v1.0.5
- Test execution date: 2025-12-18
- Total tests: 487
- Passed: 487
- Failed: 0
- Skipped: 0

Numeric tolerances: f32=1e-6, f64=1e-12

Link to test results: [URL to CI or test report]
```

### Re-certification

Implementations SHOULD re-certify conformance when:

- Specification minor version updates (v1.0 → v1.1)
- Corpus adds new tests
- Implementation changes significantly (major version, refactor)

Re-certification is NOT required for:

- Implementation bug fixes that don't affect conformance
- Performance improvements
- Internal refactoring without behavioral changes

## Non-conforming implementations

Implementations that do not meet 100% pass criteria MAY describe themselves as:

- "Core v1 compatible" (instead of "conformant")
- "Partially implements Core v1" with pass percentage
- "Based on Core v1 specification"

Such implementations MUST NOT claim "conformance" or use the term "conformant" in documentation,
marketing materials, or public statements.
