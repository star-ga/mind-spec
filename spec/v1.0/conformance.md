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

### Evidence-chain conformance (optional add-on, RFC 0016)

Implementations claiming **evidence-chain emission** (RFC 0016) MUST:

- Emit the chain as a Metadata-Attachment-Pair (MAP) epilogue per RFC 0014 (`mic@2.1`) and/or via
  the `0x4D`-sentinel binary form (`mic@3`, RFC 0021 step 2).
- Anchor `trace_hash` on the **canonical `mic@3` bytes** — `trace_hash = SHA-256(canonical mic@3
  bytes)`, the full-fidelity binary `IRModule` — per RFC 0016 GAP-1 (re-anchored 2026-05-31 after a
  collision audit found `mic@1` text can drop function-body semantics; supersedes the original GAP-1
  `mic@1`-text rule). Hashing on the `mic@1` textual form, on the `mic@2.x` binary form, or on any
  derivative serialisation is **non-conformant**.
- Emit the RFC 0021 key set when the chain is present:
  `evidence_chain.{determinism,schema=1,substrate,toolchain,trace_hash}` plus
  `evidence_chain.trace_hash_kind`. `evidence_chain.parent` is OPTIONAL.
  `evidence_chain.determinism` MUST be `"deterministic"` or `"nondeterministic"`.

**Signing status.** Default-emit conformance is **emission + hash anchoring**
(tamper-evident, unsigned). Opt-in signing (RFC 0016 Phase C) is shipped and is
**not** required for this add-on. Implementations MUST NOT describe a default
unsigned chain as "signed", and MUST NOT treat `mindc verify` passing without
`--signer-pubkey` as authorship verification.

See [`ir-stability.md`](./ir-stability.md) for the normative IR-canon contract.

## Required behaviour

For the profile(s) an implementation claims:

- **Pipeline completeness**: implementations MUST accept verified, canonical Core IR, perform
  autodiff as defined in [`autodiff.md`](./autodiff.md), and, where applicable, lower to the
  MLIR backend following [`mlir-lowering.md`](./mlir-lowering.md) rules.
- **Runtime semantics**: runtime behaviour MUST follow [`runtime.md`](./runtime.md), including the
  deterministic execution guarantees and GPU backend-selection error model (for GPU-profile claims).
- **Deterministic diagnostics**: verification failures, unsupported features, and backend selection
  errors MUST be reported via deterministic, stable diagnostics.

## Source test execution and module scope

> **Compiler integration update, pending release.** The `mindc test`
> implementation in compiler commit `eedcfb2c` implements the bounded source
> test behavior below, and compiler commits `953d7233`, `97c0d273`, `74004786`,
> `2575c1e9`, `a7f9520a` and `487dd5c7` implement the additions below to the
> extent stated in the implementation-coverage notes. None of these commits
> promotes the published compiler artifact or establishes native-backend
> conformance.

A source test runner MUST discover module-level test functions inside
transparent inline module blocks in depth-first source order. Function-local
test declarations MUST NOT enter that inventory. Multiple module-level
definitions with the same name are ambiguous when any is a test and MUST be
refused. A run that discovers no tests MUST NOT report successful verification.

For builds with project-import support, each imported function, constant and
qualified type MUST resolve to the exact defining module selected by the
manifest source closure. An ambiguous, missing or non-exported symbol MUST
fail test preparation rather than bind to an unrelated declaration with the
same short name. Bundled standard-library imports use explicit `std.*` paths;
dependencies' standard-library imports are part of the captured evaluator
closure. A bare import names a project module and does not imply `std.*`.

