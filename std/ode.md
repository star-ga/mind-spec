<!--
MIND Language Specification — Community Edition

Copyright 2025-2026 STARGA Inc.
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

# ODE Library

> **Status: informative / design-stage — not part of the shipped executable subset.** The
> signatures below use first-class function values (`fn(f64) -> f64` fields) and the
> `on(gpu0) { parallel for }` placement construct, neither of which is implemented in the
> reference compiler (v0.10.x): closures/function values are a future extension and GPU execution
> is roadmap. The `remizov_*.mind` sources live under `examples/` in `star-ga/mind` as design
> artifacts. All performance tables in this chapter are **expected/projected** figures, not
> measurements from the shipped toolchain — the GPU-scaling table in particular describes a
> backend that does not yet exist.

The `std::ode` module provides solvers for second-order linear ordinary differential equations
with variable coefficients, based on the Remizov (2025) universal formula using Chernoff
approximation of operator semigroups.

## Problem Class

Solves equations of the form:

```
a(x) f''(x) + b(x) f'(x) + (c(x) - lambda) f(x) = -g(x)
```

where `a`, `b`, `c`, `g` are known coefficient functions of `x`, `lambda` is a real spectral
parameter, and `f` is the unknown solution.

### Requirements

- `a(x) > 0` for all `x` in the domain (strictly positive leading coefficient)
- `lambda > sup |c(x)|` (spectral parameter must exceed supremum of |c|)
- `a`, `b`, `c` must be bounded and uniformly continuous with bounded derivatives
- `g` must have bounded derivatives up to order 4 for the error bound to apply

## Types

### `ODECoefficients`
```
type ODECoefficients = {
    a: fn(f64) -> f64,    // Leading coefficient (must be > 0)
    b: fn(f64) -> f64,    // First-order coefficient
    c: fn(f64) -> f64,    // Zero-order coefficient
}
```

### `ODEProblem`
```
type ODEProblem = {
    coeffs: ODECoefficients,
    g: fn(f64) -> f64,               // Right-hand side source term
    lambda: f64,                      // Spectral parameter (must be > sup|c(x)|)
    domain: (f64, f64),               // Spatial domain [x_min, x_max]
}
```

### `ODESolution`
```
type ODESolution = {
    x: tensor<f64[N]>,               // Grid points
    f: tensor<f64[N]>,               // Solution values f(x_i)
    error_bound: f64,                 // Estimated error bound O(1/n_iter)
    n_iter: i32,                      // Number of Chernoff iterations used
    n_quad: i32,                      // Number of quadrature nodes used
}
```

### `ODEConfig`
```
type ODEConfig = {
    n_grid: i32,                      // Number of spatial grid points (default: 200)
    n_iter: i32,                      // Chernoff iteration count (default: 500)
    n_quad: i32,                      // Quadrature nodes for Laplace integral (default: 64)
    t_max: f64,                       // Truncation of Laplace integral [0, t_max] (default: 10.0)
}
```

## Core Solver Functions

### `remizov_solve`
```
fn remizov_solve(problem: ODEProblem, config: ODEConfig) -> ODESolution
```
Solves the ODE using Theorem 6 (translation-based Chernoff approximation).

**Algorithm:**
1. Discretize the domain into `n_grid` points via `linspace`.
2. For each Gauss-Laguerre quadrature node `t_k` with weight `w_k`:
   - Start with `h(x) = g(x)` on the grid.
   - Apply the shift operator `S(t_k / n_iter)` iteratively `n_iter` times.
   - Accumulate `w_k * h(x)` into the Laplace integral.
3. Return the solution on the grid.

**Error bound:** `O(1 / (n_iter * (lambda - ||c||)^3))`

**Complexity:** `O(n_grid * n_iter * n_quad)`

### `remizov_solve_gpu`
```
fn remizov_solve_gpu(problem: ODEProblem, config: ODEConfig) -> ODESolution
```
GPU-parallel version. Identical algorithm but parallelizes across grid points using
`on(gpu0) { parallel for }`. Each `x_i` is independent (embarrassingly parallel).

**Complexity:** `O(n_iter * n_quad)` wall-clock with `n_grid` parallel threads.

### `remizov_feynman`
```
fn remizov_feynman(problem: ODEProblem, config: ODEConfig, n_samples: i32) -> ODESolution
```
Solves using Theorem 5 (Feynman path integral formula). Uses Monte Carlo sampling
of Gaussian random paths. Convergence is `O(1/sqrt(n_samples))`.

### `remizov_inverse`
```
fn remizov_inverse(
    x_observed: tensor<f64[N]>,
    f_observed: tensor<f64[N]>,
    g: fn(f64) -> f64,
    lambda: f64,
    lr: f64,
    n_steps: i32
) -> ODECoefficients
```
Inverse problem: given observed solution `f(x)` and known `g(x)`, recovers the
ODE coefficients `a(x)`, `b(x)`, `c(x)` using gradient descent through the
differentiable Remizov solver.

### `remizov_solve_richardson`
```
fn remizov_solve_richardson(problem: ODEProblem, config: ODEConfig) -> ODESolution
```
Applies Richardson extrapolation to accelerate convergence from O(1/n) to O(1/n^2).
Solves twice (at `n_iter` and `2*n_iter`), then computes `f_R = 2*f_{2n} - f_n`.

**Effect:** `n_iter=100` with Richardson achieves comparable accuracy to `n_iter=1000`
without it. This is the recommended solver for most use cases.

**Cost:** 3x the compute of a single solve (n + 2n iterations).

## Helper Functions

