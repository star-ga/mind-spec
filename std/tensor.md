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

# Tensor Library

The `std::tensor` module provides the core primitives for N-dimensional array construction and linear algebra.

## Constructors

### `zeros`
```
fn zeros(shape: [i64]) -> Tensor
```
Allocates a new contiguous tensor of the specified shape, initialized with 0.0.

### `ones`
```
fn ones(shape: [i64]) -> Tensor
```
Allocates a new contiguous tensor initialized with 1.0.

## Operations

### `matmul`
```
fn matmul(a: Tensor, b: Tensor) -> Tensor
```
Performs matrix multiplication. Supports broadcasting.
**Complexity:** O(M * N * K).

## Spectral Operations

### `fft`
```
fn fft(signal: Tensor) -> Tensor
```
Computes the 1D Fast Fourier Transform.
- **Real input** `[N]`: Returns complex tensor `[N/2+1, 2]` (real, imaginary pairs).
- **Complex input** `[N, 2]`: Returns complex tensor `[N, 2]`.

**Complexity:** O(N log N).

**Backend dispatch:**
| Backend | Library |
|---------|---------|
| CUDA | cuFFT |
| ROCm | rocFFT |
| Metal | vDSP / custom Cooley-Tukey shader |
| WebGPU | WGSL radix-2 Cooley-Tukey |

### `fft2d`
```
fn fft2d(signal: Tensor) -> Tensor
```
Computes the 2D Fast Fourier Transform.
- **Real input** `[H, W]`: Returns complex tensor `[H, W/2+1, 2]`.
- **Complex input** `[H, W, 2]`: Returns complex tensor `[H, W, 2]`.

**Complexity:** O(H * W * log(H * W)).

### `ifft`
```
fn ifft(spectrum: Tensor) -> Tensor
```
Computes the inverse 1D FFT with automatic 1/N normalization.
- **Complex input** `[N, 2]`: Returns complex tensor `[N, 2]` or real tensor `[N]`.

Guarantees: `ifft(fft(x)) == x` (within floating-point precision).

**Complexity:** O(N log N).

### Example: Frequency-domain filtering
```mind
use std::tensor::{fft, ifft, zeros, ones}

fn low_pass_filter(signal: Tensor, cutoff: i64) -> Tensor {
    let spectrum = fft(signal)
    let n = spectrum.shape[0]
    let mask = zeros([n, 2])
    // Keep frequencies below cutoff
    for i in 0..cutoff {
        mask[i] = ones([2])
        mask[n - 1 - i] = ones([2])
    }
    return ifft(spectrum * mask)
}
```