**Implementation coverage (informative, pending release).** On such builds the
reference runner applies that resolution rule to the dot spelling (`dep.f(x)`,
`dep.K`) and, from compiler commit `953d7233`, to the path spelling `dep::f(x)`,
`dep::K` and `crate::a::b::f(x)`, where the qualifier names a declared import by
its import name or by the full `use` path written with `::` separators. A path
to a non-exported symbol, and a standalone path import without a manifest, fail
test preparation; a path call with the wrong number of arguments is refused.
Enum-variant paths whose leading segment is a type (`Side::Left(3)`,
`Color::Red`) are not treated as imports and resolve as before. Commit
`953d7233` changes only the evaluator-side import capture, which `mindc test`
and the opt-in canonical source-lowering bridge read; the ordinary parse result
is unchanged. The ordinary parse of the path spelling for `mindc check` and
`mindc build` is described under imports and module-qualified references in
[`language.md`](./language.md#module-qualified-references) (`cd150ae7`).

Functions MUST read initialized module-level bindings from their defining
module. Caller-local bindings MUST NOT supply a missing global or override
the callee's module state. Arguments are evaluated in the caller's context,
then bound in the callee. A scalar argument replacing a tensor-named parameter
MUST NOT retain metadata from the shadowed tensor. On builds supporting
module-level loops, updates made by a loop MUST remain visible to helpers
called from that loop and after it completes.

Each test evaluation MUST isolate its mutable evaluator state from other
tests, including when workers are reused after an error. The reference
controls are `mindc_test_imports` and `mindc_test_nested_modules`. Their
standard-library digest test compares all expected digest bytes through a
project dependency; a passing digest calculation does not establish signing,
authorization, native artifact execution or cross-host byte identity.

A source test runner MUST give a value of a declared integer type the same
width and overflow behaviour that the implementation's compiled artifacts give
it, and MUST refuse a value it cannot materialise at a declared narrow width
rather than report it at a wider width. A narrow width here is any declared
integer width below 64 bits. This requirement is additive and targeted for
specification 1.7.0; this does not declare that release or promote an
unreleased compiler artifact.

**Implementation coverage (informative, pending release).** In the reference
implementation, compiled artifacts on the default MLIR build path wrap
two's-complement at the declared width
(see section 1 of [`determinism.md`](../../determinism.md)). The reference
evaluator behind `mindc test` wraps `i8`, `i16`, `i32`, `u8`, `u16` and `u32`
values, and module-local `type` aliases of them in `std-surface` builds, at the
declared width: signed widths truncate and sign-extend, unsigned widths mask.
The wrap applies at function return, at argument binding to a parameter, at
`let` and at reassignment of a binding declared with a narrow type, and at
struct-literal construction for scalar fields and for array or slice fields
with a narrow element type (`97c0d273`, `74004786`). For example,
`fn f() -> u8 { return 300 }` evaluates to 44 and
`fn g() -> i32 { return 50000 * 50000 }` to -1794967296; the compiler test
`evaluator_declared_width` records these as the compiled artifact's values.
Declarations of other types, including `i64`, `u64`, floating-point types and
`bool`, pass through unchanged. A value that cannot be materialised at a
declared narrow width, such as a string bound to a `u8` binding, is refused with
a diagnostic that names the declaration.

**Implementation coverage, arithmetic (informative, pending release).** In
`std-surface` builds the evaluator also re-wraps 8- and 16-bit intermediate `+`,
`-`, `*`, `/` and `%` results, and shift results, to the width inferred from the
operands, mirroring the compiled lowering (`2575c1e9`, `a7f9520a`): with
`a: u8 = 250`, `(a + 10) / 2` is 2 because `a + 10` wraps to 4 first, while an
operand that is a variable not declared with an 8- or 16-bit type (an `i32`,
`u32`, `i64` or `u64` variable included), or a cast to any other type (for
example `as i64` or `as i32`), leaves unmasked each operation that has it as an
operand, directly or through nested arithmetic; a narrow sub-expression that
does not contain it, such as `a + 10` in `(a + 10) / b` with `b: i64`, is still
re-wrapped. A shift whose left operand is 8- or 16-bit also masks the shift
count with the width minus one, so with `a: u8 = 1`, `a << 8` is 1. Known gaps,
where agreement with compiled artifacts is not claimed, include: 32-bit
intermediates are not re-masked by the evaluator; a field read through a
non-identifier receiver and an array element read by index are width-neutral in
intermediate arithmetic; a binding, parameter or return value of narrow-element
array or slice type is not narrowed by the evaluator (only struct fields are
narrowed element by element); fields of structs that are not registered in the
evaluated module are not narrowed at construction; signed 64-bit
`INT_MIN / -1` makes the evaluator panic (`mindc test` reports the test as
failed) where compiled output defines `INT_MIN`; and `x / 0` and `x % 0` are
evaluation errors where compiled output defines 0, except where the evaluator
treats an operand as `u64` (see section 1 of
[`determinism.md`](../../determinism.md)). Agreement is claimed only for the
covered cases. Commits `97c0d273`, `74004786`, `2575c1e9` and `a7f9520a` change
the evaluator only, and compiled artifacts are unchanged.

A source test runner MUST report a test during which an `assert` condition
evaluates to false as failed, and MUST report the assert's message when one is
written (the message may be written in the Core v1 form
`assert cond, "message"` or in the parenthesised form
`assert(cond, "message")`; the parenthesised form is additive and targeted for
specification 1.7.0; see
[`stdlib.md`](./stdlib.md#control-flow-and-assertions)). This is stricter than
the SHOULD for a runtime abort in that entry and applies to source test runners
only. This requirement is additive and targeted for specification 1.7.0; it
does not declare that release.

**Implementation coverage (informative, pending release).** The reference runner
reports such a test as `FAILED` and prints the message, for the bare spelling
`assert cond, "message"` and for the parenthesised spelling
`assert(cond, "message")` (`487dd5c7`); the parser reads the parenthesised pair
as the condition `cond` with that message. Any other parenthesised tuple
written directly as the condition, including `assert(cond, 9)` and a
three-element tuple, is refused at parse time; a condition that evaluates to a
tuple value (for example a variable bound to a tuple) is refused when
`mindc test` evaluates it. The compiler tests `assert_parenthesised_message`
and `mindc_test_evaluator_issues` cover this.

**Honest scope (informative).** At compiler commit `7831998b` the reference
evaluator has an open defect for floating-point comparisons (finding 15 of the
compiler independence audit, `docs/independence-audit-plan-20260925.md` in
`star-ga/mind`): a floating-point comparison (`f32` or `f64`, including a
comparison of a float with an integer) yields a float 1.0 or 0.0 that the
evaluator's truthiness rules do not handle. As a bare `if` condition or `match`
guard it is treated as true. Combined with `&&` or `||` it is treated as false,
so an `if` takes the else branch and an `assert` fails even when the condition
holds. `!` applied to it is refused. A `while` on such a bare condition does not
exit through its condition: it ends only by `return` or by the evaluator's
1,000,000-iteration cap, with an error, because `break` does not exit the loop
in this evaluator. Source-test verdicts, and value cells of the reference `mindc conformance`
runner (which executes cases through the same evaluator), are not conformance
evidence for programs with such a condition until it is fixed.

## Conformance verification

Conformance is evaluated by executing the published **golden test corpus** distributed with the
reference implementation in [`star-ga/mind`](https://github.com/star-ga/mind). The corpus encodes the
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
   - Note: trait-bound and general generic-instantiation tests apply only to implementations that
     ship those features; the reference implementation's executable subset (v0.10.x) implements a
     bounded single-type-parameter scalar generics slice and no traits (see
     [Types](./types.md#traits-and-generics)), so such tests are skip-documented there

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

- Error codes: at least one test per E-code cataloged in errors.md, including E6009

- Materialization tests: E6009 for a deterministic limit and an unrepresentable
  aggregate lowering operation; each refusal exits nonzero and leaves no
  runnable artifact

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
6. **Numeric precision**: Floating-point tolerance used for transcendental and vector-reduction results (MUST be ≤ 1e-6 for f32, ≤ 1e-12 for f64). Scalar IEEE-754 arithmetic (`+ − × ÷ √`) and integer/Q16.16 operations are bit-exact (0 tolerance) on the strict path; the tolerance applies only to transcendental / vector-reduction operations.

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
