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

# Decision Notes, Part 3 (Informative)

This page continues [Decision Notes](./decision-notes.md) and [part 2](./decision-notes-2.md) with the notes DN-22 to
DN-88, which the specification owner decided on 2026-11-26. They are the decisions on the grammar of the language: the
lexical rules, the expression and statement forms, the items, the types and patterns, the tensor forms and the
diagnostics. The grammar text of each decision is the left-factored form of the three grammar files
([`grammar-lexical.ebnf`](../../spec/v1.0/grammar-lexical.ebnf), [`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf),
[`grammar-ir.ebnf`](../../spec/v1.0/grammar-ir.ebnf)); the lexical decisions are stated in
[Lexical Structure](../../spec/v1.0/lexical.md).

Each note gives the decision, the options that were weighed, the reason, the forms that the decision refuses, and a
**Reference** paragraph with the measured verdict of the reference compiler v0.10.4 on the release build (`mindc check`,
and for an accepted source the native build and the exit status of its image). A probe id names the source that was
measured. A decision that replaces an older one names it in a **Replaces** line, and the older note names the new one;
the older note keeps its text. The reference does not enforce most of these decisions yet; each such form is
"decided, reference pending" until the reference front end enforces it, and a decided form that needs a rewrite of
existing sources is enforced only in a release that ships the migration tool of DN-88.

## DN-22. A const name as a pattern

**Decision.** A bare identifier in a pattern always binds a name. An arm whose pattern is a bare identifier with no guard,
and whose name is the name of a `const` item in scope, is refused: `E2301` when the arm is not the last arm, `E2314`
when it is the last one; the message gives the fix `n if n == K`. A bare unguarded binding arm that is not the last arm
is refused with `E2312`, because no later arm can match.

**Options.** (A) A bare name that names a `const` compares with the constant. (B) A bare name always binds; a name of a
`const` there is refused. (C) A second pattern form `== K`.

**Reason.** Option B. With (A) the meaning of an arm depends on what is in scope, so adding a `const` elsewhere changes
the value of a program with no message. With (B) a pattern reads the same in every scope, and the case where a reader
expects a comparison is a refusal with the fix. (C) is a second spelling of the guard `n if n == K`.

**Refused forms.** `const K: i64 = 1; match x { K => 10, _ => 20, }` (the arm `K` is not the last; `E2301`); a bare
binding arm before other arms (`E2312`).

**Reference.** `mindc check` accepts `const K = 1; match 5 { K => 10, _ => 20 }` (probe `a5_const_pat`, check status 0;
the native build refuses it with `lane.source.match`), and probe `i27_const_as_pattern` is accepted the same way: the
arm binds a new name and matches every value.

**Replaces.** Amends rule 5 of the draft [RFC 0025](./0025-patterns.md): `E2314` also covers the name of a `const`.

## DN-23. Operand and condition types

**Decision.** There is no truth value of a non-`bool`: the condition of `if`, `while` and a guard, and the operands of
`!`, `&&` and `||`, have the type `bool`. Arithmetic on `bool`, `unit`, tuples and records is refused with `E2005`.
`==` compares two values of one type; tuples and arrays compare element by element from index 0. `<` and the other
order operators take numbers only. A prefix `-` on an operand of an unsigned type is refused.

**Options.** (A) A non-zero integer is true. (B) Conditions and logical operands are `bool` only. For a prefix `-` on
an unsigned type: refuse, or wrap.

**Reason.** Option B gives one meaning for one text: `if n` and `!n` have no second reading, and an error in a
condition is a message, not a value. A prefix `-` on an unsigned value is refused because the refusal can be lifted
later and a wrap cannot be taken back; `0 - x` writes the wrap.

**Refused forms.** `if 5 { }` (`E2001`), `!5` and `true + 1` (`E2005`), `-x` with `x: u8`.

**Reference.** `mindc check` accepts `let b = true + 1;` and the image exits with the status 0 (probe `a2_bool_plus`);
it accepts `if 5 { return 7; }` and the image exits with 7 (probe `a3_if_int`); it accepts `let x = !5;` and
`return x + 10;` gives 10 (probe `a1_bang_int`); it accepts `let n: i64 = true;` and the image exits with 0
(probe `a5_scalar_mm`).

## DN-24. Statement typing rules

**Decision.** The right side of `=` has the type of the place. `e;` discards the value, and only the tail of a block
gives its value. A function body has the result type of the function. Divergence is a property of the syntax only:
`return`, `break`, `continue`, a `loop` with no `break`, and an `if` or a `match` all of whose branches diverge;
`while` and `for` never diverge. An `if` without `else` has the type `unit`. The root of a place is a `let mut`
binding (DN-8) and never a `const` (`E2402`).

**Options.** (A) Types of statements follow the value flow that the checker finds. (B) Each rule is stated by the form
alone, as above.

**Reason.** Option B: a reader and every checker reach the same type from the text, and no analysis of values decides
whether a body has a result.

**Refused forms.** `let mut x = 1; x = true;`; `fn f() -> i64 { 2; }`; `fn f() -> i64 { let x = 1; }`;
`let x = 1; x = 2;`; an assignment to a `const`.

**Reference.** `mindc check` accepts `let mut x = 1; x = true; return x;` and the image exits with 1 (probe
`a3_assign_type`); it accepts `fn f() -> i64 { 2; }` and the image exits with 2 (probe `a3_tail_semi`); it accepts
`fn f() -> i64 { let x = 1; }` and the native build refuses it with `lane.type.mismatch` (probe `a3_missing_tail`); it
accepts `let x = 1; x = 2; return x;` and the image exits with 2 (probe `a3_mut_not`); it accepts an assignment to a
`const` (probe `a4_const_assign`).

## DN-25. Evaluation order

**Decision.** One written order: the left operand, then the right one; the callee and the receiver, then the arguments
from left to right; the base before the index; the fields of a record literal in source order; for `p = e` and
`p op= e` the parts of the place from left to right, then `e`, then the store (`p op= e` reads `p` once, before `e`);
`&&` and `||` stop after the left operand when it decides the result; a trap happens at its point in this order.

**Options.** (A) Leave the order unstated. (B) One left-to-right order for every form. (C) For an assignment, the value
first and the place after it.

**Reason.** Option B: one rule covers operands, arguments, places, record fields and traps, so a program with effects
has one result, and that result is part of the bit-identity of the build. (C) would give an assignment a second order.

**Refused forms.** None; the decision fixes a value.

**Reference.** The release evaluates from left to right in every measured case: probes `e29_short_and` and
`e30_short_or` are accepted and their images exit with 7 (the right operand is not evaluated); probe
`e33_eval_order_args` is accepted by `mindc check` and refused by the native build.

## DN-26. A missing semicolon

**Decision.** A missing `;` is refused with `E1103` at the point where the `;` belongs. `mindc check` runs the syntax
check before the format check, so a syntax fault is never reported as a format difference.

**Options.** (A) Insert the `;` silently. (B) Refuse at the insertion point.

**Reason.** Option B: the text that a reader sees is the text that is checked, and the message points at the place to
change. DN-10 already requires the separators.

**Refused forms.** `let x = 1` followed by a line `return x;`; `return x }`; `break }`.

**Reference.** `mindc check` accepts `let x = 1` with no `;` followed by `return x;`, and the image exits with 1
(probe `a6_missing_semi`; probes `d09_missing_semi_let` to `d12_missing_semi_break` are accepted the same way).

## DN-27. The wildcard is not a name

**Decision.** A lone `_` is a punctuation token, never an identifier. It binds nothing: `let _ = e;` evaluates `e` and
drops the value. `_` may name a parameter, also more than one parameter of one function. Where an expression stands,
`_` has no derivation (`E1101`). ([Identifiers](../../spec/v1.0/lexical.md#identifiers).)

**Options.** (A) `_` is an ordinary name. (B) `_` is the wildcard token.

**Reason.** Option B: `_` has one meaning, "no name", and a read of it cannot see a value that was meant to be dropped.

**Refused forms.** `let _ = 7; return _;`; `f(_)`.

**Reference.** `mindc check` accepts `let _ = 7; return _;` and the image exits with 7 (probe `a5_wild_read`, also
`j01_wild_binds_name`); `let y = _;` with no earlier `_` is refused with `E2002` (probe `i24_underscore_value`).

## DN-28. The record literal and the head rule

**Decision.** `Name { f: e, ... }` builds a value of the struct `Name`, and it names each field once. In the head of
`if`, `while`, `for ... in` and `match`, an identifier followed by `{` starts the block, and a record literal there is
written in parentheses. This is a one-token rule of the parser. The grammar writes the literal with `NamePath` and
`RecordBody`.

**Options.** (A) A record literal stands everywhere, and the head is decided by a search. (B) A record literal in a
head needs parentheses.

**Reason.** Option B: `if b { }` reads the same as every other head, and the parser decides with one token.

**Refused forms.** `if p == P { x: 1 } { }` (write `if p == (P { x: 1 }) { }`); a field named twice.

**Reference.** `mindc check` refuses the valid `if c { } (3);` with `E1001`, "expected '{', found Some('(')" (probe
`a2_ident_brace_head`), and refuses `if b { } return 0;` with `E1001` (probe `a5_head_ident`, also `i16_if_b`); it
accepts the record literal `P { x: 1, y: 2 }` and the native build refuses it (probe `e58_record_literal`).

## DN-29. A call follows a name

**Decision.** A call follows a function name, a variant path (`E::A(x)`) or a method name (`x.m(a)`). The method call is
decided by one token after the name. `5(3)`, `f(1)(2)` and `(f)(2)` have no derivation (`E1101`, "a value is not a
function in this edition").

**Options.** (A) A call operator after any postfix expression. (B) A call only after a name.

**Reason.** Option B: Core v1 has no function values, so a call of any other value has no meaning; the grammar
states that, and each postfix form is decided with at most two tokens.

**Refused forms.** `5(3)`, `f(1)(2)`, `(f)(2)`.

**Reference.** `mindc check` accepts `return 5(3);` and the image exits with 5 (probe `a2_call_lit`, also
`e36_call_on_literal`); it refuses `(f)(2)` with "`f` is a function, not a value" (probe `e35_call_paren_callee`).

## DN-30. Name resolution

**Decision.** A module has one namespace for its items of every kind; parameters, fields and variants each have their
own list. A second declaration of a name is refused with `E2720` at the second one, naming the first. Every type name
resolves (`E2002`, with one hint chosen by a fixed rule: the least edit distance, then the source order; no further
diagnostic follows from it). `a.b` resolves to a module member, else to a method (`E2410`, "no such method") or a
field.

**Options.** (A) One namespace per item kind. (B) One namespace for all items.

**Reason.** Option B: a name means one item in a module, and the hint of a message is the same on every machine.

**Refused forms.** Two functions `f`; a struct and a function with one name; two parameters with one name; two variants
with one name; a parameter of an unknown type; `5.nosuchmethod()`; a read of an unknown field.

**Reference.** `mindc check` accepts two functions `f` (probe `a4_dup_fn`; the native build refuses it with
`closure.duplicate_definition`), a parameter of the unknown type `Nope` (probe `a4_unknown_type`), a read `s.nope`
(probe `a4_unknown_field`) and `return 5.nosuchmethod();` (probe `a2_method_unknown`).

## DN-31. Attribute admission by what an attribute denotes

**Decision.** The admission of an attribute keys on the triple (name, item kind, argument form) of one table, and a
lint keeps the table and its conformance rows equal. `#[test]` stands before a module-level function with no parameter
and the result `unit`. Tool attributes are DN-84.

**Options.** (A) A list of names. (B) One table keyed on name, item kind and argument form.

**Reason.** Option B: an attribute is admitted only where it has a meaning, so `#[repr(packed)]` cannot pass on the
strength of the name `repr`.

**Refused forms.** `#[repr(packed)] struct S`; `#[repr(C)] fn f()`; `#[test] fn t(x: i64)`; `#[test] fn t() -> i64`
(each `E2502`).

**Reference.** `mindc check` accepts `#[repr(packed)] struct S` (probe `a4_repr_packed`, also `attr_repr_packed`) and
`#[test] fn t() -> i64` (probe `a4_test_result`).

**Amended by.** DN-84 (tool attributes).

## DN-32. Comparison is not associative

**Decision.** A comparison operator never has a comparison as its direct operand: `a < b < c` and `a == b == c` have no
derivation (`E1101`, with the hint `a < b && b < c`).

**Options.** (A) Left-associative comparison. (B) No chain.

**Reason.** Option B: `1 < 2 < 3` compares a `bool` with an integer under (A), which is never what the text says.

**Refused forms.** `a < b < c`, `a == b == c`.

**Reference.** `mindc check` accepts `if 1 < 2 < 3 { return 1; }` and the image exits with 1 (probe `a2_cmp_chain`,
also `e01_cmp_chain_lt`).

## DN-33. `true` and `false` are keywords

**Decision.** `true` and `false` are keywords; as a name they are refused with `E1007`
([Keywords](../../spec/v1.0/lexical.md#keywords)).

**Options.** (A) Contextual words. (B) Keywords.

**Reason.** Option B: the literal has one meaning in every position.

**Refused forms.** `let true = 5;`, `fn f(false: i64)`.

**Reference.** `mindc check` accepts `let true = 5; return 1;` and the image exits with 1 (probe `a1_true_name`).

## DN-34. The complement operator `~`

**Decision.** `~e` is the bitwise complement of an integer, of the same type. `!` takes a `bool` only (DN-23).

**Options.** (A) `!` on integers. (B) `~` on integers and `!` on `bool`.

**Reason.** Option B: one operator for one meaning, and the type of the operand tells which.

**Refused forms.** `~true` (`E2005`), `!5`.

**Reference.** `mindc check` accepts `return ~x + 10;` and the native build refuses it with "unsupported construct;
use --backend=mlir" (probe `a1_tilde`, also `p51_op_tilde`, `e09_tilde_bitnot`); before this decision the
specification had no form `~`.

## DN-35. Numeric literals

**Decision.** A numeric literal is one longest run that must match one form, else `E1005` at the first character
that no form allows. A literal has no type suffix (DN-10 is kept). One `_` stands only between two digits of one digit
sequence. A decimal integer of more than one digit does not start with `0`. The exponent is `e` with an optional `-`
only. A floating-point literal operand of `as` with a floating-point target type takes the target type and is
rounded once (DN-20); every other literal operand of `as` has its default type, `i64` or `f64`, and the cast table
gives the value: `4294967297 as i32` is 1 and `2.9 as i64` is 2.
([Literals](../../spec/v1.0/lexical.md#literals).)

**Options.** (A) The lexer stops at the first character that does not fit and starts a new token. (B) One run, one
form.

**Reason.** Option B: `1.5f32` cannot be read as two tokens, and `017` cannot be read as octal by one reader and as
decimal by another.

**Refused forms.** `1.5f32`, `1i64`, `0x_FF`, `1__0`, `1_`, `017`, `1.5E3`, `1.5e+3`.

**Reference.** `mindc check` refuses `let x = 1.5f32;` with `E2002`, "unknown identifier `f32`", at the `f`: the text
is read as two tokens (probe `a1_suffix_f32`, also `c16_float_suffix_f32`); it accepts `0x_FF` (probe `a1_us_prefix`)
and `let x = 017; return x;`, whose image exits with 17 (probe `a1_leading_zero`); it accepts `1.5E-3` (probe
`c11_float_exp_neg_upper`) and `1.5e+3` (probe `c12_float_exp_plus`).

## DN-36. Exhaustiveness and pattern codes

**Decision.** `E2311` names one missing case, chosen by a fixed order: variants in declaration order, `false` before
`true`, the least uncovered integer. A pattern that does not fit its value is `E2001` at every site. A dead arm is an
error, `E2312`.

**Options.** (A) A list of missing cases, cut at a limit. (B) One case by a fixed order. For a dead arm: a warning or an
error.

**Reason.** Option B: the message has the same bytes on every machine, and an arm that can never run is a fault of
the text.

**Refused forms.** `match b { true => 1, }` (`E2311`, names `false`); an arm after an arm that matches every value
(`E2312`); `let (a, b, c) = (1, 2);` (`E2001`).

**Reference.** `mindc check` accepts `match b { true => 1, }` and the native build refuses it with `lane.source.match`
(probe `a5_nonexh_bool`); it refuses `let (a, b, c) = (1, 2);` with `E2620`, a code that the catalog does not define
(probe `a5_pat_arity`).

**Replaces.** The last sentence of rule 4 of the draft [RFC 0025](./0025-patterns.md) (a dead arm as a warning).

## DN-37. The tensor type has one spelling

**Decision.** `Tensor` is a predeclared generic type name. Its argument list is a dtype and a shape, both required:
`Tensor<f32, [2, 3]>`. The dtype set is the set of the profile (Core v1: `i32`, `i64`, `f32`, `f64`), else `E2005`
naming the set. The grammar has no rule of its own for the tensor type: `IdentifierType` takes `TypeArguments`, and a
`TypeArgument` is a type or a shape.

**Options.** (A) A rule of its own with a fixed word. (B) A predeclared generic name with required arguments.

**Reason.** Option B: one spelling, checked by the same rule as every generic type; the choice between a shape and an
array type in an argument is decided by the third token.

**Refused forms.** `Tensor<f32>`, `Tensor<bool, [2]>`, `tensor<f32[2]>`.

**Reference.** `mindc check` accepts `Tensor<f32>` with no shape (probe `a6_tensor_noshape`).

## DN-38. The word `tensor`

**Decision.** `tensor` directly followed by `(` is always the tensor constructor. A function, a parameter of a function
type or an import named `tensor` is refused with `E1007`. `tensor` stays a valid name of a value.

**Options.** (A) A user function `tensor` hides the constructor. (B) The constructor always wins and the name is
refused for functions.

**Reason.** Option B: `tensor(3)` has one meaning in every program.

**Refused forms.** `fn tensor(x: i64) -> i64`.

**Reference.** `mindc check` accepts `fn tensor(x: i64) ...; return tensor(3);`, and the image exits with 3: the
release calls the user function (probe `a6_fn_tensor`).

## DN-39. The at sign is reserved

**Decision.** `@` is a token and has no production. A source that holds it is refused with `E1105`, naming
`matmul(a, b)` (and `#[name]` for `@name`). A later decision MAY give `@` a production.

**Options.** (A) `@` is the matrix product. (B) `@` is reserved. (C) `@` is a forbidden character.

**Reason.** Option B: the matrix product already has one spelling, and the token stays free for a later decision.

**Refused forms.** `a @ b`, `@name`.

**Reference.** `mindc check` accepts `return a @ b;` on `i64` operands, and the native build refuses it with
`lane.source.tensor` (probe `a6_at_infix`, also `f04_at_int`).

## DN-40. The tensor literal

**Decision.** An array literal whose expected type is `Tensor<D, S>` is a tensor literal: its nesting is the rank and
its lengths are the dimensions, else `E3010`. A ragged literal is `E3010`. A cast to a tensor type is `E2016`.

**Options.** (A) No literal form. (B) The array literal with an expected tensor type.

**Reason.** Option B: a tensor value is written with the array form that a reader knows, and its shape is checked
against the type.

**Refused forms.** `let t: Tensor<f32, [2]> = [1.0, 2.0, 3.0];`; `[[1.0], [2.0, 3.0]]` as a tensor.

**Reference.** No probe; the published text had no literal rule (read).

## DN-41. A tail `if` followed by a minus

**Decision.** A block-like form at the start of a statement is a statement, and a non-`unit` one there is `E2001`; the
message names `(if c { 1 } else { 2 }) - 3`.

**Options.** (A) Read the form as the left operand. (B) The statement rule, with the message.

**Reason.** Option B keeps the one-token statement rule and tells the reader how to write the operand.

**Refused forms.** `fn f(c: bool) -> i64 { if c { 1 } else { 2 } - 3 }`.

**Reference.** `mindc check` accepts it and the image exits with 254: the release reads a statement and the literal
`-3` (probe `a2_tail_if_minus`, also `e47_tail_if_minus`).

## DN-42. Two slice colons inside an index

**Decision.** Inside the brackets of an index and outside any nested bracket, `::` is two slice colons. A path there is
written in parentheses: `a[(E::B)]`. ([Tokens](../../spec/v1.0/lexical.md#tokens).)

**Options.** (A) `::` is a path everywhere. (B) `::` is two slice colons at index depth.

**Reason.** Option B: `a[s::k]` has one reading, the slice from `s` with the step `k`.

**Refused forms.** `a[E::B]` (`E1101`, with the hint).

**Reference.** `mindc check` refuses `a[1::2]` with `E1001`, "expected `]` to close index expression" (probe
`a1_slice_cc`, also `p50_mun_slice_colon2`); it accepts `a[E::B]` (probe `c_index_path`).

## DN-43. No block comments

**Decision.** There is no block comment. `/*` is refused with `E1010`, whose message names line comments `//`. The code
`E1006` is withdrawn and stays in the table with its history.
([Comments and whitespace](../../spec/v1.0/lexical.md#comments-and-whitespace).)

**Options.** (A) Block comments that nest. (B) Block comments that do not nest. (C) No block comments.

**Reason.** Option C: one comment form, and no rule of depth or of `./*` is needed.

**Refused forms.** `/* c */`, `/* /* */ */`.

**Reference.** `mindc check` refuses `/* /* */ x */` with `E1001`, "unexpected `/`" (probe `a1_block_nest`, also
`c01_cmt_block_toplevel`).

## DN-44. A bounded unicode escape

**Decision.** `\u{...}` holds one to six hexadecimal digits, and its value is at most `10FFFF` and outside `D800` to
`DFFF`, else `E1004`.

**Options.** (A) Any number of digits. (B) One to six digits and a scalar value.

**Reason.** Option B: every escape gives one Unicode scalar value.

**Refused forms.** `"\u{110000}"`, `"\u{D800}"`, `"\u{}"`.

**Reference.** `mindc check` refuses `"\u{110000}"` with "unknown string escape `\u`": the release has no `\u` escape
(probe `a1_uesc_big`, also `p18_str_all_escapes`).

## DN-45. Item and statement terminators

**Decision.** An item that does not end with a block ends with `;`; an item that ends with `}` takes none; a `;` where
an item can start is refused (`E1103` or `E1101`). `assert` is a keyword statement with one form,
`assert c [, "m"];`.

**Options.** (A) An optional `;` after `const`, `use` and `assert`. (B) One rule for every terminator.

**Reason.** Option B: each form has one printed text, and `const K = 1` followed by a line that starts with `-` has one
reading.

**Refused forms.** `use std.vec` with no `;`; `fn f() { };`; `const K = 1` with no `;`; `assert(c, "m")` as a second
form.

**Reference.** `mindc check` accepts `fn f() -> i64 { return 1; };` (probe `a1_stray_semi`, also `fn_stray_semi`),
`const` with no `;` before a line that starts with `-` (probe `const_nosemi_minus`) and `use` with no `;` (probe
`use_nosemi_next`).

## DN-46. The form of a match arm

**Decision.** Every arm ends with `,`, the last one too. The body of an arm is `return [e]`, `break`, `continue`, or an
expression, optionally followed by an assignment operator and an expression (an arm statement of the type `unit`, or
diverging). A body that starts with `{` is a block expression, so `0 => { 1 } - 1,` is valid.

**Options.** (A) A block arm takes no `,`, and a body that starts with `{` is a block. (B) Every arm ends with `,`.

**Reason.** Option B: one arm form, decided with one token, and no sign rule after a block arm is needed.

**Refused forms.** `0 => { 1 } _ => 2,` (a block arm with no `,`; `E1103`).

**Reference.** `mindc check` refuses `0 => { 1 } - 1,` with `E1001`, "expected `=>` after match pattern" (probe
`c_arm_block_minus`); it accepts `0 => { 1 }, _ => { 3 },` (probe `c_arm_block_comma`) and
`match x { 0 => return 9, _ => 1, }`, which the native build refuses with `lane.source.match` (probe `a3_arm_return`).

**Replaces.** The arm sentence of DN-10, and the sign rule after a block arm of the draft [RFC 0025](./0025-patterns.md).

## DN-47. The counting loop

**Decision.** `for p in a..b B` counts from `a` up to `b`, `b` not included. `a` and `b` have one integer type and are
evaluated once, `a` first, before the first iteration. The loop is empty when `b <= a` and never overflows. `..` stands
nowhere else (`E1101`, with the hint `a[s:e]` for a slice).

**Options.** (A) `..` only in a `for` header. (B) A range value of a type of its own. (C) `s:e:k` in a `for` header.

**Reason.** Option A: a loop and a slice are two constructs with two spellings, and a range needs no type of its own
because it is not a value.

**Refused forms.** `let r = 0..4;`, `a[1..3]`.

**Reference.** `mindc check` accepts `for i in 0..4` and the image exits with 6 (probe `c_for_range`, also
`e67_range_for`, `s47_for_range_dots`).

**Amended by.** DN-80 (the closed form `a..=b`).

## DN-48. The sign is not part of a literal

**Decision.** A literal has no sign; `-` is always an operator. A unary `-` applied to a literal (with parentheses or
without) is checked as one negative value (the range rule of `E2408`, the index rule of DN-21). There is no unary `+`.
([Literals](../../spec/v1.0/lexical.md#literals).)

**Options.** (A) The lexer joins the sign to the digits where an operand can start. (B) The sign is always an operator,
and the checker reads `-` applied to a literal as one value.

**Reason.** Option B: the lexer needs no memory of the token before, and every text has one token stream. The values
of DN-20 rule 3 are kept: `let m: i32 = -2147483648;` is valid.

**Refused forms.** `+1`, `+x`; `let m: i32 = -2147483649;` (`E2408`).

**Reference.** `mindc check` accepts `if x > 0 { }` followed by `-1; return 2;` and the image exits with 2 (probe
`c_brace_minus`); it accepts `return -5.abs();`, which it reads as `(-5).abs()`, and the native build refuses it with
`lane.source.method_call` (probe `a2_neg_lit_method`). Under this decision that text is `-(5.abs())`, the value -5.

**Replaces.** The mechanism of DN-20 rule 3 (the sign as part of the literal), and the same sentence of the draft
[RFC 0025](./0025-patterns.md); the values stay.

## DN-49. Assignment is a statement

**Decision.** `p = e;` and `p op= e;` are statements with no value. The left side is a place (`E2402`). A chain, and an
assignment inside an expression, have no derivation (`E1107`, with the hint `==` in a condition).

**Options.** (A) Assignment as an expression with a value. (B) Assignment as a statement.

**Reason.** Option B: `if x = 1` cannot stand for `if x == 1`, and an assignment has one place in the text.

**Refused forms.** `a = b = 7;`, `if x = 1 { }`, `f(x = 1)`.

**Reference.** `mindc check` refuses `a = b = 7;` with `E1001`, "unexpected `=`" (probe `c_assign_chain`, also
`s15_assign_chain`), and `if x = 1` with `E1001` (probe `s17_assign_in_condition`).

## DN-50. A partial order for the bit operators

**Decision.** `&`, `|` and `^` chain only with themselves. `<<` and `>>` take two operands and do not chain. A bit
operator never stands beside another bit operator or beside `+ - * / %` without parentheses (`E1106`; the message
gives both parenthesised forms). A bit expression is an operand of a comparison: `x & 3 == 2` is `(x & 3) == 2`.

**Options.** (A) One level for all bit operators, between `*` and `+`. (B) Levels of their own. (C) A partial order:
no mix without parentheses.

**Reason.** Option C: no reader has to know a precedence of bit operators, because every mixed text names its grouping.

**Refused forms.** `1 | 2 << 1 ^ 7`, `0 - 17 >> 2`, `a << 1 << 2`, `x & y | z`.

**Reference.** `mindc check` accepts `return 1 | 2 << 1 ^ 7;` and the image exits with 1 (probe `a2_bitmix`), and
`return 0 - 17 >> 2;`, whose image exits with 252, the value -4 (probe `a2_shift_sub`); `x & 3 == 2` with `x = 6` gives 1
(probe `c_bit_cmp`).

## DN-51. The dotted operators (first form)

**Decision.** As first decided: `.*`, `./`, `.+` and `.-` leave the language, and `*`, `/`, `+` and `-` keep the tensor
rules.

**Options.** (A) The dotted operators as a second spelling of the plain ones. (C) Remove them. (D) Plain operators need
one shape, and dotted operators broadcast.

**Reason.** Option C removed the second spelling of the same meaning.

**Refused forms.** `a .* b` and the other three.

**Reference.** `mindc check` accepts `let y = t.-1;` and the native build refuses it with `lane.source.tuple` (probe
`a6_tuple_dot_minus`); it accepts `return a .+ b;` on `i64` operands (probe `a6_dot_plus_scalar`).

**Replaced by.** DN-81 (the dotted operators broadcast).

## DN-52. Context-free token rules

**Decision.** The lexer produces `<` and `>` as one-character tokens and marks each one *joined* when the next character
follows it with no space. In an expression the parser forms `>>`, `>=`, `>>=`, `<<`, `<=` and `<<=` from joined
tokens. In a type-argument list and in a type-parameter list every `>` closes one list. Directly after the token `.` a
digit run is an integer token, never a floating-point literal. ([Tokens](../../spec/v1.0/lexical.md#tokens).)

**Options.** (A) The parser splits a lexed `>>` where a list closes. (B) Joined one-character tokens.

**Reason.** Option B: the lexer needs no context, both list kinds close the same way, and `t.0.1` is two tuple indices
without a special token.

**Refused forms.** `x > = 1`, `x < < 2` (a space breaks the operator); `t.0.1e0` (`E1005`).

**Reference.** `mindc check` refuses `type X<T>= T;` with `E1001`, "expected `=` in type alias" (probe `c_ge_typeparam`,
also `p46_mun_typedecl_ge`); it accepts `t.0.1` (probe `c_tuple_pair`) and `Option<Option<i64>>= p` (probe
`p44_mun_generic_gtgteq`).

**Replaces.** The longest-match token rule for `<<=` and `>>=` and the split of a lexed `>>` or `>=` where a list
closes, in DN-12 ([Decision Notes](./decision-notes.md)) and in the drafts [RFC 0023](./0023-type-parameters-on-user-types.md)
and [RFC 0027](./0027-function-generics.md).

## DN-53. No type arguments after `as`

**Decision.** The type after `as` is a primitive type name or a name with no type-argument list; a `<` after a cast is
always a comparison.

**Options.** (A) A `<` after a cast to a name opens a type-argument list. (B) No type-argument list after `as`.

**Reason.** Option B: `x as T < y` has one reading with one token, and no cast in Core v1 needs a generic target.

**Refused forms.** `x as Option<i64>` (`E1101`).

**Reference.** `mindc check` accepts `type T = i64; if x as T < y` (probe `c_cast_alias_lt`): the release already
reads the `<` as a comparison.

**Replaces.** The reading comment of DN-6 for a cast to a name.

## DN-54. The `loop` form

**Decision.** `loop B` is a block-like statement, and `loop` is a keyword. A `loop` that no `break` ends diverges; else
its type is `unit`. `E2405` for `loop` is withdrawn.

**Options.** (A) No `loop`; write `while true`. (B) `loop` as a form.

**Reason.** Divergence is a property of the syntax (DN-24), so `while true` never diverges, and only `loop` can type a
body that never ends.

**Refused forms.** `let loop = 1;` (`E1007`).

**Reference.** `mindc check` accepts `loop { i += 1; if i == 3 { break; } }`, and the native build refuses it with
"unsupported construct" (probe `a3_loop`, also `s45_loop_keyword`).

**Replaces.** Option B of DN-7 (`loop` refused with `E2405`).

## DN-55. The primitive integer types

**Decision.** `PrimitiveType` holds `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32` and `u64`. `usize` and `isize` are
refused (`E2002`, with the fix `u64` or `i64`).

**Options.** (A) `i32` and `i64` only. (B) The eight fixed widths. (C) Also platform widths.

**Reason.** Option B: a platform width would give one program two sizes on two machines; every width here has one
size everywhere.

**Refused forms.** `usize`, `isize`; `let x: u8 = 256;` (`E2408`).

**Reference.** `mindc check` accepts `u8`, `u64` and `usize` as types; the native build refuses them with
`lane.type.int_width` (probe `j15_unsigned_types`).

## DN-56. Every item reached, attributes first

**Decision.** Every item form is reached from `Module`. Attributes come first, then `pub` (DN-83), then the word that
starts the item, for every item kind. There is one extern form, the block `extern "C" { ... }`. An enum payload list
may end with `,`.

**Options.** (A) Attributes before a function only, and a separate rule for other items. (B) One order for every item.

**Reason.** Option B: one derivation for every attributed item, with no shared prefix of unbounded length.

**Refused forms.** `extern "C" fn f();` (write it in a block); `extern "X" { }` (`E2502`).

**Reference.** `mindc check` refuses `extern "C" fn` with `E1001`, "expected '{', found Some('f')" (probe
`extern_c_fn`); it accepts an attribute before a `const` (probe `attr_on_const`) and before an `enum` (probe
`attr_on_enum`).

## DN-57. Multi-axis index and array repeat

**Decision.** `t[i, j]` indexes a tensor: at most rank items, trailing axes whole, a scalar item drops its axis and a
slice keeps it (`E3014` for too many); an array takes one item. `[v; n]` builds `n` copies of one evaluation of `v`;
`n` is an integer literal or a `const` name, and `v` has a value type. An array type length takes the same form.

**Options.** (A) One index item, and no repeat form. (B) Items separated by `,`, and `[v; n]`.

**Reason.** Option B: an axis of a tensor and a repeated array are written once, and the grammar decides each with at
most two tokens.

**Refused forms.** `t[0, 1, 2]` on a tensor of rank 2 (`E3014`); `a[0, 1]` on an array; `[h; 3]` where `h` is a
handle (`E2001`).

**Reference.** `mindc check` refuses `t[0, 1]` with `E1001`, "expected `]` to close index expression" (probe
`a6_multi_index`, also `e37_index_multi`), and `let a = [0; 4];` with `E1001`, "expected ']', found Some(';')" (probe
`a2_array_repeat`, also `j14_array_repeat`).

## DN-58. Tuple and unit type forms

**Decision.** `(T,)` is the tuple type of one element; `(T)` is not a type (`E1101`, with the hint `T` or `(T,)`); the
unit type is written `unit` only, and `()` is the unit value (DN-4).

**Options.** (A) `(T)` is `T`. (B) `(T)` is not a type.

**Reason.** Option B: each type has one spelling, and no type operator of Core v1 needs grouping.

**Refused forms.** `let t: (i64) = (5,);`, `fn f() -> ()`.

**Reference.** `mindc check` accepts `let t: (i64) = (5,);` (probe `a5_paren_type`, also `i12_paren_type_dot0`).

## DN-59. The function type

**Decision.** A function type is written `fn(T, U) -> R`; it is still not in Core v1. The form `(T) -> U` leaves.

**Options.** (A) `(T) -> U`. (B) `fn(T) -> U`.

**Reason.** Option B: a type that starts with `(` is a tuple type, and a function type starts with its own word.

**Refused forms.** `(i64) -> i64` as a type.

**Reference.** Not measured; the form is not in Core v1 (`E2037`).

## DN-60. Reserved and contextual words

**Decision.** `mut`, `loop` and `assert` join the keywords (with `true` and `false` of DN-33 and `pub` of DN-83). Every
contextual word has its own positions and is decided there with at most two tokens; the search for a derivation goes. A
keyword in a name position gives one `E1007` at the word. The `ContextualWord` rule of the lexical grammar is
documentation. ([Keywords](../../spec/v1.0/lexical.md#keywords).)

**Options.** (A) Contextual words read by the derivation that exists. (B) Keywords for the words that start a form, and
contextual words with fixed positions.

**Reason.** Option B: the reader and the parser decide the role of a word by its place, not by a search.

**Refused forms.** `let mut = 1;`, `let loop = 1;`, `fn assert()`, `fn f(true: i64)`.

**Reference.** `mindc check` refuses a source that uses `as`, `in`, `mut`, `const`, `enum`, `use` and `module` as
`let` names with `E1001`, "expected variable name", at the first of them (probe `p42_id_ctx_words`); it accepts `diff`, `dyn`, `Tensor` and `tensor` as names
(probe `j05_contextual_words_as_names`).

## DN-61. Source text safety

**Decision.** The forbidden code points (the bidirectional controls, the C0 and C1 controls other than TAB, LF and CR,
U+2028, U+2029, a BOM not at offset 0) are refused everywhere, comments and strings too, with `E1008`, named as
`U+XXXX`. Identifiers are ASCII in Core v1. A lone CR is refused.
([Source text](../../spec/v1.0/lexical.md#source-text).)

**Options.** (A) Unicode names with normalisation. (B) ASCII names and a list of forbidden code points.

**Reason.** Option B: no two texts look the same and are read differently, and no flag can turn the rule off.

**Refused forms.** U+202E in a comment; NUL in a comment; `let α = 1;` (`E1002`); a line ended by CR alone.

**Reference.** `mindc check` accepts a U+202E bidirectional override in a string and in a comment (probe
`p24_str_bidi`), U+2028 in a line comment (probe `p33_cmt_unicode_line_sep`), and a line comment ended by CR alone
(probe `c07_cmt_line_cr_only`).

## DN-62. Line strings

**Decision.** A quoted string ends on its line (`E1003` at the opening quote). A raw text of one or more lines is a run
of line strings, each `\\` up to the end of its line, joined by LF. ([Literals](../../spec/v1.0/lexical.md#literals).)

**Options.** (A) Raw line ends inside a quoted string. (B) Line strings.

**Reason.** Option B: one raw form, every line visible, and an unterminated string is reported at its own line.

**Refused forms.** A quoted string with a line end inside; a raw TAB in a quoted string (`E1008`).

**Reference.** `mindc check` reports an unterminated string at 7:1, the end of the file, with `E1001` (probe
`p60_diag_cascade`; probe `d26_unclosed_string` gives 5:1 for a fault at 2:13); a line end inside a string passes
`mindc check` (probe `d29_newline_in_string`).

## DN-63. Syntax error codes

**Decision.** `E1001` is ill-formed UTF-8 only. Syntax faults get `E1101` unexpected token, `E1102` unclosed delimiter,
`E1103` missing separator (at the insertion point), `E1104` misspelled keyword, `E1105` a form that MIND writes another
way, `E1106` operators that need parentheses, `E1107` assignment where an expression stands, `E1108` nesting too deep;
`E1007` reserved word as a name, `E1008` forbidden character, `E1009` reserved literal prefix or suffix, `E1010` `/*`;
`E2409` callee is not a function, `E2410` no such method. A file with a syntax fault gets one diagnostic, with no
cascade.

**Options.** (A) One code for every syntax fault. (B) One code per class of fault.

**Reason.** Option B: a tool and a reader learn the class of a fault from its code, and the one diagnostic is at the
right place.

**Refused forms.** None; the decision names codes.

**Reference.** `mindc check` gives `E1001` for every syntax fault of the measured set, for example "expected '}', found
None" for a missing brace (probe `d01_missing_close_brace_eof`), and it gives 3 diagnostics for `lett x = 1;` with
`--no-fmt` and 4 without it, the fourth the format drift (probe `d32_misspelled_let`).

## DN-64. Diagnostic tables

**Decision.** `E1104` fires at the Damerau-Levenshtein distance 1 from a keyword allowed at that place (3 or more
characters; ties by the keyword order of [Keywords](../../spec/v1.0/lexical.md#keywords)). `E1105` uses one fixed
table (`elif`, `func`, `var`, `switch`, `x++`, `===`, `@`, `diff T`, `tensor<f32[2]>`, `a::b` after a module, ...).
An item form in a block is refused at its first word. At module level the message says "expected an item". `E2002`
suggests only names in scope at distance 2 or less.

**Options.** (A) Suggestions from every known name. (B) Fixed tables and a fixed distance.

**Reason.** Option B: the message is the same on every machine and names the keyword that the text meant.

**Refused forms.** None; the decision fixes messages.

**Reference.** `mindc check` refuses `lett x = 1;` with `E2002`, "unknown identifier `lett` — did you mean `Text`?"
(probe `a6_typo_let`); a nested `fn inner` is refused only at its use with `E2003` (probe `a4_nested_fn`).

## DN-65. Module forms

**Decision.** Module level holds items only. A `const` initializer is a constant expression with no call. An executable
build needs one top-level `main`. `.` follows a value or a module, `::` follows a type, and the other separator is
`E2002` with the fix. A binding may not take the name of an import qualifier or of a module block in scope (`E2730`).
Visibility is `pub` on the item (DN-83).

**Options.** (A) Statements at module level. (B) Items only.

**Reason.** Option B: a module has no order of execution, and each separator has one meaning.

**Refused forms.** `let x = 1;` at module level; `const K = f();`; a build with no `main` (`E2403`); `m::f()` for a
module block member; a local named like an import qualifier.

**Reference.** `mindc check` accepts a `let` at module level (probe `a4_top_let`, also `top_level_stmt`), a build with
no `main` (probe `fn_no_main`; the build refuses it with `closure.missing_entry_root`), and `m::f()` for a module block
member (probe `module_block_call_colon`).

## DN-66. Or-patterns and nested patterns

**Decision.** `p | q` (no leading `|`) tries the alternatives from left to right; each binds the same names with the
same types (`E2313`). The guard runs at most once per `match`. `let`, `for`, parameters and arms use one `Pattern`, so
nested tuple patterns are valid; `mut` stays one per `let` (DN-8).

**Options.** (A) Patterns only in `match`. (B) One pattern grammar for every binding site.

**Reason.** Option B: one form at every site, and a guard with effects runs at most once.

**Refused forms.** `(x, 0) | (0, y) => ...` (`E2313`); `| 1 => ...`.

**Reference.** `mindc check` refuses `let ((a, b), c) = ...` with `E1001`, "expected variable name in tuple binding"
(probe `a5_let_nested`, also `j12_let_nested_wild`).

## DN-67. Predeclared variant names

**Decision.** `Some`, `None`, `Ok` and `Err` are the only spellings of those variants; no binding or declaration may take
these names (`E2042`).

**Options.** (A) Qualified and bare spellings. (B) Bare spelling only.

**Reason.** Option B: one spelling of each variant.

**Refused forms.** `Option::Some(1)` (`E2002`); `let None = 1;` (`E2042`).

**Reference.** `mindc check` accepts `Ok(x)` and `Err(e)` patterns, and the native build refuses them with
`lane.type.generic` (probe `j16_result_patterns`).

## DN-68. No `where` clause; type arguments of a method

**Decision.** A bound is written in the type-parameter list only; the `where` clause goes. `e.m::<A>(args)` gives a
method its type arguments. `where` stays a reserved word with no production, so a later decision can use it and no
program can take it as a name.

**Options.** (A) Bounds in the list and in a `where` clause. (B) Bounds in the list only.

**Reason.** Option B: one place for a bound; and a reserved word keeps the choice open for a later decision.

**Refused forms.** `fn f<T>(x: T) -> T where T: Numeric`; `where` as a name.

**Reference.** `mindc check` refuses a `where` clause with `E1001`, "expected '{', found Some('w')" (probe `g03_where`),
and `id::<i64>(5)` with `E1001` (probe `g04_turbofish`); it accepts `struct where` with a naming warning (probe
`kw_struct_name`).

**Replaces.** The `where` clause of the draft [RFC 0027](./0027-function-generics.md).

## DN-69. The nesting limit

**Decision.** A conforming implementation accepts at least 256 nested parentheses, brackets, braces, unary operators
and block-like forms, and a left-associative chain of any length. Deeper input is `E1108` at the first token past the
limit; the limit is the same on every machine and does not depend on the stack of the host.

**Options.** (A) No limit stated. (B) A stated minimum and a stated code.

**Reason.** Option B: the same source is accepted or refused on every machine, and a long chain never stops the
compiler.

**Refused forms.** 100000 nested parentheses (`E1108`).

**Reference.** `mindc check` stops with the status 134, "stack overflow", on a chain of 6000 terms (probe
`e80_long_chain`) and of 4000 terms (probe `f04_chain_4000`), and on 20000 nested parentheses (probe
`f05_parens_20000`); 3000 nested parentheses are accepted (probe `e79_deep_parens`).

## DN-70. The index operand is an integer

**Decision.** An index and a slice bound have an integer type, used exactly (`E2005`, with the hint `as i64`).

**Options.** (A) A float index truncated. (B) An integer index only.

**Reason.** Option B: no index is computed by a rounding that the text does not show.

**Refused forms.** `a[1.5]`.

**Reference.** `mindc check` accepts `a[i as i64]` with a float `i` and the image exits with 2 (probe
`e15_cast_in_index`); the text `a[1.5]` was not measured.

## DN-71. Tensor shape rules

**Decision.** A dimension that is an identifier names a `const` of the type `i64` in scope (`E3013`); `?` as a
dimension is `E1105`. Each dimension, and the count of elements, is at most 2^63 - 1 (`E3012`). `Tensor<D, []>` is the
type `D`. `==` on two tensors compares the whole values and gives one `bool` (no broadcast); `<` on tensors is
`E2008`.

**Options.** (A) Dimensions as free names. (B) Dimensions as `const` names with a stated range.

**Reason.** Option B: every shape is known at check time, and a comparison of tensors has one result type.

**Refused forms.** `Tensor<f32, [N]>` with no `const N`; `Tensor<f32, [?]>`; a dimension above 2^63 - 1; `a < b` on
tensors.

**Reference.** No probe of this line measured these forms on the release.

## DN-72. Named arguments with a colon

**Decision.** A named argument has one spelling, `name: value`, in attributes and in the tensor constructor;
`name = value` is `E1105`.

**Options.** (A) `name = value` in attributes, `name: value` in the constructor. (B) `name: value` everywhere.

**Reason.** Option B: one spelling for one meaning, the same as a field of a record literal.

**Refused forms.** `#[requires(mind_spec = "1.2")]`.

**Reference.** `mindc check` refuses `#[requires(mind_spec = "1.0")] module m;` with `E1001`, "unexpected '#'" (probe
`attr_requires`), and a named argument of a call with `E1001` (probe `fn_named_arg`).

**Replaces.** The form `name = literal` of the version attribute in rule 8 of the draft [RFC 0026](./0026-module-items.md).

## DN-73. Prefix forms with no production

**Decision.** `&x` and `3 as (i64)` have no derivation (`E1101`); Core v1 has no references.

**Options.** (A) Accept and ignore. (B) No derivation.

**Reason.** Option B: a form that has no meaning is a message, not a silent value.

**Refused forms.** `&x`, `3 as (i64)`.

**Reference.** `mindc check` accepts `let y = &x;` and the native build refuses it with `lane.source.reference` (probe
`a2_addr_of`, also `e74_addr_of`); it accepts a cast to a parenthesised type (probe `e14_cast_paren_type`).

## DN-74. Attribute list and names of the IR grammar

**Decision.** In [`grammar-ir.ebnf`](../../spec/v1.0/grammar-ir.ebnf), `AttributeValue` takes one `IntList`, and the
attribute name gives its meaning; an integer value is a `Number`. The names that the syntax grammar also uses become
`IrAttribute`, `IrDType`, `IrDimension`, `IrShape` and `IrTensorType`.

**Options.** (A) Separate list kinds for axes and shapes. (B) One list kind named by the attribute.

**Reason.** Option B: every attribute value has one derivation, and the two grammars share no rule name.

**Refused forms.** None; the encoded bytes do not change.

**Reference.** The grammar lint on the IR grammar of this line finds no undecided choice (0 rows "none up to k=3");
the IR text that the release writes was not compared in this line.

## DN-75. Faults of the grammar text

**Decision.** The comma-operator row of the precedence table goes; there is one precedence table, in
[Language](../../spec/v1.0/language.md#operator-precedence-and-associativity), and the grammar comment points to it;
the sentence "Division is not part of Core v1" goes; the comment of `Statement` names the one-token reading rule; the
conformance rows get a position and a count column; the reserved list of
[Keywords](../../spec/v1.0/lexical.md#keywords) and the `Keyword` rule change together, and a lint asserts that they
are equal.

**Options.** (A) Keep the text. (B) Fix each fault.

**Reason.** Option B: a rule that two places state must agree in both, and a lint keeps them so.

**Refused forms.** None.

**Reference.** The grammar lint of this line reports no `reserved-list-mismatch` row on the files of this line; on the
files with the `Keyword` rule of this line and the reserved list before it, it reported `assert`, `false`, `loop`,
`mut`, `pub` and `true`.

## DN-76. Rules for the text of a diagnostic

**Decision.** A message shows source text in backticks, "end of file" at the end of the input, and `U+XXXX NAME` for a
character that does not print; it never shows an internal form such as `Some('x')`. A known form of a later edition
gets one message that names its status.

**Options.** (A) Free message text. (B) Stated rules.

**Reason.** Option B: a reader sees the text that the source holds, and the message bytes are the same everywhere.

**Refused forms.** None; the decision fixes messages.

**Reference.** `mindc check` refuses `if c { } (3);` with "expected '{', found Some('(')" (probe
`a2_ident_brace_head`) and reports a missing brace as "found None" (probe `d01_missing_close_brace_eof`).

## DN-77. Doc comments and the shebang line

**Decision.** `///` documents the item or the field that follows it, and it is refused anywhere else. `//!` stands
only before the first item. A `#!` at offset 0 that `[` does not follow starts a line that the lexer skips.
([Comments and whitespace](../../spec/v1.0/lexical.md#comments-and-whitespace).)

**Options.** (A) No doc comment form. (B) Two placed forms.

**Reason.** Option B: a doc comment belongs to one item, and a script line at the top does not need a second form of
comment.

**Refused forms.** `///` before a statement; `//!` after the first item.

**Reference.** `mindc check` refuses a source with `///`, `//!` and block forms with `E1001`, "unexpected '/'", at
3:1 (probe `p29_cmt_doc_forms`), and a shebang line with `E1001`, "unexpected '#'" (probe `p36_ws_shebang`).

## DN-78. The spelling of a tuple index

**Decision.** A tuple index is `0`, or a digit from 1 to 9 followed by digits, with no `_` and no leading zero
(`E2404`).

**Options.** (A) Any digit run. (B) One spelling per index.

**Reason.** Option B: `t.1` and `t.01` cannot both name the same element.

**Refused forms.** `t.01`, `t.1_0`.

**Reference.** `mindc check` accepts `t.01` and the native build refuses it with `lane.source.tuple` (probe
`p16_tuple_leading_zero`, also `e42_tuple_index_leading_zero`).

## DN-79. Fixes of the statement area

**Decision.** The shadowing lint stays off for what DN-8 makes valid. An invalid compound-assignment target uses
`E2402`. A lone `;` is refused with the fix "remove the `;`". `+=` and the other compound operators are one token each,
so `x + = 2` is refused. (`<<=` and `>>=` are formed from joined one-character tokens by DN-52; a space breaks them
too.)

**Options.** (A) Keep the current behaviour. (B) The four fixes.

**Reason.** Option B: each fix gives one code or one token for one form.

**Refused forms.** `;` alone as a statement; `x + = 2`.

**Reference.** `mindc check` refuses a lone `;` with `E1001`, "unexpected ';'" (probe `p55_semi_empty_stmt`), and a
compound assignment to a non-place with "invalid compound-assignment target" (probe `s20_compound_nonplace`); it
accepts the bit and shift compound operators, and the native build refuses them with "unsupported construct" (probe
`s19_compound_bit_ops`).

## DN-80. The closed range

**Decision.** `a..b` is half-open and `a..=b` is closed. Both stand only in the header of a `for` loop. A range is not
a value. In a pattern only the closed form `a..=b` stands, with bounds that are integer literals or `const` names: it
takes every integer `v` with `a <= v <= b`. `..=` is one token.
([Tokens](../../spec/v1.0/lexical.md#tokens); `ForExpression` and `RangePattern` of
[`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf).)

**Options.** (A) `..` only. (B) `..` and `..=`. (C) `s:e[:k]` in a `for` header.

**Reason.** Option B: without `..=` no loop and no pattern can reach the top of a type (`0..=255` over `u8`), and a
pattern names the values that it takes, so one closed form is enough there.

**Refused forms.** `a..b` in a pattern; a range as a value (`let r = 0..=3;`); `a..=b` outside a `for` header and a
pattern.

**Reference.** `mindc check` refuses `for i in 0..=3` with `E1001`, "unexpected `=`, expected an expression" (probe
`c_for_range_incl`); a range pattern was not measured.

**Replaces.** Amends DN-47 (adds the closed form).

## DN-81. Visible broadcast

**Decision.** A plain operator on two tensors needs one dtype and one shape; a scalar operand extends. The dotted
operators `.+`, `.-`, `.*`, `./` and `.%` broadcast by the rules of [Shapes](../../spec/v1.0/shapes.md), and a dotted
operator with no tensor operand is refused. The dotted operators have the precedence of their plain operators. The
matrix product stays `matmul(a, b)`; `@` stays reserved with no production (DN-39).

**Options.** (C) Remove the dotted operators; plain operators broadcast. (D) Plain operators need one shape; dotted
operators broadcast.

**Reason.** Option D: every expansion of a shape is visible in the text and one search finds it; a silent expansion
of `[3, 1] * [1, 4]` cannot happen.

**Refused forms.** A plain operator on two tensors of different shapes (the message gives the dotted form as the fix);
`a .+ b` on two scalars; `t.-1` on a tuple.

**Reference.** `mindc check` accepts `return a .+ b;` on two `i64` operands (probe `a6_dot_plus_scalar`) and `a.*b` on
integers, which the native build refuses with `lane.source.tensor` (probe `p49_mun_dotstar_ints`). The count of plain
operators on two non-scalar shapes in existing sources needs types and was not measured.

**Replaces.** DN-51 and option A of DN-17 (the dotted operators stay, with one meaning).

## DN-82. The gradient attribute

**Decision.** The function attribute `#[grad(g, p1, ..., pk)]` declares the function `g` with the parameters of `f`;
its result is the gradient with respect to the named parameters. `diff T` is not part of Core v1 and is refused with a
hint to the attribute.

**Options.** (A) `diff T` for every floating-point type. (B) `#[grad(g, p)]` on a function, and `diff T` out of Core v1.

**Reason.** Option B: the gradient function has a written name, needs no function values, and is an ordinary function
of the IR with a fixed signature, so its result is bit-identical by the same rule as every function.

**Refused forms.** `diff Tensor<f32, [2]>`, `diff f64`.

**Reference.** `mindc check` refuses `diff Tensor<f32, [2]>` with `E1001`, "expected 'tensor' after 'diff'" (probe
`a6_diff_type`, also `f03_diff_Tensor_alone`, `i07_diff_f64`); the attribute `#[grad]` was not measured.

## DN-83. `pub` on the item

**Decision.** `pub` before an item makes it visible outside its module; `pub` is a keyword. The list form
`export { ... }` is refused, and `export` stays a reserved word with no production. In the grammar `pub` stands after
the attributes and before the word that starts a named item.

**Options.** (A) An export list. (B) `pub` on the item.

**Reason.** Option B: the visibility of an item stands at the item, and a list is a second place kept by hand.

**Refused forms.** `export { f }`, `export f;`, `pub` as a name.

**Reference.** `mindc check` accepts `pub fn` and the image exits with 5 (probe `fn_pub`), and `export { f }`, whose
image exits with 1 (probe `a4_export_brace`).

**Replaces.** Decisions 3 and 5 of the draft [RFC 0026](./0026-module-items.md) (the export list).

## DN-84. Tool attributes

**Decision.** A tool attribute has the name `tool.name`, two segments. The first segment MUST be listed in the project
file; the compiler checks the form and gives it no meaning. A tool attribute MUST NOT change a byte of the artifact,
and a gate row proves it: the IR bytes and the native image are equal with and without the attribute. A one-segment
name that is not in the attribute table is refused.

**Options.** (A) A closed list of attributes only. (B) Two-segment tool names, listed and byte-neutral.

**Reason.** Option B: a tool can mark a source in a checked namespace, and the rule that the mark changes no byte keeps
the build the same.

**Refused forms.** `#[fast]` (one segment, not in the table); `#[a.b.c]`; `#[tool.name]` whose first segment the project
file does not list.

**Reference.** `mindc check` accepts `#[fast]` before a function (probe `attr_unknown_fn`) and before a struct (probe
`attr_unknown_struct`); a two-segment name was not measured.

**Replaces.** Amends DN-31 and rule 7 of the draft [RFC 0026](./0026-module-items.md) (the closed list of attributes).

## DN-85. Type names

**Decision.** The growable sequence is `Vec<T>`, the map is `Map<K, V>`, and the string is `String`. Scalar primitive
type names are lower case; every other type name is UpperCamel. A generic type always writes all its arguments: the
bare names `Vec` and `Map` are refused, with the rewrite. `array<T>` leaves, and "array" then means the fixed `[T; N]`
only. The container model of DN-15 does not change.

**Options.** (A) `array<T>`, `map` and `string`. (B) `Vec<T>`, `Map<K, V>` and `String`.

**Reason.** Option B: one word for one meaning, and one case rule tells a scalar type from every other type.

**Refused forms.** `array<i64>`, `Vec`, `Map`, `string`, `str`.

**Reference.** No probe of this line measured these names on the release.

**Replaces.** The type names of DN-15 and DN-16.

## DN-86. The lookahead bound is a gate

**Decision.** The grammar of the specification is decided with at most 3 tokens, plus two stated one-token parser
rules (no record body in a head, DN-28; the reading of a statement start). The grammar lint runs in the checks of the
specification repository; its budget is three named decisions (the tail of a block, a record body against a head
brace, the statement reading rule), and a fourth is a failure. The target is a lint that models the two rules and the
block tail, so that the measured count is 0.

**Options.** (A) No stated bound. (B) A stated bound held by a check.

**Reason.** Option B: a later change that adds an undecided choice fails a check instead of reaching the text.

**Refused forms.** A grammar change that adds a fourth undecided choice.

**Reference.** The lint on the grammar files of this line (k up to 3) finds three choices that no k up to 3 decides,
exactly the three named ones (`Block`, `NamePath`, `Statement`); every other choice is decided with at most 3 tokens.
It also lists rows that come from its model, in which every contextual word and `_` is an identifier.

## DN-87. The conformance gate holds every decision

**Decision.** Each decision has an accept row and a reject row. A row carries the code, the position and the count of
errors. Lints assert that these lists are equal: the reserved word list and the `Keyword` rule; the attribute table and
its rows; the error code table and the errors chapter.

**Options.** (A) Rows that compare the code only. (B) Rows with code, position and count, and list lints.

**Reason.** Option B: a decision is held when a change that breaks it fails a row.

**Refused forms.** None.

**Reference.** No compiler verdict applies.

## DN-88. Migration

**Decision.** One tool rewrites the mechanical changes (suffixes, terminators, tensor spellings, type names, arm
commas, precedence parentheses, module separators): the formatter with a migration mode. A decided form that needs a
rewrite is enforced by the reference only in a release that ships this tool.

**Options.** (A) Enforce at once. (B) Enforce with the tool.

**Reason.** Option B: every program that a decision refuses has a rewrite that keeps its value, and a release does
not refuse a program that its own tool cannot fix.

**Refused forms.** None.

**Reference.** No compiler verdict applies.
