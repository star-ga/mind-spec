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

# Lexical Structure (Normative)

This chapter defines how a sequence of Unicode scalar values is transformed into a stream of
lexical tokens. Implementations MUST follow these rules before syntactic analysis. Informative
commentary that links to the reference compiler is marked accordingly. The lexical grammar
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf) derives every rule of this chapter.

## Source text

- Source files MUST be encoded as UTF-8. Implementations MAY accept other encodings as an extension
  but MUST reject ill-formed byte sequences.
- A line terminator is LF (`\n`) or CRLF (`\r\n`). For the purpose of layout, all line terminators are
  normalised to LF. A CR that LF does not follow MUST be refused.
- The Unicode byte order mark (BOM) MAY appear at the start of a source file. If present it is
  ignored during tokenisation.
- **Forbidden code points.** These code points MUST NOT appear anywhere in a source file, comments and strings
  included: U+0000 to U+0008, U+000B, U+000C, U+000E to U+001F, U+007F, U+0080 to U+009F, U+200E, U+200F,
  U+202A to U+202E, U+2066 to U+2069, U+2028, U+2029, and U+FEFF other than at offset 0 (`ForbiddenCodePoint`).
  A source with one of them MUST be refused with `E1008`; the message names the code point as `U+XXXX` with its
  Unicode name. In a string, such a value is written with an escape (`\u{202E}`). So no two texts that look the same
  are read differently.
- **Shebang.** A first line that starts with `#!` at offset 0 (after a BOM, if there is one), and in which `[` does
  not follow `#!`, is skipped by the lexer (`Shebang`). Anywhere else `#!` has no meaning of its own.

