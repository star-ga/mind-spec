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

# Math Library

The `std::math` module provides essential mathematical functions and constants.

## Constants
- **PI**: `3.14159...`
- **E**: `2.71828...`

## Functions

### `sqrt`
```text
// Not Core v1 source: a signature with no body, as an API list
fn sqrt(x: f64) -> f64
```
Computes the non-negative square root. It follows IEEE 754: the result is NaN if x < 0.

### `tanh`
```text
// Not Core v1 source: a signature with no body, as an API list
fn tanh(x: f32) -> f32
```
Computes the hyperbolic tangent (activation function).
