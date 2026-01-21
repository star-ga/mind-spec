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

# Runtime Interface (Normative)

This chapter defines the abstract runtime contract expected by Core v1. It mirrors the behaviour
implemented by public runtimes without prescribing internal threading or device strategies.

Core v1 defines a **CPU baseline profile** and a **GPU profile**:

- The **CPU profile** is the minimum conformance level. It requires support for `DeviceKind::Cpu`
  and `BackendTarget::Cpu`.
- The **GPU profile** extends the CPU profile with `DeviceKind::Gpu` and `BackendTarget::Gpu`,
  and a stable contract for how GPU backends are selected and reported as unavailable.

## Runtime model

A conforming runtime provides an abstraction capable of:

- Allocating tensors from a **tensor descriptor** containing shape, dtype, and optional device.
- Executing named **operations** matching the Core IR instruction set by providing a mechanism that
  consumes inputs and produces outputs deterministically.
- Synchronising device/stream state where relevant.

The interface is intentionally language-agnostic; concrete API surfaces MAY differ by implementation
but MUST provide equivalent capabilities.

## Devices and backends

Core v1 assumes an abstract pair:

- **Device kind** (e.g. `Cpu`, `Gpu`).
- **Backend target** (e.g. `Cpu`, `Gpu`), which selects a concrete implementation.

Runtimes that implement the **CPU profile** MUST:

- Support at least one CPU device.
- Expose a CPU backend target capable of executing canonical Core IR.

Runtimes that implement the **GPU profile** MUST, in addition:

- Support at least one GPU device (or device group) and expose a `Gpu` backend target.
- Preserve Core v1 determinism guarantees for a given module and input set, modulo implementation
  limits documented by the runtime.
- Report unsupported or unavailable GPU backends via a **stable error surface**:
  - If the selected GPU backend is not compiled in or not available at runtime, a
    backend-selection error MUST be reported and execution MUST NOT proceed.
  - Such errors MUST be distinguishable from CPU runtime errors and IR verification failures.

Runtimes MAY support additional devices or backends (e.g. specialised accelerators). Behaviour
of those non-Core backends is implementation-defined, provided it does not violate the Core v1
IR semantics for the CPU and GPU profiles.

### Backend selection errors

If a caller selects a backend target that the runtime cannot execute (for example, `Gpu` in a
CPU-only build), the runtime MUST:

- Reject execution with a backend-selection error.
- Avoid any partial execution side effects.
- Provide a diagnostic that identifies the unsupported `BackendTarget` value.

## Responsibilities

- **Semantic fidelity**: runtime implementations MUST execute operations in accordance with the IR
  semantics defined in [Core IR](./ir.md) and [Shapes](./shapes.md).
- **Determinism**: given canonical IR and identical inputs, runtimes MUST produce identical outputs
  within numeric precision guarantees of the dtype.
- **Unsupported operations**: when an operation is not implemented, the runtime MUST return a
  well-defined error (e.g. “unsupported operation”) rather than exhibiting undefined behaviour.
- **Resource management**: allocation and deallocation semantics are implementation-defined but MUST
  not violate the deterministic execution model.

Performance considerations (threading, SIMD usage, accelerator integration) are **out of scope** for
this specification. Implementations MAY optimise freely provided they preserve the semantics above.

## Error model

- **Backend selection errors**: runtimes MUST surface structured errors when a requested backend
  target (e.g. `BackendTarget::Gpu`) is unavailable or feature-gated, and MUST apply the stable
  error semantics described above for the GPU profile.

## Reference implementation status (`star-ga/mind-runtime`)

### GPU profile operations

The reference runtime (`star-ga/mind-runtime`) implements **production-grade GPU backends**:

| Backend | Status | Features |
|---------|--------|----------|
| **Metal** | Production | macOS/iOS, poison-safe locking, defragmentation, context recovery |
| **ROCm/HIP** | Production | AMD GPUs, full trait implementations, stream sync |
| **WebGPU** | Production | Cross-platform (browsers, native), WGSL shaders |
| **CUDA** | Production | NVIDIA GPUs, advanced allocator, comprehensive tests |

All backends implement:
- **Poison-safe locking** via `MutexExt.lock_or_recover()`
- **Defragmenter trait** with fragmentation scoring
- **ContextRecovery trait** for automatic recovery from poisoned contexts
- **StreamSync** for cross-stream buffer safety
- **Drop with metrics flush** for production observability

**GPU-supported operations (19)**:
- Reductions: `sum_all`, `mean_all`, `sum`, `mean`
- Elementwise: `add`, `mul`, `relu`
- Linear algebra: `matmul`, `dot`, `conv2d`
- Shape ops: `reshape`, `expand_dims`, `squeeze`, `transpose`
- Indexing: `index`, `slice`, `gather`
- GPU-specific: `copy`, `fill`

> **Note**: All GPU backends implement native kernels for their respective platforms (Metal shaders,
> HIP/CUDA kernels, WGSL compute shaders). CPU fallback is available for unsupported operations.

### GPU tensor constraints

All GPU tensors MUST satisfy the following constraints:

| Constraint | Requirement |
|------------|-------------|
| Device | `DeviceKind::Gpu` |
| Dtype | `f32` only |
| Alignment | `numel % 4 == 0` (element count must be multiple of 4) |

