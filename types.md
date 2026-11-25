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

## Tensor Type
Tensors are the core primitive, defined by a data type and a shape.
```mind
let image: Tensor<f32, [3, 224, 224]> = zeros([3, 224, 224]);
```

## Fixed-size arrays

`[T; n]` declares an array with exactly `n` elements of type `T`:

```mind
let samples: [i64; 4] = [1, 2, 3, 4];
```

An explicit `let` or `const` annotation requires a literal with the same
element count, including inside functions, branches, and loops. A three- or
five-element literal cannot initialize `[i64; 4]`. Parenthesized and nested
literals follow the same rule. See the
[normative cardinality rule](spec/v1.0/types.md#fixed-array-literal-cardinality).

## Structs
User-defined compound types.
```mind
struct Model {
    layers: i32,
    learning_rate: f32,
}
```

Struct values preserve record identity across assignment, calls and returns.
Fixed arrays copy their containers; record elements remain references to the
same records. Replacing an array element and mutating the record referenced by
an element therefore have different effects. See the
[normative identity and value rules](spec/v1.0/types.md#record-identity-and-fixed-array-values)
for the contract and current implementation limits.
