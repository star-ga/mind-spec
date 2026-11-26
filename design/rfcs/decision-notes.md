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

This page lists points where the specification text did not decide the meaning of a form that it names. A note records
the text, the behaviour of the reference compiler v0.10.4 (measured with `mindc check --no-fmt`, in the measurements of
2026-11-25 also with `--no-lint`, and with `mindc build --backend native` or `mindc build --backend mlir` where it is
named), and the options. **A note does not give a meaning, except where it records a decision.** The specification owner
decided DN-1 to DN-13 on 2026-11-24 and DN-14 to DN-21 on 2026-11-25; each note records the decision in its
**Decision** paragraph, and an RFC or an editorial change carries it into the normative text. The tables of options
stay as the record of the choice. This page holds DN-1 to DN-13; DN-14 to DN-21 stand on
[Decision Notes, Part 2](./decision-notes-2.md), in the same form.
Each note ends with the status of its forms after the decision, in the words of [Core v1 form
status](../../spec/v1.0/core-v1-forms.md); that page gives the same status to the same form. The status is **Open** only
where the note says so. The paragraph **Text before the decision** records the specification text on which the decision
was taken, as it stood before the change that carries the decision; its links lead to the place that now holds the
decided rule.

## DN-1. The operator `:=`

**Text before the decision.** `:=` was in `AssignmentOperator`
([`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf)), in the `Operator` list of
[`grammar-lexical.ebnf`](../../spec/v1.0/grammar-lexical.ebnf), in the precedence table of
[Language](../../spec/v1.0/language.md#operator-precedence-and-associativity) (row 9, "Assignment and compound
assignment") and in the token examples of [Lexical Structure](../../spec/v1.0/lexical.md#tokens). No sentence said what
`x := e` means, and no example used it.

**Reference.** `let mut x = 1; x := 2;` is refused with `E1001`, ``unexpected `:`, expected an expression``
(3:7). `let y = x := 2;` is refused in the same way.

**Options.**

| Option | Effect |
|--------|--------|
| A. Remove `:=` from the grammar, the operator list and the precedence table | The token no longer exists. The reference already behaves like this. No program changes. |
| B. Define `x := e` as `x = e` | Two spellings of one assignment. The formatter needs a rule for which one it writes. |
| C. Define `x := e` as "declare and assign" (a new binding when `x` is unbound) | Changes the scope rules: an assignment can introduce a name. Needs a rule for a name that exists in an outer scope. |

**Rows.** [`colon_assign_reject`](../../tests/conformance/syntax/colon_assign_reject.yaml) in
[`tests/conformance/syntax`](../../tests/conformance/syntax/README.md) gives the verdict of the decision.

**Decision.** Option A, decided by the specification owner on 2026-11-24. `:=` is removed from
`AssignmentOperator`, from the `Operator` list of the lexical grammar, from the precedence table and from the token
examples of the lexical chapter; `x := e` is not part of the language. The text `:=` is the two tokens `:` and `=`,
no rule of the syntactic grammar puts `=` directly after `:`, and a source such as `x := 1;` is refused
([Lexical Structure](../../spec/v1.0/lexical.md#tokens)).

**Form status.** `x := e`: Core v1 refuses.

## DN-2. `while` and `for` as expressions with a value

**Text before the decision.** `PrimaryExpression` listed `WhileExpression` and `ForExpression`. No sentence
gave the type or the value of a loop.

**Reference.** `let x = while i < 3 { i };` is refused with `E2002`, ``unknown identifier `while` ``; the same for
`for`. A loop works as a statement.

**Options.** (A) A loop is a statement and leaves `PrimaryExpression`. (B) A loop has the type `unit` and the
value `()` ([DN-4](#dn-4-the-unit-value)). (C) A loop has a value taken from a `break` with a value, which needs
a value form of `break` that the grammar does not have.

**Decision.** Option B, decided by the specification owner on 2026-11-24. This replaces the first decision of this
note, which was option A. `while` and `for` stay in `PrimaryExpression`, and a loop has the type `unit` and the value
`()` ([DN-4](#dn-4-the-unit-value)): after `let u = while c { };`, `u` is `()`. A loop that stands as a statement is a
block-like statement and takes no `;` ([Loops](../../spec/v1.0/language.md#loops)). The reason is that the rule for
block-like statements ([DN-10](#dn-10-separators-that-the-grammar-requires-and-the-reference-does-not)) is then one
rule for five forms (`if`, `match`, a block, `while` and `for`), and no production of the published grammar is
removed, so a program that the published grammar derives, such as `while c { };`, stays valid.

**Form status.** `while c { }` and `for v in xs { }`, loops of the type `unit`: Core v1. A loop as a value
(`let u = while c { };`): Core v1; reference gap (`mindc check` refuses it with `E2002`, as an unknown identifier
`while` or `for`). `while c { };`, a loop with `;`: Core v1; reference gap (the native backend refuses
`while c { ... };` as an unsupported construct and builds the same loop without the `;`).

## DN-3. The remainder operator on floating-point values

**Text before the decision.** `%` was in the precedence table and in the lexical operator list.
[Language](../../spec/v1.0/language.md) gave no rule for the type of its operands or the sign of the result.

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
This NaN is the canonical NaN of [Types](../../spec/v1.0/types.md#canonical-nan), which this decision adds: one bit
pattern for each float type, `0x7FC00000` for `f32` and `0x7FF8000000000000` for `f64` (sign bit clear, quiet bit
set, other payload bits clear). Operands of two different float types are a dtype mismatch and MUST be refused at
check time with `E2004`.
[Floating-point remainder](../../spec/v1.0/language.md#floating-point-remainder) gives the rule and its table of
special cases.

**Form status.** `a % b` on two `f32` or two `f64` operands: Core v1; reference gap (the
native backend refuses it with `lane.type.mismatch`). `a % b` and `a %= b` with an `f32` and an `f64` operand:
Core v1 refuses; reference gap (`mindc check` accepts both).

## DN-4. The unit value

**Text before the decision.** `unit` was a primitive type ([Types](../../spec/v1.0/types.md)), and the standard
library called its value `()` ([Standard Library](../../spec/v1.0/stdlib.md)). No expression production derived `()`:
`ParenthesizedExpression` and `TupleExpression` needed an inner expression.

**Reference.** `let u = ();` is accepted. `let u: unit = ();` is accepted. `let n: i64 = ();` is also accepted,
so the type of `()` is not checked against the annotation. The native backend refuses all three
(`lane.source.tuple`).

**Options.** (A) Add the production `UnitExpression = "(" , ")"` with the type `unit`, and make the check
refuse a use of `()` where another type is expected. (B) Remove the value from the language: a function without
a result type is the only way to produce no value.

**Decision.** Option A, decided by the specification owner on 2026-11-24. The production
`UnitExpression = "(" , ")"` gives the value `()` of type `unit`; the check refuses `()` where another type is
expected (an annotation, a parameter, a result type, an operand) with `E2001`
([The unit value](../../spec/v1.0/types.md#the-unit-value)).

**Form status.** `()`, the value of type `unit`: Core v1; reference gap (the native backend refuses it with
`lane.source.tuple`). `()` where another type is expected (`let n: i64 = ();`): Core v1 refuses; reference gap
(`mindc check` accepts it, also as an argument for an `i64` parameter).

## DN-5. The `^` suffix of a differentiable literal

**Text before the decision.** [Lexical Structure](../../spec/v1.0/lexical.md#literals) said that a differentiable
literal MAY include a tangent annotation with the suffix `^` and referred to
[Automatic differentiation](../../spec/v1.0/autodiff.md), which had no text for it. `DifferentiableLiteral = Literal ,
"^"` was in the lexical grammar, and `^` was also the bitwise exclusive-or operator.

**Reference.** `1.0^;` reads as the operator `^` with a missing operand, so the suffix does not exist in
practice (measured with v0.10.4).

**Options.** (A) Remove the suffix. (B) Give the suffix a meaning in the autodiff chapter and a lexical rule
that separates it from the operator (for example, no whitespace and no operand to the right).

**Decision.** Option A, decided by the specification owner on 2026-11-24. The `^` suffix is removed from the lexical
text and from the grammar (`DifferentiableLiteral`); `^` is only the exclusive-or operator, so `1.0^;` is an
exclusive-or with no right operand and is refused ([Lexical Structure](../../spec/v1.0/lexical.md#literals)).

**Form status.** `1.0^`: Core v1 refuses.

## DN-6. Precedence of `as`

**Text before the decision.** The comment at the end of [`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf)
listed `as` below `+` and `-` (level 4 of 7, where level 1 binds tightest). The table of
[Language](../../spec/v1.0/language.md#operator-precedence-and-associativity) had no row for `as`. The block of
the comment belonged to the v1.1 candidate additions.

**Reference.** `as` binds tighter than `*` (measured with v0.10.4). The two
sources disagree for an expression such as `a * b as f64`. The reference refuses `1 as bool` at check time
(`E2016`, "cast to `bool` is not permitted") and accepts `300 as u8`. It accepts `x as i64 < y`,
`x as Option<i64>> z` and `let b = x as Option < y;`.

**Options.** (A) Keep the reference and change the comment. (B) Keep the comment and change the reference.
Either choice changes the meaning of existing programs that mix `as` with `*`, `/`, `+` or `-`.

**Decision.** Option A, decided by the specification owner on 2026-11-24. `as` binds tighter than `*`, `/` and `%`
and looser than a unary operator: the comment of the grammar is corrected, and the precedence table of Language gets
a row for `as`. `a * b as f64` is `a * (b as f64)`, and `-x as f64` is `(-x) as f64`. The cast itself is defined
too: `e as T` is a `CastExpression` of the grammar, and its result has the type `T`. The rule is the same on every
substrate, bit for bit ([Casts](../../spec/v1.0/language.md#casts)):

1. Integer to integer: the value modulo 2 to the power `N`, the width of the target. A signed source is
   sign-extended, and an unsigned source is zero-extended.
2. Integer to float: round to nearest, ties to even.
3. Float to integer: truncate toward zero. A value outside the range of the target, an infinity too, gives the
   nearest bound of the target. NaN gives 0.
4. `f32` to `f64`: exact, and NaN gives the canonical NaN. `f64` to `f32`: round to nearest, ties to even; an
   overflow gives the infinity of that sign; NaN gives the canonical NaN
   ([Canonical NaN](../../spec/v1.0/types.md#canonical-nan)).
5. `bool` to integer: `false` is 0 and `true` is 1.
6. A cast to the same type is the identity: the value of `e`, bit for bit, except that a NaN gives the canonical NaN.

A cast that these six rules do not list MUST be refused at check time with `E2016` (invalid cast). An integer or a
float has no cast to `bool`: the program writes a comparison, such as `x != 0`. Every cast whose value is a
floating-point NaN gives the canonical NaN of the target type: rule 4 in both directions, and rule 6 for `f32` and
`f64`.

A later decision of the specification owner, on 2026-11-25, gives the reading rule for the type of a cast
([Casts](../../spec/v1.0/language.md#casts)). A primitive type name ends the type of a cast: `x as i64 < y` is the
comparison of `x as i64` with `y`. After any other type name, a `<` opens a type-argument list (the type reading
wins), and the rule of [Tokens](../../spec/v1.0/lexical.md#tokens) for the closing angle closes it. So
`x as Option<y>> z` is the cast `x as Option<y>` compared by `>` with `z`, and that cast is refused with `E2016`, as
a cast that the table does not list; `let b = x as Option < y;` has no reading and MUST be refused, because the list
that the `<` opens is not closed. To compare a cast to a type that is not a primitive type by `<`, a program writes
parentheses: `(x as T) < y`.

**Form status.** The precedence of `as` (`a * b as f64` is `a * (b as f64)`): Core v1. `e as T` for a pair of types
of the cast table: Core v1; reference gap (the native backend refuses `i64 as i32` and `i32 as i64` with
`lane.type.int_width`, `f64 as i32` and `f64 as f32` with `lane.source.cast`, and `f32 as f64` with
`lane.type.non_f64_float`). A cast that the table does not list (`1 as bool`, `true as f64`, `x as Option<i64>> z`):
Core v1 refuses; reference gap (`mindc check` accepts `true as f64` and `x as Option<i64>> z`; it refuses a cast to
`bool` with `E2016`). `x as i64 < y`: Core v1; reference conforms (`mindc check` accepts it).
`let b = x as Option < y;`: Core v1 refuses; reference gap (`mindc check` accepts it).

**Replaced in part by.** DN-53 ([Decision Notes, Part 3](./decision-notes-3.md)): the type after `as` takes no type-argument list, so a `<` after a cast is always a comparison; the reading rule of this note for a cast to a name is replaced.

## DN-7. Loop exits outside a loop, `loop`, labels and values

**Text before the decision.** [Language](../../spec/v1.0/language.md#loop-exits) defined `break` and `continue`
inside `while` and `for`. Nothing defined them outside a loop. `break`, `continue` and `loop` were not keywords:
`break` and `continue` were words that the grammar spells out, read as a name where no derivation read them as a loop
exit.
[Conformance](../../spec/v1.0/conformance.md) and [MLIR Lowering](../../spec/v1.0/mlir-lowering.md) mentioned `break`,
`continue` and a loop.

**Reference.** A `break` outside a loop is accepted by `mindc check --no-fmt` and refused by the native backend
(`lane.source.loop_exit_scope`). The text `loop { … }` is accepted by `mindc check --no-fmt`. With a statement in its
block (`loop { i = i + 1; }`) the native backend refuses it without a key; with an empty block the native build builds
it, and the image of `loop { } return 7;` exits with the status 7. `let loop = 1;` runs. A label `break 'a;` is refused
with `E1001`. `break 7;` is read as `break` followed by `7;`. `let loop = false; while loop { } return 3;` is
refused with `E1001`, "expected '{', found Some('r')". `let break = 4;` and `let continue = 1;` are accepted, and
the image of `let break = 4; return break;` exits with the status 4; in a loop, `break - 1;` is read as the loop exit,
and `break = 5;` is refused with `E1001`.

**Options.** (A) Refuse a loop exit outside a loop at check time. (B) Add `loop` as a keyword with a
production and a rule that it only ends with a `break`. (C) Add labels and a value to `break`. These options
are independent.

**Decision.** Decided by the specification owner on 2026-11-24, one answer for each option ([Loop
exits](../../spec/v1.0/language.md#loop-exits)). (A) Yes: a loop exit outside a loop is refused at check time with
`E2401`. (B) No: `loop` is not a keyword in Core v1. Where a statement can start, the name `loop` directly followed by
`{` (the text `loop { … }`) is refused at check time with `E2405`; the diagnostic says that Core v1 has no `loop`
statement and names the form `while true { … }`. In every other place `loop` is a name: `let loop = 1; return loop;` and
`let loop = false; while loop { } return 3;` are valid. (C) No: Core v1 has no labels and no value form of `break`; a
later RFC may add them. `break 'a;` holds an invalid token, and `break 7;` has no derivation; both are refused.

A later decision of the specification owner on the same day reserves `break` and `continue`. The first form of this
decision kept them as names where no derivation reads them as a loop exit. Now they are keywords
([Keywords](../../spec/v1.0/lexical.md#keywords)), and `LoopExitStatement` is the only rule of the grammar that holds
them. A source in which one of them stands where the grammar needs a name or an expression has no derivation and is
refused: `let break = 4;`, `break - 1;` and `break = 5;` are refused. `while c { break }` is refused because the `;`
of the loop exit is missing ([DN-10](#dn-10-separators-that-the-grammar-requires-and-the-reference-does-not)). The
reason is that a loop exit is control flow, and a reader must see it without the names that are in scope.

**Form status.** `break;` and `continue;` in the body of a loop: Core v1. `break;` and `continue;` outside the body
of every loop: Core v1 refuses; reference gap (`mindc check` accepts both). `break 'a;`, `continue 'a;` (a label)
and `break 7;` (a value): Core v1 refuses; reference gap (`mindc check` accepts `break 7;`). `break` or `continue`
where the grammar needs a name or an expression (`let break = 4;`, `let continue = 1;`, `break - 1;`, `break = 5;`):
Core v1 refuses; reference gap (`mindc check` accepts `let break = 4;` and `let continue = 1;`, and the image of
`let break = 4; return break;` exits with the status 4; in a loop it reads `break - 1;` as the loop exit; it refuses
`break = 5;` with `E1001`). `loop { }`: Core v1 refuses; reference gap (`mindc check` accepts it; with an empty block
the native build also builds it, and the image runs on past it: `loop { } return 7;` exits with the status 7).
`let loop = false; while loop { } return 3;`: Core v1; reference gap (`mindc check` refuses it with `E1001`,
"expected '{', found Some('r')"). The missing `;` of a loop exit (`while c { break }`) is in the status of
[DN-10](#dn-10-separators-that-the-grammar-requires-and-the-reference-does-not).

**Replaced in part by.** DN-54 ([Decision Notes, Part 3](./decision-notes-3.md)): `loop B` is a form of the language and `loop` is a keyword; the refusal of `loop` with `E2405` is withdrawn.

## DN-8. `let mut` and assignment to a binding

**Text before the decision.** `LetStatement` had no `mut`. [Language](../../spec/v1.0/language.md) showed
assignment to a variable (`x = y = z;`) and did not say that the variable must be declared mutable.

**Reference.** `let mut x = 1; x = 2;` and `let x = 1; x = 2;` are both accepted, and both return 2 when built natively.
`mut` has no checked effect: an assignment to a parameter, `fn f(a: i64) -> i64 { a = 3; return a; }`, is accepted too,
and so is an assignment to a `for` variable and to a `match` arm binding. The sample sources in
[FFI](../../spec/v1.0/ffi.md) use `let mut`.

**Options.** (A) Define `mut` as part of `LetStatement` and refuse an assignment to a binding without it.
(B) Remove `mut` and allow every assignment. (C) Keep both and document that `mut` is a comment.

**Decision.** Option A, decided by the specification owner on 2026-11-24. `mut` is part of `LetStatement`
(`let mut x = e;`). An assignment or a compound assignment to a place needs the root name of the place to be
declared with `let mut`. A place is a name, or a chain of index, field and tuple-index accesses on a name, so
`a[i] = e;`, `p.x = e;` and `t.0 = e;` need `let mut a`, `let mut p` and `let mut t`. A name that a parameter of a
function, the pattern of a `for` or the pattern of a `match` arm binds is not mutable. A left operand that is not a
place, or a place whose root is not mutable, is refused at check time with `E2402`
([Bindings and assignment](../../spec/v1.0/language.md#bindings-and-assignment)). A later `let` of the same name is a
new binding and not an assignment, so `let x = 1; let x = 2;` is valid: the second `let` shadows the first. The
reference enforces the rule together with its type-check work and a sweep of the dependent sources; until then it is
a known gap.

**Form status.** `let mut x = e;`: Core v1. `let x = 1; let x = 2;`, a later `let` of the same name: Core v1;
reference conforms (`mindc check` accepts it, and the image of `let x = 1; let x = 2; return x;` exits with the status
2). `a = b;`, `a += b;`, `a[i] = b;` and `t.0 = b;`, where the root of the place is bound by `let mut`: Core v1;
reference gap (the native backend refuses `a[i] = b;` with `lane.source.index_store` and `t.0 = b;` as a struct field
assignment). An assignment or a compound assignment to a place whose root is not declared with `let mut` (a `let`
without `mut`, a parameter, a `for` pattern or a `match` arm binds it): Core v1 refuses; reference gap (`mindc check`
accepts `let x = 1; x = 2;`, `x += 1` on such an `x`, `let a = [1, 2, 3]; a[0] = 5;`, and an assignment to a
parameter, to a `for` variable and to a `match` arm binding). An assignment whose left operand is not a place
(`x + 1 = 3;`): Core v1 refuses; reference gap (`mindc check` refuses it with `E1001`, not `E2402`).

## DN-9. The result type of the entry function

**Text before the decision.** No sentence defined the result type of the entry function.

**Reference.** `fn main() -> i64` builds and returns its value as the process status. `fn main() -> f64` is
accepted by `mindc check --no-fmt` and refused by the native backend with `lane.entry.f64_result`.

**Options.** Define the allowed result types of `main` (for example `i64`, `unit`) and refuse others at check
time, or define how each other result type becomes a process status.

**Decision.** Decided by the specification owner on 2026-11-24. `main` has no parameter, and its result type is
`i64` or `unit`. As for every function, the type `unit` MAY be omitted or written (`fn main() { }` and
`fn main() -> unit { }` are the same). A `main` with a parameter or with another result type is refused at check
time with `E2403` ([Entry function](../../spec/v1.0/language.md#entry-function)). The process status is the low 8
bits of the `i64` in two's complement, read as an unsigned number from 0 to 255, on every substrate (the result 300
gives the status 44, and the result -1 gives 255), and status 0 when the result type is `unit`.

**Form status.** `fn main() -> i64 { }`, `fn main() { }` and `fn main() -> unit { }`: Core v1; reference gap (the
native backend refuses `fn main() -> unit` with `lane.type.named`, and the image of `fn main() { let x = 1; }` exits
with the status 1, and with 7 for `let x = 7;`, not 0). `fn main() -> f64 { }` and `fn main(n: i64) -> i64 { }`:
Core v1 refuses; reference gap (`mindc check` accepts both).

## DN-10. Separators that the grammar requires and the reference does not

**Text before the decision.** `LetStatement` and `ExpressionStatement` ended with `;`. A `MatchArm` with an
expression ended with `,`.

**Reference.** A missing `;` after `let` or after an expression statement, and a missing `,` after an expression arm of
a `match`, are accepted. `mindc fmt` inserts the separators and plain `mindc check` then reports `fmt::drift` for the
unformatted text. A block-like statement that is not the tail and whose type is not `unit` is accepted too: the measured
source is `fn main() -> i64 { if true { 1 } else { 2 } return 0; }`, with `mindc check --no-fmt`.

**Options.** Make the reference refuse these forms (after a period in which it warns), or relax the grammar.
The first option changes programs that compile today.

This note is about the separators only. A keyword used as a name, a raw line feed in a string, and the tokens
`1e3`, `1i64`, `1.2.3`, `0XFF` and `'a'` are not open: the lexical rules of
[Lexical Structure](../../spec/v1.0/lexical.md) and [`grammar-lexical.ebnf`](../../spec/v1.0/grammar-lexical.ebnf)
give them no derivation.

**Decision.** Decided by the specification owner on 2026-11-24. `check` and `build` refuse a missing `;` and a
missing `,` of a `match` arm, with no warning period. The formatter MAY read the tolerant form, and it writes the
strict form. The rules are these ([Block-like statements](../../spec/v1.0/language.md#block-like-statements) and
[Statement separators](../../spec/v1.0/language.md#statement-separators)).

- `;` is required after `let`, after `return`, after a loop exit and after an `ExpressionStatement`.
- A block-like statement takes no `;`. The five block-like forms are `if`, `match`, a block, `while` and `for`. A
  `defer` statement takes no `;` either: it ends at the closing brace of its block, so `defer { };` has no derivation
  and is refused.
  The grammar gets `BlockLikeStatement = IfExpression | MatchExpression | BlockExpression | WhileExpression |
  ForExpression` as a form of `Statement`, with no terminator. A formatted MIND source writes these forms without
  `;`, and the published grammar could not derive that.
- Reading rule. Where a statement can start and the next token starts one of the five forms, the form is read as a
  `BlockLikeStatement` and ends at its closing brace (for an `if` with `else`, the closing brace of its last block).
  What follows starts a new statement. When the next token after that closing brace is `;`, the form and the `;` are
  an `ExpressionStatement`, so `while c { };` is a program. When nothing but the closing brace of the enclosing block
  follows, the form is the tail `Expression` of that block and gives the block its value. To use such a form as an
  operand at the start of a statement, the program writes parentheses.
- Typing. A `BlockLikeStatement` that is not the tail MUST have the type `unit`; otherwise the source is refused at
  check time with `E2001`. A value is discarded only by an `ExpressionStatement` with `;`.
- A `match` arm with an expression ends with `,`, the last arm too. An arm with a block takes no `,`.

**Form status.** `if c { }`, `match e { }`, a block, `while c { }` and `for v in xs { }` as statements with no `;`: Core
v1; reference gap (`mindc check` refuses a block that holds a statement, `{ s = s + 1; }`, with `E1001`).
`while c { };`: Core v1; reference gap (the native backend refuses `while c { ... };` as an unsupported construct and
builds the same loop without the `;`). `if c { 1 } else { 2 }` and the other forms as the tail of a block, and a block
as a value: Core v1; reference gap (`mindc check` refuses a block that holds a statement also as a value, with `E1001`,
and the native backend refuses `let b = { 4 };` with `lane.source.set`). A block-like statement that is not the tail and
whose type is not `unit` (`if c { 1 } else { 2 } return 0;`): Core v1 refuses; reference gap (`mindc check` accepts it).
`defer { };`, a `;` after the block of a `defer`: Core v1 refuses; reference gap (`mindc check` accepts it). A missing
`;` after a `let`, a `return`, a loop exit (`while c { break }`) or an expression statement, and a missing `,` after an
expression arm of a `match`: Core v1 refuses; reference gap (`mindc check` accepts a missing `;` after a `let`, an
expression statement, a `return` and a loop exit, and a missing `,`; it reads `while c { break }` as the loop exit).

**Replaced in part by.** DN-46 ([Decision Notes, Part 3](./decision-notes-3.md)) replaces the arm sentence: every arm ends with `,`, a block arm too; DN-54 adds `loop` as a sixth block-like form.

## DN-11. Tuple index and range index

**Text before the decision.** `FieldAccessOperator` was `"." , Identifier`, the grammar had no tuple index, and
`IndexExpression` had no range.

**Reference.** `t.1` on a tuple and `a[1..3]` are accepted by `mindc check --no-fmt`. So are `t.0.1` on a nested
tuple, `t.5` on a pair and `t[0]` on a tuple. The native backend refuses a tuple (`lane.source.tuple`).

**Options.** Add a tuple index (`.` followed by an integer literal) to the grammar, with the rule that it needs
a tuple type; and decide whether `a[1..3]` is the same as the slice form `a[1:3]` of the grammar or is removed.
See also [RFC 0025](./0025-patterns.md), question 7.

**Decision.** Decided by the specification owner on 2026-11-24. The grammar gets the tuple index (`TupleIndexOperator`,
[Tuple index](../../spec/v1.0/language.md#tuple-index)): `.` and a decimal integer literal with no sign, no prefix and
no suffix (`t.0`). The type of `t` must be a tuple type and the index must be less than its number of elements;
otherwise the source is refused at check time with `E2404`. Where the parser expects the `DecimalInteger` of a tuple
index and the next token is a float literal of the form digits "." digits (no exponent, no suffix), the token is read as
two tuple indices: `t.0.1` means `(t.0).1`. After an access dot, a float literal token with an exponent or a suffix is
not a tuple index, because only the form digits "." digits is read as two indices (the lexical grammar gives a float
literal no suffix, so in Core v1 such a token has an exponent): a source such as `t.0.1e0` is not derived and MUST be
refused. [RFC 0025](./0025-patterns.md#tuple-index) states the same rule in the same words. `t[0]` on a tuple has no
meaning: it is refused with `E2404`, and the diagnostic names the form `e.N`. `a[e1:e2]` takes the elements from the
index `e1` up to, and not including, the index `e2`, so `a[1:3]` takes the elements 1 and 2. This decision gave no
meaning to the other forms that `SliceExpression` derives; [DN-19](./decision-notes-2.md#dn-19-slice-bounds-and-step)
gives them one. The grammar has no range index: `a[1..3]` is refused at check time with `E2406`, and the diagnostic
names the slice form `a[1:3]`.

**Form status.** `t.0` and `t.0.1` on a tuple: Core v1; reference gap (the native backend refuses tuples with
`lane.source.tuple`). `t.0.1e0`: Core v1 refuses; reference conforms (`mindc check` refuses it with `E2002`, as the
unknown identifier `e0`). `x.0` where `x` is not a tuple, `t.N` with `N` not less than the number of elements, and
`t[0]` on a tuple: Core v1 refuses; reference gap (`mindc check` accepts all three). `t[a:b]`, the slice form: Core v1;
reference gap (`mindc check` refuses `let b = a[1:3];` on the array `[1, 2, 3, 4]` with `E1001`, "expected `]` to close
index expression"). The other forms of `SliceExpression` are in the status of
[DN-19](./decision-notes-2.md#dn-19-slice-bounds-and-step). `a[1..3]`: Core v1 refuses; reference gap (`mindc check`
accepts it).

## DN-12. Compound assignment operators

**Text before the decision.** The assignment operator list was closed: `=`, `+=`, `-=`, `*=`, `/=`, `:=`. The
operators `&`, `|`, `^`, `<<` and `>>` stood in the precedence table, but the productions that held them were not
connected to `Expression`, and no sentence gave the types of their operands or their values.

**Reference.** `%=`, `<<=`, `>>=`, `&=`, `|=` and `^=` are accepted by `mindc check --no-fmt`. `%=` builds natively;
the others are refused by the native backend without a key.

**Options.** Add the six operators to `AssignmentOperator` and the lexical operator list, or make the reference
refuse them.

**Decision.** Decided by the specification owner on 2026-11-24: add `%=`, `<<=`, `>>=`, `&=`, `|=` and `^=` to
`AssignmentOperator` and to the lexical operator list. `x op= e` means `x = x op e`, with the place `x` evaluated
once: in `a[f()] += 1` the call `f()` runs once
([Bindings and assignment](../../spec/v1.0/language.md#bindings-and-assignment)). The rules of `op` for the types of
its operands apply.

The operators of five of these forms are defined too
([Bitwise and shift operators](../../spec/v1.0/language.md#bitwise-and-shift-operators)). `&`, `|`, `^`, `<<` and
`>>` are one precedence level, left to right, tighter than `+` and `-`. `&`, `|` and `^` take two operands of the same
integer type and give the bitwise and, or and exclusive or of their two's complement bits. `<<` and `>>` take a left
operand of an integer type `T` of `N` bits and a right operand of an integer type, and give a `T`. The shift count is
the value of the right operand modulo `N` (a negative right operand uses its two's complement value); `x << c` is the
low `N` bits of `x` times 2 to the power of the count, and `x >> c` is the arithmetic shift on a signed type and the
logical shift on an unsigned type. No operator of the group traps, and `0 - 17 >> 2` gives -4. Operands of two
different integer types for `&`, `|` or `^` are refused at check time with `E2004`, and an operand that is not of an
integer type with `E2005`.

The lexer reads the longest operator, so `<<=` and `>>=` are one token each
([Lexical Structure](../../spec/v1.0/lexical.md#tokens)). Where the grammar expects the `>` that closes a
type-argument list and the next token starts with `>`, the first `>` closes the list and the rest of the token is
read again, so `let o: Option<Option<i64>>= p;` is derived as before these operators were added. The `>` that closes
the type parameters of a declaration is not read so: `type X<T>= T;` holds the token `>=` and is not derived.

**Form status.** `a %= b;`, `a <<= b;`, `a >>= b;`, `a &= b;`, `a |= b;` and `a ^= b;` where the root of `a` is bound by
`let mut`: Core v1; reference gap (the native backend builds `%=` and refuses the other five). `a & b`, `a | b` and
`a ^ b` on two operands of the same integer type, and `a << c` and `a >> c` with integer operands: Core v1; reference
gap (the native backend refuses `<<` on `i32` operands, and an `i32` count of an `i64` shift, with
`lane.type.int_width`); the `i64` values conform (the native images give `12 & 10` 8, `12 | 3` 15, `12 ^ 5` 9, `1 << 64`
1, `1 << 65` 2, `40 >> 66` 10, `1 << (0 - 63)` 2, `64 >> (0 - 61)` 8, `(0 - 17) >> 2` -5, `(1 << 63) >> 63` -1,
`20 - 17 >> 2` 16 and `6 + 5 & 3` 7). `&`, `|` or `^` with an `i32` and an `i64` operand, and an operand of the group
that is not of an integer type (`true & false`, `1.5 | 2.5`, `x << 2` with `x: f64`): Core v1 refuses; reference gap
(`mindc check` accepts all of them; the image of `true & false` builds and exits with the status 0; the native backend
refuses the float operands with `lane.type.mismatch` and the mixed widths with `lane.type.int_width`).
`let o: Option<Option<i64>>= p;`: Core v1; reference gap (the native backend refuses the type `Option<Option<i64>>` with
`lane.type.generic`, also with a space before `=`); `mindc check` accepts it.

## DN-13. A generic call whose type argument is not fixed

**Text before the decision.** [Types](../../spec/v1.0/types.md#type-inference) said that a generic function MUST
infer its type parameters when the information is sufficient, and that the caller MUST provide explicit type
arguments otherwise. The grammar had no explicit type argument at a call. The text did not say what happens when the
argument types do not fix a parameter. [Error Catalog](../../spec/v1.0/errors.md) had `E2003` (cannot infer type) and
`E2001` (type mismatch).

**Reference.** `fn z<T>(x: i64) -> i64` called as `z(1)`, and `fn mk<T>() -> i64` called as `mk()`, are accepted by
`mindc check --no-fmt`. `fn pick<T>(x: T, y: T) -> T` called as `pick(5, 1.5)` is accepted. The native backend refuses
every generic function (`lane.source.function_contract`).

**Options.** (A) Refuse a call whose type argument no argument fixes with `E2003`, and a call that gives one
parameter two types with `E2001`. (B) Accept the first kind and give the argument no meaning, because it does not
reach the result. (C) Refuse the first kind until an explicit type argument at a call exists
([RFC 0027](./0027-function-generics.md)).

**Decision.** Option A, decided by the specification owner on 2026-11-24. The compiler is deterministic and
explicit: no implicit default type is chosen. A call whose type argument no argument fixes is refused with `E2003`,
and a call that gives one parameter two types with `E2001`. [RFC 0027](./0027-function-generics.md) (rules 5 and 9)
carries the rule into the normative text. No warning period comes before the error
([RFC 0027](./0027-function-generics.md), question 6).

**Form status.** `fn f<T>(x: T) -> T { }`, a generic function, and so a call of it: Extension. The rule of this decision
applies in the edition that adds function generics ([RFC 0027](./0027-function-generics.md)).
