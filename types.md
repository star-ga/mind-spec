# Types & Variables

MIND is a statically typed language with a focus on tensor operations and memory safety.

## Primitive Types

| Type | Description | Example |
|------|-------------|---------|
| `i32`, `i64` | Signed integers | `42`, `-10` |
| `f32`, `f64` | IEEE 754 floating point | `3.14`, `1.0e-5` |
| `bool` | Boolean values | `true`, `false` |
| `str` | UTF-8 string slice | `"hello"` |

## Tensor Types

Tensors are the first-class citizens of MIND. They are parameterized by their data type and shape.

```rust
// A 3-dimensional tensor of f32s with shape [3, 224, 224]
let image: Tensor<f32, [3, 224, 224]> = load_image("cat.jpg");

// A 2x2 matrix
let matrix: Tensor<f32, [2, 2]> = tensor([
    [1.0, 0.0],
    [0.0, 1.0]
]);
```

## Structs

Structs allow you to create custom data types by grouping related values.

```rust
struct ModelConfig {
    learning_rate: f32,
    batch_size: i32,
    layers: i32,
}

let config = ModelConfig {
    learning_rate: 0.001,
    batch_size: 32,
    layers: 12,
};
```

## Type Inference

MIND's compiler can often infer types, so you don't always need to annotate them.

```rust
let x = 10; // Inferred as i32
let y = 3.14; // Inferred as f32
```
