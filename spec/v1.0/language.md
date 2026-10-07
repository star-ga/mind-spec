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

# Surface Language (Normative)

This chapter summarises the Core v1 surface language constructs that compile down to the Core IR.
Detailed lexical and type rules continue to live in the legacy chapters ([`lexical.md`](./lexical.md),
[`types.md`](./types.md)); this document consolidates the tensor-oriented subset implemented in
[`star-ga/mind`](https://github.com/star-ga/mind).

## Syntax overview

- **Modules and functions**: programs are organised as modules containing functions. Functions declare
  named parameters and return values and compile to IR module inputs/outputs.
- **Expressions**: include literals, binary operators (`+`, `-`, `*`), unary operators (e.g. `-`),
  function calls, and tensor constructors.
- **Tensor literals**: may appear with explicit dtype annotations. Rank-0 literals represent scalars.
- **Control flow**: the Core v1 spec models straight-line tensor programs; high-level control flow is
  lowered away before entering the Core IR described in [Core IR](./ir.md).

## Operator precedence and associativity

Operators are listed from highest precedence (evaluated first) to lowest precedence (evaluated last).
Operators on the same level have equal precedence and are resolved by associativity.

| Precedence | Operator | Description | Associativity | Example |
|------------|----------|-------------|---------------|---------|
| **1 (Highest)** | `()` `[]` `.` | Grouping, indexing, field access | Left-to-right | `f(x)`, `a[i]`, `x.field` |
| **2** | Unary `-` `!` | Negation, logical NOT | Right-to-left | `-x`, `!flag` |
| **3** | `*` | Multiplication (elementwise) | Left-to-right | `a * b` |
| **4** | `+` `-` | Addition, subtraction (elementwise) | Left-to-right | `a + b`, `a - b` |
| **5** | `==` `!=` `<` `>` `<=` `>=` | Comparison operators | Left-to-right | `a == b`, `x < y` |
| **6** | `&&` | Logical AND | Left-to-right | `a && b` |
| **7** | `||` | Logical OR | Left-to-right | `a || b` |
| **8** | `=` `+=` `-=` `*=` `:=` | Assignment and compound assignment | Right-to-left | `x = y`, `x += 1` |
| **9 (Lowest)** | `,` | Comma (sequence) | Left-to-right | `f(a, b, c)` |

### Precedence rules

1. **Higher precedence binds tighter**: `a + b * c` parses as `a + (b * c)`, not `(a + b) * c`
2. **Same precedence uses associativity**: `a - b + c` parses as `(a - b) + c` (left-to-right)
3. **Parentheses override precedence**: `(a + b) * c` forces addition before multiplication
4. **Function calls have highest precedence**: `f(x) + g(y)` calls functions before addition

### Examples

**Example 1: Arithmetic precedence**
```mind
let result = a + b * c - d;
// Parses as: a + (b * c) - d
// Then: (a + (b * c)) - d
```

**Example 2: Unary operators**
```mind
let neg_sum = -a + b;
// Parses as: (-a) + b

let double_neg = - -x;
// Parses as: -(- x)
```

**Example 3: Comparison and logical**
```mind
let cond = x < y && a == b;
// Parses as: (x < y) && (a == b)

let complex = a + b > c * d || flag;
// Parses as: ((a + b) > (c * d)) || flag
```

**Example 4: Assignment and compound assignment**
```mind
x = y = z;
// Parses as: x = (y = z)  (right-to-left)

a += b * c;
// Parses as: a = a + (b * c)  (compound assignment expands to assignment)
```

**Example 5: Function calls and indexing**
```mind
let value = f(x)[0] + g(y).field;
// Parses as: (f(x)[0]) + (g(y).field)
// Function calls f() and g() are evaluated first
// Then indexing [0] and field access .field
// Finally addition +
```

### Broadcasting and tensor operations

Tensor operations follow the same precedence as scalar operations:

- **Elementwise multiplication**: `A * B` where A, B are tensors uses same precedence as scalar `*`
- **Broadcasting applies**: `scalar * tensor` broadcasts scalar to tensor shape
- **Matrix multiplication**: Uses function call syntax `matmul(A, B)`, not infix operator
  - This gives it highest precedence: `matmul(A, B) + C` performs matmul first

**Example: Tensor arithmetic**
```mind
let result = alpha * X + beta * Y;
// Parses as: (alpha * X) + (beta * Y)
// Both multiplications happen before addition
// Broadcasting applies within each multiplication
```

### Associativity edge cases

**Left-associative subtraction**:
```mind
a - b - c  // Parses as (a - b) - c, NOT a - (b - c)
// Important: these are different!
// (5 - 3) - 2 = 0
// 5 - (3 - 2) = 4
```

**Right-associative assignment**:
```mind
a = b = c = 0;  // Parses as a = (b = (c = 0))
// All three variables assigned to 0
```

### Precedence vs type checking

Precedence determines parse tree structure, not type validity:

```mind
let invalid = tensor + 5;  // Parses correctly as (tensor + 5)
                           // But may fail type checking if dtypes incompatible
```

Type errors are caught AFTER parsing, during type checking phase.

### Comparison with other languages

| Language | Multiplication precedence | Assignment associativity |
|----------|---------------------------|--------------------------|
| MIND | Higher than addition | Right-to-left |
| Python | Higher than addition | Right-to-left |
| C/C++ | Higher than addition | Right-to-left |
| Julia | Higher than addition | Right-to-left |

MIND follows the **standard mathematical convention** used in most programming languages.

### Floating-point comparisons

For `f32` and `f64` operands, `<`, `<=`, `>`, `>=` and `==` are IEEE 754 ordered comparisons: each is
false when either operand is NaN. `!=` is true when either operand is NaN, so `NaN != NaN` is true.
`-0.0 == 0.0` is true (negative zero equals positive zero). Consequently `!(a < b)` and `a >= b`
differ when an operand is NaN. This is a clarification: it restates, for comparisons, the IEEE 754
requirement in the numeric-overflow rule of [Security and Safety](./security.md#tensor-safety) and
adds no operator.

**Implementation status (informative).**

- The reference MLIR path emits `arith.cmpf` with the ordered predicates `olt`, `ole`, `ogt`, `oge`
  and `oeq`. Since compiler `2597ee9c` (pending release) it emits the unordered `une` for `!=`; the
  v0.10.2 release used the ordered `one`, so `NaN != NaN` was false there.
- The native x86-64 backend (`--backend native`) matches this for `f64` since `ccbb00b8` (pending
  release). The evidence is one script gate: 14 operand pairs plus one NaN program, each also built
  with the MLIR backend, with the pair programs checked against Python float comparisons. That gate is
  run in preflight, not in CI, and covers `f64` on x86-64 only. The compiler independence audit
  records the gate as exiting 1 (its wording: "3 of 5 in-profile programs fail"), and the `ccbb00b8`
  commit message records three helper-intrinsic programs and the tensor first-fence fixture as
  already red before it. No passing run is attached here; that the 15 comparison programs pass is
  inferred from that commit message, which names only those four items as red. The 14 pair programs
  pass their operands as parameters of one function (`fn k(x: f64, y: f64)`); the NaN program
  compares a local variable with the literal `0.0`. The backend's first admission check refuses
  `f32`, `f16` and `bf16` scalars (`a1b0b5f5`), so `f32` comparisons are not available there.
- The reference `mindc test` evaluator has an open defect for `f64` comparisons used as `if` or
  `while` conditions or as `match` guards: it treats only an integer 0 as false (compiler
  independence audit, finding 15, `docs/independence-audit-plan-20260925.md` in `star-ga/mind`). Its
  verdicts are therefore not evidence for this rule.

### Grammar reference

For the complete formal grammar including precedence, see:
- **Lexical grammar**: [`grammar-lexical.ebnf`](./grammar-lexical.ebnf)
- **Syntax grammar**: [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) (expression precedence encoded in production rules)

## Types

The type system relevant to Core v1 consists of:

- **Scalar types**: numeric primitives supported by the compiler (e.g. `i64`, `f32`).
- **Tensor types**: parameterised by `dtype` and **shape**. Shape dimensions may be statically known
  integers or implementation-defined symbolic sizes where supported.
- **Shape descriptors**: ordered lists of dimensions. Shapes appear in type annotations and IR
  metadata. Device placements MAY be attached but are otherwise outside the Core v1 scope.

## Tensor operations

Surface syntax maps to the Core IR instruction set:

- **Arithmetic**: `+`, `-`, `*` lower to `BinOp` with broadcasting semantics from
  [Shapes](./shapes.md#broadcasting). Division is not part of Core v1 (see
  [IR spec](./ir.md#binary-operations)).
- **Type checking for arithmetic**: operands MUST share a dtype; shape inference uses broadcasting
  rules so scalars implicitly extend to the non-scalar operand's shape.
- **Reductions**: `sum(x, axes, keepdims)` and `mean(x, axes, keepdims)` lower to `Sum`/`Mean`.
- **Shape ops**: `reshape`, `transpose`, `expand_dims`, and `squeeze` mirror their IR counterparts.
- **Indexing**: slicing/index expressions lower to `Index`, `Slice`, or `Gather` depending on syntax.
- **Linear algebra**: `dot`, `matmul`, and `conv2d` are available as intrinsic functions mapping to the
  IR operations described in [Core IR](./ir.md#linear-and-tensor-algebra). `matmul` requires rank-2 or
  higher operands and validates contracting dimensions before emission.

Implementations MUST reject programs that request unsupported operations or incompatible shapes
according to the verification rules in [Core IR](./ir.md).

## Relationship to Core IR

Compilation of the surface language yields canonical IR modules that obey:

- **SSA-style value production** via ordered `ValueId`s.
- **Explicit tensor metadata** for dtype and shape.
- **Deterministic lowering** enabling repeatable autodiff and MLIR generation.

### Canonical translation pipeline

Surface constructs lower to the Core IR through a deterministic, type-directed
pipeline:

1. **Symbols become inputs**: every free variable in the expression context
   materialises as an `Input` instruction that records its declared type and
   shape metadata.
2. **Literals become constants**: scalar or tensor literals emit
   `ConstTensor` instructions with dtype and shape encoded explicitly.
3. **Operators become IR instructions**: arithmetic expressions lower to `BinOp`
   (with `Add`, `Sub`, or `Mul` semantics) and other intrinsic operations map to
   the IR instruction set described in [Core IR](./ir.md).
4. **Outputs are explicit**: the last produced `ValueId` is marked as the
   module output to preserve the single-definition rule.

Implementations are expected to reuse the type system rules in
[Types](./types.md) during translation so that invalid programs are rejected
before IR is emitted.

Language features beyond this tensor core (e.g. generics, traits) are covered in the broader v1.0
specification but are not required for Core v1 conformance.

## Modules and imports

### Module-qualified references

> **Status:** normative correction, targeted for specification 1.7.0; it does not declare that
> release. Earlier text of the grammar wrote import paths with `::`, which no released reference
> compiler accepted for `import`, and left the meaning of a qualifier unspecified. The separator and
> the qualifier rule below were decided by the specification owner on 2026-10-07.

Import paths separate their segments with `.` (`import a.b;`). An import binds a qualifier in the
module that declares it: the last segment of its path (`b` for `import a.b;`). In that module, a
reference `q.m`, or a call `q.m(args)`, whose head `q` is an import qualifier denotes the member `m`
exported by the module that import names. It MUST resolve to that module's member even when another
imported module, or the current module, declares a member named `m`, and it MUST be refused with
`E2002` during checking and artifact-producing builds when that module exports no member `m`; a
refused build MUST leave no artifact. A qualified type or enum variant follows the same rule (see
[Types](./types.md)). This section does not decide precedence between an import qualifier and a
local binding of the same name; that remains open.

**Implementation status (informative).** The reference resolves qualified types and enum variants by
owner as described in [Types](./types.md) (manifest projects, `cross-module-imports`). It does not
yet select the owner of a qualified function call in `mindc check` and `mindc build`: `q.f(x)` and,
since `cd150ae7` (pending release), `q::f(x)` are parsed to the bare member name `f`, with the
qualifier kept beside the AST by source span, where only the formatter reads it; type checking and
lowering see only the bare member name. Two imported modules that both export a function `f`, called
as `a.f()` and `b.f()`, therefore check without a diagnostic but fail to link
(`multiple definition of 'f'`); measured on compiler main with `cd150ae7` applied (pending release).
The `mindc test` evaluator is different: under `cross-module-imports` it captures the qualifier
separately and binds the reference to the named import (see
[Conformance](./conformance.md#source-test-execution-and-module-scope)). The reference is not
conforming to this rule for functions until the owner of a qualified call is selected in
`mindc check` and `mindc build`.

## Executable-subset status (informative)

The reference implementation's shipped executable subset (v0.10.x) covers the surface above plus
the constructs listed in [STATUS.md](../../STATUS.md), with the following **honest boundaries** —
documentation MUST NOT present these as complete:

- **Enums + `match`**: the core works end-to-end (unit variants, payload variants including `f64`
  and multi-field payloads, discriminant/`Option`/payload matching). Exhaustiveness checking and
  nested patterns beyond the shipped forms are still maturing.
- **Generics**: a **bounded slice only** — a single type parameter over scalar types. There is no
  general parametric-polymorphism surface (no multi-parameter generics, no generic containers such
  as a user-defined `map<K, V>`); `where`-clause trait bounds are specified in
  [Types](./types.md) but not implemented.
- **Closures / first-class functions**: **not implemented**. Function values, closure capture, and
  higher-order functions are future extensions (see
  [Future Extensions](./future-extensions.md)); the compiler rejects fn-as-value use fail-loud. On
  compiler main a bare name of a function of the current module, or of a function-only
  standard-surface export, used as a value is refused with
  [`E2037`](./errors.md#e2037-function-name-used-as-a-value) (`1def5dde`, pending release); see that
  entry for its limit.
- **Traits**: **not implemented** in the executable subset (no `trait` declarations, no `dyn Trait`).
- **Slices**: stubbed; byte-level work goes through the `std.string`/`std.vec` heap records and the
  byte-precise intrinsics.
- **Collections**: region-allocator-backed; `std.vec` push is non-mutating (returns a fresh `Vec`),
  `std.map` is insert-only (no removal, no in-place update) — see
  [Standard Library](./stdlib.md#four-pure-mind-modules) for the precise shipped surface. These are
  not full `Vec`/`String`/`HashMap` equivalents.
- **Range `for` loops**: the range form `for v in s..e { ... }` is not yet in the grammar:
  [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) has a `ForExpression` over an arbitrary
  `Expression` but no range expression. The reference interpreter evaluates `e` once and binds `v`
  fresh on each iteration. On compiler main, compiled output follows it when the body re-declares
  `v` with `let` or a tuple `let`: the re-declaration shadows `v` from that statement to the end of
  the iteration and does not change the iteration count (`fe9854ec`, pending release; Rust IR
  lowering, not the pure-MIND native path). Before `fe9854ec`, compiler main built such a loop to an
  executable that did not terminate; the behaviour of v0.10.2 for this shape is not established
  here. Known gap: an end bound that reads memory the body mutates through an index or field store is
  not detected, so compiled output can re-evaluate it on each iteration.
- **Assertions**: `assert cond`, `assert cond, "message"` and the parenthesised
  `assert(cond, "message")` each assert `cond` (parenthesised form: `487dd5c7`, pending release);
  the message is kept as written between the quotes. A false condition aborts an executable built
  with the default MLIR backend (SIGABRT; the message text is not printed) and fails the test under
  `mindc test`; the native backend is not covered here. Any other parenthesised tuple condition,
  such as `assert(cond, 9)` or a three-element tuple, is a parse error; the reference reports it
  with code `E1001`, which it uses for every parse error that has no dedicated code (there is no
  dedicated code for this case). The messages are
  `an assert's second operand must be a string message: ...` and
  `an assert condition must be one expression, not a tuple`. v0.10.1 and v0.10.2 parsed the
  parenthesised pair as one tuple condition, which is always truthy, so a compiled executable never
  aborted on it (earlier releases did not lower `assert`). The condition is typed `bool` by the
  [`core` module](./stdlib.md#core-module).
- **Imports and module-qualified references**: the normative rule is in
  [Module-qualified references](#module-qualified-references) above. Reference status
  (informative): the reference also accepts `import a.b as c;` and `use a.b as c` (`f2fc890d`,
  pending release), registering both the alias and the last path segment as qualifiers; the `as`
  form is not in [`grammar-syntax.ebnf`](./grammar-syntax.ebnf). `use` also accepts `::` between
  path segments as an extension. A zero-argument `.sum()` or `.mean()` on a receiver named like an
  import is a module call, not a tensor reduction (`f2fc890d`).
