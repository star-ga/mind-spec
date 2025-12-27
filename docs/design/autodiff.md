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

# Autodiff Design (Informative)

> **Status:** Stable
> **Last updated:** 2025-12-19
> **Specification reference:** [autodiff.md](../../spec/v1.0/autodiff.md)

This document explains the design rationale and implementation strategy for
MIND's automatic differentiation system.

---

## Overview

MIND uses **reverse-mode automatic differentiation** (backpropagation) as its
primary differentiation strategy. This is implemented as an IR-to-IR transformation
that produces gradient modules from forward computation modules.

## Differentiation Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Reverse-Mode Autodiff Pipeline                         │
└─────────────────────────────────────────────────────────────────────────────┘

   Forward IR Module                    Gradient IR Module
   ─────────────────                    ──────────────────

   %0 = Input("x")                      # Forward pass (unchanged)
   %1 = Input("y")                      %0 = Input("x")
   %2 = BinOp(Mul, %0, %1)              %1 = Input("y")
   %3 = Sum(%2, [], false)              %2 = BinOp(Mul, %0, %1)
   outputs: %3                          %3 = Sum(%2, [], false)

                                        # Backward pass (generated)
              ────────▶                 %4 = ConstF32(1.0)        # seed
                                        %5 = Expand(%4, [M,N])    # Sum grad
                                        %6 = BinOp(Mul, %1, %5)   # dx
                                        %7 = BinOp(Mul, %0, %5)   # dy

                                        outputs: %3, %6, %7
```

## Design Decisions

### 1. IR-Level Transformation

**Decision:** Differentiation operates on Core IR, not source AST.

**Rationale:**
- IR is simpler and normalized (no syntax sugar)
- Enables differentiation of code from any frontend
- Verification guarantees well-formed inputs
- Easier to reason about and test

### 2. Reverse Mode (Backpropagation)

**Decision:** Use reverse-mode AD for all gradients.

**Rationale:**
- Efficient for typical ML workloads (many inputs → scalar loss)
- O(1) backward pass relative to forward (vs O(n) for forward mode)
- Standard in ML frameworks (PyTorch, JAX, TensorFlow)

**Trade-off:**
- Forward mode would be more efficient for scalar → many outputs
- Could add forward mode in future versions

### 3. VJP as Primitive

**Decision:** Vector-Jacobian Product (VJP) is the fundamental primitive.

**Rationale:**
- VJP computes `v^T @ J` efficiently without forming full Jacobian
- Composes naturally with chain rule
- Standard interface for custom gradients

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              VJP Composition                                 │
└─────────────────────────────────────────────────────────────────────────────┘

   Forward: y = f(g(x))

   Backward (chain rule):

   ∂L/∂x = (∂L/∂y) @ (∂y/∂g) @ (∂g/∂x)
         = vjp_g(vjp_f(∂L/∂y))

   Each VJP transforms gradient from output to input space.
```

### 4. Gradient Rules per Operation

**Decision:** Each Core IR operation has a defined gradient rule.

**Rationale:**
- Complete coverage of instruction set
- Predictable gradient behavior
- Easy to verify correctness

**Key gradient rules:**

| Operation | Forward | Backward (VJP) |
|-----------|---------|----------------|
| BinOp(Add, a, b) | a + b | (grad, grad) |
| BinOp(Mul, a, b) | a * b | (b * grad, a * grad) |
| Sum(x, axes) | sum(x) | broadcast(grad, x.shape) |
| MatMul(A, B) | A @ B | (grad @ B^T, A^T @ grad) |
| Relu(x) | max(0, x) | grad * (x > 0) |

### 5. Static vs Dynamic

**Decision:** Gradients are computed statically on IR.

**Rationale:**
- No runtime tracing overhead
- Enables ahead-of-time optimization
- Predictable memory usage
- Supports compilation to GPU kernels

**Trade-off:**
- Control flow requires unrolling or structured AD
- Dynamic computation graphs need re-differentiation

## Gradient Accumulation

When a value is used multiple times, gradients accumulate:

```
   Forward:                          Backward:

   %0 = Input("x")                   # x used twice in forward
   %1 = BinOp(Mul, %0, %0)           # d(x*x)/dx = 2x
   %2 = Sum(%1)
                                     # Gradient for %0 accumulates:
                                     # grad_x = grad_from_left + grad_from_right
                                     #        = %0 * grad + %0 * grad
                                     #        = 2 * %0 * grad
```

## Broadcasting in Gradients

Gradients must handle broadcasting inversely:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Broadcasting and Gradients                           │
└─────────────────────────────────────────────────────────────────────────────┘

   Forward:                              Backward:

   a: [3, 4]    ─┐                      grad_out: [3, 4]
                 ├── broadcast ──▶ c    ──────────────┬─▶ grad_a: [3, 4]
   b: [4]       ─┘     add                            │
                                                      └─▶ grad_b: [4]
                                                          (sum over axis 0)

   When shapes differ, gradient for smaller tensor sums over broadcast dims.
```

## Memory Considerations

Reverse-mode AD requires saving intermediate values ("tape"):

```
   Forward Pass                         Backward Pass

   %0 = Input                           # Saved values needed:
   %1 = MatMul(%0, W1)     ─ save ─▶    %0, %1, %2 for backward
   %2 = Relu(%1)           ─ save ─▶
   %3 = MatMul(%2, W2)     ─ save ─▶
   %4 = Loss(%3, target)

   Memory = O(depth * tensor_size)
```

**Optimization strategies:**
- Checkpointing: recompute instead of save
- Gradient accumulation: process batches incrementally
- Memory-efficient attention patterns

## Error Handling

Autodiff can fail for several reasons (E5xxx errors):

| Error | Cause | Resolution |
|-------|-------|------------|
| E5001 | Non-differentiable operation | Use stop_gradient or custom VJP |
| E5002 | Integer dtype input | Cast to float or mark as non-differentiable |
| E5003 | Missing custom gradient | Implement custom VJP |
| E5004 | Gradient shape mismatch | Fix custom gradient implementation |

## Future Considerations

### Forward Mode

Could add for Jacobian-vector products (JVP) when efficient:
- Sensitivity analysis
- Computing specific Jacobian columns

### Higher-Order Differentiation

Differentiating gradient functions:
- Hessian-vector products
- Second-order optimization

### Control Flow

Structured AD for:
- Loops with fixed bounds
- Conditional branches

---

[Back to Design Index](./index.md) | [Autodiff Spec](../../spec/v1.0/autodiff.md)
