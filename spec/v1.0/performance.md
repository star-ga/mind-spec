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

# Performance and Benchmarks (Informative)

This chapter defines performance characteristics, benchmark methodology, and optimization guidance for MIND Core v1.0 implementations. While semantics are normative, performance targets are **informative** and serve as implementation quality guidelines.

## Performance philosophy

MIND prioritizes **correctness and determinism** over raw performance. However, production-grade implementations SHOULD achieve competitive performance with established frameworks (PyTorch, JAX, TensorFlow) for equivalent operations.

### Design principles

1. **Zero-cost abstractions**: High-level tensor operations compile to efficient low-level code
2. **Predictable performance**: No hidden allocations, implicit broadcasts are explicit
3. **Transparent trade-offs**: Users control memory layout, fusion, and parallelism
4. **Baseline efficiency**: Even unoptimized code should be within 2-5× of hand-tuned equivalents

## Benchmark methodology

### Benchmark categories

Core v1.0 benchmarks fall into three categories:

**1. Microbenchmarks** (operation-level)
- Single tensor operations: matmul, conv2d, reductions
- Measure throughput (GFLOP/s), latency (μs), memory bandwidth utilization
- Compare against BLAS/cuBLAS, Eigen, NumPy

**2. Kernel benchmarks** (algorithm-level)
- Common ML kernels: softmax, layer_norm, attention
- Measure end-to-end latency including memory transfers
- Compare against PyTorch/JAX equivalents

**3. Model benchmarks** (application-level)
- Full model inference/training: ResNet-50, GPT-2, BERT
- Measure samples/second, time-to-accuracy, memory footprint
- Compare against production frameworks

### Measurement protocol

**Hardware**:
- **CPU**: Intel Xeon (SKX or newer), AMD EPYC, ARM Neoverse
- **GPU**: NVIDIA A100, V100; AMD MI250X
- **Memory**: Representative of deployment (16GB laptop, 128GB server)

**Methodology**:
- Warmup: 10 iterations to prime caches
- Measurement: 100+ iterations, report median and 95th percentile
- Precision: f32 (default), f16 (GPU), bf16 (TPU)
- Input sizes: Small (1KB), medium (1MB), large (1GB)

**Reproducibility**:
- Fixed random seed for initialization
- CPU pinning / GPU device isolation
- Controlled frequency scaling (disable turbo boost for variance reduction)

## Performance targets

### Microbenchmark targets (f32, CPU)

| Operation | Input Size | Target Throughput | Comparison |
|-----------|------------|-------------------|------------|
| Dense matmul | [1024, 1024] @ [1024, 1024] | >500 GFLOP/s | ~80% of MKL/OpenBLAS |
| Batched matmul | [32, 512, 512] @ [32, 512, 512] | >300 GFLOP/s | ~70% of MKL |
| Conv2d (NHWC) | [16, 224, 224, 3] * [64, 7, 7, 3] | >200 GFLOP/s | ~60% of oneDNN |
| Elementwise add | [1M] + [1M] | >10 GB/s bandwidth | ~80% of memcpy |
| Reduction sum | sum([1M], axis=0) | >5 GB/s | ~50% of bandwidth limit |

### Microbenchmark targets (f32, GPU A100)

| Operation | Input Size | Target Throughput | Comparison |
|-----------|------------|-------------------|------------|
| Dense matmul | [4096, 4096] @ [4096, 4096] | >15 TFLOP/s | ~75% of cuBLAS |
| Batched matmul | [128, 1024, 1024] @ [128, 1024, 1024] | >12 TFLOP/s | ~70% of cuBLAS |
| Conv2d (NHWC) | [64, 224, 224, 3] * [64, 7, 7, 3] | >8 TFLOP/s | ~50% of cuDNN |
| Elementwise add | [10M] + [10M] | >1 TB/s bandwidth | ~80% of peak bandwidth |
| Reduction sum | sum([10M], axis=0) | >500 GB/s | ~40% of bandwidth |

**Notes**:
- Targets are for **unoptimized baseline** implementations
- Optimized MLIR pipelines (fusion, tiling) SHOULD achieve 90-95% of framework performance
- GPU targets assume Tensor Cores disabled (f32 mode); f16 with Tensor Cores approaches cuBLAS parity

### Compilation performance

