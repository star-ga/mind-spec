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

# Foreign Function Interface (Normative)

This chapter specifies the **Foreign Function Interface (FFI)** for interoperability between MIND and other languages (C, C++, Python, Rust). It defines ABI stability, data layout, lifetime management, and binding generation for Core v1.0.

## Scope and stability

The FFI is **feature-gated** (enabled via `--features=ffi` or similar compiler flag) and targets **C ABI compatibility** as the lowest common denominator for cross-language interop.

### ABI stability guarantees

- **Within minor versions** (v1.x → v1.y): ABI is **stable** (no recompilation required)
- **Across major versions** (v1.x → v2.x): ABI MAY change (recompilation required)
- **Struct layout**: Follows C layout rules (`#[repr(C)]` in Rust)
- **Calling convention**: Uses platform default C convention (cdecl on x86, AAPCS on ARM)

## C API fundamentals

### Header generation

MIND implementations MUST provide a mechanism to generate C headers:

```bash
mind build --emit-ffi-header model.mind -o model.h
```

Generated headers include:
- Struct definitions for tensor descriptors
- Function declarations for exported MIND functions
- Opaque handle types for runtime objects
- Error code enumerations

### Type mapping

#### Primitive types

| MIND Type | C Type | Size | Alignment |
|-----------|--------|------|-----------|
| `i32` | `int32_t` | 4 bytes | 4 bytes |
| `i64` | `int64_t` | 8 bytes | 8 bytes |
| `f32` | `float` | 4 bytes | 4 bytes |
| `f64` | `double` | 8 bytes | 8 bytes |
| `bool` | `uint8_t` | 1 byte | 1 byte |
| `unit` | `void` | 0 bytes | 1 byte |

#### Tensor descriptors

```c
// Opaque tensor handle (managed by MIND runtime)
typedef struct MindTensor MindTensor;

// Tensor descriptor for FFI boundary
typedef struct {
    void* data;           // Pointer to contiguous data buffer
    int64_t* shape;       // Array of dimension sizes [d0, d1, ..., dN]
    int32_t rank;         // Number of dimensions
    MindDtype dtype;      // Data type enum
    MindDevice device;    // Device location (CPU, GPU)
} MindTensorDesc;

// Data type enumeration
typedef enum {
    MIND_DTYPE_F32 = 0,
    MIND_DTYPE_F64 = 1,
    MIND_DTYPE_I32 = 2,
    MIND_DTYPE_I64 = 3,
    MIND_DTYPE_BOOL = 4,
} MindDtype;

// Device enumeration
typedef enum {
    MIND_DEVICE_CPU = 0,
    MIND_DEVICE_GPU = 1,
} MindDevice;
```

#### Function signatures

MIND functions with `export` annotation generate C-compatible entry points:

```mind
// MIND function (exports wrapper around standard library)
export fn matmul(a: tensor<f32[m, k]>, b: tensor<f32[k, n]>) -> tensor<f32[m, n]> {
    return tensor::matmul(a, b);  // Calls standard library matmul
}
```

Generated C header:
```c
// Exported function (caller manages memory)
MindTensor* mind_matmul(const MindTensorDesc* a, const MindTensorDesc* b, MindError* error);

// Cleanup function
void mind_tensor_free(MindTensor* tensor);
```

## Memory management

### Ownership model

**Caller-owned inputs**:
- Caller allocates input tensor buffers
- MIND runtime DOES NOT take ownership
- Buffers MUST remain valid for duration of call
- Caller frees buffers after call returns

**Callee-owned outputs**:
- MIND runtime allocates output tensor buffers
- Caller receives opaque `MindTensor*` handle
- Caller MUST call `mind_tensor_free()` to deallocate
- Failing to free results in memory leak

### Lifetime rules

```c
// Correct usage
MindTensorDesc input_desc = { .data = input_data, .shape = shape, ... };
MindError error = {0};

// Call MIND function (runtime allocates output)
MindTensor* output = mind_matmul(&input_desc, &other_input_desc, &error);
if (output == NULL) {
    fprintf(stderr, "Error: %s\n", error.message);
    return -1;
}

// Use output data
const MindTensorDesc* output_desc = mind_tensor_get_desc(output);
float* result_data = (float*)output_desc->data;

// Cleanup (REQUIRED)
mind_tensor_free(output);
```

