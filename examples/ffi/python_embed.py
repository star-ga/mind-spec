#!/usr/bin/env python3
"""
MIND Language Example: Python Embedding
Specification reference: spec/v1.0/ffi.md#python-bindings

This example demonstrates:
1. Loading MIND modules from Python
2. Calling MIND functions with NumPy arrays
3. Automatic differentiation from Python
"""

import numpy as np

# Import MIND Python bindings
# Reference: spec/v1.0/ffi.md#python-bindings
import mind

# ============================================
# Loading and calling MIND functions
# ============================================

def basic_usage():
    """Demonstrate basic MIND function calls from Python."""

    # Load a compiled MIND module
    # Reference: spec/v1.0/ffi.md#python-bindings
    module = mind.load_module("my_module.mind")

    # Create input tensors as NumPy arrays
    a = np.array([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]], dtype=np.float32)

    b = np.array([[1.0, 1.0, 1.0],
                  [1.0, 1.0, 1.0]], dtype=np.float32)

    # Call MIND function
    # NumPy arrays automatically convert to MIND tensors
    result = module.add_tensors(a, b)

    # Result is a NumPy array
    print(f"Result shape: {result.shape}")  # (2, 3)
    print(f"Result:\n{result}")

    return result


# ============================================
# Automatic differentiation from Python
# Reference: spec/v1.0/ffi.md#python-bindings
# Reference: spec/v1.0/autodiff.md
# ============================================

def autodiff_example():
    """Demonstrate MIND autodiff from Python."""

    # Define a MIND function inline using mind.jit
    @mind.jit
    def loss_fn(x, y, w):
        """Compute MSE loss: mean((x @ w - y)^2)"""
        pred = mind.matmul(x, w)
        diff = pred - y
        return mind.mean(diff * diff)

    # Create training data
    x = np.random.randn(100, 10).astype(np.float32)
    y = np.random.randn(100, 1).astype(np.float32)
    w = np.random.randn(10, 1).astype(np.float32)

    # Compute loss
    loss = loss_fn(x, y, w)
    print(f"Loss: {loss}")

    # Compute gradients using MIND autodiff
    # Reference: spec/v1.0/autodiff.md
    grad_fn = mind.grad(loss_fn, argnums=2)  # gradient w.r.t. w
    grad_w = grad_fn(x, y, w)

    print(f"Gradient shape: {grad_w.shape}")  # (10, 1)

    # Gradient descent step
    learning_rate = 0.01
    w_new = w - learning_rate * grad_w

    return w_new


# ============================================
# Working with MIND IR from Python
# Reference: spec/v1.0/ir.md
# Reference: spec/v1.0/ffi.md
# ============================================

def ir_manipulation():
    """Demonstrate MIND IR access from Python."""

    # Parse MIND source to IR
    source = """
    fn square(x: Tensor<f32, [2, 3]>) -> Tensor<f32, [2, 3]> {
        x * x
    }
    """

    # Compile to IR module
    ir_module = mind.compile(source)

    # Inspect IR structure
    # Reference: spec/v1.0/ir.md#ir-module-model
    print(f"Number of operations: {len(ir_module.operations)}")
    print(f"Inputs: {ir_module.inputs}")
    print(f"Outputs: {ir_module.outputs}")

    # Print textual IR
    # Reference: spec/v1.0/ir.md#reference-encoding
    print("IR text:")
    print(ir_module.to_text())

    # Apply autodiff transformation
    # Reference: spec/v1.0/autodiff.md
    grad_module = mind.autodiff(ir_module)

    print("\nGradient IR:")
    print(grad_module.to_text())


# ============================================
# NumPy interoperability
# Reference: spec/v1.0/ffi.md#python-bindings
# ============================================

def numpy_interop():
    """Zero-copy NumPy interoperability."""

    # Create NumPy array
    np_array = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)

    # Convert to MIND tensor (zero-copy if contiguous)
    mind_tensor = mind.from_numpy(np_array)

    # Perform MIND operations
    result = mind.relu(mind_tensor)
    result = mind.sum(result, axes=[1], keepdims=False)

    # Convert back to NumPy (zero-copy)
    np_result = result.numpy()

    print(f"Result: {np_result}")  # [6.0, 15.0]


# ============================================
# Custom operations and extensions
# Reference: spec/v1.0/ffi.md
# ============================================

def custom_op_example():
    """Register custom operations from Python."""

    # Define a custom operation
    @mind.custom_op("my_activation")
    def my_activation_forward(x):
        """Custom activation: x * sigmoid(x) (SiLU/Swish)"""
        return x * (1.0 / (1.0 + np.exp(-x)))

    # Define custom gradient
    @my_activation_forward.defvjp
    def my_activation_backward(x, grad_output):
        """VJP for custom activation."""
        sig = 1.0 / (1.0 + np.exp(-x))
        return grad_output * (sig + x * sig * (1 - sig))

    # Use in MIND computation
    x = np.array([[-1.0, 0.0, 1.0]], dtype=np.float32)
    result = mind.my_activation(x)

    print(f"Custom op result: {result}")


if __name__ == "__main__":
    print("=== Basic Usage ===")
    basic_usage()

    print("\n=== Autodiff Example ===")
    autodiff_example()

    print("\n=== IR Manipulation ===")
    ir_manipulation()

    print("\n=== NumPy Interop ===")
    numpy_interop()

    print("\n=== Custom Op ===")
    custom_op_example()
