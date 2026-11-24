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

This page lists points where the specification text does not decide the meaning of a form that it
names. A note records the text, the behaviour of the reference compiler v0.10.4 (measured with
`mindc check --no-fmt`, and `mindc build --backend native` where it is named), and the options. **A note
does not give a meaning, except where it records a decision.** Each point needs a decision of the specification
owner, and then an RFC or an editorial change. Each note ends with the status that [Core v1 form status](../../spec/v1.0/core-v1-forms.md)
gives to its forms. The status is **Open** only where the note says so.

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

**Form status.** Open. `x := e` is in the grammar and has no meaning.

## DN-2. `while` and `for` as expressions with a value

**Text today.** `PrimaryExpression` lists `WhileExpression` and `ForExpression`. No sentence gives the type or
the value of a loop.

**Reference.** `let x = while i < 3 { i };` is refused with `E2002`, ``unknown identifier `while` ``; the same for
`for`. A loop works as a statement.

**Options.** (A) A loop is a statement and leaves `PrimaryExpression`. (B) A loop has the type `unit` and the
value `()` ([DN-4](#dn-4-the-unit-value)). (C) A loop has a value taken from a `break` with a value, which needs
a value form of `break` that the grammar does not have.

**Form status.** Core v1, reference gap. The grammar lists the loop as an expression; the reference refuses a loop as a value.

## DN-3. The remainder operator on floating-point values

**Text today.** `%` is in the precedence table and in the lexical operator list. [Language](../../spec/v1.0/language.md)
gives no rule for the type of its operands or the sign of the result.

**Reference.** `let x: f64 = 7.5 % 2.0;` is accepted by `mindc check --no-fmt`. The native backend refuses it with
`lane.type.mismatch`. For integer operands `%` builds and runs.

**Options.** (A) `%` is defined for integers only; a float operand is refused at check time. (B) `%` on floats
is the truncated remainder (the result has the sign of the left operand). (C) `%` on floats is the IEEE 754
remainder (round to nearest). A decision must also fix the result for a zero or infinite right operand and for
NaN, because the result must be bit-identical on every substrate.

**Form status.** Core v1 for `%` on integers. `%` on floats is accepted by `mindc check --no-fmt` and has no rule in the text (this note).

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

**Form status.** Open.

## DN-5. The `^` suffix of a differentiable literal

**Text today.** [Lexical Structure](../../spec/v1.0/lexical.md#literals) says that a differentiable literal MAY
include a tangent annotation with the suffix `^` and refers to [Automatic differentiation](../../spec/v1.0/autodiff.md),
which has no text for it. `DifferentiableLiteral = Literal , "^"` is in the lexical grammar, and `^` is also
the bitwise exclusive-or operator.

**Reference.** `1.0^;` reads as the operator `^` with a missing operand, so the suffix does not exist in
practice (measured with v0.10.4).

**Options.** (A) Remove the suffix. (B) Give the suffix a meaning in the autodiff chapter and a lexical rule
that separates it from the operator (for example, no whitespace and no operand to the right).

**Form status.** Open.

## DN-6. Precedence of `as`

**Text today.** The comment at the end of [`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf) lists `as`
below `+` and `-` (level 4 of 7, where level 1 binds tightest). The table of
[Language](../../spec/v1.0/language.md#operator-precedence-and-associativity) has no row for `as`. The block of
the comment belongs to the v1.1 candidate additions.

**Reference.** `as` binds tighter than `*` (measured with v0.10.4). The two
sources disagree for an expression such as `a * b as f64`.

**Options.** (A) Keep the reference and change the comment. (B) Keep the comment and change the reference.
Either choice changes the meaning of existing programs that mix `as` with `*`, `/`, `+` or `-`.

**Form status.** Candidate. The precedence of `as` is open.

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

**Form status.** `break` and `continue` in a loop are Core v1. A loop exit outside a loop and `loop` are Open.

## DN-8. `let mut` and assignment to a binding

**Text today.** `LetStatement` has no `mut`. [Language](../../spec/v1.0/language.md) shows assignment to a
variable (`x = y = z;`) and does not say that the variable must be declared mutable.

**Reference.** `let mut x = 1; x = 2;` and `let x = 1; x = 2;` are both accepted, and both return 2 when built
natively. `mut` has no checked effect. The sample sources in [FFI](../../spec/v1.0/ffi.md) use `let mut`.

**Options.** (A) Define `mut` as part of `LetStatement` and refuse an assignment to a binding without it.
(B) Remove `mut` and allow every assignment. (C) Keep both and document that `mut` is a comment.

**Form status.** Extension (`let mut`).

## DN-9. The result type of the entry function

**Text today.** The entry function is not defined as to its result type.

**Reference.** `fn main() -> i64` builds and returns its value as the process status. `fn main() -> f64` is
accepted by `mindc check --no-fmt` and refused by the native backend with `lane.entry.f64_result`.

**Options.** Define the allowed result types of `main` (for example `i64`, `unit`) and refuse others at check
time, or define how each other result type becomes a process status.

**Form status.** Open.

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

**Form status.** Open for a missing `;` and a missing `,` of a `match` arm.

## DN-11. Tuple index and range index

**Text today.** `FieldAccessOperator = "." , Identifier`; `IndexExpression` has no range.

**Reference.** `t.1` on a tuple and `a[1..3]` are accepted by `mindc check --no-fmt`. The native backend refuses a tuple
(`lane.source.tuple`).

**Options.** Add a tuple index (`.` followed by an integer literal) to the grammar, with the rule that it needs
a tuple type; and decide whether `a[1..3]` is the same as the slice form `a[1:3]` of the grammar or is removed.
See also [RFC 0025](./0025-patterns.md), open question 7.

**Form status.** Extension (`t.1` and `a[1..3]`).

## DN-12. Compound assignment operators

**Text today.** The assignment operator list is closed: `=`, `+=`, `-=`, `*=`, `/=`, `:=`.

**Reference.** `%=`, `<<=`, `>>=`, `&=`, `|=` and `^=` are accepted by `mindc check --no-fmt`. `%=` builds natively;
the others are refused by the native backend without a key.

**Options.** Add the six operators to `AssignmentOperator` and the lexical operator list, or make the reference
refuse them.

**Form status.** Extension (the six compound operators).

## DN-13. A generic call whose type argument is not fixed

**Text today.** [Types](../../spec/v1.0/types.md#generics-in-core-v1) says that the type argument of a function
with one type parameter is inferred at each call from the argument types. It does not say what happens when
the argument types do not fix it. [Error Catalog](../../spec/v1.0/errors.md) has `E2003` (cannot infer type) and
`E2001` (type mismatch).

**Reference.** `fn z<T>(x: i64) -> i64` called as `z(1)`, and `fn mk<T>() -> i64` called as `mk()`, are accepted
by `mindc check --no-fmt`. `fn pick<T>(x: T, y: T) -> T` called as `pick(5, 1.5)` is accepted. The native backend refuses
every generic function (`lane.source.function_contract`).

**Options.** (A) Refuse a call whose type argument no argument fixes with `E2003`, and a call that gives one
parameter two types with `E2001`. (B) Accept the first kind and give the argument no meaning, because it does not
reach the result. (C) Refuse the first kind until an explicit type argument at a call exists
([RFC 0027](./0027-function-generics.md)).

**Decision.** Option A, decided by the specification owner on 2026-11-24. The compiler is deterministic and
explicit: no implicit default type is chosen. The rule is in [Types](../../spec/v1.0/types.md#generics-in-core-v1).
The reference accepts these calls, and [Core v1 form status](../../spec/v1.0/core-v1-forms.md) lists that as a
gap. Whether a warning period comes before the error is open ([RFC 0027](./0027-function-generics.md),
open question 6).

**Form status.** Core v1 refuses, reference gap.
