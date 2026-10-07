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

# MLIR Lowering (Normative — Downstream Interchange)

> **Backend role (pivot 2026-06-24):** The MLIR-text backend is the **downstream-interchange and
> exotic-chip-reach backend**, not the normative self-host target. The normative self-host target is
> the **native-ELF backend** (the pure-MIND native emitter in `examples/mindc_mind`; on compiler main
> it is reached through `mindc build --backend native` (`52bd6d3b`, pending release); the bridge reads
> the frozen compiler from `examples/mindc_mind/testdata/selfhost_loop/stage1.elf` and the seed modules
> from `std/`, both relative to the working directory, unless `MINDC_NATIVE_ELF` / `MINDC_STD_DIR` are
> set; the published v0.10.2 refuses `--backend native` with `error[backend]`), whose output is a pure
> function of the source image it is given (the user sources plus the seed standard-library modules, in
> the fixed order of the committed std manifest) and is therefore deterministic-by-construction. It
> admits only a frozen subset of programs and emits a static x86-64 executable only; programs outside
> that subset are refused with `error[backend-native]` (exit status 3 at the bridge's admission fence; a
> program the fence admits can still be rejected by the frozen compiler with its own non-zero status)
> and there is no MLIR fallback. MLIR-text remains a first-class output for interoperability with the
> LLVM/MLIR ecosystem and for reaching accelerator targets (TPU, NPU, custom silicon) available in the
> commercial `mind-runtime` under license. Both backends are supported and maintained; only the
> self-host designation differs.

This chapter specifies the deterministic lowering of canonical Core IR into MLIR for the feature-gate
that ships with the public compiler. The rules cover only the stable, publicly implemented subset.

## Scope and prerequisites

- Lowering is **feature-gated** (e.g. via an `mlir-lowering` feature flag in the compiler).
- The input module MUST be **verified and canonicalised** per [Core IR](./ir.md).
- Lowering produces deterministic MLIR textual IR suitable for snapshot testing and downstream
  consumption. Minor changes may occur between MIND versions but are stable within a release.
- Core v1 MLIR lowering rules target the CPU backend. Any GPU-specific MLIR dialects or pipelines are
  experimental and outside the scope of this chapter (see [Runtime](./runtime.md#gpu-backends-open-core-not-production-shipped)).

## Lowering patterns

### Constants

- Scalars and tensors lower to `arith.constant` with explicit MLIR tensor types.

### Tensor allocation and fill

- Zero-initialised tensors are represented using `tensor.empty` followed by `linalg.fill` fed by a
  separate `arith.constant` for the fill value.

### Matrix multiplication

- `MatMul` lowers to `linalg.matmul` in **destination-passing style**:
  - A `tensor.empty` destination is created with the inferred result shape.
  - The destination is passed via `outs` and the filled tensor is the operation result.

### Convolution

- `Conv2d` lowers to `linalg.conv_2d_nhwc_hwcf` with **NHWC** input and **HWCF** filter.
- Destination-passing mirrors matmul: allocate with `tensor.empty`, feed through `outs`.
- Verification ensures input and filter channels match before lowering.

### Elementwise and reductions

- Elementwise `BinOp` instructions lower to MLIR arithmetic ops on broadcasted tensors using MLIR
  canonical broadcasting utilities.
- `Sum` and `Mean` lower to reduction patterns that preserve `keepdims` semantics; `Mean` divides by
  the reduced element count explicitly.

## Determinism and stability

- Given canonical IR, the emitted MLIR text is **deterministic**. Ordering follows IR instruction
  order and canonical operand ordering rules.
- The textual form is stable **within a compiler release**. Future releases MAY evolve op selections
  or attributes but MUST preserve semantics for the defined Core v1 operations.
- **Reference build driver and library-routine names (informative).** When the reference build driver
  compiles emitted MLIR into an object, a shared library or an executable through the external LLVM
  toolchain, it marks every `func.func` definition with the passthrough attribute `"nobuiltin"`: it
  adds `attributes {passthrough = ["nobuiltin"]}`, or merges the entry into an `attributes`
  dictionary the header already has. The aim is that LLVM does not treat a MIND function named like a
  C library routine (for example `pow`, `sin` or `exp`) as that routine, and does not replace a call
  to it with a host routine or a folded constant (see
  [Determinism](../../determinism.md#5-compiler-optimizations-cannot-change-observable-behaviour)).
  The evidence is one runtime test with three probe names (`pow`, `sin`, `exp`) built as a shared
  library; it is not an audit of every libm symbol. Declarations are untouched, and marking an
  already-marked definition changes nothing. The marking is applied by the build driver, not by the
  lowering emitter: the text printed by `mindc --emit-mlir` does not carry the attribute, so the
  deterministic textual-IR rule above is unaffected. It applies only on that artifact-build path. The
  feature-gated `mlir-exec`, `mlir-jit` and `mlir-gpu` execution modes of the `mind` binary do not
  apply it, and the native-ELF backend does not invoke the LLVM toolchain. It does not by itself make
  transcendental functions correctly rounded or bit-identical across substrates, which remains
  roadmap (see [Standard Library](./stdlib.md#numeric-precision)). Compiler `9c231f50`, pending
  release; it is not part of the published v0.10.2 artifact.