Additional implementation guidance is available in the reference compiler documentation under
[`star-ga/mind`](https://github.com/star-ga/mind) (informative).

## Tokens

Tokens are classified as follows:

1. **Identifiers** — sequences that begin with an ASCII letter, or with `_` followed by at least one letter, digit or
   underscore, and go on with letters, digits, or underscores.
2. **Keywords** — reserved words listed in [Keywords](#keywords).
3. **Literals** — numeric, string, and boolean literals as defined below.
4. **Operators and punctuation** — symbols such as `+`, `->`, and `=>`, the character `#` that
   starts an attribute (`#[name]`, [Attributes](./language.md#attributes)), and the wildcard `_`.

The operators and the punctuation are the ones that `Operator` and `Punctuation` of
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf) list. The lexer reads the longest operator that the text
spells (longest match), except that a token that starts with `<` or `>` is that one character (**Joined angles**,
below): `x+=1` holds the one token `+=`, and `x<<=1` holds the joined tokens `<`, `<` and `=`, which the parser
reads as the operator `<<=`. Every compound assignment operator is written with no space in it, so `x + = 2` holds
`+` and `=` and is not derived.

- **Range tokens.** `..` and `..=` are one token each, and `..=` is not `..` and `=`. They stand only in the header of
  a `for` loop (`for i in 0..n`, `for i in 0..=255`), and `..=` also in a range pattern (`1..=9 =>`); a range is not a
  value ([`grammar-syntax.ebnf`](./grammar-syntax.ebnf), `ForExpression`, `RangePattern`). The digits before `..`
  form an integer literal: `0..4` is the tokens `0`, `..` and `4`.
- **Dotted operators.** `.+`, `.-`, `.*`, `./` and `.%` are one token each, so `a.*b` holds the token `.*` and is
  not a field access, and `t.-1` holds `.-`. They are the broadcast operators, with the precedence of `+`, `-`,
  `*`, `/` and `%` ([Operator precedence](./language.md#operator-precedence-and-associativity)).
- **Complement.** `~` is one token, the bitwise complement of an integer; `!` takes a `bool`.
- **Reserved token `@`.** `@` is a token, and no rule of the syntactic grammar spells it: a source that holds it
  MUST be refused. The matrix product is written `matmul(a, b)`, and an attribute `#[name]`.

**Joined angles.** The lexer produces each `<` and `>` as a token of its own and marks it *joined* when the next
character follows it with no space. Where an operator stands, a `>` joined to a `>` is the operator `>>`, a `>` joined
to `=` is `>=`, and `>>` joined to `=` is `>>=`; the same holds for `<<`, `<=` and `<<=`. A space breaks them:
`x > = 1` is not derived. Where a type-argument list or the type-parameter list of a declaration is open
(`CloseAngle` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)), each `>` closes one list. So
`let o: Option<Option<i64>>= p;` is derived: the first `>` closes the inner list, the second `>` closes the outer
list, and `=` is left. A `>` closes only a list that is open: in `let o: Option<i64>>= p;` the first `>` closes the
list, `>=` is left where the `let` needs `=`, and the source MUST be refused. `type X<T>= T;` is derived: the `>`
closes the type parameters and `=` is left.

**Colon of a slice.** Inside the brackets of an index and outside any nested pair of `(` and `)`, `[` and `]`, or `{`
and `}`, the text `::` is two `:` of a
slice (`SliceColon` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf)): `a[::2]` is the slice with the start and the
end omitted and the step 2, and `a[s::k]` is the slice from `s` with the step `k`. A path there is written in
parentheses: `a[(E::B)]`.

**Tuple index.** Directly after the token `.`, a run of digits is an integer token, never a floating-point literal:
`t.0.1` is the tokens `t`, `.`, `0`, `.` and `1`, and it means `(t.0).1`. A tuple index is `0`, or a digit from `1`
to `9` followed by digits, with no `_` and no leading `0`; `t.01` and `t.1_0` MUST be refused with
[`E2404`](./errors.md#e2404-invalid-tuple-index). This rule alone decides a run of digits and `_` directly after the
token `.`, so such a run never gets `E1005`; a run there that holds a letter, as in `t.0.1e0`, MUST be refused with
[`E1005`](./errors.md#e1005-invalid-numeric-literal).

MIND has no operator `:=`. The text `:=` is the two tokens `:` and `=`, no rule of the syntactic grammar
puts `=` directly after `:`, and an implementation MUST refuse a source such as `x := 1;`.

Whitespace and comments separate tokens but are otherwise discarded.

### Identifiers

Identifiers MUST match the regular expression `[A-Za-z][A-Za-z0-9_]*|_[A-Za-z0-9_]+`: identifiers are ASCII in Core
v1. A character outside ASCII in code, outside a string and a comment, MUST be refused with
[`E1002`](./errors.md#e1002-invalid-character-in-identifier).

**Wildcard.** A lone `_` is not an identifier: it is the wildcard token, and it never names a value. It binds nothing:
`let _ = e;` evaluates `e` and drops the value, and `_` may name a parameter, also several parameters of one function.
Where an expression stands, `_` has no derivation (`return _;` is refused).

### Keywords

The following keywords are reserved and MAY NOT be used as identifiers:

```
fn    let    type    struct    trait
if    else   match   while     for
return defer import  export    where
break continue true  false     mut
loop  assert pub
```

Keywords MUST be matched prior to identifiers. A keyword where a name stands (`let mut = 1;`, `fn true()`,
`let loop = 2;`) MUST be refused with `E1007`, one diagnostic at the word. This list and the `Keyword` rule of
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf) are equal. `true` and `false` are the boolean literals and are
reserved. `pub` marks an item visible outside its module. `where` and `export` are reserved, and no rule of the
syntactic grammar spells them: a source that uses either word MUST be refused.

The syntactic grammar also spells out words that are not in this list (`ContextualWord` of
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf)); they are not reserved
([Words that the grammar spells out](./language.md#words-that-the-grammar-spells-out)). The lexer produces each of them
as an identifier. Each has its own positions in the syntactic grammar, and at each of them at most two tokens decide
whether the word is the spelled word or a name: `let diff = 1; return diff;` is valid. `tensor` directly followed by
`(` is always the tensor constructor, so a function, a parameter of a function type or an import named `tensor` MUST
be refused with `E1007`; `tensor` stays a valid name of a value.

### Literals

- **Integer literals** consist of digits, with no sign and no suffix. Binary (`0b`), octal (`0o`),
  and hexadecimal (`0x`) prefixes are allowed. A decimal integer of more than one digit does not start with `0`:
  `017` MUST be refused with [`E1005`](./errors.md#e1005-invalid-numeric-literal).
- **No sign.** A `-` before a literal is always the unary operator, and there is no unary `+`. So `a-1` is a
  subtraction, and `-2147483648` is the operator `-` applied to the literal `2147483648`. The checker reads a unary
  `-` applied to a literal (with parentheses or without) as one negative value, so `let m: i32 = -2147483648;` holds
  a value that `i32` can hold ([Type of a literal](./types.md#type-of-a-literal)). `-5.abs()` is `-(5.abs())`.
- **Digit separator.** One `_` stands only between two digits of one digit sequence: `1_000` and `0xFF_FF` are valid,
  and `0x_FF`, `1__0`, `1_` and `1_.5` MUST be refused with [`E1005`](./errors.md#e1005-invalid-numeric-literal).
- **Floating-point literals** follow the grammar `<digits>.<digits>(e-?<digits>)?`: the exponent is written with a
  lower-case `e` and an optional `-` only.
- **One run, one form.** A numeric literal is the longest run of letters, digits, `_` and `.` that starts with a digit
  (a `.` only between two digits and never in a run directly after the token `.`, and a `-` only directly after the
  `e` of an exponent). The whole run MUST match one form of the grammar, else the source MUST be refused with
  [`E1005`](./errors.md#e1005-invalid-numeric-literal) at the first character that no form allows. A run of digits
  and `_` directly after the token `.` is a tuple index, and **Tuple index** (above) decides it: `t.01` is `E2404`,
  not `E1005`. A literal has no
  type suffix: `1.5f32` and `7u8` are refused; a literal takes its type from its context, or from a cast
  (`1.5 as f32`).
- **String literals** are enclosed in double quotes. A quoted string ends on the line where it starts: a line end inside it
  MUST be refused with [`E1003`](./errors.md#e1003-unterminated-string-literal) at the opening `"`, and a raw TAB
  inside it with `E1008` (the escape `\t` writes a tab). A string literal has no prefix and no suffix: a string
  literal directly followed by a letter, a digit, `_` or `"`, and an identifier directly followed by `"`, MUST be
  refused with [`E1009`](./errors.md#e1009-reserved-literal-prefix-or-suffix) (`"a"b`, `b"a"`). The escape
  sequences are listed in [String escapes](./language.md#string-escapes); any other escape sequence MUST be
  diagnosed with
  [`E1004`](./errors.md#e1004-invalid-escape-sequence). The escape `\u{...}` holds one to six hexadecimal digits,
  and its value is at most `10FFFF` and outside `D800` to `DFFF`; any other `\u{...}` MUST be refused with `E1004`.
- **Line strings.** A raw text, also one of several lines, is written as line strings: `\\` followed by every
  character up to the end of the line, raw, with no escape. Line strings on lines that follow each other, with only
  spaces and tabs before each `\\`, form one string literal; the lines are joined with LF, and the value has no LF
  after the last line (`LineStringLiteral`).
- **Boolean literals** are `true` and `false`; both are keywords.
- A literal has no suffix `^`. The character `^` is only the exclusive-or operator, so `1.0^;` is an
  exclusive-or with no right operand and MUST be refused.

### Comments and whitespace

- Line comments begin with `//` and continue to the end of the line.
- There is no block comment: `/*` MUST be refused with `E1010`, whose message names line comments `//`.
- A comment that begins with `///` is a doc comment: it documents the item or the field that follows it, and in any
  other place it MUST be refused. A comment that begins with `//!` documents the module and stands only before the
  first item of the file.
- Whitespace consists of spaces, tabs, and line terminators. Implementations MAY treat adjacent line
  terminators as a single blank line for layout purposes.

## Layout and indentation

The language uses explicit delimiters and does not impose indentation-based scoping. Implementations
MAY offer linting or formatting guidance, but layout is not part of the normative grammar.

## Diagnostics

When encountering an invalid token the implementation MUST emit a diagnostic that includes the
source range of the offending sequence. A file with a lexical or a syntax fault gets one diagnostic, at the first
fault, and no further diagnostic follows from it. A message shows source text in backticks, writes "end of file" at
the end of the input, and names a character that does not print as `U+XXXX` with its Unicode name.
