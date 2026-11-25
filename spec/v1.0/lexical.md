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
commentary that links to the reference compiler is marked accordingly.

## Source text

- Source files MUST be encoded as UTF-8. Implementations MAY accept other encodings as an extension
  but MUST reject ill-formed byte sequences.
- Line terminators consist of LF (`\n`), CR (`\r`), or CRLF (`\r\n`). For the purpose of layout,
  all line terminators are normalised to LF.
- The Unicode byte order mark (BOM) MAY appear at the start of a source file. If present it is
  ignored during tokenisation.

Additional implementation guidance is available in the reference compiler documentation under
[`star-ga/mind`](https://github.com/star-ga/mind) (informative).

## Tokens

Tokens are classified as follows:

1. **Identifiers** — sequences that begin with a letter or underscore followed by letters, digits, or
   underscores.
2. **Keywords** — reserved words listed in [Keywords](#keywords).
3. **Literals** — numeric, string, and boolean literals as defined below.
4. **Operators and punctuation** — symbols such as `+`, `->`, and `=>`, and the character `#` that
   starts an attribute (`#[name]`, [Attributes](./language.md#attributes)).

The operators and the punctuation are the ones that `Operator` and `Punctuation` of
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf) list. The lexer reads the longest operator that the text
spells (longest match): `x<<=1` holds the one token `<<=`, not `<<` and `=` and not `<` and `<=`, and
`x>>=1` holds the one token `>>=`. The elementwise operators `.*`, `./`, `.+` and `.-`
([Operator precedence](./language.md#operator-precedence-and-associativity)) are one token each, so `a.*b`
holds the token `.*` and is not a field access.

**Closing angle.** Where the syntactic grammar expects the `>` that closes a type-argument list
(`CloseAngle` of [`grammar-syntax.ebnf`](./grammar-syntax.ebnf): the type arguments of `Tensor<...>` and of a
named type such as `Option<...>`) and the next token starts with `>` (`>>`, `>=` or `>>=`), the first `>` is
that closing token, and the rest of the token is read again as a token: `>>` gives `>` and `>`, `>=` gives `>` and
`=`, and `>>=` gives `>` and `>=`. So `let o: Option<Option<i64>>= p;` is derived: the first `>` of `>>=`
closes the inner list, the rest `>=` gives the `>` that closes the outer list, and `=` is left. A `>` closes
only a list that is open: in `let o: Option<i64>>= p;` the first `>` closes the list, `>=` is left where the
`let` needs `=`, and the source MUST be refused. Everywhere else longest match decides, so `x >>= 1` holds
the one token `>>=`, and the `>` that closes the type parameters of a declaration is not read so:
`type X<T>= T;` holds the token `>=` and is not derived.

**Colon of a slice.** Where the syntactic grammar expects a `:` of a slice (`SliceColon` of
[`grammar-syntax.ebnf`](./grammar-syntax.ebnf)) and the next token is `::`, the first `:` is that token and the
rest `:` is read again as a token: `a[::2]` is the slice with the start and the end omitted and the step 2.

MIND has no operator `:=`. The text `:=` is the two tokens `:` and `=`, no rule of the syntactic grammar
puts `=` directly after `:`, and an implementation MUST refuse a source such as `x := 1;`.

Whitespace and comments separate tokens but are otherwise discarded.

### Identifiers

Identifiers MUST match the regular expression `[\p{XID_Start}_][\p{XID_Continue}_]*`. Implementations
MUST treat identifiers with different Unicode normalisation forms as distinct.

### Keywords

The following keywords are reserved and MAY NOT be used as identifiers:

```
fn    let    type    struct    trait
if    else   match   while     for
return defer import  export    where
break continue
```

Keywords MUST be matched prior to identifiers.

The syntactic grammar also spells out words that are not in this list; they are not reserved
([Words that the grammar spells out](./language.md#words-that-the-grammar-spells-out)).

### Literals

- **Integer literals** consist of an optional sign followed by digits. Binary (`0b`), octal (`0o`),
  and hexadecimal (`0x`) prefixes are allowed.
- **Sign.** A `-` or `+` directly before the digits of an integer or floating-point literal, with no character between,
  is part of the literal only where an operand can start: at the start of an expression, after an operator, after `(`,
  `[`, `{`, `,`, `;`, `=` or `:`, after a keyword, or after the `}` that ends a block-like statement
  ([Block-like statements](./language.md#block-like-statements)). After an identifier, a literal, `)`, `]` or any other
  `}` it is an operator. So `a-1` is a subtraction, `if x > 0 { }` followed by `-1;` holds the literal `-1`, `{ 1 } -1`
  as an operand is a subtraction, and `let m: i32 = -2147483648;` holds the one literal `-2147483648`, which `i32` can
  hold.
- **Floating-point literals** follow the grammar `<digits>.<digits>([eE][+-]?<digits>)?`. The lexer
  reads one also after the token `.`: `t.0.1` is the tokens `t`, `.` and `0.1`, and the syntactic grammar
  reads the token `0.1` as two tuple indices ([Tuple index](./language.md#tuple-index)).
- **String literals** are enclosed in double quotes. The escape sequences are listed in
  [String escapes](./language.md#string-escapes); any other escape sequence MUST be diagnosed with
  [`E1004`](./errors.md#e1004-invalid-escape-sequence).
- **Boolean literals** are `true` and `false`.
- A literal has no suffix `^`. The character `^` is only the exclusive-or operator, so `1.0^;` is an
  exclusive-or with no right operand and MUST be refused.

### Comments and whitespace

- Line comments begin with `//` and continue to the end of the line.
- Block comments begin with `/*` and end with `*/`. Block comments MAY nest.
- Whitespace consists of spaces, tabs, and line terminators. Implementations MAY treat adjacent line
  terminators as a single blank line for layout purposes.

## Layout and indentation

The language uses explicit delimiters and does not impose indentation-based scoping. Implementations
MAY offer linting or formatting guidance, but layout is not part of the normative grammar.

## Diagnostics

When encountering an invalid token the implementation MUST emit a diagnostic that includes the
source range of the offending sequence. Implementations SHOULD attempt to recover and continue
lexing to report additional errors.
