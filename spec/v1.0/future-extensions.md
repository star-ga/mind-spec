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

# Future Extensions (Informative)

This chapter documents forward-looking considerations for domain-specific extensions to the MIND language and standard library. These are **informative** (not normative) and represent planned or potential features that maintain compatibility with Core v1 while extending its capabilities for specialized applications.

## Purpose

Future extensions allow MIND to evolve beyond the Core v1 baseline while maintaining:

1. **Backward compatibility**: Core v1 programs continue to work unchanged
2. **Opt-in adoption**: Extensions are feature-gated or in separate modules
3. **Specification clarity**: Core semantics remain stable while extensions evolve
4. **Domain expertise**: Specialized features leverage MIND's strengths for specific domains

This chapter serves as a design space exploration and compatibility guide for implementers and library authors.

---

## Neuroscience & Brain-Computer Interfaces

### Motivation

MIND's combination of static shape inference, reverse-mode autodiff, ultra-low-latency compilation, and deterministic execution makes it uniquely suited for real-time neural signal processing and brain-computer interface (BCI) applications. These applications require:

- **Sub-millisecond inference**: Real-time decoding for invasive BCI systems (Neuralink-style implants, ECoG arrays)
- **Multi-channel time-series processing**: Native operations on neural data with Channel × Time × Batch structure
- **On-device adaptation**: Gradient-based decoder optimization directly on resource-constrained BCI hardware
- **Reproducibility**: Deterministic builds critical for FDA-regulated medical devices and peer-reviewed neuroscience
- **Safety-critical execution**: Memory safety and verified execution for implanted medical devices

### Proposed Extensions

#### 1. Neural Time-Series Tensor Types (Informative)

**Concept**: Specialized tensor layouts optimized for multi-channel neural recordings:

```mind
// Proposed syntax (not yet implemented)
type NeuroSignal<T, C: i64, T: i64, B: i64> = tensor<T[C, T, B]>
  with layout = ChannelTimeBatch
  where C = channels, T = time_samples, B = trials/batches
```

**Rationale**:
- Neural data naturally has Channel × Time structure (e.g., 128 ECoG channels × 1000 time samples × 32 trials)
- Explicit layout hints enable MLIR/LLVM optimizations for time-series locality
- Compatible with Core v1 tensor semantics (just annotated shape metadata)

**Shape inference considerations**:
- Broadcasting preserves channel/time semantics (e.g., bias per channel broadcasts over time)
- Reductions typically sum/mean over trials, preserve channel-time structure
- Convolutions along time axis for temporal filtering (1D conv over time dimension)

#### 2. Standard Library Module: `mind::neuro` (Future)

**Proposed module hierarchy**:

```
mind::neuro::
  filters::     # Signal processing filters
    bandpass(signal, low_freq, high_freq, fs) -> filtered
    notch(signal, freq, quality, fs) -> filtered
    ica_decomposition(signal, n_components) -> (sources, mixing_matrix)

  features::    # Feature extraction for BCI
    common_spatial_patterns(X, y, n_components) -> (filters, patterns)
    wavelet_transform(signal, wavelet, scales) -> coefficients
    spectral_power(signal, freq_bands, fs) -> power_per_band

  decoders::    # Neural decoder templates
    kalman_decoder(observations, state_model) -> decoded_trajectory
    lstm_decoder(spikes, hidden_dim) -> intent_logits

  io::          # Neural data formats
    load_edf(path) -> (data, metadata)      # European Data Format
    load_gdf(path) -> (data, metadata)      # General Data Format
    load_nwb(path) -> NWBFile               # Neurodata Without Borders
```

**Implementation considerations**:
- All operations compatible with Core v1 autodiff (differentiable where meaningful)
- ICA/CSP leverage standard linear algebra (eigendecomposition, SVD)
- Wavelet/spectral operations use FFT (potential future extension to `math::` module)
- IO functions return standard tensors + metadata (no new fundamental types)

#### 3. Performance Requirements for BCI

**Real-time constraints**:

| Application | Latency Budget | Throughput | Hardware Profile |
|-------------|---------------|------------|------------------|
| Invasive BCI (implant) | <1 ms | 30 kHz × 128 ch | ARM Cortex-M7, RISC-V |
| ECoG grid decoding | <5 ms | 10 kHz × 256 ch | Edge GPU (Jetson) |
| Non-invasive EEG | <10 ms | 1 kHz × 64 ch | CPU (mobile) |
| Research offline analysis | Best effort | Variable | CPU/GPU cluster |

**Compiler optimizations needed**:
- MLIR loop fusion for filter chains (bandpass → notch → feature extraction)
- Circular buffer support for streaming inference (avoid re-allocating tensors)
- Fixed-point arithmetic for embedded targets (int8/int16 quantization)
- SIMD vectorization for multi-channel operations (process 4-8 channels in parallel)

#### 4. Determinism and Reproducibility

**Neuroscience requirements**:

BCI and neuroscience applications have stricter determinism requirements than typical ML workloads:

1. **Bitwise reproducibility**: Same input data MUST produce identical decoder outputs across:
   - Compiler versions (MIND 1.x series)
   - Hardware targets (x86, ARM, RISC-V)
   - Runtime configurations (single-threaded, multi-threaded with same seed)

2. **Regulatory compliance**: FDA Class III medical devices require:
   - Verified compilation (no undefined behavior)
   - Traceable builds (source hash → binary hash mapping)
   - Audit logs for decoder updates (track model version deployed to each patient)

3. **Peer review**: Published neuroscience papers using MIND decoders MUST allow:
   - Exact replication of results from source code
   - Verification against reported metrics (no floating-point drift across platforms)

**Proposed guarantee**:
> MIND Core v1 with `--deterministic` flag guarantees bitwise-identical IR, MLIR, and LLVM output for identical source and compiler version. Numeric results match within 1 ULP for f32 operations.

#### 5. Integration with Existing Features

Neural signal processing leverages MIND's existing strengths:

| MIND Feature | BCI Application |
|--------------|-----------------|
| **Static shapes** | Multi-channel arrays known at compile time (128 channels, 1000 samples) |
| **Autodiff** | Train Kalman filter parameters, adapt decoders online with gradient descent |
| **MLIR lowering** | Fuse filter chains (bandpass→notch→feature) into tight loops |
| **Edge runtime** | Deploy to ARM Cortex-M in implanted devices (<100 KB binary + model) |
| **Determinism** | FDA compliance, reproducible research, peer review |

---

## Other Domain Extensions (Placeholder)

This section reserves space for future domain-specific extensions:

### Embedded AI & TinyML
- Quantization-aware training primitives (fake_quant, symmetric/asymmetric quantization)
- Model compression (pruning, knowledge distillation)
- Hardware-specific intrinsics (Arm MVE, RISC-V vector extensions)

### Safety-Critical Systems
- Formal verification hooks (proof-carrying code annotations)
- Bounded arithmetic (saturation, overflow traps)
- Worst-case execution time (WCET) analysis

### Distributed Training
- Multi-node collectives (allreduce, allgather, reduce_scatter)
- Pipeline parallelism primitives
- Data-parallel gradient synchronization

---

## Extension Guidelines

When proposing new domain extensions:

1. **Justify with Core v1 limitations**: Show what cannot be expressed efficiently with existing features
2. **Maintain backward compatibility**: Extensions MUST NOT break Core v1 programs
3. **Provide opt-in mechanism**: Feature gates, separate modules, or explicit imports
4. **Define success criteria**: Performance targets, correctness requirements, adoption metrics
5. **Prototype first**: Implement as external library before proposing standard library inclusion

See [RFC process](../../design/rfc-process.md) for formal proposal procedure.

---

## Versioning

Future extensions follow the specification versioning policy:

- **Minor versions (v1.1, v1.2)**: MAY add new modules or functions to standard library
- **Feature gates**: Experimental extensions gated behind `--features=neuro` until stabilized
- **Deprecation policy**: Extensions MAY be deprecated if superseded by better approaches
- **Breaking changes**: Major version bump (v2.0) required for incompatible changes

See [`versioning.md`](./versioning.md) for detailed policy.
