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
[`cputer/mind`](https://github.com/cputer/mind).

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
  [IR spec](./ir.md#arithmetic-operations)).
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
