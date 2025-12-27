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

# Types & Variables

MIND is a statically typed language with a focus on tensor operations and safety.

## Primitive Types
- **i32 / i64**: Signed integers.
- **f32 / f64**: IEEE 754 floating point numbers.
- **bool**: Boolean (`true` / `false`).
- **str**: UTF-8 string slices.

## Tensor Type
Tensors are the core primitive, defined by a data type and a shape.
```rust
let image: Tensor<f32, [3, 224, 224]>;
```

## Structs
User-defined compound types.
```rust
struct Model {
    layers: i32,
    learning_rate: f32,
}
```