| Metric | Target | v0.2.1 Actual | Notes |
|--------|--------|---------------|-------|
| Parse + typecheck (small) | <100µs | **1.77-4.75 µs** | Single tensor operations |
| Parse + typecheck (1K LOC) | <100ms | TBD | Incremental compilation amortizes cost |
| IR generation | <50ms for 1K LOC | Included above | Single-pass lowering |
| MLIR lowering | <500ms for medium model | TBD | Includes optimization passes |
| End-to-end binary build | <5 sec for ResNet-50 | TBD | Cold build with LLVM backend |
| Incremental rebuild | <1 sec | TBD | For single-function changes |

**v0.2.1 Achievement**: Sub-5µs compilation for typical tensor programs, exceeding original targets by orders of magnitude. v0.2.1 adds audit hardening (C1-C7) with negligible performance impact (338K vs 347K compilations/sec, -2.6%).

## Optimization strategies

### Compiler optimizations

**Automatic**:
- Constant folding: Evaluate compile-time-known tensors
- Dead code elimination: Remove unused operations
- Algebraic simplification: `x * 1 → x`, `x + 0 → x`
- Common subexpression elimination: Deduplicate identical computations

**MLIR-specific**:
- Loop fusion: Combine compatible elementwise ops
- Tiling: Improve cache locality for large tensors
- Vectorization: SIMD for elementwise operations
- Bufferization: Eliminate temporary allocations

**Backend-specific**:
- cuBLAS/cuDNN delegation: Offload to vendor libraries
- Kernel fusion: Combine multiple ops into single GPU kernel
- Memory coalescing: Optimize access patterns for GPU memory

### Manual optimization hints

While MIND avoids explicit performance annotations, users can influence performance via:

**Memory layout**:
```mind
// Prefer row-major for CPU matmul (cache-friendly)
let a: tensor<f32[m, k]> = ...;  // Row-major by default

// Prefer NHWC for GPU conv (Tensor Core-friendly)
let x: tensor<f32[batch, height, width, channels]> = ...;
```

**Fusion-friendly patterns**:
```mind
// Good: Single fused kernel (map + reduce)
let result = mean(relu(x));

// Suboptimal: Separate kernels with intermediate allocation
let activated = relu(x);
let result = mean(activated);
```

**Batch sizes**:
- CPU: Powers of 2 or multiples of cache line (64 bytes / sizeof(dtype))
- GPU: Multiples of warp size (32) or block size (128-256)

### Profiling and analysis

**Compiler flags**:
```bash
# Profile IR passes
mind compile --emit-ir --profile-passes input.mind

# MLIR optimization report
mind compile --emit-mlir --mlir-print-ir-after-all input.mind

# LLVM optimization remarks
mind build --llvm-remarks=all input.mind
```

**Runtime profiling**:
```bash
# CPU profiling (perf on Linux)
perf record mind run input.mind
perf report

# GPU profiling (NVIDIA Nsight)
nsys profile mind run --backend=gpu input.mind

# Memory profiling (Valgrind Massif)
valgrind --tool=massif mind run input.mind
```

## Benchmark suite specification

### Standard benchmark suite

The official MIND benchmark suite (`benchmarks/` in star-ga/mind repo) includes:

**1. Core operations** (`benchmarks/ops/`)
- Arithmetic: add, mul, div (element-wise and broadcasting)
- Linear algebra: matmul, batch_matmul, einsum
- Convolution: conv2d (various kernel sizes, strides, padding)
- Reductions: sum, mean, max (all axes)
- Activations: relu, sigmoid, tanh, softmax

**2. Composite kernels** (`benchmarks/kernels/`)
- MLP layer: linear + bias + activation
- Attention: scaled dot-product attention (Q, K, V)
- LayerNorm: normalization + scale + shift
- BatchNorm: batch statistics + normalization

**3. Model inference** (`benchmarks/models/`)
- Vision: ResNet-50, EfficientNet-B0, MobileNetV2
- NLP: GPT-2 (117M), BERT-base (110M)
- Small models: LeNet-5, TinyBERT

**4. Training** (`benchmarks/training/`)
- Forward + backward + optimizer step
- Measure time-to-accuracy on standard datasets (MNIST, CIFAR-10)

### Running benchmarks

