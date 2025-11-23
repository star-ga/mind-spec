import React from 'react';
import Link from 'next/link';

export default function TensorLibPage() {
  return (
    <div className="max-w-4xl">
      <h1 className="text-4xl font-bold text-slate-900 mb-4">Tensor Library</h1>
      <p className="text-xl text-slate-600 mb-8 leading-relaxed">
        The <code>std::tensor</code> module provides the core primitives for N-dimensional array construction 
        and linear algebra. It is designed to be the foundational building block for all AI workloads in MIND.
      </p>

      {/* Module Overview */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 mb-12">
        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Module Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="text-xs font-semibold text-slate-400 block mb-1">Import</span>
            <code className="text-sm text-indigo-600 bg-white border border-slate-200 px-2 py-1 rounded">
              use std::tensor;
            </code>
          </div>
          <div>
             <span className="text-xs font-semibold text-slate-400 block mb-1">Performance</span>
             <p className="text-sm text-slate-600">
               Backed by MLIR/LLVM. Operations are zero-copy where possible.
             </p>
          </div>
        </div>
      </div>

      <h2 className="text-2xl font-bold text-slate-900 mt-12 mb-6">Constructors</h2>
      
      {/* zeros() */}
      <div className="mb-12 border-b border-slate-100 pb-10">
        <h3 className="font-mono text-lg text-indigo-700 mb-2">zeros</h3>
        <code className="block bg-slate-900 text-slate-50 p-4 rounded-md font-mono text-sm mb-4">
          fn zeros(shape: [i64]) -&gt; Tensor
        </code>
        <p className="text-slate-700 mb-4">
          Allocates a new contiguous tensor of the specified <code>shape</code>, initialized with all elements set to <code>0.0</code>.
        </p>
        
        <h4 className="font-bold text-slate-900 text-sm mb-2">Parameters</h4>
        <ul className="list-disc pl-5 text-slate-600 mb-4 space-y-1">
          <li><code>shape</code>: A compile-time or runtime array of integers defining the dimensions (e.g., <code>[3, 224, 224]</code>).</li>
        </ul>

        <h4 className="font-bold text-slate-900 text-sm mb-2">Example</h4>
        <pre className="bg-slate-50 border border-slate-200 p-4 rounded-md text-sm text-slate-800 overflow-x-auto">
{`// Create a 2x3 matrix of zeros
let z = tensor::zeros([2, 3]);
print(z);
// Output: [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]`}
        </pre>
      </div>

      {/* ones() */}
      <div className="mb-12 border-b border-slate-100 pb-10">
        <h3 className="font-mono text-lg text-indigo-700 mb-2">ones</h3>
        <code className="block bg-slate-900 text-slate-50 p-4 rounded-md font-mono text-sm mb-4">
          fn ones(shape: [i64]) -&gt; Tensor
        </code>
        <p className="text-slate-700 mb-4">
          Allocates a new contiguous tensor of the specified <code>shape</code>, initialized with all elements set to <code>1.0</code>.
        </p>
        <h4 className="font-bold text-slate-900 text-sm mb-2">Example</h4>
        <pre className="bg-slate-50 border border-slate-200 p-4 rounded-md text-sm text-slate-800">
{`let mask = tensor::ones([1, 512]);`}
        </pre>
      </div>

      {/* eye() */}
      <div className="mb-12 border-b border-slate-100 pb-10">
        <h3 className="font-mono text-lg text-indigo-700 mb-2">eye</h3>
        <code className="block bg-slate-900 text-slate-50 p-4 rounded-md font-mono text-sm mb-4">
          fn eye(n: i64) -&gt; Tensor
        </code>
        <p className="text-slate-700 mb-4">
          Constructs a square <code>n x n</code> identity matrix with ones on the main diagonal and zeros elsewhere.
        </p>
      </div>

      <h2 className="text-2xl font-bold text-slate-900 mt-12 mb-6">Operations</h2>

      {/* matmul() */}
      <div className="mb-12 border-b border-slate-100 pb-10">
        <h3 className="font-mono text-lg text-indigo-700 mb-2">matmul</h3>
        <code className="block bg-slate-900 text-slate-50 p-4 rounded-md font-mono text-sm mb-4">
          fn matmul(a: Tensor, b: Tensor) -&gt; Tensor
        </code>
        <p className="text-slate-700 mb-4">
          Performs matrix multiplication. This operation supports automatic broadcasting for batched inputs.
          Backends (CPU/GPU) are selected automatically at runtime.
        </p>

        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6">
          <p className="text-amber-900 text-sm">
            <strong>Note:</strong> Inner dimensions must match. If <code>a</code> is <code>(M, K)</code> and <code>b</code> is <code>(K, N)</code>, the result is <code>(M, N)</code>.
            Dimension mismatches raise a runtime error (or compile-time error if shapes are static).
          </p>
        </div>

        <h4 className="font-bold text-slate-900 text-sm mb-2">Complexity</h4>
        <p className="text-slate-600 mb-4 text-sm">
          O(M * N * K) - Optimized via BLAS or CUTLASS backends.
        </p>

        <h4 className="font-bold text-slate-900 text-sm mb-2">Example: Linear Layer</h4>
        <pre className="bg-slate-50 border border-slate-200 p-4 rounded-md text-sm text-slate-800 overflow-x-auto">
{`let input  = tensor::zeros([32, 128]); // Batch 32, Dim 128
let weight = tensor::ones([128, 64]);  // Dim 128, Out 64

// Result shape: [32, 64]
let output = tensor::matmul(input, weight);`}
        </pre>
      </div>

      {/* transpose() */}
      <div className="mb-12">
        <h3 className="font-mono text-lg text-indigo-700 mb-2">transpose</h3>
        <code className="block bg-slate-900 text-slate-50 p-4 rounded-md font-mono text-sm mb-4">
          fn transpose(x: Tensor) -&gt; Tensor
        </code>
        <p className="text-slate-700 mb-4">
          Swaps the last two dimensions of the tensor. For a 2D matrix, this is a standard transposition.
        </p>
        <h4 className="font-bold text-slate-900 text-sm mb-2">Example</h4>
        <pre className="bg-slate-50 border border-slate-200 p-4 rounded-md text-sm text-slate-800">
{`let m = tensor::eye(3); // 3x3
let t = tensor::transpose(m);`}
        </pre>
      </div>

    </div>
  );
}
