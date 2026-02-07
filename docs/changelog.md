# Changelog

All notable changes to the MIND Language Specification are documented here.

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.2] - 2026-02-07

### Milestone: v0.2.0 Performance Specification Update (15× parser speedup)

Updated performance benchmarks to reflect v0.2.0 hand-written recursive descent parser.

### Changed

- **Performance benchmarks** - Updated with v0.2.0 criterion results:
  - scalar_math: 1.77 µs (was 26 µs, **14.7× faster**)
  - matmul operations: 2.8-2.9 µs (was 45-46 µs, **15.6× faster**)
  - New benchmarks: tensor_ops (4.75 µs), reductions (2.92 µs), reshape_ops (2.80 µs)
  - Added compilations/sec column: 347,000+ compilations per second

- **Version history table** - Added v0.2.0 entry:
  - v0.2.0: 1.77-2.84 µs, 347,000 compilations/sec (hand-written recursive descent)

- **Framework comparisons** - Updated all speedup calculations:
  - vs PyTorch 2.0: ~1,200,000-1,800,000× faster
  - vs Mojo 0.25.7: ~321,000-513,000× faster

---

## [1.1.1] - 2026-02-04

### Milestone: Performance Specification Update (v0.1.7)

Updated performance benchmarks and compiler targets to reflect production v0.1.7 measurements.

### Changed

- **Performance benchmarks** - Updated with v0.1.7 verified results:
  - scalar_math: 26 µs (was 25 µs)
  - matmul operations: 45-46 µs (was 52-55 µs, **-18% improvement**)
  - Parser optimization: Reordered `choice()` combinator for faster parsing

- **Version history table** - New section documenting benchmark progression:
  - Baseline (Dec 2025): 21-37 µs (minimal parser)
  - v0.1.6: 26-55 µs (full typed tensors)
  - v0.1.7: 26-46 µs (parser optimization)

- **Framework comparisons** - Updated all speedup calculations:
  - vs PyTorch 2.0: ~77,000-122,000× faster
  - vs Mojo 0.25.7: ~20,000-35,000× faster
  - vs JAX/XLA/TVM: ~220-3,850× faster

### Notes

The ~22% overhead vs baseline is the cost of production features (typed tensors, imports, function lowering). v0.1.7's parser optimization recovers ~18% of matmul overhead.

---

## [1.1.0] - 2025-12-27

### Milestone: Production GPU Backends & AI Protocol

This release brings production-grade GPU backends and AI-native tooling for seamless
integration with modern AI development workflows.

### Added

- **MindIR Compact (MIC) Format** - RFC-0001:
  - Token-efficient IR serialization (4x reduction vs JSON)
  - Line-oriented format for Git-friendly diffs
  - Deterministic canonicalization with roundtrip guarantee
  - Security limits (input size, node count, shape dims, interner capacity)
  - Thread-safe string interning with bounded memory

- **Mind AI Protocol (MAP)** - RFC-0002:
  - Compiler-in-the-loop protocol for AI agents
  - Structured diagnostics with fix suggestions
  - Incremental patching (insert, delete, replace, batch)
  - Security modes (no_io, no_unsafe, pure_only)
  - Poison-safe session management

- **Production GPU Backends** (mind-runtime):
  - Metal backend with full trait implementations
  - ROCm/HIP backend for AMD GPUs
  - WebGPU backend for cross-platform support
  - CUDA backend with production parity
  - Features: poison-safe locking, defragmentation, context recovery, stream sync

### Changed

- Updated STATUS.md to reflect 10 implemented RFCs
- Updated implemented.md with MIC and MAP entries
- GPU backends now production-ready (previously MockGpuBackend)

---

## [1.0.0] - 2025-12-19

### Milestone: 100% Specification Complete

The Core v1 specification is now stable and complete, with all reference implementations
verified and passing.

### Added

- **14 specification chapters** - All marked stable:
  - Surface Language, Core IR, Static Autodiff, Shapes & Tensor Semantics
  - Standard Library, Error Catalog, Conformance, Versioning & Stability
  - MLIR Lowering, Runtime Interface, Security & Safety
  - Performance & Benchmarks, Foreign Function Interface, Future Extensions

- **3 EBNF grammar files** - Complete formal grammar:
  - `grammar-lexical.ebnf` - Lexical structure
  - `grammar-syntax.ebnf` - Surface language syntax
  - `grammar-ir.ebnf` - Core IR textual format

- **13 example files** - Comprehensive examples:
  - Basics (3): hello_tensor, broadcasting, reductions
  - Autodiff (2): simple_grad, mlp_backward
  - Linear Algebra (2): matmul, conv2d
  - FFI (2): c_bindings.mind, python_embed.py
  - IR (4): simple_module, autodiff_output, matmul_module, reduction_module

- **Reference implementation sync**:
  - `star-ga/mind` compiler: 69 tests passing, LLVM 18, 0 Clippy warnings
  - `star-ga/mind-runtime`: 33+ tests, GPU docs, release workflow

### Changed

- Updated `STATUS.md` with reference implementation status
- Updated `docs/README.md` to reflect v1.0 stable status
- Added status badges to main `README.md`

---

## [0.9.0] - 2025-11-07

### Added

- Initial draft of Core v1 specification chapters
- RFC process documentation
- Design principles

---

[Back to Spec Index](./spec/index.md)