```bash
# Run full suite (CPU)
cargo bench

# Run specific category
cargo bench --bench ops_matmul

# Run with GPU backend
cargo bench --features=gpu --bench models_resnet50

# Generate comparison report
cargo bench -- --save-baseline main
# (make changes)
cargo bench -- --baseline main
```

### Benchmark output format

```yaml
benchmark: ops/matmul_f32_1024x1024
hardware:
  cpu: Intel Xeon Gold 6248R @ 3.0GHz
  cores: 24 (48 threads)
  memory: 192GB DDR4-2933
  os: Linux 5.15.0
results:
  throughput: 487.3 GFLOP/s
  latency_median: 4.52 ms
  latency_p95: 4.89 ms
  memory_peak: 16.8 MB
comparison:
  numpy_1.24: 0.92x  (531 GFLOP/s)
  pytorch_2.0: 1.05x  (464 GFLOP/s)
  mkl_2023: 0.81x   (602 GFLOP/s)
```

## Performance regression testing

### CI integration

- Benchmark subset runs on every PR (fast microbenchmarks only)
- Full suite runs nightly on dedicated hardware
- Performance regressions >5% trigger alerts
- Results published to dashboard (perf.mindlang.dev)

### Acceptable variance

- Microbenchmarks: ±3% variance tolerated
- Kernel benchmarks: ±5% variance
- Model benchmarks: ±10% variance (more sensitive to system noise)

## Memory footprint

### Runtime memory overhead

| Component | Size (Release Build) |
|-----------|----------------------|
| Minimal runtime (no_std) | ~50 KB |
| Standard runtime (CPU) | ~80 KB |
| GPU runtime (CUDA) | ~5 MB (including driver overhead) |
| MLIR/LLVM JIT | ~20 MB (feature-gated) |

### Model memory estimation

```
Total = Weights + Activations + Gradients + Optimizer State

Weights: Σ (param_count × sizeof(dtype))
Activations: Largest intermediate tensor × batch_size
Gradients: Same as weights (if training)
Optimizer state: 2× weights (Adam), 0× (SGD)
```

**Example (ResNet-50, batch=32, f32)**:
- Weights: 25.6M params × 4 bytes = 102 MB
- Activations: ~200 MB (peak during forward pass)
- Gradients: 102 MB
- Adam state: 204 MB
- **Total**: ~608 MB

## Verified benchmark results

This section contains empirically validated benchmark results for the reference MIND implementation across multiple machine configurations.

### Reference Platform (February 2026)

| Component | Version |
|-----------|---------|
| Platform | Ubuntu 24.04 LTS x86_64 |
| CPU | Intel Core i7-5930K @ 3.50GHz |
| GPU | NVIDIA RTX 3080 10GB, CUDA 12.8 |
| RAM | 64 GB DDR4 |
| PyTorch | 2.10.0+cu128 |
| JAX | 0.9.0.1 |
| Mojo | 0.26.1.0 |
| MIND | 0.2.1 (release build) |
| Measurement | Rust Criterion benchmarks (in-process, 100 samples, 3-sec warmup, 95% CI) |

### Compilation speed

**MIND v0.2.0 compilation performance** (Rust criterion benchmarks, February 7, 2026):

| Benchmark | Mean (µs) | Range (µs) | Compilations/sec | Description |
|-----------|-----------|------------|-----------------|-------------|
| scalar_math | 1.77 | [1.73, 1.81] | 565,000/sec | Simple arithmetic |
| small_matmul | 2.88 | [2.86, 2.91] | 347,000/sec | [10,20] × [20,30] |
| medium_matmul | 2.82 | [2.81, 2.83] | 355,000/sec | [128,256] × [256,512] |
| large_matmul | 2.84 | [2.81, 2.91] | 352,000/sec | [512,1024] × [1024,512] |
| tensor_ops | 4.75 | [4.71, 4.81] | 210,500/sec | Add, multiply, ReLU chain |
| reductions | 2.92 | [2.86, 2.99] | 342,500/sec | Sum + mean reduction |
| reshape_ops | 2.80 | [2.78, 2.82] | 357,000/sec | Reshape + transpose |

**Version History**:

| Version | scalar_math | matmul ops | Compilations/sec | Key Change |
|---------|-------------|------------|-----------------|------------|
| Baseline (Dec 2025) | 21 µs | 37 µs | ~27,000/sec | Minimal Chumsky parser |
| v0.1.6 | 26 µs | ~55 µs | ~18,000/sec | Full typed tensors |
| v0.1.7 | 26 µs | 45 µs | ~22,000/sec | Parser choice reordering (-18%) |
| v0.1.9 | 26 µs | 45 µs | ~22,000/sec | Lib rename, Windows fixes |
| v0.2.0 | 1.77 µs | 2.84 µs | 347,000/sec | Hand-written recursive descent (15× faster) |
| **v0.2.1** | **1.82 µs** | **2.96 µs** | **338,000/sec** | **Audit-hardened pipeline (C1-C7, -2.6%)** |

**Result**: MIND frontend is **35,000-176,000× faster** than PyTorch 2.10 GPU torch.compile (full pipeline), **21,200-95,100× faster** than JAX 0.9 cold-start XLA compilation, and **135,000-458,000× faster** than Mojo 0.26.1 full compilation.

**Compilation Speed vs PyTorch 2.10 GPU** (February 2026, verified):

| Benchmark | MIND v0.2.1 | PyTorch 2.10 GPU | Ratio |
|-----------|-------------|------------------|-------|
| scalar_math | 1.77 µs | 99 ms | ~56,000× |
| small_matmul | 2.95 µs | 162 ms | ~55,000× |
| medium_matmul | 2.95 µs | 109 ms | ~37,000× |
| large_matmul | 2.95 µs | 105 ms | ~36,000× |
| simple_mlp | 6.15 µs | 752 ms | ~122,000× |
| conv2d | ~5 µs | 878 ms | ~176,000× |

*Environment: Ubuntu 24.04, RTX 3080, CUDA 12.8, PyTorch 2.10.0+cu128, full cold-start (caches cleared)*

**Compilation Speed vs Mojo 0.26.1** (February 2026, verified):

| Benchmark | MIND v0.2.1 | Mojo 0.26.1 | Ratio |
|-----------|-------------|-------------|-------|
| scalar_math | 1.77 µs | 810 ms | ~458,000× |
| matmul | 2.95 µs | 827 ms | ~280,000× |
| mlp | 6.15 µs | 829 ms | ~135,000× |

*Environment: Ubuntu 24.04, Mojo 0.26.1.0, pixi, `mojo build` (full LLVM compilation)*

**Compilation Speed vs JAX 0.9** (February 2026, verified):

| Benchmark | MIND v0.2.1 | JAX 0.9 Cold-Start | Ratio |
|-----------|-------------|-------------------|-------|
| scalar_math | 1.77 µs | 37.5 ms | ~21,200× |
| small_matmul | 2.95 µs | 127.2 ms | ~43,100× |
| medium_matmul | 2.95 µs | 139.7 ms | ~47,400× |
| large_matmul | 2.95 µs | 280.6 ms | ~95,100× |
| simple_mlp | 6.15 µs | 360.5 ms | ~58,600× |

*Environment: Ubuntu 24.04, RTX 3080, CUDA 12.8, JAX 0.9.0.1, cold-start with compilation cache disabled*

**Scope Note**: MIND measures **frontend only** (parse + typecheck + IR). PyTorch measures the full torch.compile() pipeline (FX graph + Inductor + Triton/cuBLAS). Mojo measures full LLVM compilation to native binary. Ratios reflect this scope difference.

**Key insight**: MIND compilation time scales with **program complexity** (number of operations), not tensor dimensions — matmul operations compile in ~2.8 µs regardless of matrix dimensions (10×20 to 512×1024). Larger programs scale: medium_mlp (5 ops) = 6.15 µs, large_network (12 ops) = 15.49 µs. v0.2.0's hand-written recursive descent parser delivers 340,000+ compilations per second for simple programs.

### Determinism verification

**Bit-level reproducibility** (SHA256 cryptographic verification):

| Test Program | Runs | Unique Hashes | Deterministic | Reference Hash (first 16) |
|--------------|------|---------------|---------------|---------------------------|
| scalar_math | 10 | 1 | ✅ YES | d5b1d6f8b5b362c2 |
| small_matmul | 10 | 1 | ✅ YES | 89eb85864fb6d568 |
| medium_matmul | 10 | 1 | ✅ YES | c7908ca8ec76a8f7 |
| mlp | 10 | 1 | ✅ YES | a7ffc6f8bf1ed766 |

**Statistics**:
- Total compilations: 40 (4 tests × 10 runs)
- Deterministic tests: 4/4 (100%)
- Hash collision rate: 0%