### Thread safety

**Runtime handles**:
- `MindRuntime` handles are **NOT thread-safe** by default
- Concurrent calls from multiple threads require external synchronization
- Implementations MAY provide thread-safe variants (`MindRuntimeThreadSafe`)

**Tensor handles**:
- Read-only access is thread-safe (multiple readers)
- Write access requires exclusive ownership
- Passing tensors between threads transfers ownership

## Error handling

### Error codes

```c
typedef enum {
    MIND_OK = 0,
    MIND_ERROR_INVALID_INPUT = 1,
    MIND_ERROR_SHAPE_MISMATCH = 2,
    MIND_ERROR_DTYPE_MISMATCH = 3,
    MIND_ERROR_OUT_OF_MEMORY = 4,
    MIND_ERROR_DEVICE_UNAVAILABLE = 5,
    MIND_ERROR_RUNTIME_FAILURE = 6,
} MindErrorCode;

typedef struct {
    MindErrorCode code;
    char message[256];  // Human-readable error description
} MindError;
```

### Error propagation

All FFI functions return error status via output parameter:

```c
// Function signature with error reporting
MindTensor* mind_conv2d(
    const MindTensorDesc* input,
    const MindTensorDesc* kernel,
    int32_t stride,
    const char* padding,
    MindError* error  // Output: error details
);

// Usage
MindError error = {0};
MindTensor* output = mind_conv2d(input, kernel, 1, "valid", &error);
if (output == NULL) {
    // Check error code and message
    switch (error.code) {
        case MIND_ERROR_SHAPE_MISMATCH:
            fprintf(stderr, "Shape error: %s\n", error.message);
            break;
        case MIND_ERROR_OUT_OF_MEMORY:
            fprintf(stderr, "OOM: %s\n", error.message);
            break;
        default:
            fprintf(stderr, "Unknown error: %s\n", error.message);
    }
    return -1;
}
```

## Python bindings

### Official bindings: `mindlang` package

Python bindings are provided via the `mindlang` package (PyPI):

```bash
pip install mindlang
```

**Architecture**:
- Thin wrapper over C FFI using `ctypes` or `cffi`
- NumPy array zero-copy interop
- Pythonic error handling (exceptions)
- Type hints for IDE support

### Usage example

```python
import mindlang as mind
import numpy as np

# Initialize runtime
runtime = mind.Runtime(backend="cpu")

# Create tensors from NumPy arrays (zero-copy)
a = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
b = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)

# Call MIND function
result = runtime.matmul(a, b)

# Result is NumPy array (zero-copy view)
print(result)  # [[19. 22.] [43. 50.]]

# Cleanup (automatic via __del__)
del runtime
```

### Zero-copy data sharing

**NumPy → MIND**:
- NumPy arrays with C-contiguous layout are passed directly (no copy)
- Fortran-contiguous arrays are copied to C layout
- Strided arrays are copied to contiguous layout

**MIND → NumPy**:
- MIND tensors are wrapped as NumPy arrays with custom destructor
- Memory is managed by MIND runtime until NumPy array is garbage-collected

### Python API design

```python
class Runtime:
    def __init__(self, backend: str = "cpu", device_id: int = 0):
        """Initialize MIND runtime"""

    def matmul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Matrix multiplication"""

    def conv2d(self, input: np.ndarray, kernel: np.ndarray,
               stride: int = 1, padding: str = "valid") -> np.ndarray:
        """2D convolution"""

    def __del__(self):
        """Cleanup runtime resources"""
```

## C++ bindings

### Header-only wrapper

C++ bindings use RAII for automatic resource management:

```cpp
#include <mind/runtime.hpp>

namespace mind {

class Tensor {
public:
    Tensor(const float* data, std::vector<int64_t> shape);
    ~Tensor();  // Automatic cleanup

    // Disable copy, enable move
    Tensor(const Tensor&) = delete;
    Tensor(Tensor&&) noexcept;

    const float* data() const;
    std::span<const int64_t> shape() const;
};

class Runtime {
public:
    Runtime(Device device = Device::CPU);

    Tensor matmul(const Tensor& a, const Tensor& b);
    Tensor conv2d(const Tensor& input, const Tensor& kernel,
                  int stride = 1, std::string_view padding = "valid");
};

}  // namespace mind
```