### `linspace`
```
fn linspace(start: f64, end: f64, n: i32) -> tensor<f64[N]>
```
Returns `n` evenly spaced points in `[start, end]`.

### `gauss_laguerre_nodes`
```
fn gauss_laguerre_nodes(n: i32) -> (tensor<f64[N]>, tensor<f64[N]>)
```
Returns `(nodes, weights)` for `n`-point Gauss-Laguerre quadrature, used to
compute `integral_0^infinity e^{-t} f(t) dt ≈ sum_k w_k f(t_k)`.

### `interp_linear`
```
fn interp_linear(x_grid: tensor<f64[N]>, y_grid: tensor<f64[N]>, x_query: f64) -> f64
```
Piecewise linear interpolation. Given grid values, interpolates to an arbitrary query point.
Required because the shift operator evaluates `g` at non-grid points `x + 2*sqrt(a(x)*t)`.

## The Shift Operator

The translation-based shift operator from Theorem 6 (Remizov, 2025):

```
S(t) f(x) = (1/4) f(x + 2 sqrt(a(x) t))
           + (1/4) f(x - 2 sqrt(a(x) t))
           + (1/2) f(x + 2 b(x) t)
           + t c(x) f(x)
```

**Key property:** `lim_{t->0} (S(t)f - f) / t = a(x)f'' + b(x)f' + c(x)f`

The Chernoff product formula then gives:
```
e^{tA} f = lim_{n->inf} (S(t/n))^n f
```

And the ODE solution is recovered via Laplace transform:
```
f(x) = integral_0^infinity e^{-lambda t} (e^{tA} g)(x) dt
      ≈ integral_0^infinity e^{-lambda t} ((S(t/n))^n g)(x) dt
```

## Numerical Stability

### Interpolation Error Accumulation

Each application of the shift operator evaluates the function at non-grid points via
interpolation. With linear interpolation (O(h^2) per step) over `n_iter` steps, the total
interpolation error is `O(n_iter * h^2)`. This competes with the Chernoff convergence
`O(1/n_iter)`. For the errors to balance, the grid spacing must satisfy:

```
h = O(1/n_iter)    with linear interpolation
h = O(1/sqrt(n_iter))  with cubic spline interpolation
```

**Recommendation:** For n_iter=500, use at least n_grid=200 (h ≈ 0.05 on [-5,5]).

### Lambda Selection

Lambda must satisfy `lambda > sup|c(x)|`. In practice:

| Lambda choice | Behavior |
|---------------|----------|
| Near minimum | Slow Laplace decay; more quadrature nodes needed |
| 2-4x minimum | Good balance of accuracy and conditioning |
| 8-16x minimum | Fast convergence but small solution magnitude |
| Very large | Numerical underflow in solution values |

**Default:** `lambda = 4 * sup|c(x)| + 1.0`

### Divergence Conditions

The iteration diverges when:
- `lambda < sup(c(x))`: Laplace integral diverges
- `a(x) <= 0` at any point: shift becomes imaginary (ill-posed)
- Grid too coarse for the shift size: interpolation error dominates

## Expected Performance

### Accuracy (constant-coefficient test, n_grid=200, n_quad=24)

| Method | n_iter | L_inf Error | Correct Digits |
|--------|--------|-------------|:--------------:|
| Plain Chernoff | 100 | ~1e-2 | 2.0 |
| Plain Chernoff | 500 | ~2e-3 | 2.7 |
| Richardson | 100 | ~4e-5 | 4.4 |
| Richardson | 200 | ~1e-5 | 5.0 |

### GPU Scaling (n_iter=200, n_quad=20)

| n_grid | CPU/GPU Speedup |
|--------|:---------------:|
| 100 | ~1x |
| 1,000 | ~7x |
| 10,000 | ~25x |

### Comparison vs Finite Differences

| n_grid | FD Error (O(h^2)) | Remizov+Richardson |
|--------|------------------:|:------------------:|
| 50 | ~1.6e-2 | ~4e-5 |
| 200 | ~1.0e-3 | ~4e-5 |
| 800 | ~6.3e-5 | ~4e-5 |

Remizov accuracy is independent of grid size (depends on n_iter). Finite differences
require grid refinement for accuracy. Remizov does not require matrix assembly,
tridiagonal solves, or explicit boundary condition encoding.

## File Manifest

| File | Repository | Purpose |
|------|-----------|---------|
| `std/ode.md` | mind-spec | This specification |
| `remizov_solver.mind` | mind | Core solver + Richardson extrapolation |
| `remizov_gpu.mind` | mind | GPU-parallel solver + batch lambda sweep |
| `remizov_inverse.mind` | mind | Coefficient recovery via autodiff |
| `remizov_verify.mind` | mind | Verification suite (5 tests) |
| `remizov_feynman.mind` | mind | Monte Carlo Feynman path integral solver |
| `remizov_benchmark.mind` | mind | 6-benchmark performance suite |
| `remizov-ode-solver.mdx` | mindlang.dev | Documentation + benchmarks |

## References

- Remizov, I.D. (2025). "Chernoff approximations as a method for finding the resolvent
  of a linear operator and solving a linear ODE with variable coefficients."
  arXiv:2301.06765v4.
- Remizov, I.D. (2025). Vladikavkaz Mathematical Journal, Vol. 27, No. 4, pp. 124-135.
- Chernoff, P.R. (1968). "Note on product formulas for operator semigroups."
  J. Functional Analysis 2, 238-242.
- Remizov, I.D., Spatola, M. (2024). "Upper and lower estimates for rate of convergence
  in the Chernoff product formula." Israel Journal of Mathematics.
