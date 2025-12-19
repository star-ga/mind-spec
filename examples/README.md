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

# MIND Language Examples

This directory contains standalone example programs demonstrating MIND language features
as specified in the [Core v1 specification](../spec/v1.0/overview.md).

## Directory Structure

```
examples/
├── README.md                 # This file
├── basics/                   # Basic tensor operations
│   ├── hello_tensor.mind     # Tensor creation and arithmetic
│   ├── broadcasting.mind     # Broadcasting semantics
│   └── reductions.mind       # Sum, mean, and other reductions
├── autodiff/                 # Automatic differentiation
│   ├── simple_grad.mind      # Basic gradient computation
│   └── mlp_backward.mind     # MLP backpropagation
├── linear_algebra/           # Linear algebra operations
│   ├── matmul.mind           # Matrix multiplication
│   └── conv2d.mind           # 2D convolution
├── ffi/                      # Foreign function interface
│   ├── c_bindings.mind       # C interop example
│   └── python_embed.py       # Python embedding example
└── ir/                       # Core IR examples
    ├── simple_module.ir      # Basic IR module
    ├── autodiff_output.ir    # Autodiff-generated IR
    ├── matmul_module.ir      # Matrix multiplication IR
    └── reduction_module.ir   # Reduction operations IR
```

## Running Examples

Examples require a MIND implementation that conforms to Core v1. See the reference
implementation at [cputer/mind](https://github.com/cputer/mind).

```bash
# Run a MIND source file
mind run examples/basics/hello_tensor.mind

# Compile to IR
mind compile --emit-ir examples/basics/hello_tensor.mind

# Execute IR directly
mind-runtime examples/ir/simple_module.ir
```

## Example Categories

### Basics

Fundamental tensor operations including creation, arithmetic, and shape manipulation.
These examples demonstrate the surface language syntax from
[`language.md`](../spec/v1.0/language.md).

### Autodiff

Automatic differentiation examples showing gradient computation as specified in
[`autodiff.md`](../spec/v1.0/autodiff.md). Includes forward and backward pass
demonstrations.

### Linear Algebra

Matrix operations and convolutions as specified in
[`ir.md`](../spec/v1.0/ir.md#linear-and-tensor-algebra). Examples cover `Dot`,
`MatMul`, and `Conv2d` operations.

### FFI

Foreign function interface examples demonstrating C, C++, Python, and Rust bindings
as specified in [`ffi.md`](../spec/v1.0/ffi.md).

### IR

Raw Core IR examples showing the textual encoding format from
[`grammar-ir.ebnf`](../spec/v1.0/grammar-ir.ebnf).

## Relationship to Specification

Each example includes comments referencing the relevant specification sections.
Examples are validated against the [conformance test corpus](../spec/v1.0/conformance.md)
and should produce identical results on any conforming implementation.

## Contributing

New examples are welcome! Please ensure:

1. Examples are self-contained and runnable
2. Comments reference relevant spec sections
3. Expected output is documented
4. Examples pass on the reference implementation