### Usage example

```cpp
#include <mind/runtime.hpp>
#include <iostream>

int main() {
    mind::Runtime runtime(mind::Device::CPU);

    std::vector<float> a_data = {1.0f, 2.0f, 3.0f, 4.0f};
    mind::Tensor a(a_data.data(), {2, 2});

    std::vector<float> b_data = {5.0f, 6.0f, 7.0f, 8.0f};
    mind::Tensor b(b_data.data(), {2, 2});

    // RAII handles memory automatically
    mind::Tensor result = runtime.matmul(a, b);

    std::cout << "Result: ";
    for (size_t i = 0; i < 4; ++i) {
        std::cout << result.data()[i] << " ";
    }
    std::cout << "\n";

    return 0;  // Automatic cleanup
}
```

## Rust bindings

### Safe wrapper

Rust bindings use the `mind-sys` crate for low-level FFI and `mind` crate for safe API:

```rust
use mind::{Runtime, Tensor, Device};

fn main() -> Result<(), mind::Error> {
    let runtime = Runtime::new(Device::Cpu)?;

    let a = Tensor::from_slice(&[1.0_f32, 2.0, 3.0, 4.0], &[2, 2])?;
    let b = Tensor::from_slice(&[5.0_f32, 6.0, 7.0, 8.0], &[2, 2])?;

    let result = runtime.matmul(&a, &b)?;

    println!("Result: {:?}", result.as_slice());

    Ok(())  // Automatic cleanup via Drop trait
}
```

### Zero-cost abstraction

```rust
// Rust wrapper is zero-cost (no runtime overhead)
pub struct Tensor {
    handle: *mut ffi::MindTensor,  // Opaque C pointer
}

impl Tensor {
    pub fn matmul(&self, other: &Tensor) -> Result<Tensor, Error> {
        let mut error = ffi::MindError::default();
        let result = unsafe {
            ffi::mind_matmul(self.as_desc(), other.as_desc(), &mut error)
        };
        if result.is_null() {
            Err(Error::from_ffi(error))
        } else {
            Ok(Tensor { handle: result })
        }
    }
}

impl Drop for Tensor {
    fn drop(&mut self) {
        unsafe { ffi::mind_tensor_free(self.handle); }
    }
}
```

## WebAssembly bindings

### WASM target support

MIND supports WebAssembly via `wasm32-unknown-unknown` target:

```bash
mind build --target=wasm32-unknown-unknown --features=ffi model.mind -o model.wasm
```

**Limitations**:
- CPU backend only (no GPU, no SIMD by default)
- Smaller runtime footprint (~200 KB)
- Suitable for browser-based inference

### JavaScript API

```javascript
import init, { Runtime } from './model.js';

async function main() {
    await init();  // Load WASM module

    const runtime = new Runtime("cpu");

    const a = new Float32Array([1, 2, 3, 4]);
    const b = new Float32Array([5, 6, 7, 8]);

    const result = runtime.matmul(a, [2, 2], b, [2, 2]);

    console.log(result);  // Float32Array [19, 22, 43, 50]

    runtime.free();  // Manual cleanup
}

main();
```

## Interoperability best practices

### Data layout compatibility

**Row-major tensors** (C, NumPy, PyTorch default):
```
[2, 3] tensor: [[a, b, c], [d, e, f]]
Memory layout: [a, b, c, d, e, f]
```

**Column-major tensors** (Fortran, MATLAB, Julia):
```
[2, 3] tensor (column-major): [[a, b, c], [d, e, f]]
Memory layout: [a, d, b, e, c, f]
```

MIND uses **row-major (C layout)** by default. Implementations SHOULD support column-major via explicit transpose or layout annotation.

### Minimizing copies

**Best practices**:
1. Use contiguous memory buffers (avoid strided views)
2. Align allocations to 64-byte boundaries for SIMD
3. Pin memory for GPU transfers (avoid pageable memory)
4. Use zero-copy views when possible (NumPy, PyTorch)

### Version compatibility