Tensors that violate these constraints MUST be rejected at allocation time or prior to execution.

### GPU operation semantics

**copy** (1 input, 1 output):
Copies input tensor to output tensor. Shapes must match exactly.

**fill** (1 input, 1 output):
Fills the output tensor with a constant value. Due to the GPU alignment constraint
(`numel % 4 == 0`), scalar 1-element tensors cannot be allocated on GPU. Therefore,
the fill value is read from `inputs[0].data[0]` — the first element of the input tensor.
The remaining elements of the input tensor are ignored (padding).

Example (pseudocode):
```
value_tensor = allocate(shape=[4], device=Gpu)  // 4 elements for alignment
write(value_tensor, [42.0, 0.0, 0.0, 0.0])      // fill value in first element

output = allocate(shape=[8], device=Gpu)
run_op("fill", inputs=[value_tensor], outputs=[output])
// output now contains [42.0, 42.0, 42.0, 42.0, 42.0, 42.0, 42.0, 42.0]
```

### Target hardware

- **CUDA version**: 12+ (production)
- **ROCm/HIP**: 5.0+ (production)
- **Metal**: macOS 10.15+ / iOS 13+ (production)
- **WebGPU**: Chrome 113+, Firefox 120+, Safari 17+ (production)
- **LLVM version**: 18 (for JIT adapter)
- **Rust version**: 1.73+ (minimum)

### Integer overflow handling

The runtime uses different strategies based on context:

- **Checked arithmetic**: Used for user-controlled inputs (shapes, axes); returns `ExecError::InvalidArg` on overflow
- **Saturating arithmetic**: Used for stride calculations; saturates to `usize::MAX`
- **Wrapping arithmetic**: Used for safe reverse-indexing in `broadcast_shape()`

## Distributed execution

The reference runtime provides production-grade distributed training primitives:

### Transport layer

TCP-based transport with connection pooling, message serialization, and ring topology helpers:

| Component | Description |
|-----------|-------------|
| `TcpTransport` | Connection management with configurable timeouts and buffer sizes |
| `TransportConfig` | Bind address, connect timeout, buffer size configuration |
| `Message` / `MessageType` | Serialization protocol for collective operations |
| Ring topology | `left_neighbor()`, `right_neighbor()` helpers for ring-based collectives |

### Communication backends

Abstract `Backend` trait with concrete implementations:

| Backend | Target | Features |
|---------|--------|----------|
| `NcclBackend` | NVIDIA GPU | FFI bindings to NCCL library, optimized for GPU clusters |
| `GlooBackend` | CPU / cross-platform | Pure Rust implementation, TCP/IP transport |

Both backends implement:
- `all_reduce(tensor, op)` - Sum, Average, Max, Min, Product operations
- `broadcast(tensor, root)` - Distribute from root to all workers
- `all_gather(input, output)` - Gather tensors from all workers
- `reduce_scatter(input, output, op)` - Reduce and scatter result
- `barrier()` - Synchronization barrier

### Collective operations

Bandwidth-optimal `RingAllReduce` implementation:

- **Phase 1 (Scatter-reduce)**: N-1 iterations, each worker sends chunk to right neighbor and reduces incoming chunk
- **Phase 2 (All-gather)**: N-1 iterations, propagate final reduced chunks around the ring
- **Efficiency**: Each worker sends/receives 2*(N-1)/N of total data

Supported reduction operations:
- `Sum` (default)
- `Average`
- `Max`
- `Min`
- `Product`

### Fault tolerance

Elastic training with automatic failure detection and recovery:

| Component | Description |
|-----------|-------------|
| `FaultToleranceConfig` | min/max workers, elastic mode, checkpoint interval, heartbeat settings |
| `WorkerFailure` | Tracks rank, detection time, failure reason, handled status |
| `FailureReason` | HeartbeatTimeout, WorkerError, NetworkFailure, ProcessCrash, Unknown |
| `ClusterHealth` | total/alive/ready workers, pending failures, cluster state, can_train flag |
| `RecoveryAction` | Continue, WaitForReplacement, RestartFromCheckpoint, Abort |

Recovery workflow:
1. Heartbeat monitoring detects missed heartbeats
2. Worker marked as failed after `max_heartbeat_misses` consecutive misses
3. Recovery action determined based on cluster state and configuration
4. Elastic mode allows training to continue with remaining workers
5. Checkpoint-based recovery restores training state on failure

### Pipeline parallelism

`PipelineScheduler` for model partitioning across devices:

| Component | Description |
|-----------|-------------|
| `PipelineStage` | Stage index, layer range, assigned device |
| `MicroBatch` | Batch ID, stage, forward/backward data |
| `ScheduleType` | GPipe (synchronous), PipeDream (asynchronous), Interleaved |

Pipeline execution overlaps forward and backward passes across micro-batches for improved throughput.

### Coordinator

`DistributedCoordinator` manages cluster state:

- Worker registration and heartbeat tracking
- Cluster state machine (Initializing, Running, Paused, Failed, Shutdown)
- Failure detection and recovery coordination
- Checkpoint management with `CheckpointInfo`
- Builder pattern via `CoordinatorBuilder` for flexible initialization
