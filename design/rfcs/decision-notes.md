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

# Decision Notes (Informative)

This page lists points where the specification text did not decide the meaning of a form that it
names. A note records the text, the behaviour of the reference compiler v0.10.4 (measured with
`mindc check --no-fmt`, and `mindc build --backend native` where it is named), and the options. **A note
does not give a meaning, except where it records a decision.** The specification owner decided every point on
2026-11-24; each note records the decision in its **Decision** paragraph, and an RFC or an editorial change carries
it into the normative text. The tables of options stay as the record of the choice. Each note ends with the status
of its forms after the decision; the change that carries the decision brings
[Core v1 form status](../../spec/v1.0/core-v1-forms.md) to the same status. The status is **Open** only where the
note says so.

## DN-1. The operator `:=`

**Text today.** `:=` is in `AssignmentOperator` ([`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf)),
in the `Operator` list of [`grammar-lexical.ebnf`](../../spec/v1.0/grammar-lexical.ebnf), in the precedence
table of [Language](../../spec/v1.0/language.md#operator-precedence-and-associativity) (row 9, "Assignment
and compound assignment") and in the token examples of [Lexical Structure](../../spec/v1.0/lexical.md#tokens).
No sentence says what `x := e` means, and no example uses it.

**Reference.** `let mut x = 1; x := 2;` is refused with `E1001`, ``unexpected `:`, expected an expression``
(3:7). `let y = x := 2;` is refused in the same way.

**Options.**

| Option | Effect |
|--------|--------|
| A. Remove `:=` from the grammar, the operator list and the precedence table | The token no longer exists. The reference already behaves like this. No program changes. |
| B. Define `x := e` as `x = e` | Two spellings of one assignment. The formatter needs a rule for which one it writes. |
| C. Define `x := e` as "declare and assign" (a new binding when `x` is unbound) | Changes the scope rules: an assignment can introduce a name. Needs a rule for a name that exists in an outer scope. |

**Rows.** `colon_assign_*` in [`tests/conformance/syntax`](../../tests/conformance/syntax/README.md) record the
reference behaviour (kind `reference-observed`).

**Decision.** Option A, decided by the specification owner on 2026-11-24. `:=` is removed from
`AssignmentOperator`, from the `Operator` list of the lexical grammar, from the precedence table and from the token
examples of the lexical chapter; `x := e` is not part of the language.

**Form status.** Not in the language: Core v1 refuses `x := e`. The reference refuses it too.

## DN-2. `while` and `for` as expressions with a value

**Text today.** `PrimaryExpression` lists `WhileExpression` and `ForExpression`. No sentence gives the type or
the value of a loop.

**Reference.** `let x = while i < 3 { i };` is refused with `E2002`, ``unknown identifier `while` ``; the same for
`for`. A loop works as a statement.

**Options.** (A) A loop is a statement and leaves `PrimaryExpression`. (B) A loop has the type `unit` and the
value `()` ([DN-4](#dn-4-the-unit-value)). (C) A loop has a value taken from a `break` with a value, which needs
a value form of `break` that the grammar does not have.

**Decision.** Option B, decided by the specification owner on 2026-11-24. This replaces the first decision of this
note, which was option A. `while` and `for` stay in `PrimaryExpression`, and a loop has the type `unit` and the value
`()` ([DN-4](#dn-4-the-unit-value)). The reason is that the rule for block-like statements
([DN-10](#dn-10-separators-that-the-grammar-requires-and-the-reference-does-not)) is then one rule for five forms
(`if`, `match`, a block, `while` and `for`), and no production of the published grammar is removed, so a program that
the published grammar derives, such as `while c { };`, stays valid.

**Form status.** Core v1: a loop has the type `unit`. Reference gap: the reference refuses a loop where a value
stands (`E2002`, measured above).

## DN-3. The remainder operator on floating-point values

**Text today.** `%` is in the precedence table and in the lexical operator list. [Language](../../spec/v1.0/language.md)
gives no rule for the type of its operands or the sign of the result.

**Reference.** `let x: f64 = 7.5 % 2.0;` is accepted by `mindc check --no-fmt`. The native backend refuses it with
`lane.type.mismatch`. For integer operands `%` builds and runs.

**Options.** (A) `%` is defined for integers only; a float operand is refused at check time. (B) `%` on floats
is the truncated remainder (the result has the sign of the left operand). (C) `%` on floats is the IEEE 754
remainder (round to nearest). A decision must also fix the result for a zero or infinite right operand and for
NaN, because the result must be bit-identical on every substrate.

**Decision.** Option B, decided by the specification owner on 2026-11-24. On `f32` and `f64`, `a % b` is the
truncated remainder `a - n * b`, where `n` is `a / b` truncated toward zero; the result is exact and has the sign of
`a`. The special cases are normative: an infinite `a` or a zero `b` gives NaN; a finite `a` with an infinite `b`
gives `a`; a zero `a` with a `b` that is not zero and not NaN gives `a` with its sign; any NaN operand gives NaN.
This NaN is the canonical NaN: [Types](../../spec/v1.0/types.md) has none, so this change defines one bit pattern
for each float type, `0x7FC00000` for `f32` and `0x7FF8000000000000` for `f64` (sign bit clear, quiet bit set, other
payload bits clear).

**Form status.** Core v1 for `%` on integers and on floats. `%` on floats is a reference gap: the native backend
refuses it with `lane.type.mismatch`.

## DN-4. The unit value

**Text today.** `unit` is a primitive type ([Types](../../spec/v1.0/types.md)); the standard library calls its
value `()` ([Standard Library](../../spec/v1.0/stdlib.md)). No expression production derives `()`:
`ParenthesizedExpression` and `TupleExpression` need an inner expression.

**Reference.** `let u = ();` is accepted. `let u: unit = ();` is accepted. `let n: i64 = ();` is also accepted,
so the type of `()` is not checked against the annotation. The native backend refuses all three
(`lane.source.tuple`).

**Options.** (A) Add the production `UnitExpression = "(" , ")"` with the type `unit`, and make the check
refuse a use of `()` where another type is expected. (B) Remove the value from the language: a function without
a result type is the only way to produce no value.

**Decision.** Option A, decided by the specification owner on 2026-11-24. The production
`UnitExpression = "(" , ")"` gives the value `()` of type `unit`; the check refuses `()` where another type is
expected.

**Form status.** Core v1, reference gap: the reference accepts `let n: i64 = ();`, and the native backend refuses
`()`.

## DN-5. The `^` suffix of a differentiable literal

**Text today.** [Lexical Structure](../../spec/v1.0/lexical.md#literals) says that a differentiable literal MAY
include a tangent annotation with the suffix `^` and refers to [Automatic differentiation](../../spec/v1.0/autodiff.md),
which has no text for it. `DifferentiableLiteral = Literal , "^"` is in the lexical grammar, and `^` is also
the bitwise exclusive-or operator.

**Reference.** `1.0^;` reads as the operator `^` with a missing operand, so the suffix does not exist in
practice (measured with v0.10.4).

**Options.** (A) Remove the suffix. (B) Give the suffix a meaning in the autodiff chapter and a lexical rule
that separates it from the operator (for example, no whitespace and no operand to the right).

**Decision.** Option A, decided by the specification owner on 2026-11-24. The `^` suffix is removed from the lexical
text and from the grammar (`DifferentiableLiteral`); `^` is only the exclusive-or operator.

**Form status.** Not in the language. The reference reads `1.0^` as the operator with a missing operand, which agrees
with the decision.

## DN-6. Precedence of `as`

**Text today.** The comment at the end of [`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf) lists `as`
below `+` and `-` (level 4 of 7, where level 1 binds tightest). The table of
[Language](../../spec/v1.0/language.md#operator-precedence-and-associativity) has no row for `as`. The block of
the comment belongs to the v1.1 candidate additions.

**Reference.** `as` binds tighter than `*` (measured with v0.10.4). The two
sources disagree for an expression such as `a * b as f64`. The reference refuses `1 as bool` at check time
(`E2016`, "cast to `bool` is not permitted") and accepts `300 as u8`.

**Options.** (A) Keep the reference and change the comment. (B) Keep the comment and change the reference.
Either choice changes the meaning of existing programs that mix `as` with `*`, `/`, `+` or `-`.

**Decision.** Option A, decided by the specification owner on 2026-11-24. `as` binds tighter than `*`: the comment
of the grammar is corrected, and the precedence table of Language gets a row for `as`. `a * b as f64` is
`a * (b as f64)`. The cast itself is defined too: `e as T` is a `CastExpression` of the grammar, and its result has
the type `T`. The rule is the same on every substrate, bit for bit:

1. Integer to integer: the value modulo 2^N of the width N of the target. A signed source is sign-extended, and an
   unsigned source is zero-extended.
2. Integer to float: round to nearest, ties to even.
3. Float to integer: truncate toward zero. A value outside the range of the target gives the nearest bound of the
   target. NaN gives 0.
4. `f32` to `f64`: exact. `f64` to `f32`: round to nearest, ties to even; an overflow gives the infinity of that
   sign; NaN gives the canonical NaN of [DN-3](#dn-3-the-remainder-operator-on-floating-point-values).
5. `bool` to integer: `false` is 0 and `true` is 1.
6. A cast to the same type is the identity.

Every other cast is refused at check time as a type error (`E2001`). A cast of an integer or a float to `bool` is
refused too: the program writes a comparison.

**Form status.** Core v1: the precedence of `as` and the cast rule. The reference agrees on the precedence. Its
cast results are measured row by row, and each difference is a reference gap.

## DN-7. Loop exits outside a loop, `loop`, labels and values

**Text today.** [Language](../../spec/v1.0/language.md#loop-exits) defines `break` and `continue` inside `while` and
`for`. Nothing defines them outside a loop. `loop` is not a keyword. [Conformance](../../spec/v1.0/conformance.md)
and [MLIR Lowering](../../spec/v1.0/mlir-lowering.md) mention `break`, `continue` and a loop.

**Reference.** A `break` outside a loop is accepted by `mindc check --no-fmt` and refused by the native backend
(`lane.source.loop_exit_scope`). The text `loop { … }` is accepted by `mindc check --no-fmt` and refused by the native
backend without a key. `let loop = 1;` runs. A label `break 'a;` is refused with `E1001`. `break 7;` is read
as `break` followed by `7;`.

**Options.** (A) Refuse a loop exit outside a loop at check time. (B) Add `loop` as a keyword with a
production and a rule that it only ends with a `break`. (C) Add labels and a value to `break`. These options
are independent.

**Decision.** Decided by the specification owner on 2026-11-24, one answer for each option. (A) Yes: a loop exit
outside a loop is refused at check time. (B) No: `loop` is not a keyword in Core v1, and the text `loop { … }` is
refused at check time with a key. (C) No: Core v1 has no labels and no value form of `break`; a later RFC may add
them.

**Form status.** `break` and `continue` in a loop are Core v1. Core v1 refuses a loop exit outside a loop and the
text `loop { … }`: reference gap, because `mindc check --no-fmt` accepts both. Labels and `break` with a value are
not in Core v1.

## DN-8. `let mut` and assignment to a binding

**Text today.** `LetStatement` has no `mut`. [Language](../../spec/v1.0/language.md) shows assignment to a
variable (`x = y = z;`) and does not say that the variable must be declared mutable.

**Reference.** `let mut x = 1; x = 2;` and `let x = 1; x = 2;` are both accepted, and both return 2 when built
natively. `mut` has no checked effect: an assignment to a parameter, `fn f(a: i64) -> i64 { a = 3; return a; }`, is accepted too.
The sample sources in [FFI](../../spec/v1.0/ffi.md) use `let mut`.

**Options.** (A) Define `mut` as part of `LetStatement` and refuse an assignment to a binding without it.
(B) Remove `mut` and allow every assignment. (C) Keep both and document that `mut` is a comment.

**Decision.** Option A, decided by the specification owner on 2026-11-24. `mut` is part of `LetStatement`
(`let mut x = e;`). An assignment or a compound assignment to a place needs the root name of the place to be
declared with `let mut`. A place is a name, or a chain of index, field and tuple-index accesses on a name, so
`a[i] = e;`, `p.x = e;` and `t.0 = e;` need `let mut a`, `let mut p` and `let mut t`. A parameter and the variable of a
`for` are not mutable. An assignment to a name that is not mutable is refused. The reference enforces it together with
its type-check work and a sweep of the dependent sources; until then it is a known gap.

**Form status.** Core v1 (`let mut`), reference gap: the reference accepts an assignment to a binding without
`mut`, and to a parameter.

## DN-9. The result type of the entry function

**Text today.** The entry function is not defined as to its result type.

**Reference.** `fn main() -> i64` builds and returns its value as the process status. `fn main() -> f64` is
accepted by `mindc check --no-fmt` and refused by the native backend with `lane.entry.f64_result`.

**Options.** Define the allowed result types of `main` (for example `i64`, `unit`) and refuse others at check
time, or define how each other result type becomes a process status.

**Decision.** Decided by the specification owner on 2026-11-24. `main` has no parameter, and its result type is
`i64` or `unit`. As for every function, the type `unit` MAY be omitted or written (`fn main() { }` and
`fn main() -> unit { }` are the same). Another result type is refused at check time. The process status is the low
8 bits of the `i64` on every substrate, and status 0 when the result type is `unit`.

**Form status.** Core v1, reference gap: `mindc check --no-fmt` accepts `fn main() -> f64`.

## DN-10. Separators that the grammar requires and the reference does not

**Text today.** `LetStatement` and `ExpressionStatement` end with `;`. A `MatchArm` with an expression ends
with `,`.

**Reference.** A missing `;` after `let` or after an expression statement, and a missing `,` after an
expression arm of a `match`, are accepted. `mindc fmt` inserts the separators and plain `mindc check` then reports
`fmt::drift` for the unformatted text.

**Options.** Make the reference refuse these forms (after a period in which it warns), or relax the grammar.
The first option changes programs that compile today.

This note is about the separators only. A keyword used as a name, a raw line feed in a string, and the tokens
`1e3`, `1i64`, `1.2.3`, `0XFF` and `'a'` are not open: the normative text forbids them
([Lexical Structure](../../spec/v1.0/lexical.md)) and [Core v1 form status](../../spec/v1.0/core-v1-forms.md)
lists them as "Core v1 refuses, reference gap".

**Decision.** Decided by the specification owner on 2026-11-24. `check` and `build` refuse a missing `;` and a
missing `,` of a `match` arm, with no warning period. The formatter MAY read the tolerant form, and it writes the
strict form. The rules are these.

- `;` is required after `let`, after `return`, after a loop exit and after an `ExpressionStatement`.
- A block-like statement takes no `;`. The five block-like forms are `if`, `match`, a block, `while` and `for`.
  The grammar gets `BlockLikeStatement = IfExpression | MatchExpression | BlockExpression | WhileExpression |
  ForExpression` as a form of `Statement`, with no terminator. A formatted MIND source writes these forms without
  `;`, and the published grammar could not derive that.
- Reading rule. Where a statement can start and the next token starts one of the five forms, the form is read as a
  `BlockLikeStatement` and ends at its closing brace. What follows starts a new statement. When nothing but the
  closing brace of the enclosing block follows, the form is the tail `Expression` of that block and gives the block
  its value. To use such a form as an operand at the start of a statement, the program writes parentheses.
- Typing. A `BlockLikeStatement` that is not the tail MUST have the type `unit`. A value is discarded only by an
  `ExpressionStatement` with `;`.
- A `match` arm with an expression ends with `,`. An arm with a block takes no `,`.

**Form status.** Core v1 refuses a missing `;` and a missing `,` of a `match` arm: reference gap. Core v1 also
refuses a block-like statement that is not the tail and has a type other than `unit`: reference gap, because
`fn main() -> i64 { if true { 1 } else { 2 } return 0; }` is accepted by `mindc check --no-fmt`.

## DN-11. Tuple index and range index

**Text today.** `FieldAccessOperator = "." , Identifier`; `IndexExpression` has no range.

**Reference.** `t.1` on a tuple and `a[1..3]` are accepted by `mindc check --no-fmt`. So are `t.0.1` on a nested
tuple, `t.5` on a pair and `t[0]` on a tuple. The native backend refuses a tuple (`lane.source.tuple`).

**Options.** Add a tuple index (`.` followed by an integer literal) to the grammar, with the rule that it needs
a tuple type; and decide whether `a[1..3]` is the same as the slice form `a[1:3]` of the grammar or is removed.
See also [RFC 0025](./0025-patterns.md), question 7.

**Decision.** Decided by the specification owner on 2026-11-24. The grammar gets the tuple index: `.` and a decimal
integer literal without sign or suffix (`t.0`); it needs a tuple type and an index below its arity.
Where the parser expects the `DecimalInteger` of a tuple index and the next token is a float literal of the form
digits "." digits (no exponent, no suffix), the token is read as two tuple indices: `t.0.1` means `(t.0).1`.
[RFC 0025](./0025-patterns.md#tuple-index) carries the production and states the same rule in the same words. `a[1:3]` is the only slice form: `a[1..3]` is
refused at check time, and the message names the slice form. `t[0]` on a tuple has no meaning.

**Form status.** Core v1 for `t.1`, reference gap: the native backend refuses a tuple. Core v1 refuses `t.5` on a
pair and `t[0]` on a tuple (`E2404`), and refuses `a[1..3]`: reference gap, because `mindc check --no-fmt` accepts all
three.

## DN-12. Compound assignment operators

**Text today.** The assignment operator list is closed: `=`, `+=`, `-=`, `*=`, `/=`, `:=`.

**Reference.** `%=`, `<<=`, `>>=`, `&=`, `|=` and `^=` are accepted by `mindc check --no-fmt`. `%=` builds natively;
the others are refused by the native backend without a key.

**Options.** Add the six operators to `AssignmentOperator` and the lexical operator list, or make the reference
refuse them.

**Decision.** Decided by the specification owner on 2026-11-24: add `%=`, `<<=`, `>>=`, `&=`, `|=` and `^=` to
`AssignmentOperator` and to the lexical operator list. `x op= e` means `x = x op e`, with the place `x` evaluated
once.

**Form status.** Each compound operator has the status of its operator: `%=` is Core v1, and `<<=`, `>>=`, `&=`,
`|=` and `^=` belong to the v1.1 candidate block with the bitwise and shift operators. Reference gap: the native
backend refuses these five without a key.

## DN-13. A generic call whose type argument is not fixed

**Text today.** [Types](../../spec/v1.0/types.md#type-inference) says that a generic function MUST infer its type
parameters when the information is sufficient, and that the caller MUST provide explicit type arguments otherwise.
The grammar has no explicit type argument at a call. The text does not say what happens when
the argument types do not fix a parameter. [Error Catalog](../../spec/v1.0/errors.md) has `E2003` (cannot infer type) and
`E2001` (type mismatch).

**Reference.** `fn z<T>(x: i64) -> i64` called as `z(1)`, and `fn mk<T>() -> i64` called as `mk()`, are accepted
by `mindc check --no-fmt`. `fn pick<T>(x: T, y: T) -> T` called as `pick(5, 1.5)` is accepted. The native backend refuses
every generic function (`lane.source.function_contract`).

**Options.** (A) Refuse a call whose type argument no argument fixes with `E2003`, and a call that gives one
parameter two types with `E2001`. (B) Accept the first kind and give the argument no meaning, because it does not
reach the result. (C) Refuse the first kind until an explicit type argument at a call exists
([RFC 0027](./0027-function-generics.md)).

**Decision.** Option A, decided by the specification owner on 2026-11-24. The compiler is deterministic and
explicit: no implicit default type is chosen. The change that carries this decision adds the rule to [Types](../../spec/v1.0/types.md#type-inference).
The reference accepts these calls, and [Core v1 form status](../../spec/v1.0/core-v1-forms.md) lists that as a
gap. No warning period comes before the error ([RFC 0027](./0027-function-generics.md), question 6).

**Form status.** Core v1 refuses, reference gap.