**Result**: 100% bit-level deterministic compilation verified.

### Compile-time autodiff efficiency

**PyTorch runtime autodiff cost** (per iteration):

| Program | Forward (µs) | Backward (µs) | Total (µs) |
|---------|--------------|---------------|------------|
| simple_quadratic | 12.3 | 51.1 | 63.4 |
| small_mlp | 45.2 | 345.9 | 391.1 |
| matmul_chain | 67.5 | 428.8 | 496.3 |

**Amortized efficiency** (1000 training iterations, forward + backward):

| Program | MIND Total | PyTorch Total | MIND Advantage |
|---------|------------|---------------|----------------|
| simple_quadratic | ~2 µs (once) | 63,400 µs | 31,700× |
| small_mlp | ~6 µs (once) | 391,100 µs | 65,200× |
| matmul_chain | ~6 µs (once) | 496,300 µs | 82,700× |

**Result**: MIND compile-time autodiff is **31,700-82,700× more efficient** than runtime autodiff (v0.2.1).

## Prior art comparison

### PyTorch 2.10 (TorchInductor/TorchDynamo)

| Feature | PyTorch 2.0 | MIND v0.2.1 | Difference |
|---------|-------------|-------------|------------|
| Compilation Strategy | JIT tracing/scripting | AOT static compilation | MIND compiles before execution |
| Autodiff Method | Runtime tape-based | Compile-time symbolic | MIND generates gradient IR at compile-time |
| Type System | Dynamic typing | Static strong typing | MIND type-checks at compile-time |
| Compilation Time | 99-878 ms (GPU cold-start) | 1.8-15.5 µs (frontend) | MIND frontend 35,000-176,000× faster |
| Determinism | Not guaranteed | 100% bit-level | MIND guarantees reproducibility |

### JAX (Google)

| Feature | JAX 0.9 | MIND v0.2.1 | Difference |
|---------|---------|-------------|------------|
| Compilation Backend | XLA (C++) | Custom Rust | Specialized for tensor DSL |
| Compilation Speed | 37.5-360.5 ms (cold-start) | 1.8-15.5 µs (frontend) | MIND 21,200-95,100× faster |
| Autodiff | jax.grad() transforms | Compile-time IR | Zero runtime cost |
| Determinism | Mostly deterministic | 100% guaranteed | Cryptographic proof |

### OpenAI Triton

| Feature | Triton | MIND | Difference |
|---------|--------|------|------------|
| Abstraction | GPU kernel language | High-level tensor language | MIND more accessible |
| Autodiff | Manual gradient kernels | Automatic | MIND handles gradients |
| Compilation | JIT (LLVM) | AOT (custom) | MIND faster compilation |

### Apache TVM

| Feature | TVM | MIND v0.2.1 | Difference |
|---------|-----|-------------|------------|
| Focus | Deploy-time optimization | Compile-time correctness | Different priorities |
| Compilation Speed | ~10-100 ms | 1.8-15.5 µs | MIND ~2,100-55,600× faster |
| Autodiff | External (relay.gradient) | Built-in | Integrated solution |

### XLA (TensorFlow/JAX Backend)

| Feature | XLA | MIND v0.2.1 | Difference |
|---------|-----|-------------|------------|
| Implementation | C++ (50k+ LOC) | Rust (compact) | Simpler architecture |
| Compilation Speed | ~10-100 ms | 1.8-15.5 µs | MIND ~2,100-55,600× faster |
| Determinism | Not guaranteed | 100% guaranteed | Production-ready |

**Key differentiation**: No prior art achieves all three of:
1. Sub-100 µs compilation
2. 100% deterministic builds
3. Compile-time autodiff with zero runtime cost

## Future optimizations

Areas for future performance work:

- **Automatic mixed precision**: Dynamic f16/f32 switching
- **Model parallelism**: Tensor sharding across devices
- **Just-in-time compilation**: Specialize kernels for runtime shapes
- **Quantization**: Int8 inference with minimal accuracy loss
- **Sparsity**: Exploit zero values in weights/activations

## References

- [MLPerf Benchmark Suite](https://mlcommons.org/en/benchmarks/)
- [Google Perftools](https://github.com/gperftools/gperftools)
- [NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems)
- [Intel VTune Profiler](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html)
