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
| **3** | `as` | Cast (`CastExpression`); the right operand is a type | Left-to-right | `a * b as f64` is `a * (b as f64)` |
| **4** | `*` `/` `%` `.*` `./` | Multiplication, division, remainder (elementwise `.*` `./`) | Left-to-right | `a * b`, `a % n` |
| **5** | `<<` `>>` `&` `^` `\|` | Shift and bitwise operators (one level, [rules](#bitwise-and-shift-operators)) | Left-to-right | `a << 2`, `x & mask` |
| **6** | `+` `-` `.+` `.-` | Addition, subtraction (elementwise `.+` `.-`) | Left-to-right | `a + b`, `a - b` |
| **7** | `==` `!=` `<` `>` `<=` `>=` | Comparison operators | Left-to-right | `a == b`, `x < y` |
| **8** | `&&` | Logical AND | Left-to-right | `a && b` |
| **9** | `\|\|` | Logical OR | Left-to-right | `a \|\| b` |
| **10** | `=` `+=` `-=` `*=` `/=` `%=` `<<=` `>>=` `&=` `\|=` `^=` | Assignment and compound assignment | Right-to-left | `x = y`, `x += 1`, `x <<= 2` |
| **11 (Lowest)** | `,` | Comma (sequence) | Left-to-right | `f(a, b, c)` |

> **Shift and bitwise operators bind tighter than `+` and `-`.** This differs from C and Rust,
> where `+` and `-` bind tighter than shifts and bitwise operators. In MIND `0 - 17 >> 2` parses as
> `0 - (17 >> 2)` and evaluates to `-4`; in C and Rust it is `(0 - 17) >> 2`, which is `-5`. Likewise
> `a + b & c` is `a + (b & c)` in MIND. Write explicit parentheses whenever a shift or bitwise
> operator meets `+` or `-` in one expression.

A cast `e as T` binds tighter than `*`, `/` and `%` and looser than a unary operator: `a * b as f64` is
`a * (b as f64)`, `-x as f64` is `(-x) as f64`, and `x as i64 as f64` is `(x as i64) as f64`. The type of
`e as T` is `T`. [Casts](#casts) gives the casts that are allowed and their values.

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
let mut x = 0;
let mut y = 0;
let z = 1;
x = y = z;
// Parses as: x = (y = z)  (right-to-left)

let mut a = 1;
let b = 2;
let c = 3;
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
let mut a = 1;
let mut b = 1;
let mut c = 1;
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
  and `oeq`. Since compiler `2597ee9c` (v0.10.3) it emits the unordered `une` for `!=`; the
  v0.10.2 release used the ordered `one`, so `NaN != NaN` was false there.
- The native x86-64 backend (`--backend native`) matches this for `f64` since `ccbb00b8` (v0.10.3). The evidence is
  one script gate: 14 operand pairs plus one NaN program, each also built with the MLIR backend, with the pair
  programs checked against Python float comparisons. That gate is run in preflight, not in CI, and covers `f64` on
  x86-64 only. The compiler independence audit records the gate as exiting 1 (its wording: "3 of 5 in-profile programs
  fail"), and the `ccbb00b8` commit message records three helper-intrinsic programs and the tensor first-fence fixture
  as already red before it. No passing run is attached here; that the 15 comparison programs pass is inferred from
  that commit message, which names only those four items as red. The 14 pair programs pass their operands as
  parameters of one function (`fn k(x: f64, y: f64)`); the NaN program compares a local variable with the literal
  `0.0`. The backend's first admission check refuses `f32`, `f16` and `bf16` scalars (`a1b0b5f5`), so `f32`
  comparisons are not available there.
- The reference `mindc test` evaluator has an open defect for `f64` comparisons used as `if` or
  `while` conditions or as `match` guards: it treats only an integer 0 as false (compiler
  independence audit, finding 15, `docs/independence-audit-plan-20260925.md` in `star-ga/mind`). Its
  verdicts are therefore not evidence for this rule.

### Floating-point remainder

For two operands of the same type `f32` or `f64`, `a % b` is the truncated remainder and has that type. Its
value is `a - n * b`, where `n` is the quotient `a / b` truncated toward zero to an integer, computed exactly:
the result is the exact value and is never rounded. A nonzero result has the sign of `a`, and its magnitude is
less than the magnitude of `b`. Operands of two different float types are a dtype mismatch and MUST be
refused at check time with [`E2004`](./errors.md#e2004-dtype-mismatch-in-binary-operation).

The special cases below are normative and complete for `f32` and `f64`. The first row that matches decides
the result. "Canonical NaN" is the bit pattern of [Canonical NaN](./types.md#canonical-nan) for the type.

| Row | Left operand `a` | Right operand `b` | `a % b` |
|-----|------------------|-------------------|---------|
| 1 | NaN | any value | canonical NaN |
| 2 | any value | NaN | canonical NaN |
| 3 | infinite | any value | canonical NaN |
| 4 | finite | zero (`+0.0` or `-0.0`) | canonical NaN |
| 5 | finite | infinite | `a` |
| 6 | zero (`+0.0` or `-0.0`) | finite and not zero | `a` (the zero keeps its sign) |
| 7 | finite and not zero | finite and not zero | the truncated remainder; a zero result has the sign of `a` |

### Bitwise and shift operators

`&`, `|`, `^`, `<<` and `>>` are one precedence level, left to right, tighter than `+` and `-`
(`BitwiseExpression` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)). An integer type is a type that
[Casts](#casts) names so. The rows below are the complete rule for the operand types and the values. `N` is
the width in bits of the type `T` of the left operand.

| Row | Expression | Operands | Type | Value |
|-----|------------|----------|------|-------|
| 1 | `a & b`, `a \| b`, `a ^ b` | `a` and `b` have the same integer type `T` | `T` | The bitwise and, or and exclusive or of the two's complement bits of `a` and `b`. |
| 2 | `a << c` | `a` has an integer type `T`; `c` has an integer type | `T` | The low `N` bits of `a` times 2 to the power `s`, in two's complement for a signed `T`. |
| 3 | `a >> c`, `T` signed | as row 2 | `T` | The arithmetic shift: the floor of `a` divided by 2 to the power `s`. |
| 4 | `a >> c`, `T` unsigned | as row 2 | `T` | The logical shift: the floor of `a` divided by 2 to the power `s`. |

The shift count `s` is the value of `c` modulo `N`, so a count is always from 0 to `N - 1`; a negative `c`
uses its two's complement value modulo `N`. For `T` = `i64`: `1 << 64` is 1, `1 << 65` is 2,
`1 << (0 - 63)` is 2, and `(0 - 17) >> 2` is -5. No operator of this group traps, and every result is
bit-identical on every substrate. `0 - 17 >> 2` is `0 - (17 >> 2)` and gives -4.

Operands of two different integer types for `&`, `|` or `^` MUST be refused at check time with
[`E2004`](./errors.md#e2004-dtype-mismatch-in-binary-operation). An operand of this group whose type is not an
integer type, for example a `bool`, an `f32` or an `f64`, MUST be refused at check time with
[`E2005`](./errors.md#e2005-invalid-dtype-for-operation). The compound assignments `&=`, `|=`, `^=`, `<<=` and
`>>=` ([Bindings and assignment](#bindings-and-assignment)) use these rules.

### Casts

`e as T` (`CastExpression` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)) converts the value of `e` to the
type `T`, and its type is `T`. The rows below are the complete rule, and every row is bit-exact on every
substrate. An integer type is `i32`, `i64`, or an integer type that an implementation adds as an extension,
signed or unsigned. `N` is the width in bits of the target type. "Canonical NaN" is the bit pattern of
[Canonical NaN](./types.md#canonical-nan) for `T`.

| Row | Type of `e` | Type `T` | Value of `e as T` |
|-----|-------------|----------|-------------------|
| 1 | integer type | integer type | The value modulo 2 to the power `N`: a signed `e` is sign-extended and an unsigned `e` is zero-extended, and the low `N` bits are the result, in two's complement for a signed `T`. `4294967297 as i32` is 1, and `2147483648 as i32` is -2147483648. |
| 2 | integer type | `f32` or `f64` | The value rounded to the nearest value of `T`, ties to even. |
| 3 | `f32` or `f64` | integer type | The value truncated toward zero. A value outside the range of `T`, an infinity too, gives the nearest bound of `T`. NaN gives 0. `2.9 as i64` is 2, `(0.0 - 2.9) as i64` is -2, and `1.0e30 as i32` is 2147483647. |
| 4 | `f32` | `f64` | The same value, exact. NaN gives the canonical NaN. |
| 5 | `f64` | `f32` | The value rounded to the nearest `f32`, ties to even. A value whose rounded magnitude is greater than the largest finite `f32` (an overflow) gives the infinity of its sign. NaN gives the canonical NaN. |
| 6 | `bool` | integer type | `false` gives 0, and `true` gives 1. |
| 7 | any type | the same type | The identity: the value of `e`, bit for bit, except that a NaN gives the canonical NaN. |

**Reading rule for the type of a cast.** A primitive type name ends the type of a cast: `x as i64 < y` is the
comparison of `x as i64` with `y`. After any other type name, a `<` opens a type-argument list (the type reading
wins), and the rule of [Tokens](./lexical.md#tokens) for the closing angle closes it. So `x as Option<y>> z` is the
cast `x as Option<y>` compared by `>` with `z`, and `let b = x as Option < y;` has no reading and MUST be refused,
because the list that the `<` opens is not closed.
To compare a cast to a type that is not a primitive type by `<`, a program writes
parentheses: `(x as T) < y`.

A cast that the table does not list MUST be refused at check time with
[`E2016`](./errors.md#e2016-invalid-cast). An integer or a float has no cast to `bool`: the program writes a
comparison, such as `x != 0`. Rows 1 and 7 give the same value for an integer type cast to itself. Every cast
whose value is a floating-point NaN gives the canonical NaN of `T`: rows 4 and 5, and row 7 for `f32` and `f64`.

### Grammar reference

For the complete formal grammar including precedence, see:
- **Lexical grammar**: [`grammar-lexical.ebnf`](./grammar-lexical.ebnf)
- **Syntax grammar**: [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) (expression precedence encoded in production
  rules)

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
- **Elementwise operators**: `.*`, `./`, `.+` and `.-` follow the operand rule of the arithmetic operators above:
  the operands share a dtype, the shapes follow the [broadcasting rules](./shapes.md#broadcasting), and a scalar
  extends to the shape of the other operand. Operands of two different dtypes MUST be refused at check time with
  [`E2004`](./errors.md#e2004-dtype-mismatch-in-binary-operation). On two scalar operands of one numeric type, the
  result is the value of the plain operator with that type: `a .* b` is `a * b`, `a ./ b` is `a / b`, `a .+ b` is
  `a + b`, and `a .- b` is `a - b`.
- **Tensor constructor**: `tensor(e)` and `tensor(e, dtype: D)` (`TensorConstructor`) make a tensor from the
  value of `e`. Its shape is the shape of `e`: a scalar `e` gives rank 0, and an array literal gives its
  dimensions (`tensor([[1, 2], [3, 4]])` has the shape `[2, 2]`). With a dtype argument the dtype is `D`;
  without one it is the type of a scalar `e` or the element type of an array `e`, which MUST be a dtype (`i32`,
  `i64`, `f32` or `f64`); another element type, such as `bool`, MUST be refused at check time with
  [`E2005`](./errors.md#e2005-invalid-dtype-for-operation). The dtype argument is not an expected type for `e`.
  When `D` differs from the element type of `e`, each element is converted as `as` converts it where the
  [cast table](#casts) gives a cast from that type to `D` (`tensor(3, dtype: f32)` holds `3.0`); where the table
  gives no such cast, the constructor MUST be refused at check time with [`E2016`](./errors.md#e2016-invalid-cast).
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

## Core v1 scope

[`grammar-syntax.ebnf`](./grammar-syntax.ebnf) marks every form that is written for a later edition
with the words "NOT IN CORE v1". Read without its marked parts, the grammar is the Core v1 grammar.
The marked forms are: function types, function expressions (closures), trait declarations,
`dyn Trait`, type parameters on `struct`, `enum`, `trait` and `type` declarations, and type
arguments on user-declared types. A marked form is not part of Core v1: a conforming
implementation refuses it or documents it as an extension. [Core v1 forms](./core-v1-forms.md) lists the
status of each form.

## Attributes

An attribute is written `#[name]` or `#[name(arg, ...)]` (`Attribute` of
[`grammar-syntax.ebnf`](./grammar-syntax.ebnf)). An argument is an identifier, a literal, or an identifier bound
to a literal (`#[requires(mind_spec = "1.2")]`). The spelling without `#`, `[name]`, is not an attribute; inside a
block it reads as an array expression.

In Core v1 an attribute stands directly before a function declaration (`FunctionDeclaration`). An attribute before a
function declaration is part of Core v1 when this specification defines its name for that position. This chapter
defines `#[raw_memory]` and `#[raw_memory(sealed)]` ([Raw memory](./memory.md#raw-memory)). An attribute before a function
declaration whose name this specification does not define for that position MUST be refused at check time.

An attribute before another item (`AttributedItem` in the "v1.1 candidate additions" block of the grammar, which
`Module` does not reach) is not derived by the Core v1 grammar. The specification defines two such attributes:
`#[repr(C)]` before a `struct` declaration ([Struct layout attribute](./ffi.md#struct-layout-attribute)) and
`#[requires(mind_spec = "M.N")]` ([Versioning](./versioning.md)). In Core v1 both are extensions. Before another item,
an attribute whose name this specification does not define for that position MUST be refused at check time too,
for example `#[fast] struct S { a: i64, }`.

## Raw memory

Raw memory, the attribute `raw_memory` and its refusals are defined in
[Memory model](./memory.md#raw-memory).

## Entry function

The entry function of a program is the function named `main`. `main` MUST have no parameter, and its
result type MUST be `i64` or `unit`. As for every function, the result type `unit` may be omitted or written:
`fn main() -> i64 { ... }`, `fn main() { ... }` and `fn main() -> unit { ... }` are the forms. A `main` with a
parameter or with another result type MUST be refused at check time with
[`E2403`](./errors.md#e2403-invalid-entry-function). When `main` returns the `i64` value `v`, the process
status is the low 8 bits of `v` in two's complement, read as an unsigned number from 0 to 255, on every
substrate: the result 300 gives the status 44, and the result -1 gives the status 255. When the result type
of `main` is `unit`, the process status is 0.

## Bindings and assignment

`let p = e;` binds the names of the pattern `p`. `let mut p = e;` binds every name of `p` as a mutable binding. A name
that a `let` without `mut`, a parameter of a function, the pattern of a `for` or the pattern of a `match` arm binds is
not mutable. A later `let` of the same name is a new binding and not an assignment, so `let x = 1; let x = 2;` is
valid.

The left operand of an assignment or of a compound assignment is a place: a name, or a chain of index,
field and tuple-index accesses on a name (`x`, `a[i]`, `p.f`, `t.0`, `a[i].f.1`). The name at the start of
the chain is the root of the place. An assignment or a compound assignment to a place needs the root name to
be declared with `let mut`. A left operand that is not a place, or a place whose root is not mutable, MUST
be refused at check time with [`E2402`](./errors.md#e2402-invalid-assignment-target): after
`let a = [1, 2];`, the statement `a[0] = 5;` is refused.

The compound assignment operators are `+=`, `-=`, `*=`, `/=`, `%=`, `<<=`, `>>=`, `&=`, `|=` and `^=`.
`x op= e` means `x = x op e`, where `op` is the operator before the `=`, and the place `x` is evaluated once:
in `a[f()] += 1` the call `f()` runs once. The rules of `op` for the types of its operands apply.

## Loops

`while c { ... }` and `for p in e { ... }` are expressions (`WhileExpression` and `ForExpression` of
[`grammar-syntax.ebnf`](./grammar-syntax.ebnf)). A loop has the type `unit`, and its value is `()`
([The unit value](./types.md#the-unit-value)): after `let u = while c { };`, `u` is `()`. A loop that
stands as a statement is a [block-like statement](#block-like-statements) and takes no `;`.

## Block-like statements

The five forms `if`, `match`, a block, `while` and `for` may stand as a statement with no `;` after them
(`BlockLikeStatement` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)). A `defer` statement takes no `;`
either: it ends at the closing brace of its block (`DeferStatement`), so `defer { };` has no derivation and
MUST be refused. Every other statement ends with its `;` ([Statement separators](#statement-separators)).

**Reading rule.** Where a statement can start and the next token starts one of the five forms, the form is
read as a `BlockLikeStatement` and ends at its closing brace (for an `if` with `else`, the closing brace of its
last block); what follows starts a new statement. Two cases come before this rule:

1. When the next token after that closing brace is `;`, the form and the `;` are an `ExpressionStatement`.
   So `while c { };` is a program, and `if c { 1 } else { 2 };` discards the value of the `if`.
2. When nothing but the closing brace of the enclosing block follows, the form is the tail `Expression` of
   that block and gives the block its value: `fn f(c: bool) -> i64 { if c { 1 } else { 2 } }` returns 1 or 2.

To use such a form as an operand at the start of a statement, the program writes parentheses:
`(if c { 1 } else { 2 }) + x;`. Without them, `if c { 1 } else { 2 } - x;` is the statement
`if c { 1 } else { 2 }` and then the statement `- x;`.

**Unit rule.** A `BlockLikeStatement` that is not the tail MUST have the type `unit`; otherwise the source
MUST be refused at check time with [`E2001`](./errors.md#e2001-type-mismatch). A value is discarded only by
an `ExpressionStatement` with `;`. So `if c { 1 } else { 2 } return 0;` is refused, and
`if c { 1 } else { 2 }; return 0;` is valid.

## Loop exits

Inside the body of a `while` or a `for`, the statements `break;` and `continue;` end the innermost
loop and start its next iteration, respectively. A `break` or a `continue` that is not inside the body
of a `while` or a `for` MUST be refused at check time with
[`E2401`](./errors.md#e2401-loop-exit-outside-a-loop). A loop exit takes no value and no label, and its
`;` is required ([Statement separators](#statement-separators)): no token of the
[lexical grammar](./grammar-lexical.ebnf) starts with `'`, so `break 'a;` contains an invalid token and
MUST be diagnosed, and `break 7;` has no derivation and MUST be refused.

`break` and `continue` are keywords ([Lexical Structure](./lexical.md#keywords)), and `LoopExitStatement` is
the only rule of the grammar that holds them. A source in which one of them stands where the grammar needs a
name or an expression has no derivation and MUST be refused: `let break = 4;`, `break - 1;` and
`break = 5;` are refused. `while c { break }` is refused because the `;` of the loop exit is missing.

Core v1 has no `loop` statement: `loop` is a name and not a keyword. Where a statement can start, the name `loop`
directly followed by `{` (the form `loop { ... }`) is a name followed by a block with no `;` between them, which no
rule derives. Where a statement can start, the name `loop` directly followed by `{` MUST be refused at check time with
[`E2405`](./errors.md#e2405-no-loop-statement), and the diagnostic MUST say that Core v1 has no `loop` statement and
name the form `while true { ... }`. In every other place `loop` is a valid name: `let loop = 1; return loop;` and
`let loop = false; while loop { } return 3;` are valid, because in the second source `loop` stands after `while`,
where an expression starts and not a statement. The range after `in` (`for i in a..b`) is not defined by the
grammar; it is an extension.

## Tuple index

`e.N` (`TupleIndexOperator`) is the element `N` of the tuple `e`, counted from 0: after `let t = (4, 5);`, `t.0` is 4
and `t.1` is 5. `N` is a decimal integer literal with no sign and no prefix. Where the parser expects the
`DecimalInteger` of a tuple index and the next token is a float literal of the form digits "." digits (no exponent, no
suffix), the token is read as two tuple indices: `t.0.1` means `(t.0).1`. After an access dot, a float literal token
with an exponent or a suffix is not a tuple index, because only the form digits "." digits is read as two indices (the
lexical grammar gives a float literal no suffix, so in Core v1 such a token has an exponent): a source such as
`t.0.1e0` is not derived and MUST be refused. The type of `e` MUST be a tuple type and `N` MUST be less than its
number of elements; otherwise the source MUST be refused at check time with
[`E2404`](./errors.md#e2404-invalid-tuple-index). An index operator `e[i]` on a tuple has no meaning: when the type of
`e` is a tuple type, `e[i]` MUST be refused with `E2404`, and the diagnostic MUST name the form `e.N`.

`a[s:e:k]` (`SliceExpression`) is a slice: it takes the elements of the axis from the index `s` up to, and not
including, the index `e`, with the step `k`. An omitted `s` is 0, an omitted `e` is the length of the axis, and an
omitted `k` is 1, so for an axis of length `n`, `a[:e]` is `a[0:e:1]`, `a[s:]` is `a[s:n:1]`, `a[:]` is `a[0:n:1]`
and `a[s:e]` is `a[s:e:1]`. The form lowers to the `Slice` operation of [Core IR](./ir.md#indexing-and-slicing) with
these bounds and this step, and the shape of the result follows the shape rule of that operation: `a[1:3]` takes the
elements 1 and 2, and `a[0:4:2]` takes the elements 0 and 2. The lexer reads `::` as one token
([Tokens](./lexical.md#tokens)), so `a[::2]` is not derived; with the start and the end omitted, a step is written
`a[: :2]`. The grammar has no range index:
an index operator whose index is two expressions with `..` between them, such as `a[1..3]`, is not derived; it MUST be
refused at check time with [`E2406`](./errors.md#e2406-range-index), and the diagnostic MUST name the slice form
`a[1:3]`.

## Field access and method calls

`x.f` (`FieldAccessOperator`) is the field `f` of the value `x`. `x.m(a)` (`MethodCallOperator`) is a method call: it
calls the method `m` of the type of `x` with the receiver `x` and the arguments `a`, for example `o.unwrap_or(0)` on an
`Option<i64>` ([`core` module](./stdlib.md#pattern-matching-support)). When `x` is an import qualifier, `x.m(a)` is the
call of the member `m` of that module ([Module-qualified references](#module-qualified-references)). A call operator
never directly follows a field access (`PostfixExpression` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)), so
`x.m(a)` has one derivation, the method call. A call of a function value that a field holds is written `(x.m)(a)`.
A field access `x.f` whose `f` is not a field of the type of `x` MUST be refused at check time.

## Statement separators

The separators are the ones that [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) writes. `;` is required after a `let`,
after a `return`, after a loop exit and after an `ExpressionStatement`; a `BlockLikeStatement` and a `defer` statement
take none ([Block-like statements](#block-like-statements)). A `match` arm with an expression ends with `,`, the last
arm too; an arm with a block takes none (`MatchArm`). Checking and building MUST refuse a source in which one of these
separators is missing. A missing separator has no meaning in the language.

A source formatter MAY read a source in which such a separator is missing and write it with the
separator. That reading is a repair of the text that the formatter does before it writes the strict form;
it does not make the source without the separator a program of the language, and a checker or a build
MUST NOT accept that source.

## Words that the grammar spells out

The syntactic grammar spells out words that are not keywords (`in`, `as`, `const`, `enum`, `module`, `use`, `assert`,
`mut`, `diff`, `dyn`, `Tensor`, `tensor`, `dtype`, the primitive type names and `_`).
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf) lists them as `ContextualWord`: the lexer produces each of them as an
identifier, and this edition does not reserve them. A source is read by the derivation in which a rule of the
syntactic grammar spells the word out, when such a derivation exists. A source with no such derivation reads the word
as an identifier. This is the only rule for these words. The rows give the verdict that the rule has for a source. The
grammar does not look at declarations, so `tensor(1);` is the constructor also where a function `tensor` is declared.

| Source | Readings of the word | Meaning |
|--------|---------------------------|---------|
| `tensor(1, 2);` with `struct P { }` and `fn tensor(a: P, b: P) { }` declared | One: a call of the function `tensor`. `TensorConstructor` takes `, dtype :` after its first argument, so no derivation spells the word out. | The call of the user function `tensor` with two arguments |
| `tensor(1);` | Two: a `TensorConstructor`, and a call of the name `tensor`. | The tensor constructor |
| `let _ = 1;` | Two: a `WildcardPattern`, and an `IdentifierPattern` named `_`. | The wildcard |
| `let x: i64 = 1;` | Two: the primitive type `i64`, and an `IdentifierType` named `i64`. | The primitive type |
| `let in = 1; return in;` | One: the name `in` as an identifier. No rule spells the word out here. | The name `in` |
| `let mut = 1;` | One: an `IdentifierPattern` named `mut`. A `let` that spells `mut` out needs a pattern after it. | The name `mut`, bound without `mut` |

## String escapes

The escape sequences of a string literal are `\n`, `\r`, `\t`, `\0`, `\\`, `\'`, `\"` and
`\u{HEX}` (one or more hexadecimal digits), as in `EscapeSequence` of
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf). Any other escape sequence MUST be diagnosed with
[`E1004`](./errors.md#e1004-invalid-escape-sequence).

## Macros are not part of the language (informative)

MIND has no macros. A form such as `println!("x")`, `vec![1, 2]` or `panic!("x")` is not a macro
call and is not part of the language. Use the function form, for example the
`println` and `panic` functions of [Standard Library](./stdlib.md).

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
since `cd150ae7` (v0.10.3), `q::f(x)` are parsed to the bare member name `f`, with the
qualifier kept beside the AST by source span, where only the formatter reads it; type checking and
lowering see only the bare member name. Two imported modules that both export a function `f`, called
as `a.f()` and `b.f()`, therefore check without a diagnostic but fail to link
(`multiple definition of 'f'`); measured with `cd150ae7` applied (v0.10.3).
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
  [Future Extensions](./future-extensions.md)); the compiler rejects fn-as-value use fail-loud. Since
  v0.10.3 a bare name of a function of the current module, or of a function-only
  standard-surface export, used as a value is refused with
  [`E2037`](./errors.md#e2037-function-name-used-as-a-value) (`1def5dde`, v0.10.3); see that
  entry for its limit.
- **Traits**: **not implemented** in the executable subset (no `trait` declarations, no `dyn Trait`).
- **Slices**: stubbed; byte-level work goes through the `std.string`/`std.vec` heap records and the
  byte-precise intrinsics.
- **Collections**: `array<T>`, `Vec`, `Map` and `String` are container records that change in place
  ([Memory model](./memory.md#records-and-containers)); `std.map` is insert-only (no removal) — see
  [Standard Library](./stdlib.md#four-pure-mind-modules) for the precise shipped surface. These are
  not full `Vec`/`String`/`HashMap` equivalents.
- **Range `for` loops**: the range form `for v in s..e { ... }` is not yet in the grammar:
  [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) has a `ForExpression` over an arbitrary
  `Expression` but no range expression. The reference interpreter evaluates `e` once and binds `v`
  fresh on each iteration. Since v0.10.3, compiled output follows it when the body re-declares
  `v` with `let` or a tuple `let`: the re-declaration shadows `v` from that statement to the end of
  the iteration and does not change the iteration count (`fe9854ec`, v0.10.3; Rust IR
  lowering, not the pure-MIND native path). Before `fe9854ec`, the compiler built such a loop to an
  executable that did not terminate; the behaviour of v0.10.2 for this shape is not established
  here. Known gap: an end bound that reads memory the body mutates through an index or field store is
  not detected, so compiled output can re-evaluate it on each iteration.
- **Assertions**: `assert cond`, `assert cond, "message"` and the parenthesised
  `assert(cond, "message")` each assert `cond` (parenthesised form: `487dd5c7`, v0.10.3);
  the message is kept as written between the quotes. A false condition aborts an executable built
  with the MLIR backend (`--backend mlir`; SIGABRT; the message text is not printed) and fails the test under
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
  v0.10.3), registering both the alias and the last path segment as qualifiers; the `as`
  form is not in [`grammar-syntax.ebnf`](./grammar-syntax.ebnf). `use` also accepts `::` between
  path segments as an extension. A zero-argument `.sum()` or `.mean()` on a receiver named like an
  import is a module call, not a tensor reduction (`f2fc890d`).
