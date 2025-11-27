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
