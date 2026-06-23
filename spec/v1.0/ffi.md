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

The FFI is **feature-gated** (enabled via `--features=ffi-c` compiler flag) and targets **C ABI compatibility** as the lowest common denominator for cross-language interop.

### ABI stability guarantees

- **Within minor versions** (v1.x → v1.y): ABI is **stable** (no recompilation required)
- **Across major versions** (v1.x → v2.x): ABI MAY change (recompilation required)
- **Struct layout**: Follows C layout rules (`#[repr(C)]` in Rust)
- **Calling convention**: Uses platform default C convention (cdecl on x86, AAPCS on ARM)

## C API fundamentals

### Header generation

MIND implementations MUST provide a mechanism to generate C headers (feature-gated behind `ffi-c`):

```bash
mind --emit-ffi-c model.h model.mind
```

Generated headers include:
- Struct definitions for tensor descriptors
- Function declarations for exported MIND functions
- Opaque handle types for runtime objects
- Error code enumerations

### Type mapping

#### Primitive types

The reference compiler (v0.10.0) currently exports these primitive types via FFI:

| MIND Type | C Type | Size | Alignment | Status |
|-----------|--------|------|-----------|--------|
| `i32` | `int32_t` | 4 bytes | 4 bytes | ✅ Supported |
| `f32` | `float` | 4 bytes | 4 bytes | ✅ Supported |

**Not yet emitted** (planned for future releases):
- `i64` / `int64_t`
- `f64` / `double`
- `bool` / `uint8_t`
- `unit` / `void`

#### Tensor descriptors

The reference compiler (v0.10.0) emits the following C API (feature: `ffi-c`):

```c
// Data type enumeration (reference compiler v0.10.0)
typedef enum {
    MIND_I32 = 0,
    MIND_F32 = 1,
} MindDType;

// Shape descriptor
typedef struct {
    uint32_t rank;              // Number of dimensions
    const uint64_t* dims;       // Array of dimension sizes [d0, d1, ..., dN]
} MindShape;

// Tensor descriptor for FFI boundary
typedef struct {
    MindDType dtype;            // Data type enum
    MindShape shape;            // Shape descriptor
    void* data;                 // Pointer to contiguous data buffer
    uint64_t byte_len;          // Total byte length of data buffer
} MindTensor;

// I/O descriptor (pairs a name with a tensor)
typedef struct {
    const char* name;           // Name of input or output
    MindTensor tensor;          // The tensor data
} MindIO;

// Model metadata
typedef struct {
    uint32_t inputs_len;        // Number of inputs
    uint32_t outputs_len;       // Number of outputs
    const char* model_name;     // Name of the model
    uint64_t model_version;     // Model version
} MindModelMeta;
```

#### Function signatures

The reference compiler (v0.10.0) generates the following core FFI functions:

```c
// Get model metadata
int mind_model_meta(MindModelMeta* out);

// Get model input/output descriptors
int mind_model_io(
    MindIO* inputs_out, uint32_t cap_inputs,
    MindIO* outputs_out, uint32_t cap_outputs
);

// Run inference
int mind_infer(
    const MindIO* inputs, uint32_t inputs_len,
    MindIO* outputs, uint32_t outputs_len
);

// Memory management
void* mind_alloc(uint64_t size);
void mind_free(void* p);

// Error handling
const char* mind_last_error(void);
```

**Return values**: Functions return 0 on success, negative values on error. Error details are available via `mind_last_error()`.

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

## Reference implementation C API

The MIND compiler (feature flag: `--features ffi-c`) generates a stable C FFI interface. The reference implementation (`star-ga/mind-runtime`) provides an open-core C API for model execution and memory management.

### Core API (open-core)

The minimum stable API (as of v0.10.0) consists of:
- 6 exported functions (lifecycle + memory + inference + errors)
- 2 enumeration types (data types, model metadata)
- 4 struct types (shape, tensor, I/O descriptor, model metadata)

### Memory semantics

- **Tensor storage**: Heap-allocated via `mind_alloc()`
- **Allocation**: Caller-managed; zero-initialization is not guaranteed
- **Deallocation**: Caller must call `mind_free()` on all allocations
- **Memory layout**: Row-major (C-style contiguous)
- **Data pointer lifetime**: Caller retains ownership; buffers must remain valid for the duration of API calls

### Numerical tolerances

Conformance tests use appropriate precision for each data type:
- `f32` operations: single-precision floating-point semantics
- `i32` operations: signed 32-bit integer semantics

## References

- [Rust FFI Guide](https://doc.rust-lang.org/nomicon/ffi.html)
- [NumPy C API](https://numpy.org/doc/stable/reference/c-api/)
- [PyTorch C++ API](https://pytorch.org/cppdocs/)
- [WebAssembly Reference](https://webassembly.github.io/spec/)
