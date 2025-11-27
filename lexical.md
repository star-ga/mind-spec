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

# Lexical Structure

This chapter provides the normative specification for the lexical analysis of the MIND programming language.

## 1. Source Text Representation
MIND source files must be encoded as **UTF-8**. The compiler performs normalization on line endings prior to tokenization.

## 2. Comments and Whitespace
- **Line Comments:** Begin with `//`.
- **Block Comments:** Begin with `/*` and end with `*/`. Block comments **can be nested**.

## 3. Identifiers
MIND follows Unicode Standard Annex #31:
```regex
Identifier := [\p{XID_Start}_] [\p{XID_Continue}_]*
```

## 4. Keywords
The following tokens are reserved:
| | | | | |
| :--- | :--- | :--- | :--- | :--- |
| `fn` | `let` | `type` | `struct` | `trait` |
| `if` | `else` | `match` | `while` | `for` |

## 5. Literals
- **Integers:** `123`, `0xFF`, `0b101`
- **Floats:** `3.14`, `1.0e-4`
- **Tangents:** `1.0^` (Differentiable literal)
