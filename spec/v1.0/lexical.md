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
3. **Literals** — numeric, string, boolean, and differentiable literals as defined below.
4. **Operators and punctuation** — symbols such as `+`, `->`, and `:=`, and the character `#` that
   starts an attribute (`#[name]`, [Attributes](./language.md#attributes)).

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
```

Keywords MUST be matched prior to identifiers.

The syntactic grammar also spells out words that are not in this list (`in`, `as`, `break`, `continue`, `const`,
`enum`, `module`, `use`, `assert`, `diff`, `dyn`, `tensor`, `dtype`, the primitive type names and `_`).
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf) lists them as `ContextualWord`: the lexer produces each of them as
an identifier and the parser reads it by its position. This edition does not reserve them.

### Literals

- **Integer literals** consist of an optional sign followed by digits. Binary (`0b`), octal (`0o`),
  and hexadecimal (`0x`) prefixes are allowed.
- **Floating-point literals** follow the grammar `<digits>.<digits>([eE][+-]?<digits>)?`.
- **String literals** are enclosed in double quotes. The escape sequences are `\n`, `\r`, `\t`, `\0`,
  `\\`, `\'`, `\"` and `\u{HEX}` (one to any number of hexadecimal digits), as in
  [`grammar-lexical.ebnf`](./grammar-lexical.ebnf). Any other escape sequence MUST be diagnosed with
  [`E1004`](./errors.md#e1004-invalid-escape-sequence).
- **Boolean literals** are `true` and `false`.
- **Differentiable literals** MAY include tangent annotations using the `^` suffix (see
  [Automatic differentiation](./autodiff.md)).

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
