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

- **Modules and items**: a module holds items only: functions, type declarations, structs, enums, constants,
  module blocks, imports, `use` declarations and extern blocks ([Items and modules](#items-and-modules)). Functions
  declare named parameters and a result type and compile to IR module inputs and outputs.
- **Statements**: `let`, assignment, expression statements, `return`, `defer`, loop exits, `assert` and the
  block-like forms ([Bindings and assignment](#bindings-and-assignment), [Block-like statements](#block-like-statements),
  [Statement separators](#statement-separators)).
- **Expressions**: literals, the unary operators `-`, `!` and `~`, the binary operators of
  [the precedence table](#operator-precedence-and-associativity), casts, calls, method calls, index, slice and tuple
  index, record literals, `if`, `match`, the loops and the tensor constructor.
- **Tensor literals**: may appear with explicit dtype annotations. Rank-0 literals represent scalars.
- **Control flow**: `if`, `match`, `while`, `for`, `loop`, `break`, `continue` and `return` are forms of the surface
  language. They are lowered before the [Core IR](./ir.md), which holds straight-line tensor programs.

## Operator precedence and associativity

This table is the one precedence table of the specification; the comment of `Expression` in
[`grammar-syntax.ebnf`](./grammar-syntax.ebnf) points to it, and the rules of that grammar derive it. The forms are
listed from the one that binds tightest to the one that binds loosest.

| Level | Operators | Description | Associativity | Example |
|-------|-----------|-------------|---------------|---------|
| **1 (highest)** | `[]` `.f` `.N` `.m(...)`, and `(...)` after a name | Index and slice, field access, tuple index, method call, call | Left to right | `a[i]`, `p.x`, `t.0`, `o.unwrap_or(0)`, `f(x)` |
| **2** | Unary `-` `!` `~` | Negation, logical not, bitwise complement | Right to left | `-x`, `!flag`, `~m` |
| **3** | `as` | Cast (`CastExpression`); the right operand is a type | Left to right | `a * b as f64` is `a * (b as f64)` |
| **4** | `*` `/` `%` `.*` `./` `.%` | Multiplication, division, remainder; the dotted forms broadcast | Left to right | `a * b`, `a % n`, `t .* u` |
| **5** | `+` `-` `.+` `.-` | Addition, subtraction; the dotted forms broadcast | Left to right | `a + b - c`, `t .+ u` |
| **beside 4 and 5** | `&` `\|` `^` `<<` `>>` | Bit operators ([rules](#bitwise-and-shift-operators)) | `&`, `\|` and `^` chain only with themselves; `<<` and `>>` do not chain | `x & mask`, `(a << 2) + 1` |
| **6** | `==` `!=` `<` `>` `<=` `>=` | Comparison | None: no chain | `a == b`, `x < y` |
| **7** | `&&` | Logical and | Left to right | `a && b` |
| **8 (lowest)** | `\|\|` | Logical or | Left to right | `a \|\| b` |

Assignment is not an operator: `p = e;` and `p op= e;` are statements and have no value
([Bindings and assignment](#bindings-and-assignment)). The comma separates the elements of a list and the arguments of
a call; it is not an operator.

A cast `e as T` binds tighter than `*`, `/` and `%` and looser than a unary operator: `a * b as f64` is
`a * (b as f64)`, `-x as f64` is `(-x) as f64`, and `x as i64 as f64` is `(x as i64) as f64`. The type of
`e as T` is `T`. [Casts](#casts) gives the casts that are allowed and their values.

### Precedence rules

1. **Higher precedence binds tighter**: `a + b * c` parses as `a + (b * c)`, not `(a + b) * c`.
2. **Same precedence uses associativity**: `a - b + c` parses as `(a - b) + c` (left to right).
3. **Parentheses override precedence**: `(a + b) * c` forces addition before multiplication.
4. **Postfix forms bind tightest**: `f(x) + g(y)` calls the functions before the addition, and `-5.abs()` is
   `-(5.abs())`, because a unary operator applies to the whole postfix expression.
5. **Bit operators do not mix without parentheses.** An operand of a bit operator is a cast expression or a tighter
   form. `&`, `|` and `^` chain only with the same operator (`a & b & c`), and `<<` and `>>` take two operands and do
   not chain. A bit operator beside another bit operator, or beside `+`, `-`, `*`, `/`, `%` or a dotted operator,
   without parentheses has no derivation and MUST be refused with `E1106`; the message gives both parenthesised
   forms. So `0 - 17 >> 2`, `a + b & c`, `x & y | z`, `1 | 2 << 1 ^ 7` and `a << 1 << 2` are refused, and
   `(0 - 17) >> 2` and `0 - (17 >> 2)` are valid. A bit expression is an operand of a comparison: `x & 3 == 2` is
   `(x & 3) == 2`.
6. **Comparison is not associative.** A comparison operator never has a comparison as its direct operand:
   `a < b < c` and `a == b == c` have no derivation and MUST be refused with `E1101`; the message gives the form
   `a < b && b < c`. With parentheses a comparison is an operand: `(a < b) == c` is derived.

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
let z = 1;
x = z;
// A statement: it stores the value of z in x and has no value

let mut a = 1;
let b = 2;
let c = 3;
a += b * c;
// A statement: a = a + (b * c), with the place a evaluated once
```

A chain `x = y = z;` and an assignment inside an expression, such as `if x = 1 { }`, have no derivation and MUST be
refused with `E1107`; the message names `==` for a comparison.

**Example 5: Function calls and indexing**
```mind
let value = f(x)[0] + g(y).field;
// Parses as: (f(x)[0]) + (g(y).field)
// The left operand is evaluated first: f(x), then the index [0];
// then g(y) and the field access .field; finally the addition +
```

**Example 6: Bit operators**
```mind
let high = (x & 0xF0) >> 4;
let shifted = (a << 2) + 1;
let low_set = x & 3 == 2;
// Parses as: (x & 3) == 2
```

### Tensor operators and broadcasting

A plain arithmetic operator (`+`, `-`, `*`, `/`, `%`) on two tensors needs one dtype and one shape; a scalar operand
extends to the shape of the tensor operand. A plain operator on two tensors of different shapes MUST be refused at
check time with [`E3015`](./errors.md#e3015-plain-operator-on-two-shapes), and the fix is the dotted operator. The
dotted operators `.+`, `.-`, `.*`, `./` and `.%` broadcast the shapes of their operands by the
[broadcasting rules](./shapes.md#broadcasting); they have the precedence of their plain operators. A dotted operator
MUST be refused at check time with [`E3016`](./errors.md#e3016-dotted-operator-with-no-expansion) when it expands no
operand: on two tensors of one shape, with a scalar operand, or with no tensor operand; the fix is the plain operator.
So every expansion of a shape is written in the text, and a text with no expansion has one spelling.

The matrix product is the function `matmul(a, b)` ([Tensor operations](#tensor-operations)); as a call it binds
tighter than every operator: `matmul(A, B) + C` performs the product first. `@` is a reserved token with no production
([Tokens](./lexical.md#tokens)).

**Example: Tensor arithmetic**
```mind
let result = alpha * X + beta * Y;
// Parses as: (alpha * X) + (beta * Y)
// alpha and beta are scalars and extend; X and Y have one dtype and one shape

let grid = col .* row;
// col has the shape [3, 1] and row the shape [1, 4]: the dotted operator broadcasts to [3, 4]
```

### Associativity edge cases

**Left-associative subtraction**:
```mind
let r = a - b - c;  // Parses as (a - b) - c, NOT a - (b - c)
// Important: these are different!
// (5 - 3) - 2 = 0
// 5 - (3 - 2) = 4
```

### Precedence vs type checking

Precedence determines parse tree structure, not type validity:

```mind
let invalid = t + 5;  // Parses correctly as (t + 5)
                      // But may fail type checking if dtypes incompatible
```

Type errors are caught AFTER parsing, during type checking phase.

### Operand and condition types

There is no truth value of a value that is not a `bool`. The condition of `if` and `while`, the guard of a `match` arm,
and the operands of `!`, `&&` and `||` MUST have the type `bool`. A condition of another type MUST be refused at check
time with [`E2001`](./errors.md#e2001-type-mismatch) (`if 5 { }`), an operand of `!` of another type with
[`E2005`](./errors.md#e2005-invalid-dtype-for-operation) (`!5`), and an operand of `&&` or `||` of another type MUST be
refused at check time.

The arithmetic operators (`+`, `-`, `*`, `/`, `%` and the dotted operators) take numbers and tensors; an operand of the
type `bool`, `unit`, a tuple type or a struct type MUST be refused at check time with
[`E2005`](./errors.md#e2005-invalid-dtype-for-operation) (`true + 1`). `==` and `!=` compare two values of one type;
two tuples or two arrays compare element by element from index 0. `<`, `<=`, `>` and `>=` take numbers only. A
prefix `-` on an operand of an unsigned integer type MUST be refused at check time; `0 - x` writes the wrapping
subtraction. `~e` is the bitwise complement of an integer `e` and has its type; `!` takes a `bool` only. The unary
operators are `-`, `!` and `~`: there is no unary `+`, and Core v1 has no references, so `+x` and `&x` have no
derivation and MUST be refused with `E1101`.

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

`&`, `|`, `^`, `<<` and `>>` are the bit operators (`BitwiseTail` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)),
and `~` is the bitwise complement (`UnaryOperator`). A bit operator never stands beside another bit operator or an
arithmetic operator without parentheses (rule 5 of [Precedence rules](#precedence-rules)). An integer type is a type
that [Casts](#casts) names so. The rows below are the complete rule for the operand types and the values. `N` is the
width in bits of the type `T` of the left operand, or of the operand of `~`.

| Row | Expression | Operands | Type | Value |
|-----|------------|----------|------|-------|
| 1 | `a & b`, `a \| b`, `a ^ b` | `a` and `b` have the same integer type `T` | `T` | The bitwise and, or and exclusive or of the two's complement bits of `a` and `b`. |
| 2 | `a << c` | `a` has an integer type `T`; `c` has an integer type | `T` | The low `N` bits of `a` times 2 to the power `s`, in two's complement for a signed `T`. |
| 3 | `a >> c`, `T` signed | as row 2 | `T` | The arithmetic shift: the floor of `a` divided by 2 to the power `s`. |
| 4 | `a >> c`, `T` unsigned | as row 2 | `T` | The logical shift: the floor of `a` divided by 2 to the power `s`. |
| 5 | `~a` | `a` has an integer type `T` | `T` | Each of the `N` bits of `a` inverted, in two's complement for a signed `T`: `~0` is -1 for `i64`, and 255 for `u8`. |

The shift count `s` is the value of `c` modulo `N`, so a count is always from 0 to `N - 1`; a negative `c`
uses its two's complement value modulo `N`. For `T` = `i64`: `1 << 64` is 1, `1 << 65` is 2,
`1 << (0 - 63)` is 2, and `(0 - 17) >> 2` is -5. No operator of this group traps, and every result is
bit-identical on every substrate. `0 - 17 >> 2` has no derivation and MUST be refused with `E1106`; `0 - (17 >> 2)`
gives -4.

Operands of two different integer types for `&`, `|` or `^` MUST be refused at check time with
[`E2004`](./errors.md#e2004-dtype-mismatch-in-binary-operation). An operand of this group whose type is not an
integer type, for example a `bool`, an `f32` or an `f64`, MUST be refused at check time with
[`E2005`](./errors.md#e2005-invalid-dtype-for-operation); `~true` is refused so. The compound assignments `&=`, `|=`, `^=`, `<<=` and
`>>=` ([Bindings and assignment](#bindings-and-assignment)) use these rules.

### Casts

`e as T` (`CastExpression` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)) converts the value of `e` to the
type `T`, and its type is `T`. The rows below are the complete rule, and every row is bit-exact on every
substrate. An integer type is one of the primitive integer types: `i8`, `i16`, `i32` and `i64` are signed, and `u8`,
`u16`, `u32` and `u64` are unsigned ([Type formation](./types.md#type-formation)). `N` is the width in bits of the target type. "Canonical NaN" is the bit pattern of
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

**The type of a cast.** The type after `as` is a primitive type name or a name with no type-argument list
(`CastType`). A `<` after a cast is therefore always a comparison: `x as i64 < y` and `x as T < y` compare the cast
with `y`. A cast to a type with type arguments, such as `x as Option<i64>`, and a cast to a parenthesised type, such as
`3 as (i64)`, have no derivation and MUST be refused with `E1101`.

A cast that the table does not list MUST be refused at check time with
[`E2016`](./errors.md#e2016-invalid-cast). An integer or a float has no cast to `bool`: the program writes a
comparison, such as `x != 0`. Rows 1 and 7 give the same value for an integer type cast to itself. Every cast
whose value is a floating-point NaN gives the canonical NaN of `T`: rows 4 and 5, and row 7 for `f32` and `f64`.

### Grammar reference

For the complete formal grammar including precedence, see:
- **Lexical grammar**: [`grammar-lexical.ebnf`](./grammar-lexical.ebnf)
- **Syntax grammar**: [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) (expression precedence encoded in production
  rules)

### Lookahead of the grammar

Every choice of the syntactic grammar is decided by at most three tokens of lookahead, with two stated one-token
rules of the parser beside the grammar. The first is the head rule: in the head of `if`, `while`, `for` and `match`,
an identifier followed by `{` starts the block, and a record literal there is written in parentheses
([Record literals](#record-literals)). The second is the statement reading rule: where a statement can start, the
token `if`, `match`, `{`, `while`, `for` or `loop` starts a block-like statement
([Block-like statements](#block-like-statements)). With the tail expression of a block, which the token after the
common form decides (a `;` or an assignment operator makes a statement, the closing `}` makes the tail), these are the
three choices that a check of the grammar names as not decided by three tokens alone. The check also names choices
where a word of the grammar (such as `i64` or `tensor`) or the wildcard `_` could be read as an identifier; the token
rules decide them: `_` is never an identifier ([Identifiers](./lexical.md#identifiers)), and a word is decided with at
most two tokens ([Words that the grammar spells out](#words-that-the-grammar-spells-out)). This bound is a rule of the
specification: a change of the grammar that adds a fourth such choice is not accepted, and the grammar check of the
specification repository is the gate that holds it.

### Nesting depth

An implementation MUST accept at least 256 levels of nesting of parentheses, brackets, braces, unary operators and
block-like forms, and a left-associative chain of binary operators, such as `a + b + c`, of any length. Its limit
is one fixed number, the same on every substrate, and it does not depend on the stack of the host. Input that nests
deeper than the limit MUST be refused with `E1108` at the first token past the limit.

## Evaluation order

A program is evaluated in one written order, from left to right, for every form:

1. A binary operator evaluates its left operand, then its right operand. `&&` and `||` evaluate the right operand only
   when the left operand does not decide the result: in `false && e` and in `true || e`, `e` is not evaluated.
2. A call evaluates its arguments from left to right. A method call evaluates the receiver, then the arguments from left
   to right.
3. An index evaluates the base, then the index items and the bounds of a slice in the order in which they are written.
4. A record literal evaluates its fields in source order.
5. For `p = e;` and `p op= e;`, the parts of the place `p` are evaluated from left to right (the base before the
   index), then `e`, then the value is stored. `p op= e` reads `p` once, before `e`: in `a[f()] += g();` the call `f()`
   runs, then the element is read, then `g()` runs, then the sum is stored.
6. A trap, such as the [defined stop](./memory.md#the-defined-stop), happens at its point in this order: every
   evaluation before that point has happened, and none after it.

The bounds of a counting `for` loop are evaluated once, the first bound first, before the first iteration
([Loops](#loops)). This order is part of the bit-identity of a build: a program with effects has one result.

## Types

The type system relevant to Core v1 consists of:

- **Scalar types**: the primitive types `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32`, `u64`, `f32`, `f64`, `bool`
  and `unit` ([Type formation](./types.md#type-formation)).
- **Tensor types**: `Tensor<D, S>`, parameterised by a `dtype` `D` and a **shape** `S`; both arguments are written. A
  dimension of a shape is an integer literal or the name of a `const` of the type `i64` in scope (`Dimension` of
  [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)).
- **Shape descriptors**: ordered lists of dimensions. Shapes appear in type annotations and IR
  metadata. Device placements MAY be attached but are otherwise outside the Core v1 scope.

## Tensor operations

Surface syntax maps to the Core IR instruction set:

- **Arithmetic**: `+`, `-`, `*` and `/` lower to `BinOp` ([IR spec](./ir.md#binary-operations)).
- **Type checking for arithmetic**: operands MUST share a dtype. A plain operator on two tensors needs one shape, and a
  scalar operand extends to the shape of the tensor operand
  ([Tensor operators and broadcasting](#tensor-operators-and-broadcasting)).
- **Dotted operators**: `.+`, `.-`, `.*`, `./` and `.%` broadcast: the operands share a dtype, and the shapes follow
  the [broadcasting rules](./shapes.md#broadcasting). Operands of two different dtypes MUST be refused at check time
  with [`E2004`](./errors.md#e2004-dtype-mismatch-in-binary-operation). A dotted operator that expands no operand
  MUST be refused at check time with [`E3016`](./errors.md#e3016-dotted-operator-with-no-expansion).
- **Tensor constructor**: `tensor(e)` and `tensor(e, dtype: D)` (`TensorConstructor`) make a tensor from the
  value of `e`. Its shape is the shape of `e`: a scalar `e` gives rank 0, and an array literal gives its
  dimensions (`tensor([[1, 2], [3, 4]])` has the shape `[2, 2]`), and a tensor `e` gives its shape. With a dtype
  argument the dtype is `D`; without one it is the type of a scalar `e`, the element type of an array `e` at every
  nesting level, or the dtype of a tensor `e`, which MUST be a dtype (`i32`, `i64`, `f32` or `f64`); another type,
  such as `bool`, a tuple, a struct or `String`, MUST be refused at check time with
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
   (with `Add`, `Sub`, `Mul` or `Div` semantics) and other intrinsic operations map to
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
The marked forms are: function types (`fn(T) -> U`), function expressions (closures), trait
declarations, `dyn Trait`, the type `diff T`, type parameters on `struct`, `enum`, `trait` and `type`
declarations, type arguments on user-declared types, and the type arguments of a method call
(`e.m::<A>(x)`). A marked form is not part of Core v1: a conforming
implementation refuses it or documents it as an extension. [Core v1 forms](./core-v1-forms.md) lists the
status of each form.

## Attributes

An attribute is written `#[name]` or `#[name(arg, ...)]` (`Attribute` of
[`grammar-syntax.ebnf`](./grammar-syntax.ebnf)). An argument is an identifier, a literal, or a name and a literal joined
by `:` (`#[requires(mind_spec: "1.2")]`); the form `name = literal` has no derivation. The spelling without `#`,
`[name]`, is not an attribute; inside a block it reads as an array expression.

Attributes stand before an item, first, before `pub` and before the word that starts the item (`ModuleItem`): one
order for every item kind, so `#[test] pub fn t() { }` has one derivation. An attribute is admitted by one table, keyed
by its name, the kind of the item that it stands before, and its argument form. The table below is that table.

| Name | Item | Argument form | Meaning | Status |
|------|------|---------------|---------|--------|
| `raw_memory` | a function declaration | none, or `(sealed)` | [Raw memory](./memory.md#raw-memory) | Core v1 |
| `test` | a function declaration at module level with no parameter and the result type `unit` | none | the function is a test | Core v1 |
| `grad` | a function declaration `f` | `(g, p1, ..., pk)`: identifiers, `p1` to `pk` parameters of `f` | declares the function `g` with the parameters of `f`; the result of `g` is the gradient of `f` with respect to `p1` to `pk` | Core v1 |
| `repr` | a `struct` declaration | `(C)` | [Struct layout attribute](./ffi.md#struct-layout-attribute) | extension |
| `requires` | the module line `module m;` | `(mind_spec: "M.N")` | [Versioning](./versioning.md) | extension |

An attribute whose name has one segment MUST be refused at check time with
[`E2502`](./errors.md#e2502-invalid-attribute) when the table has no row for its name, the item kind and the argument
form: `#[fast] struct S { a: i64, }`, `#[repr(packed)] struct S { a: i64, }`, `#[repr(C)] fn f() { }`,
`#[test] fn t(x: i64) { }` and `#[test] fn t() -> i64 { return 0; }` are refused. A row marked "extension" holds for
an implementation that provides the form; the module line is not derived by the Core v1 grammar.

**Tool attributes.** An attribute whose name has two segments, `#[tool.name]` or `#[tool.name(arg, ...)]`, is a tool
attribute. Its first segment MUST be listed in the project file; otherwise the attribute MUST be refused at check time.
The compiler checks its form and gives it no meaning. A tool attribute MUST NOT change a byte of the artifact: the IR
bytes and the native image of a program are the same with and without it. This proof is a gate of the reference
compiler repository: it compares the IR bytes and the native image with and without the attribute, and a mutant that
changes one byte turns it red. A name of
three or more segments, such as `#[a.b.c]`, has no derivation.

## Raw memory

Raw memory, the attribute `raw_memory` and its refusals are defined in
[Memory model](./memory.md#raw-memory).

## Entry function

The entry function of a program is the function named `main`. An executable build needs one `main` at the top
level of the program; a build with none MUST be refused with
[`E2403`](./errors.md#e2403-invalid-entry-function). `main` MUST have no parameter, and its
result type MUST be `i64` or `unit`. As for every function, the result type `unit` may be omitted or written:
`fn main() -> i64 { ... }`, `fn main() { ... }` and `fn main() -> unit { ... }` are the forms. A `main` with a
parameter or with another result type MUST be refused at check time with
[`E2403`](./errors.md#e2403-invalid-entry-function). When `main` returns the `i64` value `v`, the process
status is the low 8 bits of `v` in two's complement, read as an unsigned number from 0 to 255, on every
substrate: the result 300 gives the status 44, and the result -1 gives the status 255. When the result type
of `main` is `unit`, the process status is 0.

## Bindings and assignment

`let p = e;` binds the names of the pattern `p` ([Patterns and match](#patterns-and-match)); a `let` pattern may be
nested, such as `let ((a, b), c) = ((1, 2), 3);`. `let mut p = e;` binds every name of `p` as a mutable binding; one
`mut` stands per `let`. `let _ = e;` evaluates `e` and drops the value: `_` binds nothing. A name that a `let` without
`mut`, a parameter of a function, the pattern of a `for` or the pattern of a `match` arm binds is not mutable. A later
`let` of the same name is a new binding and not an assignment, so `let x = 1; let x = 2;` is valid.

Assignment is a statement and has no value: `p = e;` and `p op= e;` (`ExpressionStatement` with an
`AssignmentOperator`). A chain `a = b = c;` and an assignment inside an expression, such as `if x = 1 { }` or
`f(x = 1)`, have no derivation and MUST be refused with `E1107`. The left operand of an assignment or of a compound
assignment is a place: a name, or a chain of index, field and tuple-index accesses on a name (`x`, `a[i]`, `p.f`,
`t.0`, `a[i].f.1`). The name at the start of the chain is the root of the place. An assignment or a compound assignment
to a place needs the root name to be declared with `let mut`; a `const` is never the root of a place. A left operand
that is not a place, a place whose root is not mutable, and a place whose root is a `const` MUST be refused at check
time with [`E2402`](./errors.md#e2402-invalid-target-of-a-change): after `let a = [1, 2];`, the statement `a[0] = 5;`
is refused. The right operand of `=` MUST have the type of the place; otherwise the statement MUST be refused at check
time with [`E2001`](./errors.md#e2001-type-mismatch): after `let mut x = 1;`, the statement `x = true;` is refused.

The compound assignment operators are `+=`, `-=`, `*=`, `/=`, `%=`, `<<=`, `>>=`, `&=`, `|=` and `^=`; each is
written with no space in it (`<<=` and `>>=` are formed from joined tokens, the others are one token each,
[Tokens](./lexical.md#tokens)), so `x + = 2` is refused. `x op= e` means `x = x op e`, where `op` is the operator
before the `=`, and the place
`x` is evaluated once: in `a[f()] += 1` the call `f()` runs once. The order is that of
[Evaluation order](#evaluation-order). The rules of `op` for the types of its operands apply.

**Statement types.** `e;` evaluates `e` and discards its value; only the tail expression of a block gives the block its
value. The body of a function has the result type of the function: `fn f() -> i64 { 2; }` and
`fn f() -> i64 { let x = 1; }` MUST be refused at check time with [`E2001`](./errors.md#e2001-type-mismatch). An `if`
without `else` has the type `unit`. Divergence is a property of the text alone: `return`, `break`, `continue`, a `loop`
that no `break` ends, and an `if` or a `match` all of whose branches diverge, diverge; `while` and `for` never diverge.
A body or a branch that diverges satisfies every expected type.

## Loops

`while c { ... }`, `for p in e { ... }` and `loop { ... }` are expressions (`WhileExpression`, `ForExpression` and
`LoopExpression` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)). A `while` loop and a `for` loop have the type
`unit`, and their value is `()` ([The unit value](./types.md#the-unit-value)): after `let u = while c { };`, `u` is `()`.
`loop B` runs the block `B` again and again until a `break` ends it: a `loop` that a `break` ends has the type `unit`,
and a `loop` that no `break` ends diverges, so `fn f() -> i64 { loop { return 1; } }` is valid. A loop that stands as a
statement is a [block-like statement](#block-like-statements) and takes no `;`.

**Counting loops.** `for p in a..b B` counts from `a` up to `b`, `b` not included, and `for p in a..=b B` counts from
`a` up to `b`, `b` included. `a` and `b` MUST have one integer type. They are evaluated once, `a` first, before the
first iteration. The loop `a..b` is empty when `b <= a`, and the loop `a..=b` is empty when `b < a`. The counter
never overflows: a loop `a..=b` whose `b` is the largest value of the type runs its last iteration with `b` and ends.
`..` and `..=` stand only in the header of a `for` loop and, for `..=`, in a [range pattern](#patterns-and-match): a
range is not a value, so `let r = 0..4;` and `a[1..3]` have no derivation and MUST be refused with `E1101`; the message
for an index names the slice form `a[1:3]`.
Without `..` or `..=`, the expression after `in` is an ordinary expression.

A `for` loop over a container ([Records and containers](./memory.md#records-and-containers)) reads the length of
the container one time, at the start of the loop. For each index from 0 to that length minus 1, in order, one
iteration binds the pattern to the element at that index. Elements that are added during the loop are not visited,
and an element that is no longer there when its iteration starts makes the [defined stop](./memory.md#the-defined-stop)
of an index outside the container, with [`E6001`](./errors.md#e6001-out-of-bounds-index).

## Block-like statements

The six forms `if`, `match`, a block, `while`, `for` and `loop` may stand as a statement with no `;` after them
(`BlockLikeStatement` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)). A `defer` statement takes no `;`
either: it ends at the closing brace of its block (`DeferStatement`), so `defer { };` has no derivation and
MUST be refused. Every other statement ends with its `;` ([Statement separators](#statement-separators)).

**Reading rule.** Where a statement can start and the next token starts one of the six forms (`if`, `match`, `{`,
`while`, `for` or `loop`), the form is read as a `BlockLikeStatement` and ends at its closing brace (for an `if` with
`else`, the closing brace of its last block); what follows starts a new statement. This is a one-token rule of the
parser ([Lookahead of the grammar](#lookahead-of-the-grammar)). Two cases come before this rule:

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
`if c { 1 } else { 2 }; return 0;` is valid. For a form that a `-` follows, as in
`fn f(c: bool) -> i64 { if c { 1 } else { 2 } - 3 }`, the diagnostic MUST name the form with parentheses,
`(if c { 1 } else { 2 }) - 3`.

## Loop exits

Inside the body of a `while`, a `for` or a `loop`, the statements `break;` and `continue;` end the innermost
loop and start its next iteration, respectively. A `break` or a `continue` that is not inside the body
of a `while`, a `for` or a `loop` MUST be refused at check time with
[`E2401`](./errors.md#e2401-loop-exit-outside-a-loop). A loop exit takes no value and no label, and its
`;` is required ([Statement separators](#statement-separators)): no token of the
[lexical grammar](./grammar-lexical.ebnf) starts with `'`, so `break 'a;` contains an invalid token and
MUST be diagnosed, and `break 7;` has no derivation and MUST be refused. In a `match` arm, `break` and `continue` are
an arm body and take the `,` of the arm ([Patterns and match](#patterns-and-match)).

`break`, `continue` and `loop` are keywords ([Lexical Structure](./lexical.md#keywords)). A source in which one of
them stands where the grammar needs a name or an expression has no derivation and MUST be refused: `let break = 4;`,
`break - 1;`, `break = 5;` and `let loop = 1;` are refused, a keyword in a name position with `E1007`.
`while c { break }` is refused because the `;` of the loop exit is missing.

## Tuple index

`e.N` (`TupleIndexOperator`) is the element `N` of the tuple `e`, counted from 0: after `let t = (4, 5);`, `t.0` is 4
and `t.1` is 5. `N` is `0`, or a digit from 1 to 9 followed by digits, with no sign, no prefix, no `_` and no leading
zero; `t.01` and `t.1_0` MUST be refused with [`E2404`](./errors.md#e2404-invalid-tuple-index). Directly after the token
`.` the lexer reads a digit run as an integer token ([Tokens](./lexical.md#tokens)), so `t.0.1` means `(t.0).1`, and
`t.0.1e0` is refused with [`E1005`](./errors.md#e1005-invalid-numeric-literal). The type of `e` MUST be a tuple type and
`N` MUST be less than its number of elements; otherwise the source MUST be refused at check time with
[`E2404`](./errors.md#e2404-invalid-tuple-index). An index operator `e[i]` on a tuple has no meaning: when the type of
`e` is a tuple type, `e[i]` MUST be refused with `E2404`, and the diagnostic MUST name the form `e.N`.

`a[s:e:k]` (an `IndexItem` with a `SliceTail`) is a slice: it takes the elements of the axis from the index `s` up to,
and not including, the index `e`, with the step `k`. An omitted `s` is 0, an omitted `e` is the length of the axis, and
an omitted `k` is 1, so for an axis of length `n`, `a[:e]` is `a[0:e:1]`, `a[s:]` is `a[s:n:1]`, `a[:]` is
`a[0:n:1]` and `a[s:e]` is `a[s:e:1]`. The form lowers to the `Slice` operation of
[Core IR](./ir.md#indexing-and-slicing) with these bounds and this step, and the shape of the result follows the shape
rule of that operation: `a[1:3]` takes the elements 1 and 2, and `a[0:4:2]` takes the elements 0 and 2. An index or a
slice bound outside its axis is the case of [Index bounds](./ir.md#index-bounds). An index and a slice bound MUST have
an integer type, used exactly; another type MUST be refused at check time with
[`E2005`](./errors.md#e2005-invalid-dtype-for-operation), and the message names `as i64`: `a[1.5]` is refused.

Inside the brackets of an index and outside any nested pair of `(` and `)`, `[` and `]`, or `{` and `}`, the text `::`
is two slice colons
([Tokens](./lexical.md#tokens)): `a[::2]` is `a[0:n:2]`, and `a[s::k]` is the slice from `s` with the step `k`. A path
there is written in parentheses, `a[(E::B)]`. So `a[E::B]` is the slice from `E` with the step `B`: after
`const E: i64 = 1;` and `const B: i64 = 2;` it is `a[1::2]`. When `E` names a type and not a value, the bound is not a
value, and the name rule refuses the source at check time. The grammar has no range index: `a[1..3]` is not derived ([Loops](#loops)).

## Field access and method calls

`x.f` (`MemberOperator` with no call) is the field `f` of the value `x`. `x.m(a)` (`MemberOperator` with a
`CallOperator`) is a method call: it calls the method `m` of the type of `x` with the receiver `x` and the arguments
`a`, for example `o.unwrap_or(0)` on an `Option<i64>` ([`core` module](./stdlib.md#pattern-matching-support)). One
token after the name decides between the two: a `(` makes the method call. When `x` is an import qualifier, `x.m(a)` is
the call of the member `m` of that module ([Module-qualified references](#module-qualified-references)). `a.b`
resolves to a member of a module when `a` is an import qualifier, else to a method or to a field of the type of `a`.
A method call whose `m` is not a method of the type of `x` MUST be refused at check time with `E2410` ("no such
method"): `5.nosuchmethod()` is refused. A field access `x.f` whose `f` is not a field of the type of `x` MUST be
refused at check time, unless `x` is an import qualifier. A generic method takes its type arguments as
`e.m::<A>(x)` (`MemberOperator`); this form is not in Core v1 ([Core v1 scope](#core-v1-scope)).

A call follows only a function name, a variant path (`E::A(x)`) or a method name (`NamePath` and `MemberOperator` of
the grammar). Core v1 has no function values, so a call of any other value has no derivation and MUST be refused with
`E1101`, with the message "a value is not a function in this edition": `5(3)`, `f(1)(2)`, `(f)(2)` and `(x.m)(a)` are
refused.

## Record literals

`Name { f: e, ... }` (`NamePath` with a `RecordBody`) builds a value of the struct `Name`. It names each field of the
struct once; a field named twice MUST be refused at check time. The fields are evaluated in source order
([Evaluation order](#evaluation-order)). In the head of `if`, `while`, `for ... in` and `match`, an identifier
followed by `{` starts the block, and a record literal there is written in parentheses: `if p == (P { x: 1 }) { }` is
valid, and `if p == P { x: 1 } { }` has no derivation and MUST be refused with `E1101`, with the form in parentheses in
the message. So `if b { }` reads the same as every other head.

## Patterns and match

A pattern (`Pattern` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)) stands in a `let`, in the header of a `for`
and in a `match` arm; every site uses the one `Pattern` rule, so a nested tuple pattern is valid at every site. A
parameter of a function is a name or `_` (`Parameter`); `_` may name several parameters of one function. The pattern
of a `let` and of a `for` MUST be irrefutable: a name, `_`, or a tuple or a record pattern whose parts are all
irrefutable. A refutable pattern there, such as `let Some(x) = o;` or `for 0 in xs { }`, MUST be refused at check time
with [`E2310`](./errors.md#e2310-refutable-pattern-in-a-binding), and the help text names `match`. The forms are:

- **A name** (`IdentifierPattern`): a bare identifier always binds a new name, in every scope. The predeclared
  variant names `Some`, `None`, `Ok` and `Err` are never bound: a bare `None` is the variant `None`.
- **The wildcard** `_` (`WildcardPattern`): it matches every value and binds nothing. `_` is not a name: where an
  expression stands, it has no derivation (`return _;` MUST be refused with `E1101`).
- **A tuple** `(p1, p2)` (`TuplePattern`), **a variant** `E::A`, `E::A(p)` or `Some(p)` (`VariantPattern`), and
  **a record** `P { x, y: q }` (`RecordPattern`).
- **A literal** (`LiteralPattern`): an integer literal with an optional `-`, `true`, `false` or a string literal.
- **A range** `a..=b` (`RangePattern`): it matches every integer `v` with `a <= v` and `v <= b`; its bounds are integer
  literals, each with an optional `-`, or `const` names. A range pattern has only the closed form: `a..b` in a
  pattern has no derivation and MUST be refused.
- **Alternatives** `p | q`: the alternatives are tried from left to right, and each alternative MUST bind the same
  names with the same types; otherwise the source MUST be refused with `E2313`: `(x, 0) | (0, y) => 1,` is refused. A
  pattern has no leading `|`: `| 1 => 2,` has no derivation and MUST be refused with `E1101`.

A pattern that does not fit the type of its value MUST be refused with [`E2001`](./errors.md#e2001-type-mismatch) at
every site: `let (a, b, c) = (1, 2);` is refused. `Some`, `None`, `Ok` and `Err` are the only spellings of those
variants: `Option::Some(1)` MUST be refused with
[`E2002`](./errors.md#e2002-unresolved-name-or-qualified-owner), and a binding or a declaration that takes one of these
names, such as `let None = 1;`, MUST be refused with `E2042`.

**Match.** `match e { arms }` (`MatchExpression`) tries its arms in order. Every arm ends with `,`, the last one too
(`MatchArm`): `0 => { 1 } _ => 2,` MUST be refused with `E1103`, at the point where the `,` belongs. An arm is a
pattern, an optional guard `if c`, `=>` and a body (`ArmBody`). The body is `return` with an optional expression,
`break`, `continue`, or an expression optionally followed by an assignment operator and an expression; an arm with an
assignment is an arm statement of the type `unit`. A body that starts with `{` is a block expression, so
`0 => { 1 } - 1,` is valid and its body is `{ 1 } - 1`. The guard has the type `bool` and is evaluated at most once
per `match`.

```mind
let r = match x {
    0 => 10,
    1..=9 => 20,
    n if n < 0 => { 30 },
    _ => 40,
};
```

A bare unguarded name arm matches every value. When its name is the name of an enum variant or of a `const` item in
scope, the arm MUST be refused, with `E2301` when it is not the last arm and with `E2314` when it is the last arm; the
message gives the fix `n if n == K`. Any other bare unguarded name arm that is not the last arm MUST be refused with
`E2312`, because no later arm can run. A dead arm, which no value can reach because the arms before it match every
value it matches, MUST be
refused with `E2312`. A `match` that does not cover every value of its operand MUST be refused with `E2311`, and the
message names one missing case, chosen by a fixed order: the variants in declaration order, `false` before `true`, and
the least integer that no arm covers. `match b { true => 1, }` is refused, and the message names `false`.

## Statement separators

The separators are the ones that [`grammar-syntax.ebnf`](./grammar-syntax.ebnf) writes. `;` is required after a `let`,
after a `return`, after a loop exit, after an `assert` and after an `ExpressionStatement`, an assignment too; a
`BlockLikeStatement` and a `defer` statement take none ([Block-like statements](#block-like-statements)). Every `match`
arm ends with `,`, the last arm too (`MatchArm`). An item that does not end with a block (`type`, `const`, `import`,
`use`, a function signature) ends with `;`, and an item that ends with `}` takes none. Checking and building MUST
refuse a source in which one of these separators is missing, with `E1103` at the point where the separator belongs:
`let x = 1` followed by a line `return x;`, `return x }`, `break }`, `use std.vec` with no `;` and `const K = 1` with
no `;` are refused. A missing separator has no meaning in the language. A `;` that stands where no statement and no
item needs it, such as `fn f() { };` or a lone `;` in a block, MUST be refused, and the message says "remove the
`;`". `mindc check` runs the check of the syntax before the check of the format, so a missing separator is reported as
a syntax fault and not as a difference of format.

`assert` is a keyword, and an assertion has one form, `assert c;` or `assert c, "message";` (`AssertStatement`). `c`
has the type `bool`. A second form such as `assert(c, "m");` is not an assertion with a message; the grammar reads it
as an `assert` of one parenthesised tuple, which is not a `bool`, and it MUST be refused at check time.

A source formatter MAY read a source in which such a separator is missing and write it with the
separator. That reading is a repair of the text that the formatter does before it writes the strict form;
it does not make the source without the separator a program of the language, and a checker or a build
MUST NOT accept that source.

## Words that the grammar spells out

The keywords are reserved ([Keywords](./lexical.md#keywords)); among them are `mut`, `loop`, `assert`, `true`, `false`
and `pub`. A keyword where a name stands MUST be refused with `E1007`, one diagnostic at the word: `let mut = 1;`,
`let loop = 1;`, `fn assert() { }` and `fn f(true: i64) { }` are refused.

The syntactic grammar also spells out words that are not keywords (`in`, `as`, `const`, `enum`, `module`, `use`,
`extern`, `diff`, `dyn`, `tensor`, `dtype` and the primitive type names).
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf) lists them as `ContextualWord`, a rule for documentation: the lexer
produces each of them as an identifier. Each of them has its own positions in the syntactic grammar, and at each
position at most two tokens decide whether the word is the spelled word or a name; there is no search for a derivation.
Where the grammar spells the word out at that position, the word is the spelled word; elsewhere it is a name:
`let diff = 1; return diff;` is valid.

| Source | Meaning |
|--------|---------|
| `tensor(1);` | The tensor constructor: `tensor` directly followed by `(` is always the constructor. |
| `fn tensor(a: i64) { }` | Refused with `E1007`: a function, a parameter of a function type or an import named `tensor` is refused, because a call of it could not be written. `tensor` stays a valid name of a value. |
| `let _ = 1;` | The wildcard: `_` is a token of its own and not a name. |
| `let x: i64 = 1;` | The primitive type `i64`. |
| `let diff = 1; return diff;` | The name `diff`: no rule spells the word out after `let`. |
| `let mut = 1;` | Refused with `E1007`: `mut` is a keyword. |

## String escapes

The escape sequences of a string literal are `\n`, `\r`, `\t`, `\0`, `\\`, `\'`, `\"` and
`\u{HEX}` (one to six hexadecimal digits, a value of at most `10FFFF` and outside `D800` to `DFFF`), as in
`EscapeSequence` of [`grammar-lexical.ebnf`](./grammar-lexical.ebnf). Any other escape sequence MUST be diagnosed with
[`E1004`](./errors.md#e1004-invalid-escape-sequence).

## Macros are not part of the language (informative)

MIND has no macros. A form such as `println!("x")`, `vec![1, 2]` or `panic!("x")` is not a macro
call and is not part of the language. Use the function form, for example the
`println` and `panic` functions of [Standard Library](./stdlib.md).

## Items and modules

### Module level

A module holds items only (`Module` and `ModuleItem` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)): a statement
at module level, such as `let x = 1;`, MUST be refused. Every item form is reached from `Module`. The attributes of an
item come first, then `pub`, then the word that starts the item ([Attributes](#attributes)). The external functions of
a program are written in one form, the block `extern "C" { fn f(x: i64) -> i64; }` (`ExternDeclaration`): `extern "C"
fn f();` has no derivation, and an ABI string other than `"C"` MUST be refused with
[`E2502`](./errors.md#e2502-invalid-attribute). An enum payload list may end with `,`.

The initializer of a `const` is a constant expression with no call: `const K: i64 = f();` MUST be refused at check
time with [`E2001`](./errors.md#e2001-type-mismatch).

A module has one namespace for its items of every kind; the parameters of a function, the fields of a struct and the
variants of an enum each have their own list. A second declaration of a name in one of them MUST be refused with
`E2720` at the second declaration, and the message names the first: two functions `f`, a struct and a function with
one name, two parameters with one name and two variants with one name are refused. Every type name MUST resolve; an
unknown type name MUST be refused with [`E2002`](./errors.md#e2002-unresolved-name-or-qualified-owner), with at most
one hint, chosen by a fixed rule (the least edit distance, then the source order), and no further diagnostic follows
from it.

`.` follows a value or a module, and `::` follows a type: `q.f()` calls the member `f` of the module `q`, and
`E::A` names a variant of the type `E`. `::` after a module MUST be refused with
[`E2731`](./errors.md#e2731-path-separator-after-a-module), with the edit to the dot form: `m::f()` for a member of the
module block `m` is refused, and the fix is `m.f()`. `.` after a type MUST be refused with
[`E2002`](./errors.md#e2002-unresolved-name-or-qualified-owner), and the message gives the fix. A binding MUST NOT take the name of an import qualifier or of a module block in
scope; such a binding MUST be refused with `E2730`.

### Visibility

`pub` before an item makes the item visible outside its module (`ModuleItem`); an item without `pub` is visible only in
its module. `pub` is a keyword, and it stands after the attributes of the item and before the word that starts a named
item: a function, a `type`, a `struct`, an `enum`, a `const`, a `trait` or a module block (`pub fn f() -> i64 { 1 }`).
There is no export list: `export` is a reserved word that no rule spells, so `export { f }` and `export f;` MUST be
refused.

### Module-qualified references

> **Status:** normative correction, targeted for specification 1.7.0; it does not declare that
> release. Earlier text of the grammar wrote import paths with `::`, which no released reference
> compiler accepted for `import`, and left the meaning of a qualifier unspecified. The separator and
> the qualifier rule below were decided by the specification owner on 2026-10-07.

Import paths separate their segments with `.` (`import a.b;`). An import binds a qualifier in the
module that declares it: the last segment of its path (`b` for `import a.b;`). In that module, a
reference `q.m`, or a call `q.m(args)`, whose head `q` is an import qualifier denotes the `pub` member `m`
of the module that import names. It MUST resolve to that module's member even when another
imported module, or the current module, declares a member named `m`, and it MUST be refused with
`E2002` during checking and artifact-producing builds when that module has no `pub` member `m`; a
refused build MUST leave no artifact. A qualified type or enum variant follows the same rule (see
[Types](./types.md)). A local binding never hides an import qualifier: a binding with the name of an
import qualifier in scope is refused with `E2730` ([Module level](#module-level)).

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
  general parametric-polymorphism surface (no multi-parameter generics, no user-defined generic
  containers such as a user-defined `Table<K, V>`); trait bounds in a type-parameter list are specified in
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
- **Collections**: `Vec<T>`, `Map<K, V>` and `String` are container records that change in place
  ([Memory model](./memory.md#records-and-containers)); `std.map` is insert-only (no removal) — see
  [Standard Library](./stdlib.md#four-pure-mind-modules) for the precise shipped surface, which is smaller than a
  full container library.
- **Range `for` loops**: the grammar derives `for v in s..e { ... }` and `for v in s..=e { ... }`
  ([Loops](#loops)). The reference v0.10.4 refuses `for i in 0..=3` with `E1001` (probe `c_for_range_incl`). The
  reference interpreter evaluates `e` once and binds `v`
  fresh on each iteration. Since v0.10.3, compiled output follows it when the body re-declares
  `v` with `let` or a tuple `let`: the re-declaration shadows `v` from that statement to the end of
  the iteration and does not change the iteration count (`fe9854ec`, v0.10.3; Rust IR
  lowering, not the pure-MIND native path). Before `fe9854ec`, the compiler built such a loop to an
  executable that did not terminate; the behaviour of v0.10.2 for this shape is not established
  here. Known gap: an end bound that reads memory the body mutates through an index or field store is
  not detected, so compiled output can re-evaluate it on each iteration.
- **Assertions**: the form of the language is `assert cond;` or `assert cond, "message";`
  ([Statement separators](#statement-separators)). The reference also accepts `assert cond` with no `;` and the
  parenthesised `assert(cond, "message")`, and each asserts `cond` (parenthesised form: `487dd5c7`, v0.10.3);
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
  form is not in [`grammar-syntax.ebnf`](./grammar-syntax.ebnf). The reference `use` also accepts `::`
  between path segments, which this specification refuses ([Module level](#module-level)). A zero-argument
  `.sum()` or `.mean()` on a receiver named like an
  import is a module call, not a tensor reduction (`f2fc890d`).
