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
> the **native-ELF backend** (the pure-MIND native emitter in `examples/mindc_mind`). The output of
> the native backend is a pure function of the source image it is given: the user sources plus the seed
> standard-library modules, in the fixed order of the committed std manifest. It is therefore
> deterministic-by-construction.
>
> The native backend is reached through `mindc build --backend native` since `52bd6d3b`. It is the
> default backend of `mindc build` since v0.10.3. `--backend mlir` or `[build] backend = "mlir"` selects
> the MLIR backend. `mindc` never changes the backend by itself. The published v0.10.2 refuses
> `--backend native` with `error[backend]`.
>
> The frozen compiler and the seed standard-library modules are embedded in the `mindc` binary.
> `MINDC_NATIVE_ELF` names another compiler in place of the embedded one (a test hook).
> `MINDC_STD_DIR` names a directory of std modules in place of the embedded copy.
>
> The native backend admits only a defined subset of programs (candidate `native-lane-v1`). It emits an
> x86-64 Linux executable only. A program outside that subset, or a host that is not x86-64 Linux, is
> refused by name (exit status 3, no artifact; see
> [Native backend refusals](#native-backend-refusals-informative)). There is no MLIR fallback.
>
> MLIR-text remains a first-class output for interoperability with the
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
  roadmap (see [Standard Library](./stdlib.md#numeric-precision)). Compiler `9c231f50`, part
  of v0.10.3 and later; it is not part of the published v0.10.2 artifact.

## Native backend refusals (informative)

This section records the reference implementation `mindc` v0.10.4. It is informative: it is not part of
Core v1, and another implementation MAY use other keys.

**Compiler mark.** The host runs a native compiler only when that compiler carries the lane mark
`nblane02`. A compiler with another mark, or with none (for example `nblane01`), is refused with one
message that names `nblane02` (`native.compiler_mark`). No image is written. The host does not judge the
program of such a compiler with a historical profile. The compiler that is embedded in `mindc` v0.10.4
carries `nblane02`.

**Refusal line.** The native compiler names each refusal in one line and exits with status 3 and no
artifact:

```
error[native-lane]: the program is outside candidate native-lane-v1 (<key>) at line L, column C of the composed user image. No artifact written.
```

A site in the std region says `in the std region.`

**Extern keys.** The native compiler alone judges an `extern "C"` declaration. The host types each
declaration and admits it whatever its name. The compiler refuses a declaration in this order:

| Order | Key | Name | Meaning |
|-------|-----|------|---------|
| 1 | 67 | `lane.extern.callconv` | the calling convention is not supported (`callconv(.win64)` is 67 even when the name has no row) |
| 2 | 64 | `lane.extern.unknown_symbol` | the name has no row (a `__mind_` name is 64) |
| 3 | 65 | `lane.extern.arity` | the parameter count differs from the row |
| 4 | 66 | `lane.extern.signature_mismatch` | a parameter or result type differs from the row |

A varargs marker, an `f64` parameter and a `u32` result on a name that has a row are 66. Twelve parameters on a
name that has a row are 65. On a name that has no row, each of them is 64. A parameter or result type that is not
a scalar of the registry (a struct, a `#[repr(C)]` struct, a type alias, a pointer to a struct) is judged like any
other width: 66, or 65 when the count differs. A defect that stands earlier in the source keeps its word. The
reason word of a refusal is `key * 4294967296 + site`, where the site is the byte offset of the declaration name
from the start of the composed image. The capability mark of the named refusals is `nblxk001`.

A second declaration of an extern with equal types, in one block or in several, is accepted. A declaration with
other types is refused.

The extern table of the native compiler has the rows 89 to 98: `readlink`, `bind`, `getsockname`, `sendto`,
`recvfrom`, `getenv`, `creat`, `poll`, `listen` and `getsockopt`. Each is bound through `libc.so.6` at
`GLIBC_2.2.5`. A declaration must spell the signature of its row exactly. The capability mark of these rows is
`nblibc03`.

**Loops and free.** The host does not refuse a `__mind_free` in a loop: the rule `lane.alloc.free_in_loop`
is removed. A bare `break` or `continue` in a seed body that a loop calls is refused with
`lane.source.loop_exit_scope`.

**Strings.** The host types `String`, a string literal and a field read as the i64 word. The keys
`lane.source.string` and (for a field read) `lane.source.struct` are no longer raised by the host. A
field write and every other type name (`u8`, `i16`, `usize` and the rest) are still refused. A `let` of any
type, or a loop binder, with the name of a `String` parameter makes that name a non-`String` in its scope: a
field read of it is refused with `lane.source.struct`. The `.addr` and `.len` of a `String` parameter are
accepted in a pointer cast (`p.addr as *const u8`); `.cap`, another receiver and a shadowing `let` are not. A string
literal with a raw line feed or an escape that the lexer does not know is refused with
`lane.string.raw_newline` or `lane.string.escape` at its own position. The string family is judged
before the extern family. Of two refused constructs, the smaller position wins.

**String literal handle.** The handle `{addr, len, cap = 0}` of a string literal is written at compile
time into the read-only literal segment. A store through it faults. A literal that is evaluated in a loop
allocates nothing. The read-only literal window is 8 MiB. It counts the literal bytes, the alignment gap (0 to 7
bytes) and the 24 handle bytes of every literal site. The compiler refuses a program that passes it.

**Memory profiles.** `mindc build --backend native --native-profile <default|bounded>` (v0.10.3) selects the
memory layout of the image. `default` has a 1 GiB arena and a 4 GiB stack. `bounded` has a 768 MiB arena, a 1 MiB
unmapped guard and a 384 MiB stack, and its images load under `RLIMIT_AS` = 2 GiB. An allocation
past the arena cap in a bounded image ends with `error: native arena exhausted` and exit status 70. In v0.10.4 a
default-profile image whose source frees at a loop position takes a free-list runtime on the 1 GiB arena
(freed blocks are reused, a full arena ends the same way); every other `default`-profile image keeps the bump allocator and its bytes.
The line `// mind: native_alloc = bump` in the leading comment block keeps the bump allocator.

**Group intrinsic rows.** The native compiler has three AVX2 group rows. Each returns 0 and writes
memory. Kind 87 `__mind_group_bank_i64(ptrs, bank, plane, pixels, group)` takes five i64 arguments. Kind 88
`__mind_group_acc32_i64(out, bank, off, pos, neg, init)` takes six. Kind 89 `__mind_group_accrows_i64(desc)`
takes one descriptor and walks many accumulator rows in one call: each row adds and subtracts bank rows into
an accumulator row. Kinds 87 and 88 are in v0.10.3. Kind 89 and the complete set of modes are in v0.10.4.
Kinds 87 and 88 probe the CPU and take a scalar path without AVX2. Kind 89 has one AVX2 path (ymm0 to ymm7)
behind the ymm entry guard of the program. A program that calls none of the three rows compiles to the same
bytes as before.

The argument bits are as follows. A reserved bit that is set stops the program with a trap (`ud2`, SIGILL)
before any store.

| Kind | Argument bits | Meaning |
| ---- | ------------- | ------- |
| 87 | `group` bit 4 | Skips the CPU probe and takes the AVX2 path. The group used is `group & 15`. |
| 87 | `group` bit 5 | Stores the low 32 bits of each code (4-byte rows). |
| 87 | `group` bits 5 and 6 | Reads u32 channels, 8 pixels per vector step. |
| 87 | `group` bit 6 alone, bits 7 to 63 | Trap. |
| 88 | `init` in [2^62, 2^63) | Skips the CPU probe, clears bit 62 and decides "keep" on the cleared value. |
| 88 | `init` above 3 after that arm (bits 2 to 61, bit 63, every negative value) | Trap. |
| 89 | `desc[7]` bit 0 | Keeps or adds to `out`. |
| 89 | `desc[7]` bit 2 | i32 walk over a 4-byte bank (64 lanes). Bits 63 to 32 hold the segment bound. A bound of 2^31 or more takes an exact i64 fallback. |
| 89 | `desc[7]` bit 3 | Two terms per loop step. |
| 89 | `desc[7]` bit 4 | u16 lane offsets. |
| 89 | `desc[7]` bit 5 | Epilogue tail over the stored rows. `desc[8]` holds the row records, `desc[9]` the trip flag that the call writes, `desc[10]` the limit. |
| 89 | `desc[7]` bit 7 | Finishes each row in registers instead. `desc` is i64[15], `desc[11]` to `desc[14]` give the src and dst rows and their steps, and the out row is not written. |
| 89 | `desc[7]` bit 8 | src and dst are u32. Only with bit 5 or bit 7, and `desc[10]` must fit in 32 bits. |
| 89 | bit 1 with bit 2, 3 or 4; bit 6; bits 9 to 31; bits 63 to 32 without bit 2; bit 8 without bit 5 or bit 7 | Trap. |

The descriptor fields of kind 89 are `out, out_step, bank, off, starts, starts_step, rows, init`, and the
mode bits are in `desc[7]`. For the i32 walk every code must fit in i32. The bound field is written as
`min(B, 0xFFFFFFFF)`, and with a bound below 2^31 every partial sum must stay in i32. An overlap that the
module headers of the compiler do not allow is an error of the caller.

The caller's duty: a program that sets a probe-skip bit must also hold a guarded row (any ymm row or kind 89).
Without one, a CPU without AVX2 stops at the first VEX instruction (SIGILL, exit status 132) and prints no
`isa.avx2_missing` line.

Changed in v0.10.4: kinds 87 and 88 trap on a reserved argument bit. The released v0.10.3 did not. For such a
`group`, kind 87 read and wrote nothing, and kind 88 took such an `init` as a zero start (`acc[i] = 0`) and ran to
its end. A program that passes such a value and exited 0 on v0.10.3 now ends with SIGILL. Pass only the bits that
the table lists. The argument bits and the descriptor fields are also in
[`docs/compiler/NATIVE_LANE_PROFILE.md`](https://github.com/star-ga/mind/blob/v0.10.4/docs/compiler/NATIVE_LANE_PROFILE.md)
of the compiler repository.