**Runtime version check**:
```c
const char* mind_version(void);
int mind_abi_version(void);

// Usage
if (mind_abi_version() != MIND_ABI_VERSION_1_0) {
    fprintf(stderr, "ABI mismatch: expected %d, got %d\n",
            MIND_ABI_VERSION_1_0, mind_abi_version());
    return -1;
}
```

## Security considerations

### Input validation

FFI entry points MUST validate:
- Null pointers (reject with `MIND_ERROR_INVALID_INPUT`)
- Tensor shape sanity (no negative dimensions, no overflow)
- Data buffer alignment (warn if misaligned, copy if necessary)

### Sandboxing

FFI functions execute in the caller's process:
- No inherent sandboxing (unlike WASM)
- Malicious inputs MUST NOT cause memory corruption
- Out-of-bounds access MUST be detected (runtime checks or memory safety)

## Future extensions

Planned FFI improvements:

- **Swift bindings**: Native Swift API with `@_cdecl` interop
- **Java/JNI bindings**: For Android and server deployments
- **Go bindings**: Via CGo for Go-based services
- **Async API**: Non-blocking execution with callbacks/futures

## Reference implementation C API (`mind-runtime`)

The `cputer/mind-runtime` provides the following C API (feature flag: `--features ffi`):

### Enumerations

```c
typedef enum {
    MIND_STATUS_OK = 0,
    MIND_STATUS_INVALID_ARG = 1,
    MIND_STATUS_UNSUPPORTED = 2,
    MIND_STATUS_RUNTIME_ERROR = 3,
    MIND_STATUS_INTERNAL_ERROR = 4,
} mind_status_t;

typedef enum {
    MIND_DTYPE_F32 = 0,
    MIND_DTYPE_U8 = 1,
    MIND_DTYPE_F16 = 2,
    MIND_DTYPE_I32 = 3,
} mind_dtype_t;

typedef enum {
    MIND_DEVICE_CPU = 0,
    MIND_DEVICE_GPU = 1,
} mind_device_t;
```

### Opaque types

```c
typedef struct mind_runtime_s mind_runtime_t;
typedef struct mind_tensor_s mind_tensor_t;
```

### Function signatures

```c
// Runtime lifecycle
mind_status_t mind_runtime_new(
    mind_device_t device,
    mind_runtime_t **out_rt
);

void mind_runtime_free(mind_runtime_t *rt);

// Tensor memory management
mind_status_t mind_tensor_alloc(
    mind_runtime_t *rt,
    mind_dtype_t dtype,
    const int64_t *shape,
    size_t rank,
    mind_tensor_t **out_tensor
);

void mind_tensor_free(mind_runtime_t *rt, mind_tensor_t *tensor);

// Tensor I/O
mind_status_t mind_tensor_write_f32(
    mind_runtime_t *rt,
    mind_tensor_t *tensor,
    const float *data,
    size_t len
);

mind_status_t mind_tensor_read_f32(
    mind_runtime_t *rt,
    mind_tensor_t *tensor,
    float *data,
    size_t len
);

// Operator execution
mind_status_t mind_runtime_run_op(
    mind_runtime_t *rt,
    const char *op_name,
    mind_tensor_t *const *inputs,
    size_t num_inputs,
    mind_tensor_t *const *outputs,
    size_t num_outputs
);
```

**Total**: 7 exported functions, 3 enums, 2 opaque types.

### Memory semantics

- **Tensor storage**: `Vec<f32>` backed (standard Rust heap allocation)
- **Allocation**: Zero-initialized with validated shapes
- **Deallocation**: RAII via `mind_runtime_free()` / `mind_tensor_free()`
- **Memory layout**: Row-major (C-style)
- **GPU alignment**: 4-byte alignment required (`numel % 4 == 0`)

### Numerical tolerances

Conformance tests use `1e-5` tolerance for floating-point comparisons in autodiff gradient validation.

## References

- [Rust FFI Guide](https://doc.rust-lang.org/nomicon/ffi.html)
- [NumPy C API](https://numpy.org/doc/stable/reference/c-api/)
- [PyTorch C++ API](https://pytorch.org/cppdocs/)
- [WebAssembly Reference](https://webassembly.github.io/spec/)
