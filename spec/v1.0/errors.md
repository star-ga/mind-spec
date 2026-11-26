<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Error Catalog (Normative)

This chapter enumerates the error categories, error codes, and diagnostic requirements for Core v1
implementations. All errors MUST be deterministic and MUST include sufficient context for debugging.

## Error categories

Core v1 defines six primary error categories:

1. **Lexical and syntax errors (E1xxx)**: malformed source text and invalid tokens (E10xx), and faults of the
   syntax (E11xx)
2. **Type errors (E2xxx)**: type mismatches, unresolved types, trait violations
3. **Shape errors (E3xxx)**: broadcasting failures, dimension mismatches, invalid shapes
4. **Verification errors (E4xxx)**: IR verification failures, SSA violations
5. **Autodiff errors (E5xxx)**: differentiation failures, unsupported operations
6. **Runtime and artifact-production errors (E6xxx)**: execution failures, backend unavailability, resource errors, compiler materialization refusal

Each error code follows the pattern `E[category][number]` where category is 1-6 and number is a
three-digit identifier.

## Code table

This table lists every code of the catalog, once. A code has one meaning: the meaning of its entry below. A code
that a decision withdraws stays in the table with its history and is never given another meaning. A check of the
specification repository asserts that this table and the entries of this chapter hold the same codes with the same
names, and that a code that a chapter or a conformance row names is a code of this table.

**Fix classes (DN-88).** The repair table is permanent: a refused form keeps its repair in every later edition. Each
code has one fix class, in the column "Fix class":

- **EXACT**: one rewrite, found from the tokens alone.
- **TYPED**: one rewrite, and the checker must know a type or the kind of a name to find it.
- **CHOICE**: two candidates, in a fixed order.
- **NONE**: no rewrite; the message names the form to write.

The class holds for every trigger of the code. `E1105` has one class for each row of its table. The record of a
diagnostic whose class is EXACT or TYPED carries the edit (the start and the end of the replaced text, and the new
text); a CHOICE diagnostic carries its two edits in the fixed order. A conformance row whose code has the class EXACT
or TYPED carries the text after the fix (`fix`), and the gate applies the edit and checks the result against it. The
check command with the fix mode is the entry for tools and agents: release 0.10.4 has it as `mindc check --fix`, and on
a `let` with no `;` it inserts the `;` (probe `e4_b_fix_semi`).

| Code | Name | Status | Fix class |
|------|------|--------|-----------|
| [`E1001`](#e1001-invalid-utf-8-sequence) | Invalid UTF-8 sequence | in force | NONE |
| [`E1002`](#e1002-invalid-character-in-identifier) | Invalid character in identifier | in force | NONE |
| [`E1003`](#e1003-unterminated-string-literal) | Unterminated string literal | in force | NONE |
| [`E1004`](#e1004-invalid-escape-sequence) | Invalid escape sequence | in force | NONE |
| [`E1005`](#e1005-invalid-numeric-literal) | Invalid numeric literal | in force | NONE |
| [`E1006`](#e1006-unterminated-block-comment) | Unterminated block comment | withdrawn by DN-43; the entry keeps its history | NONE |
| [`E1007`](#e1007-reserved-word-as-a-name) | Reserved word as a name | in force | NONE |
| [`E1008`](#e1008-forbidden-character) | Forbidden character | in force | NONE |
| [`E1009`](#e1009-reserved-literal-prefix-or-suffix) | Reserved literal prefix or suffix | in force | NONE |
| [`E1010`](#e1010-block-comment) | Block comment | in force | NONE |
| [`E1101`](#e1101-unexpected-token) | Unexpected token | in force | NONE |
| [`E1102`](#e1102-unclosed-delimiter) | Unclosed delimiter | in force | NONE |
| [`E1103`](#e1103-missing-separator) | Missing separator | in force | EXACT |
| [`E1104`](#e1104-misspelled-keyword) | Misspelled keyword | in force | EXACT |
| [`E1105`](#e1105-form-that-mind-writes-another-way) | Form that MIND writes another way | in force | by row |
| [`E1106`](#e1106-operators-that-need-parentheses) | Operators that need parentheses | in force | CHOICE |
| [`E1107`](#e1107-assignment-where-an-expression-stands) | Assignment where an expression stands | in force | NONE |
| [`E1108`](#e1108-nesting-too-deep) | Nesting too deep | in force | NONE |
| [`E2001`](#e2001-type-mismatch) | Type mismatch | in force | NONE |
| [`E2002`](#e2002-unresolved-name-or-qualified-owner) | Unresolved name or qualified owner | in force | NONE |
| [`E2003`](#e2003-cannot-infer-type) | Cannot infer type | in force | NONE |
| [`E2004`](#e2004-dtype-mismatch-in-binary-operation) | Dtype mismatch in binary operation | in force | NONE |
| [`E2005`](#e2005-invalid-dtype-for-operation) | Invalid dtype for operation | in force | NONE |
| [`E2006`](#e2006-trait-bound-not-satisfied) | Trait bound not satisfied | in force | NONE |
| [`E2007`](#e2007-arity-mismatch) | Arity mismatch | in force | NONE |
| [`E2008`](#e2008-operator-not-defined-for-tensor-operands) | Operator not defined for tensor operands | in force | NONE |
| [`E2016`](#e2016-invalid-cast) | Invalid cast | in force | NONE |
| [`E2026`](#e2026-numeric-scalar-used-as-a-known-struct) | Numeric scalar used as a known struct | in force | NONE |
| [`E2032`](#e2032-unsupported-slice-call-abi) | Unsupported slice call ABI | in force | NONE |
| [`E2033`](#e2033-borrowed-slice-capability-violation) | Borrowed slice capability violation | in force | NONE |
| [`E2036`](#e2036-non-integer-value-stored-into-a-narrow-integer-element) | Non-integer value stored into a narrow integer element | in force | NONE |
| [`E2037`](#e2037-function-name-used-as-a-value) | Function name used as a value | in force | NONE |
| [`E2042`](#e2042-predeclared-name-taken-by-a-declaration-or-a-binding) | Predeclared name taken by a declaration or a binding | in force | NONE |
| [`E2300`](#e2300-collection-mutation-in-expression-position) | Collection mutation in expression position | in force | NONE |
| [`E2301`](#e2301-non-final-enum-variant-binding-collision) | Non-final enum-variant binding collision | in force | NONE |
| [`E2310`](#e2310-refutable-pattern-in-a-binding) | Refutable pattern in a binding | in force | NONE |
| [`E2311`](#e2311-match-not-exhaustive) | Match not exhaustive | in force | NONE |
| [`E2312`](#e2312-arm-that-no-value-can-reach) | Arm that no value can reach | in force | NONE |
| [`E2313`](#e2313-alternatives-that-bind-different-names) | Alternatives that bind different names | in force | NONE |
| [`E2314`](#e2314-final-binding-arm-that-names-a-variant-or-a-constant) | Final binding arm that names a variant or a constant | in force | NONE |
| [`E2401`](#e2401-loop-exit-outside-a-loop) | Loop exit outside a loop | in force | NONE |
| [`E2402`](#e2402-invalid-target-of-a-change) | Invalid target of a change | in force | NONE |
| [`E2403`](#e2403-invalid-entry-function) | Invalid entry function | in force | NONE |
| [`E2404`](#e2404-invalid-tuple-index) | Invalid tuple index | in force | NONE |
| [`E2405`](#e2405-no-loop-statement) | No loop statement | withdrawn by DN-54; the entry keeps its history | NONE |
| [`E2406`](#e2406-range-index) | Range index | withdrawn by DN-47; the entry keeps its history | NONE |
| [`E2407`](#e2407-struct-with-no-layout) | Struct with no layout | in force | NONE |
| [`E2408`](#e2408-literal-out-of-range) | Literal out of range | in force | NONE |
| [`E2409`](#e2409-callee-is-not-a-function) | Callee is not a function | in force | NONE |
| [`E2410`](#e2410-no-such-method) | No such method | in force | NONE |
| [`E2501`](#e2501-raw-memory-use-outside-a-raw-memory-function) | Raw memory use outside a raw memory function | in force | NONE |
| [`E2502`](#e2502-invalid-attribute) | Invalid attribute | in force | NONE |
| [`E2701`](#e2701-impl-of-an-undeclared-trait) | Impl of an undeclared trait | in force | NONE |
| [`E2702`](#e2702-duplicate-impl) | Duplicate impl | in force | NONE |
| [`E2703`](#e2703-method-that-the-trait-does-not-declare) | Method that the trait does not declare | in force | NONE |
| [`E2707`](#e2707-trait-method-missing-from-an-impl) | Trait method missing from an impl | in force | NONE |
| [`E2720`](#e2720-duplicate-name) | Duplicate name | in force | NONE |
| [`E2730`](#e2730-binding-that-hides-a-module-name) | Binding that hides a module name | in force | NONE |
| [`E2731`](#e2731-path-separator-after-a-module) | Path separator after a module | in force | TYPED |
| [`E3001`](#e3001-broadcasting-failure) | Broadcasting failure | in force | NONE |
| [`E3002`](#e3002-rank-mismatch) | Rank mismatch | in force | NONE |
| [`E3003`](#e3003-dimension-mismatch) | Dimension mismatch | in force | NONE |
| [`E3004`](#e3004-invalid-axis) | Invalid axis | in force | NONE |
| [`E3005`](#e3005-duplicate-axis) | Duplicate axis | in force | NONE |
| [`E3006`](#e3006-negative-dimension) | Negative dimension | in force | NONE |
| [`E3007`](#e3007-element-count-mismatch) | Element count mismatch | in force | NONE |
| [`E3008`](#e3008-invalid-permutation) | Invalid permutation | in force | NONE |
| [`E3009`](#e3009-squeeze-dimension-not-1) | Squeeze dimension not 1 | in force | NONE |
| [`E3010`](#e3010-invalid-shape-in-literal) | Invalid shape in literal | in force | NONE |
| [`E3011`](#e3011-index-outside-its-axis) | Index outside its axis | in force | NONE |
| [`E3012`](#e3012-shape-too-large) | Shape too large | in force | NONE |
| [`E3013`](#e3013-unknown-dimension-name) | Unknown dimension name | in force | NONE |
| [`E3014`](#e3014-too-many-index-items) | Too many index items | in force | NONE |
| [`E3015`](#e3015-plain-operator-on-two-shapes) | Plain operator on two shapes | in force | TYPED |
| [`E3016`](#e3016-dotted-operator-with-no-expansion) | Dotted operator with no expansion | in force | TYPED |
| [`E4001`](#e4001-ssa-violation-use-before-definition) | SSA violation (use before definition) | in force | NONE |
| [`E4002`](#e4002-ssa-violation-multiple-definitions) | SSA violation (multiple definitions) | in force | NONE |
| [`E4003`](#e4003-undefined-output) | Undefined output | in force | NONE |
| [`E4004`](#e4004-invalid-input-declaration) | Invalid input declaration | in force | NONE |
| [`E4005`](#e4005-constant-verification-failure) | Constant verification failure | in force | NONE |
| [`E4006`](#e4006-index-list-length-mismatch) | Index list length mismatch | in force | NONE |
| [`E4007`](#e4007-slice-parameters-length-mismatch) | Slice parameters length mismatch | in force | NONE |
| [`E4008`](#e4008-invalid-slice-step) | Invalid slice step | in force | NONE |
| [`E4009`](#e4009-conv2d-channel-mismatch) | Conv2d channel mismatch | in force | NONE |
| [`E4010`](#e4010-conv2d-invalid-strides) | Conv2d invalid strides | in force | NONE |
| [`E4011`](#e4011-gather-invalid-indices-dtype) | Gather invalid indices dtype | in force | NONE |
| [`E5001`](#e5001-unsupported-operation) | Unsupported operation | in force | NONE |
| [`E5002`](#e5002-gradient-verification-failure) | Gradient verification failure | in force | NONE |
| [`E5003`](#e5003-invalid-axis-in-gradient) | Invalid axis in gradient | in force | NONE |
| [`E5004`](#e5004-unsupported-shape-in-gradient) | Unsupported shape in gradient | in force | NONE |
| [`E5005`](#e5005-non-differentiable-input) | Non-differentiable input | in force | NONE |
| [`E6001`](#e6001-out-of-bounds-index) | Out-of-bounds index | in force | NONE |
| [`E6002`](#e6002-backend-unavailable) | Backend unavailable | in force | NONE |
| [`E6003`](#e6003-unsupported-operation-on-backend) | Unsupported operation on backend | in force | NONE |
| [`E6004`](#e6004-allocation-failure) | Allocation failure | in force | NONE |
| [`E6005`](#e6005-numeric-overflow) | Numeric overflow | in force | NONE |
| [`E6006`](#e6006-invalid-numeric-value) | Invalid numeric value | in force | NONE |
| [`E6007`](#e6007-execution-timeout) | Execution timeout | in force | NONE |
| [`E6008`](#e6008-device-error) | Device error | in force | NONE |
| [`E6009`](#e6009-compiler-materialization-refusal) | Compiler materialization refusal | in force | NONE |
| [`E6010`](#e6010-invalid-manifest-export) | Invalid manifest export | in force | NONE |
## E1xxx: Lexical and syntax errors

Lexical errors (E10xx) occur during tokenization, before syntactic or semantic analysis. Syntax errors (E11xx) occur
when the token sequence has no derivation in [`grammar-syntax.ebnf`](./grammar-syntax.ebnf). Each top-level item gets
at most one lexical or syntax diagnostic, at its first fault; the parser continues at the next token in column 1 that
can start an item, and no type diagnostic follows from the fault ([Diagnostics](./lexical.md#diagnostics)). A syntax fault never has the code `E1001`.

### E1001: Invalid UTF-8 sequence
- **Trigger**: Source file contains ill-formed UTF-8 byte sequences. This is the only trigger of `E1001`: a fault
  of the syntax has a code of E11xx (DN-63).
- **Required context**: byte offset, invalid sequence (first 4 bytes in hex)
- **Example**: `E1001: Invalid UTF-8 sequence at offset 42: [0xFF, 0xFE, 0x00, 0x01]`

### E1002: Invalid character in identifier
- **Trigger**: in code, outside a string and a comment, a character that starts no token: a character outside
  ASCII (identifiers are ASCII in Core v1, [Identifiers](./lexical.md#identifiers)), such as `α` in `let α = 1;` or
  a typographic quote `“`, or an ASCII character that no token rule starts with, such as `$` or a backtick. A
  forbidden code point is `E1008`.
- **Required context**: source location, offending character (as `U+XXXX` with its name when it does not print)
- **Example**: `E1002: the character '$' starts no token at line 5, column 12`

### E1003: Unterminated string literal
- **Trigger**: a quoted string literal that has no closing quote before the end of its line or the end of the file;
  a quoted string ends on the line where it starts ([Literals](./lexical.md#literals))
- **Required context**: start location of the string literal: the diagnostic stands at the opening quote
- **Example**: `E1003: Unterminated string literal starting at line 10, column 8`

### E1004: Invalid escape sequence
- **Trigger**: Unrecognized escape sequence in string literal (e.g., `\q`), or an escape `\u{...}` that does not
  hold one to six hexadecimal digits, or whose value is above `10FFFF` or in `D800` to `DFFF` (`"\u{110000}"`)
- **Required context**: source location, invalid escape
- **Example**: `E1004: Invalid escape sequence '\q' at line 10, column 15`

### E1005: Invalid numeric literal
- **Trigger**: Malformed integer or floating-point literal (e.g., `0b2`, `1.2.3`): a numeric run that matches no form
  of the grammar ([Literals](./lexical.md#literals)), including a type suffix (`1.5f32`, `7u8`), a `_` that does
  not stand between two digits of one digit sequence (`0x_FF`, `1__0`, `1_`), a decimal integer of more than one
  digit that starts with `0` (`017`), an exponent other than `e` with an optional `-` (`1.5E3`, `1.5e+3`), and a
  float token directly after the access dot of a tuple index (`t.0.1e0`). A run of digits and `_` directly after the
  token `.` is a tuple index and never gets this code: `t.01` is [`E2404`](#e2404-invalid-tuple-index)
- **Required context**: source location of the first character that no form allows, literal text
- **Example**: `E1005: Invalid binary literal '0b2' at line 3, column 10`

### E1006: Unterminated block comment
- **Status**: withdrawn by DN-43: the language has no block comment, and `/*` is `E1010`. This entry keeps the
  history; the code is never reused.
- **Trigger (before DN-43)**: Block comment `/* ... */` not closed before EOF
- **Required context**: start location of block comment
- **Example**: `E1006: Unterminated block comment starting at line 20, column 1`

### E1007: Reserved word as a name
- **Trigger**: a keyword of [Keywords](./lexical.md#keywords) where the grammar needs a name: `let mut = 1;`,
  `let loop = 2;`, `let true = 5;`, `fn f(false: i64)`; and a function, a parameter of a function type or an import
  named `tensor` (`fn tensor(x: i64) -> i64`), because `tensor` followed by `(` is always the constructor
- **Required context**: the word and its location: one diagnostic at the word
- **Example**: `E1007: 'loop' is a keyword and cannot name a binding at line 2, column 9`

### E1008: Forbidden character
- **Trigger**: a forbidden code point anywhere in a source file, comments and strings included
  ([Source text](./lexical.md#source-text)), or a raw TAB inside a quoted string
- **Required context**: the location and the code point as `U+XXXX` with its Unicode name
- **Example**: `E1008: forbidden character U+202E RIGHT-TO-LEFT OVERRIDE at line 3, column 14`

### E1009: Reserved literal prefix or suffix
- **Trigger**: a string literal directly followed by an identifier character or by `"`, or an identifier directly
  followed by `"`: a prefix or a suffix of a string literal, which is reserved (`"a"b`, `b"a"`)
- **Required context**: the literal, the prefix or suffix, and its location
- **Example**: `E1009: a string literal takes no suffix 'b' at line 1, column 13`

### E1010: Block comment
- **Trigger**: the text `/*` outside a string and a comment; there is no block comment
  ([Comments and whitespace](./lexical.md#comments-and-whitespace))
- **Required context**: the location of `/*`, with the fix: line comments `//`
- **Example**: `E1010: MIND has no block comment; write each line as a '//' comment at line 2, column 5`

### E1101: Unexpected token
- **Trigger**: the parser expects one token of a set and finds another, and no other E11xx code describes the
  fault; this includes every form that has no derivation, for example `5(3)` (a value is not a function in this
  edition), `a < b < c`, `+x`, `&x`, `(T)` as a type, `a[1..3]` and `let r = 0..4;`
- **Required context**: the found token text, the expected set (at most 4, in the order of the grammar), the position
  of the found token, and the hint that a chapter names for the form
- **Example**: ``E1101: unexpected `<`: a comparison is not an operand of a comparison; write `a < b && b < c` at line 2, column 14``

### E1102: Unclosed delimiter
- **Trigger**: a `(`, `[` or `{` that has no matching closer before a closer of another kind or the end of the file
- **Required context**: the position where the parser stopped, and the opener as a related location
- **Example**: ``E1102: the `{` at line 1, column 17 is not closed at end of file at line 4, column 1``

### E1103: Missing separator
- **Trigger**: a `;` or a `,` that the grammar requires is missing: after a `let`, a `return`, a loop exit or an
  expression statement, after a match arm, between fields, arguments or items
  ([Statement separators](./language.md#statement-separators))
- **Required context**: the insertion point (the end of the previous token), the separator and the found token
- **Example**: ``E1103: insert `;` after `1` at line 2, column 14``

### E1104: Misspelled keyword
- **Trigger**: a statement or an item that fails to parse, whose first word (or the word where an `else` can stand)
  has 3 or more characters and is at the Damerau-Levenshtein distance 1 from a keyword that the grammar allows at
  that place. Ties go to the first keyword in the order of [Keywords](./lexical.md#keywords).
- **Required context**: the word, the keyword and the location of the word
- **Example**: ``E1104: `lett` is not a keyword; did you mean `let`? at line 2, column 5``
- A valid program never gets `E1104`: `let lets = 1;` is valid.

### E1105: Form that MIND writes another way
- **Trigger**: a form of the fixed table below whose status is "Core v1 refuses", at the start of the form. The
  table is part of this specification, so every implementation gives the same message. It is the table of habit
  forms (DN-64): forms that writers produce, each with its MIND form, its status, its fix class
  ([Code table](#code-table)) and the measured verdict of release 0.10.4 (`mindc check --no-fmt --no-lint`, then the
  native build when the check passes; each verdict names its probe). A row with another status names the code or the
  chapter that decides it.
- **Required context**: the form, the MIND form of the table, the location
- **Example**: ``E1105: MIND writes `else if`, not `elif` at line 5, column 7``
- No word of the table is at the Damerau-Levenshtein distance 1 from a keyword, so no source gets both `E1104` and
  `E1105`: `fun` gets `E1104`, which names `fn`.

| Form | MIND form | Status | Fix class | Release 0.10.4 (measured) |
|------|-----------|--------|-----------|---------------------------|
| `elif`, `elsif`, `elseif` | `else if` | Core v1 refuses | EXACT | refused with `E1001`, "expected '}', found Some('2')" (`e4_x_elif`, `e4_x_elsif`, `e4_x_elseif`) |
| `def`, `func`, `function` where an item can start | `fn` | Core v1 refuses | EXACT | refused with `E1001`, "unexpected `>`, expected an expression" (`e4_x_def`, `e4_x_func`, `e4_x_function`) |
| `var`, `val` where a statement can start | `let` or `let mut` | Core v1 refuses | CHOICE | refused with `E2002`, "unknown identifier `var`", and two more diagnostics (`e4_x_var`, `e4_x_val`) |
| `do` after the condition of a loop | no word: the block follows the condition | Core v1 refuses | EXACT | refused with `E1001`, "expected '{', found Some('d')" (`e4_x_do`) |
| `then` after the condition of an `if` | no word: the block follows the condition | Core v1 refuses | EXACT | refused with `E1001`, "expected '{', found Some('t')" (`e4_x_then`) |
| `switch` | `match` | Core v1 refuses | EXACT | refused with `E1001`, "expected '}', found Some('=')" (`e4_x_switch`) |
| `x++` | `x += 1` | Core v1 refuses | EXACT | refused with `E1001`, "unexpected `+`, expected an expression" (`e4_x_plusplus`) |
| `===` | `==` | Core v1 refuses | EXACT | refused with `E1001`, "unexpected `=`, expected an expression" (`e4_x_eqeqeq`) |
| `@` between two operands | `matmul(a, b)` (DN-39) | Core v1 refuses | EXACT | accepted on `i64` operands; the native build refuses it with `lane.source.tensor` (`e4_x_at_infix`) |
| `@name` before an item | `#[name]` (DN-39) | Core v1 refuses | EXACT | refused with `E1001`, "unexpected `@`" (`e4_x_at_name`) |
| `diff` in a type position | the attribute `#[grad(g, p)]` before the function ([Source form](./autodiff.md#source-form-the-gradient-attribute)) | Core v1 refuses | NONE | refused with `E1001`, "expected 'tensor' after 'diff'" (`e4_x_diff`) |
| `tensor<f32[2]>` | `Tensor<f32, [2]>` ([The tensor type](./shapes.md#the-tensor-type)) | Core v1 refuses | EXACT | accepted; the native build refuses it with `lane.type.tensor` (`e4_x_tensor_old`) |
| `?` as a dimension | an integer literal or the name of a `const` of the type `i64` | Core v1 refuses | NONE | refused with `E1001`, "expected dimension (integer or symbol)" (`e4_x_qdim`) |
| `name = value` as a named argument of an attribute or of the tensor constructor | `name: value` | Core v1 refuses | EXACT | the constructor is refused with `E2003`, "unsupported call to `tensor`" (`e4_x_named_eq`) |
| A macro call `name!(...)`: `println!("x")`, `vec![1, 2]`, `assert!(c)` | the function call `println("x")`, the array literal `[1, 2]`, the statement `assert c;` ([Macros](./language.md#macros-are-not-part-of-the-language-informative)) | Core v1 refuses | EXACT | refused with `E1001`, "macro invocation `vec!` is not supported; MIND has no macros" (`e4_h_macro_vec`, `e4_h_macro_println`) |
| A reference type `&T` or `&mut T` where `T` is not a slice type: `fn f(x: &i64)` | the type `T`: Core v1 has no references, and a value is passed by value; the slice types `&[T]` and `&mut [T]` are an extension ([Slice call implementation boundary](./types.md#slice-call-implementation-boundary)) | Core v1 refuses | NONE | accepted; the native build refuses `&i64` and `&mut i64` with `lane.type.reference` (`e4_h_ref_type`, `e4_h_ref_mut`) |
| A closure bar `\|x: i64\| x + 1` | a function item `fn`; Core v1 has no function values | Core v1 refuses | NONE | refused with `E1001`, "expected ';', found Some(':')" (`e4_h_closure`) |
| `if let P = e { B }` | `match e { P => { B }, _ => { }, }` | Core v1 refuses | EXACT | refused with `E1001`, "expected '{', found Some('S')" (`e4_h_if_let`) |
| The postfix question mark: `?` directly after an operand (`g()?`) | `match e { Ok(v) => v, Err(x) => return Err(x), }`, and the same with `Some` and `None` for an `Option` | Core v1 refuses | NONE | accepted for `g()?` on a `Result<i64, i64>`; the native build refuses it with `lane.type.generic` (`e4_h_question`) |
| An inherent impl block `impl S { fn get(s: S) -> i64 { } }` | functions at module level, `fn get(s: S) -> i64` | Extension ([Core v1 Forms](./core-v1-forms.md)); not `E1105` | NONE | refused with `E1001`, "expected `for` in `impl Trait for Type`" (`e4_h_impl`) |

### E1106: Operators that need parentheses
- **Trigger**: a bit operator (`&`, `|`, `^`, `<<`, `>>`) beside another bit operator or beside `+`, `-`, `*`, `/`,
  `%` or a dotted operator with no parentheses between them, or a chain of shifts (`a << 1 << 2`)
  ([Operator precedence](./language.md#operator-precedence-and-associativity))
- **Required context**: the two operators, their location, and both forms with parentheses
- **Example**: ``E1106: `|` and `<<` need parentheses: write `1 | (2 << 1)` or `(1 | 2) << 1` at line 1, column 30``

### E1107: Assignment where an expression stands
- **Trigger**: `=` or a compound assignment operator after an operand, where a binary operator can stand, inside an
  expression: a chain `a = b = 7;`, a condition `if x = 1 { }`, an argument `f(x = 1)`; an assignment is a statement
  ([Bindings and assignment](./language.md#bindings-and-assignment)). A `=` where an operand must stand, as in
  `x > = 1`, is `E1101`
- **Required context**: the operator and its location; in a condition, the hint `==`
- **Example**: ``E1107: an assignment is a statement, not an expression; to compare, write `==` at line 2, column 10``

### E1108: Nesting too deep
- **Trigger**: an input that nests parentheses, brackets, braces, unary operators and block-like forms deeper than the
  limit of the implementation, which is at least 256 and the same on every substrate
  ([Nesting depth](./language.md#nesting-depth)); a left-associative chain of any length is not nesting
- **Required context**: the location of the first token past the limit, and the limit
- **Example**: `E1108: nesting deeper than 256 at line 1, column 270`

## E2xxx: Type errors

Type errors occur during type checking and type inference.

### E2001: Type mismatch
- **Trigger**: Expression has type that doesn't match expected type
- **Required context**: expression location, expected type, actual type
- **Example**: `E2001: Type mismatch at line 15, column 10: expected 'f32', found 'i32'`
- **Also**: a condition that is not a `bool` (`if 5 { }`); a pattern that does not fit its value, at every pattern
  site (`let (a, b, c) = (1, 2);`, DN-36); a block-like statement that is not the tail and whose type is not `unit`;
  a `const` initializer that is not a constant expression; an array repeat `[v; n]` whose `v` is a handle

### E2002: Unresolved name or qualified owner
- **Trigger**: reference to an undeclared variable, or to a qualified type or
  enum variant whose owner is unknown, unimported, ambiguous, or does not
  export that declaration, or a reference `q.m` or a call `q.m(args)` whose
  head `q` is an import qualifier and whose module exports no member `m`
  ([Module-qualified references](./language.md#module-qualified-references)). A qualified type and an enum
  variant path are extensions of Core v1
  ([Module-qualified type ownership](./types.md#module-qualified-type-ownership)).
  This covers a bare-headed `Enum::Variant`
  value or pattern whose head names an enum declared by another
  project module, when the current module declares no type of that name and
  (a) no import exports a type of that name, including when the module that
  declares the enum is imported but does not export it, (b) several imports
  export one, or (c) the single import exports an enum of that name that does
  not declare the variant. Recognising a qualified path during parsing does not
  establish semantic module ownership.
- **Implementation status**: bare-headed variant resolution is implemented in
  the reference compiler v0.10.3 (compiler commit `1def5dde`). It applies in compiler builds with
  the `cross-module-imports` feature, which is not a default feature, wherever
  several source modules are checked or built together (see Scope). The
  control `cross_module_enum_variant_lowering` is compiled only with the
  `mlir-build` and `cross-module-imports` features on a unix host. Checking
  reports a located E2002, and the project build refuses to embed the module
  as a runtime fallback.
- **Also**: the names `usize` and `isize` (fix `u64` or `i64`); `.` after a type, where `::` follows a type
  ([Module level](./language.md#module-level)); `::` after a module is
  [`E2731`](#e2731-path-separator-after-a-module); a qualified spelling of a predeclared variant (`Option::Some(1)`,
  fix `Some(1)`).
- **Suggestions**: at most one, chosen by a fixed rule: a name in scope at that place at an edit distance of 2 or
  less, the least distance first, then the first in source order. No further diagnostic follows from the
  unresolved name.
- **Required context**: unresolved name or qualified path and source location
- **Examples**: `E2002: Undefined variable 'x' at line 8, column 5`;
  ``E2002: unknown module-qualified type `config.Mode` ``;
  ``E2002: enum `Table` in `Table::Other` is not visible in this module; import the module that declares it``;
  ``E2002: ambiguous enum `Table` in `Table::Other`: several imported modules export it; qualify it with its module``;
  ``E2002: unknown variant `X` of imported enum `Table` ``
- **Scope**: the reference reports the three bare-variant messages above only
  when its owner registry is built from several source modules: by a project
  build, by a single-file entry that imports modules of its enclosing manifest
  project, or by `mindc check` run on several files or on a directory that
  holds several, which builds the registry from the checked files and does not
  read a `Mind.toml`. A single source checked or built on its own gets none of
  them. It reports them only when the head names an enum that some project
  module declares; a head that names no project enum, and the `Option` and
  `Result` heads, are not inspected by this check. It inspects a unit-variant
  value path (`Enum::Variant`) and a `match` pattern, which is reported at its
  match arm. It does not inspect a payload-constructor call
  (`Enum::Variant(...)`) or a struct-variant literal (`Enum::Variant { ... }`).
  A type that the
  current module declares keeps lexical precedence over an imported type of the
  same name.

### E2003: Cannot infer type
- **Trigger**: Type inference fails due to insufficient constraints
- **Required context**: expression location, inference context
- **Example**: `E2003: Cannot infer type for variable 'result' at line 12, column 8`

### E2004: Dtype mismatch in binary operation
- **Trigger**: Binary operation operands have different dtypes (mixing i32 with f32)
- **Required context**: operation location, left dtype, right dtype
- **Example**: `E2004: Dtype mismatch in Add at line 10, column 15: i32 + f64`

### E2005: Invalid dtype for operation
- **Trigger**: Operation applied to an operand whose type or dtype the operation does not support (e.g., Log on
  integers, or a `bool`, `f32` or `f64` operand of `&`, `|`, `^`, `<<` or `>>`), or the argument `e` of the tensor
  constructor `tensor(e)` without a dtype argument when the type of `e` gives no dtype
  ([Tensor operations](./language.md#tensor-operations))
- **Required context**: operation name, actual dtype, supported dtypes
- **Also**: an operand of `!`, `+`, `-`, `*`, `/`, `%` of a type that the operator does not take (`!5`, `true + 1`,
  `~true`); a dtype of a tensor type outside the set of the profile (`Tensor<bool, [2]>`,
  [The tensor type](./shapes.md#the-tensor-type)); an index or a slice bound that is not of an integer type
  (`a[1.5]`, hint `as i64`)
- **Example**: `E2005: Log requires floating-point dtype, found i32 at line 20, column 10`

### E2006: Trait bound not satisfied
- **Trigger**: Type does not implement required trait
- **Required context**: type, required trait, source location
- **Example**: `E2006: Type 'MyStruct' does not implement 'Differentiable' at line 25, column 5`

### E2007: Arity mismatch
- **Trigger**: Function called with wrong number of arguments
- **Required context**: function name, expected arity, actual arity, call location
- **Example**: `E2007: Function 'matmul' expects 2 arguments, found 3 at line 18, column 12`

### E2008: Operator not defined for tensor operands
- **Trigger**: `<`, `<=`, `>` or `>=` with a tensor operand ([Comparison of tensors](./shapes.md#comparison-of-tensors));
  `==` and `!=` on two tensors give one `bool`
- **Required context**: the operator, the operand types and the location
- **Example**: `E2008: '<' is not defined for 'Tensor<f32, [2]>' operands at line 1, column 70`

### E2016: Invalid cast

- **Trigger**: a cast `e as T` whose pair of types is not a row of the cast table
  ([Casts](./language.md#casts)), for example an integer or a float cast to `bool`; or a tensor constructor
  `tensor(e, dtype: D)` where the table gives no cast from the element type of `e` to `D`
  ([Tensor operations](./language.md#tensor-operations)); or a cast to a tensor type
  ([Tensor literals](./shapes.md#tensor-literals)).
- **Required context**: the type of `e`, the type `T` and the location, with the fix: for a cast to `bool`,
  the comparison `e != 0`.
- **Example**: `E2016: no cast from 'i64' to 'bool'; write 'x != 0' at line 2, column 13`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2016`.

### E2026: Numeric scalar used as a known struct

- **Implementation status**: released in v0.10.3 (compiler `24897697`) for
  inferred bindings and reassignment; see [struct literal bindings](./types.md#struct-literal-bindings).
- **Trigger**: a provably numeric scalar is used where a locally declared
  struct is required, including replacement of a known struct binding.
- **Required context**: the binding, declared struct name and offending value
  span. Construct a struct value instead. A same-struct replacement must not
  be diagnosed as scalar narrowing.
- Unknown types do not establish known struct identity. General structural
  compatibility checking remains outside this diagnostic's implemented scope.

### E2032: Unsupported slice call ABI

- **Implementation status**: implemented in the reference compiler v0.10.3; see the
  [slice call boundary](./types.md#slice-call-implementation-boundary).
- **Trigger**: unsupported slice layout, a call argument without proven
  compatible dynamic-array provenance, or a slice/array result that is not
  proven on every required path, or the scalar result of `set` assigned back
  to an owned array (`xs = xs.set(index, value)`, see the
  [slice call boundary](./types.md#slice-call-implementation-boundary)).
  Explicit slice-typed local bindings are also outside the current lowering
  boundary.
- **Required context**: the affected declaration, argument, or result; the
  unsupported layout or missing provenance; and a source span. The compiler
  refuses before artifact emission.

### E2033: Borrowed slice capability violation

- **Implementation status**: implemented in the reference compiler v0.10.3.
- **Trigger**: read-only mutation, ownership operations, capability erasure,
  escape through a non-slice parameter or return, or a slice-containing
  aggregate or struct field.
- **Required context**: the binding or operation, the capability being lost or
  operation being attempted, and its source span. A declared slice return may
  preserve a compatible slice capability. The compiler preserves borrowed
  capabilities through branch and loop joins.

The reference checker does not provide general lifetime inference or mutable-alias
exclusivity analysis; those guarantees remain future work.

### E2036: Non-integer value stored into a narrow integer element

- **Implementation status**: implemented in the reference compiler v0.10.3;
  additive Core v1 catalog entry targeted for specification 1.7.0. It does not
  declare that release. Reference compiler
  commit `0a8b34a5`, merged with
  [compiler PR #263](https://github.com/star-ga/mind/pull/263) at `1833f095`;
  see [record identity implementation coverage](./types.md#implementation-coverage).
- **Trigger**: an indexed assignment whose destination element type, after
  resolving type aliases, is `i8`, `u8`, `i16` or `u16`, and whose right-hand
  side is proven not to be an integer value. That is either a known
  non-integer scalar class (for example a float literal, a float-typed
  binding, a float-returning call, or a cast to a float type) or an opaque
  handle: a string, a declared struct value, a value of an array, tuple,
  generic, slice, reference, tensor, raw-pointer or function-pointer type, or
  an array, tuple, struct, map or set literal, or a reference expression.
  `bool` counts as an integer class.
- **Required context**: the assigned value's span and guidance to use an
  explicit numeric conversion.
- **Scope**: best effort. A right-hand side whose type the checker cannot
  establish is admitted, and integer right-hand sides, including integer
  aliases and integer values outside the element's range, are not diagnosed by
  this rule. The reference resolves module-local `type` aliases when it builds
  the element types of struct fields; a destination whose element type is
  written as an alias elsewhere, such as in a parameter annotation, is
  classified by its written spelling and is admitted. The reference runs the
  check only in builds with the `std-surface` feature, which is a default
  feature. An indexed destination whose array, fixed-array or slice type the
  checker cannot establish is not checked, and the check runs only inside
  function bodies. Struct-field arrays and parameters typed as a fixed array,
  `array<T>` or a slice are checked; a local `let` fixed-array binding
  initialised from an array literal (for example
  `let xs: [u8; 4] = [0, 0, 0, 0]`) is not recorded, so a store into it is not
  checked. The compiler controls `fixed_array_narrow_assignment_types` and
  `fixed_array_struct_field_run` cover struct-field arrays only.
- The rule refuses a proven opaque handle instead of truncating it to the cell
  width; a handle the checker cannot prove is not covered.
- **Example**: `E2036: a narrow integer array element cannot store a proven non-integer or opaque-handle value; use an explicit numeric conversion`

### E2037: Function name used as a value

- **Implementation status**: implemented in the reference compiler v0.10.3;
  additive Core v1 catalog entry targeted for specification 1.7.0. It does not
  declare that release. Reference compiler
  commit `1def5dde`; the rule does not depend on the `cross-module-imports`
  feature, and without the default `std-surface` feature
  (`--no-default-features`) the function-only standard-surface names are not
  collected, so only the module's own functions are classified. Its only
  controls, in `cross_module_enum_variant_lowering`, are compiled with the
  `mlir-build` and `cross-module-imports` features on a unix host.
- **Trigger**: a bare identifier in value position whose only meaning is a
  function of the current module or a function-only standard-surface export.
  Function values are not part of the executable subset. A function type
  `fn(T) -> U` written in a Core v1 source has the same code: it is the type of a
  function value ([Type formation](./types.md#type-formation), DN-59). Member-access
  receivers such as `sha256.hash(...)` are not affected.
- **Required context**: the function name and the source location of the
  reference.
- **Limit**: the reference classifies identifiers only inside function bodies;
  a module-level `const` or `let` initializer is not checked by this rule. A
  function name that resolves only through another project module's exports is
  not classified by the reference, which does not report `E2037` for it.
- **Check/build**: the reference refuses the build rather than lowering the
  module.
- **Example**: ``E2037: `null` is a function, not a value: first-class functions are not yet supported``

### E2042: Predeclared name taken by a declaration or a binding

- **Trigger**: a declaration or a binding that takes a predeclared name: a user type named like a predeclared type
  or bound name (`struct String { }`), and a binding or a declaration named `Some`, `None`, `Ok` or `Err`
  (`let None = 1;`, DN-67)
- **Required context**: the name, its location and what it names
- **Example**: `E2042: 'None' is a predeclared variant and cannot name a binding at line 2, column 9`

### E2300: Collection mutation in expression position

- **Implementation status**: implemented in the reference compiler v0.10.3.
- **Trigger**: a `push` on a container that stands neither as a statement nor in the update
  `xs = xs.push(value)` of the same place: a nested expression, a call argument, a condition, a match
  value or guard, or the initializer or right side of another binding
  ([Changing a container](./memory.md#changing-a-container)). The arguments of an allowed push are still
  checked for nested violations. Separate result-type rules still apply, so assigning the
  scalar result of `set` back to an array is `E2032`.
- **Required context**: the mutating call, its collection receiver, a source span, and guidance to write the push as a
  statement or as the update of the same place. The decision is type-aware, so an equally named user-defined method on a
  non-collection receiver is not refused.
- **Check/build contract**: checking and artifact-producing builds MUST refuse
  the same source with `E2300`; a refused build MUST terminate as a user error
  and leave no artifact.

### E2301: Non-final enum-variant binding collision

- **Implementation status**: implemented in the reference compiler v0.10.3.
- **Trigger**: an unguarded bare-identifier match arm occurs before the final
  arm and its identifier collides with a registered enum variant or with the
  name of a `const` item in scope (DN-22). Such an arm is neither a qualified
  discriminant test nor a valid final catch-all; for a `const`, the fix is
  `n if n == K`.
- **Required context**: the colliding identifier and source span, with guidance
  to qualify the variant, rename the binding, or move a catch-all binding to
  the final arm. A wildcard arm remains valid under first-match semantics.
- **Check/build contract**: checking and artifact-producing builds MUST refuse
  the same source with `E2301`; a refused build MUST terminate as a user error
  and leave no artifact.

### E2310: Refutable pattern in a binding

- **Trigger**: the pattern of a `let` or of a `for` is refutable: it is not a name, `_`, or a tuple or a record
  pattern whose parts are all irrefutable ([Patterns and match](./language.md#patterns-and-match)), as in
  `let Some(x) = o;` and `for 0 in xs { }`. A predeclared variant name taken by a binding (`let None = 1;`) is
  [`E2042`](#e2042-predeclared-name-taken-by-a-declaration-or-a-binding)
- **Required context**: the pattern and its location, and help text that names `match`
- **History**: the draft [RFC 0025](../../design/rfcs/0025-patterns.md) gives this code to the same fault (rule 3)
- **Example**: ``E2310: the pattern of a `let` must match every value; to test one case, write `match` at line 3, column 9``

### E2311: Match not exhaustive

- **Trigger**: a `match` that does not cover every value of its operand ([Patterns and match](./language.md#patterns-and-match))
- **Required context**: one missing case, chosen by a fixed order: the variants in declaration order, `false` before
  `true`, the least uncovered integer
- **Example**: ``E2311: `match` does not cover `false` at line 1, column 30``

### E2312: Arm that no value can reach

- **Trigger**: a match arm that no value can reach, because an earlier arm matches every value it matches; this
  includes every arm after an unguarded bare binding arm, and a bare unguarded binding arm that is not the last arm
  and whose name is not the name of an enum variant or of a `const` item in scope (that arm is
  [`E2301`](#e2301-non-final-enum-variant-binding-collision))
- **Required context**: the arm, its location and the earlier arm
- **History**: the draft [RFC 0025](../../design/rfcs/0025-patterns.md) named this fault the warning `W2312`; DN-36
  makes it this error.
- **Example**: `E2312: this arm is never reached: the arm at line 2, column 9 matches every value, at line 3, column 9`

### E2313: Alternatives that bind different names

- **Trigger**: an or-pattern `p | q` whose alternatives do not bind the same names with the same types, or a
  pattern that binds one name twice
- **Required context**: the pattern, the name and the two alternatives
- **Example**: ``E2313: `x` is bound in one alternative and not in the other at line 3, column 9``

### E2314: Final binding arm that names a variant or a constant

- **Trigger**: an unguarded bare-identifier arm that is the last arm and whose name is the name of an enum variant or
  of a `const` item in scope (DN-22)
- **Required context**: the name and its location, with the fix: the variant pattern `E::A`, the guard
  `n if n == K`, or another name for the binding
- **Example**: ``E2314: `K` names a constant; to compare, write `n if n == K` at line 3, column 9``

### E2401: Loop exit outside a loop

- **Trigger**: a `break` or a `continue` that is not inside the body of a `while`, a `for` or a `loop`
  ([Loop exits](./language.md#loop-exits)).
- **Required context**: the word and its source location, with the fix: move the statement into the body of a
  loop, or remove it.
- **Example**: `E2401: 'break' is not inside a loop at line 2, column 5`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2401`.

### E2402: Invalid target of a change

- **Trigger**: an assignment, a compound assignment, or a method call that changes a container, whose left
  operand or receiver is not a place, or is a place whose root name is not declared with `let mut`: a name that a
  `let` without `mut`, a parameter, the pattern of a `for` or the pattern of a `match` arm binds
  ([Bindings and assignment](./language.md#bindings-and-assignment),
  [Changing a container](./memory.md#changing-a-container)).
- **Required context**: the left operand or the receiver, the location of the assignment or of the call and, for
  a place, the location of the binding of its root, with the fix: declare the root with `let mut`, or change a
  place.
- **Also**: a place whose root is a `const` item, and the target of a compound assignment that is not a place.
- **Example**: `E2402: cannot assign to 'x', which is not declared with 'let mut', at line 3, column 5`;
  `E2402: cannot change 'xs' by 'push': 'xs' is not declared with 'let mut', at line 3, column 5`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2402`.

### E2403: Invalid entry function

- **Trigger**: the entry function `main` has a parameter, or a result type other than `i64` and `unit`
  ([Entry function](./language.md#entry-function)); or a build of an executable from a module with no top-level
  `main` ([Module level](./language.md#module-level)).
- **Required context**: the location of `main`, the parameter or the result type that is not allowed, and the
  fix: no parameter, and the result type `i64` or `unit` (written or omitted).
- **Example**: `E2403: the entry function 'main' must return i64 or unit, found 'f64' at line 1, column 14`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2403`.

### E2404: Invalid tuple index

- **Trigger**: a tuple index `e.N` where the type of `e` is not a tuple type, or where `N` is not less than the
  number of elements of the tuple; or an index operator `e[i]` where the type of `e` is a tuple type
  ([Tuple index](./language.md#tuple-index)); or a tuple index `N` that is not `0` or a digit 1 to 9 followed by
  digits (`t.01`, `t.1_0`).
- **Required context**: the expression, its type and the location, with the fix: an index `e.N` with `N`
  from 0 to the number of elements minus 1, written with `.` for a tuple.
- **Example**: `E2404: a tuple is indexed with '.N', not '[i]': write 't.0' at line 3, column 12`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2404`.

### E2405: No loop statement

- **Status**: withdrawn by DN-54: `loop B` is a form of the language and `loop` is a keyword
  ([Loops](./language.md#loops)). This entry keeps the history; the code is never reused.
- **Trigger (before DN-54)**: where a statement can start, the name `loop` directly followed by `{` (the form
  `loop { ... }`), which no rule of the grammar derives. Core v1 has no `loop` statement
  ([Loop exits](./language.md#loop-exits)).
- **Required context**: the location of `loop`, with the fix: the form `while true { ... }`.
- **Example**: `E2405: Core v1 has no 'loop' statement; write 'while true { ... }' at line 2, column 5`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2405`.

### E2406: Range index

- **Status**: withdrawn by DN-47: `..` stands only in the header of a `for` loop, and `a[1..3]` has no derivation, so
  it is [`E1101`](#e1101-unexpected-token) with the slice form in the message ([Loops](./language.md#loops)). This
  entry keeps the history; the code is never reused.
- **Trigger (before DN-47)**: an index operator whose index is two expressions with `..` between them (the form `a[1..3]`),
  which no rule of the grammar derives. The slice forms are `a[s:e:k]` and its forms with omitted parts
  ([Tuple index](./language.md#tuple-index)).
- **Required context**: the index expression and its location, with the fix: the slice form, for example
  `a[1:3]`.
- **Example**: `E2406: a range is not an index; write the slice 'a[1:3]' at line 3, column 15`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2406`.

### E2407: Struct with no layout

- **Trigger**: a struct that holds itself ([Type formation](./types.md#type-formation)), which has no size; or a
  struct with the attribute `#[repr(C)]` that has a field whose type has no layout in
  [Struct layout attribute](./ffi.md#struct-layout-attribute) (for example `unit`, a tuple or a tensor).
- **Required context**: the struct, the field and its type, with the fix: for a struct that holds itself, a field
  that does not hold the struct; for a `#[repr(C)]` struct, a field type of that list.
- **Example**: `E2407: field 'b' of repr(C) struct 'Q' has the type '(i32, i32)' with no layout at line 4, column 5`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2407`.

### E2408: Literal out of range

- **Trigger**: an integer literal whose value is outside the range of its type, or a floating-point literal whose
  value, rounded to its type, is greater in magnitude than the largest finite value of that type
  ([Type of a literal](./types.md#type-of-a-literal)).
- **Required context**: the literal, its type and its location, with the fix: a literal in the range of the type,
  or another type.
- **Example**: `E2408: the literal 3000000000 is outside the range of i32 at line 2, column 18`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2408`.

### E2409: Callee is not a function

- **Trigger**: a call `x(args)` whose name `x` resolves to a value that is not a function, such as a binding or a
  parameter (`let f = 1; f(2)`); Core v1 has no function values
- **Required context**: the name, what it resolves to, and the location of the call
- **Example**: ``E2409: `f` is a value of the type `i64`, not a function, at line 2, column 12``

### E2410: No such method

- **Trigger**: a method call `x.m(args)` whose `m` is not a method of the type of `x`
  ([Field access and method calls](./language.md#field-access-and-method-calls)): `5.nosuchmethod()`
- **Required context**: the method name, the type of `x` and the location
- **Example**: ``E2410: no such method `nosuchmethod` on `i64` at line 1, column 30``

### E2501: Raw memory use outside a raw memory function

- **Trigger**: a raw memory use in the body of a function that is not declared with `#[raw_memory]` or
  `#[raw_memory(sealed)]` ([Raw memory](./memory.md#raw-memory)): a call of a raw memory function, except in a
  function of the standard library; or a region block, that is where a statement can start the name `region`
  directly followed by `{` ([Region blocks](./memory.md#region-blocks)), also in a function of the standard
  library and also where an implementation does not provide region blocks; not in the body of a function whose
  attribute `raw_memory` `E2502` refuses, which gets the one code `E2502`.
- **Required context**: the called function or the region block, its location and the function that holds it, with the
  fix: declare that function with `#[raw_memory]`, or with `#[raw_memory(sealed)]` when no parameter and no result of it
  carries an address.
- **Example**: `E2501: '__mind_load_i64' is raw memory; mark 'read_at' with #[raw_memory] at line 2, column 12`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2501`.

### E2502: Invalid attribute

- **Trigger**: an attribute whose name this specification does not define, a defined attribute at a position
  that its definition does not give, or a defined attribute with an argument form that its definition does not
  give ([Attributes](./language.md#attributes)). It holds for every attribute: `raw_memory`
  ([Raw memory](./memory.md#raw-memory)), `repr` ([Struct layout attribute](./ffi.md#struct-layout-attribute))
  and `requires` ([Versioning](./versioning.md)).
- **Required context**: the attribute, its location and the item after it, with the fix: an attribute that this
  specification defines, at a position and with an argument form that its definition gives.
- **Also**: an attribute whose name has one segment and that the attribute table of
  [Attributes](./language.md#attributes) does not list for its item kind and argument form (`#[fast]`,
  `#[repr(packed)]`, `#[test] fn t(x: i64) { }`); an `extern` block with an ABI string other than `"C"`.
- **Example**: `E2502: 'raw_memory' stands only before a function declaration at line 1, column 1`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E2502`.

### E2701: Impl of an undeclared trait

- **Trigger**: an `impl Trait for Type` block names a trait that no `trait` declaration declares.
- **Required context**: the trait name and the source location of the `impl`.
- **Example**: `E2701: Impl of undeclared trait 'Nope' for type 'P' at line 4, column 1`
- **Scope**: the `trait` declaration is not in Core v1 ([Core v1 forms](./core-v1-forms.md)). An implementation
  that accepts `trait` and `impl` blocks MUST use this code for this fault.

### E2702: Duplicate impl

- **Trigger**: two `impl Trait for Type` blocks name the same trait and the same type.
- **Required context**: the trait name, the type name and the source location of the second block.
- **Example**: `E2702: Duplicate impl of trait 'T' for type 'P' at line 12, column 1`
- **Scope**: as for E2701.

### E2703: Method that the trait does not declare

- **Trigger**: an `impl Trait for Type` block defines a method that the trait does not declare.
- **Required context**: the method name, the trait name and the source location of the method.
- **Example**: `E2703: Method 'extra' is not declared in trait 'T' at line 11, column 5`
- **Scope**: as for E2701.

### E2707: Trait method missing from an impl

- **Trigger**: an `impl Trait for Type` block lacks a method that the trait declares.
- **Required context**: the trait name, the type name, the missing method name and the source location of the
  `impl`.
- **Example**: `E2707: Impl of trait 'T' for type 'P' is missing method 'put' at line 8, column 1`
- **Scope**: as for E2701.

### E2720: Duplicate name

- **Trigger**: a second declaration of a name in one namespace: the items of a module (all kinds together), the
  parameters of a function, the fields of a struct, the variants of an enum ([Module level](./language.md#module-level))
- **Required context**: the name, the location of the second declaration, and the first as a related location
- **Example**: `E2720: 'f' is declared twice; the first declaration is at line 1, column 4, at line 3, column 4`

### E2730: Binding that hides a module name

- **Trigger**: a binding that takes the name of an import qualifier or of a module block in scope
  ([Module level](./language.md#module-level))
- **Required context**: the binding, its location and the import or module block that it would hide
- **Example**: `E2730: the binding 'io' hides the import 'io' at line 4, column 9`

### E2731: Path separator after a module

- **Trigger**: `::` after the name of a module: an import qualifier or a module block, as in `m::f()` for the member
  `f` of the module block `m` ([Module level](./language.md#module-level)); `.` follows a module
- **Required context**: the path and its location, with the edit to the dot form (`m.f()`)
- **Example**: ``E2731: `m` is a module; write `m.f()`, not `m::f()` at line 8, column 12``

## E3xxx: Shape errors

Shape errors occur during shape inference, broadcasting, or shape validation.

### E3001: Broadcasting failure
- **Trigger**: Shapes incompatible for broadcasting: the operands of a dotted operator (`.+`, `.-`, `.*`, `./`, `.%`)
  or the batch dimensions of `matmul` ([Elementwise binary](./shapes.md#elementwise-binary))
- **Required context**: operand shapes, failing dimension index, extents at failing dimension
- **Example**: `E3001: Broadcasting failed at dimension 1: shape [3, 4] incompatible with [3, 5]`

### E3002: Rank mismatch
- **Trigger**: Operation requires specific rank(s)
- **Required context**: operation name, expected rank(s), actual rank, source location
- **Example**: `E3002: MatMul requires rank ≥ 2, found rank 1 at line 30, column 8`

### E3003: Dimension mismatch
- **Trigger**: Specific dimensions don't match when required (e.g., MatMul K dimension)
- **Required context**: operation, dimension name, expected extent, actual extent
- **Example**: `E3003: MatMul contracting dimension mismatch: lhs[-1]=5, rhs[-2]=6 at line 22, column 10`

### E3004: Invalid axis
- **Trigger**: Axis index out of range for tensor rank
- **Required context**: operation, axis value, tensor rank, source location
- **Example**: `E3004: Sum axis 3 out of range for rank-3 tensor at line 15, column 20`

### E3005: Duplicate axis
- **Trigger**: Reduction or reshape specifies same axis multiple times
- **Required context**: operation, axis list, duplicate axis
- **Example**: `E3005: Sum has duplicate axis 1 in axes [0, 1, 1] at line 12, column 15`

### E3006: Negative dimension
- **Trigger**: a shape that contains a negative dimension
  ([Tensor ranks and shapes](./shapes.md#tensor-ranks-and-shapes)), or a fixed array type `[T; n]` whose
  length `n` is negative ([Fixed-array literal cardinality](./types.md#fixed-array-literal-cardinality)); a
  dimension or a length of 0 is valid, and the marker `-1` of a reshape is not a dimension; a negative dimension that
  is known only at run time makes the [defined stop](./memory.md#the-defined-stop), whose diagnostic names this code
- **Required context**: shape, invalid dimension index, value
- **Example**: `E3006: Invalid dimension -1 in shape [3, -1, 5] at line 18, column 10`

### E3007: Element count mismatch
- **Trigger**: Reshape preserves element count but new shape has different product, or a reshape whose marker `-1`
  cannot be computed because another entry of the new shape is 0 ([Shape manipulation](./ir.md#shape-manipulation))
- **Required context**: original shape, new shape, original count, new count
- **Example**: `E3007: Reshape element count mismatch: [2, 3] (6 elements) to [2, 4] (8 elements) at line 10, column 5`

### E3008: Invalid permutation
- **Trigger**: Transpose permutation invalid (wrong length, duplicate indices, out of range)
- **Required context**: permutation, tensor rank, specific violation
- **Example**: `E3008: Transpose permutation [0, 2, 2] has duplicate axis 2 for rank-3 tensor at line 20, column 8`

### E3009: Squeeze dimension not 1
- **Trigger**: Squeeze attempted on dimension with extent ≠ 1
- **Required context**: axis, actual extent, tensor shape
- **Example**: `E3009: Squeeze axis 1 has extent 3, must be 1 in shape [2, 3, 1] at line 14, column 12`

### E3010: Invalid shape in literal
- **Trigger**: Tensor literal shape doesn't match declared shape, or a ragged literal, whose nested lists at one depth
  have different lengths ([Tensor literals](./shapes.md#tensor-literals))
- **Required context**: declared shape, inferred shape from data
- **Example**: `E3010: Tensor literal shape mismatch: declared [2, 3], inferred [2, 2] at line 8, column 10`

### E3011: Index outside its axis
- **Trigger**: an index, or a slice bound, outside its axis that is an integer literal with its sign, with or
  without parentheses around it (one pair or more), where the type gives the extent of the axis
  ([Index bounds](./ir.md#index-bounds)); no other index or bound
- **Required context**: the index or the bound, the extent of the axis, source location
- **Example**: `E3011: index 4 is outside the axis of extent 4 at line 3, column 12`
- **Check/build contract**: checking and artifact-producing builds MUST refuse the same source with `E3011`.

### E3012: Shape too large
- **Trigger**: a dimension, or the count of elements of a shape, above 2^63 - 1
  ([The tensor type](./shapes.md#the-tensor-type))
- **Required context**: the shape and its location
- **Example**: `E3012: the shape [9223372036854775808] is larger than 2^63 - 1 at line 1, column 21`

### E3013: Unknown dimension name
- **Trigger**: an identifier in a shape that does not name a `const` of the type `i64` in scope
  ([The tensor type](./shapes.md#the-tensor-type))
- **Required context**: the name and its location
- **Example**: `E3013: 'N' in a shape is not a const of the type i64 at line 1, column 22`

### E3014: Too many index items
- **Trigger**: an index of a tensor with more items than the rank of the tensor, or an index of an array with more
  than one item ([Indexing a tensor](./shapes.md#indexing-a-tensor))
- **Required context**: the index, the rank and the location
- **Example**: `E3014: 3 index items for a tensor of rank 2 at line 1, column 45`

### E3015: Plain operator on two shapes
- **Trigger**: a plain operator `+`, `-`, `*`, `/` or `%` on two tensors of different shapes
  ([Tensor operators and broadcasting](./language.md#tensor-operators-and-broadcasting), DN-81)
- **Required context**: the operator and its location, the two shapes, and the edit to the dotted operator
- **Example**: ``E3015: `*` on the shapes [3, 1] and [1, 4] does not broadcast; write `col .* row` at line 2, column 16``

### E3016: Dotted operator with no expansion
- **Trigger**: a dotted operator `.+`, `.-`, `.*`, `./` or `.%` that expands no operand: its operands are two tensors
  of one shape, or one operand is a scalar, or no operand is a tensor
  ([Tensor operators and broadcasting](./language.md#tensor-operators-and-broadcasting), DN-81)
- **Required context**: the operator and its location, and the edit to the plain operator
- **Example**: ``E3016: `.+` expands no operand here; write `a + b` at line 2, column 14``

## E4xxx: Verification errors

Verification errors occur during IR verification before execution or optimization.

### E4001: SSA violation (use before definition)
- **Trigger**: Operand ValueId references undefined or future value
- **Required context**: instruction index, operand ValueId, definition ValueId (if exists)
- **Example**: `E4001: Instruction 10 uses %15 before definition (defined at instruction 20)`

### E4002: SSA violation (multiple definitions)
- **Trigger**: Same ValueId defined more than once
- **Required context**: ValueId, first definition location, second definition location
- **Example**: `E4002: ValueId %12 defined multiple times: instruction 8 and instruction 15`

### E4003: Undefined output
- **Trigger**: Module output references ValueId that doesn't exist
- **Required context**: output index, ValueId
- **Example**: `E4003: Output 2 references undefined ValueId %42`

### E4004: Invalid input declaration
- **Trigger**: Input instruction has invalid metadata (missing name, invalid dtype/shape)
- **Required context**: input index, specific issue
- **Example**: `E4004: Input 0 missing required 'name' attribute`

### E4005: Constant verification failure
- **Trigger**: ConstTensor data doesn't match declared dtype/shape
- **Required context**: ValueId, declared dtype/shape, data issue
- **Example**: `E4005: ConstTensor %5 element count mismatch: shape [2, 3] requires 6 elements, found 5`

### E4006: Index list length mismatch
- **Trigger**: Index operation index list length doesn't match tensor rank
- **Required context**: ValueId, tensor rank, index list length
- **Example**: `E4006: Index %10 has 2 indices for rank-3 tensor`

### E4007: Slice parameters length mismatch
- **Trigger**: Slice starts/ends/steps have different lengths or don't match rank
- **Required context**: ValueId, tensor rank, starts/ends/steps lengths
- **Example**: `E4007: Slice %8 starts/ends/steps length mismatch: 3/3/2 for rank-3 tensor`

### E4008: Invalid slice step
- **Trigger**: Slice step is zero; a negative step that is known only at run time makes the
  [defined stop](./memory.md#the-defined-stop), whose diagnostic names this code
- **Required context**: ValueId, dimension, step value
- **Example**: `E4008: Slice %10 has zero step at dimension 1`

### E4009: Conv2d channel mismatch
- **Trigger**: Conv2d input channels don't match filter channels
- **Required context**: ValueId, input channels, filter channels
- **Example**: `E4009: Conv2d %15 channel mismatch: input.shape[3]=16, filter.shape[2]=32`

### E4010: Conv2d invalid strides
- **Trigger**: Conv2d strides not length 2 or contain non-positive values
- **Required context**: ValueId, strides value
- **Example**: `E4010: Conv2d %20 invalid strides [1, 0]: must be length 2 with positive values`

### E4011: Gather invalid indices dtype
- **Trigger**: Gather indices tensor has non-integer dtype
- **Required context**: ValueId, indices dtype
- **Example**: `E4011: Gather %12 indices have dtype f32, must be i32 or i64`

## E5xxx: Autodiff errors

Autodiff errors occur during gradient computation.

### E5001: Unsupported operation
- **Trigger**: Operation lacks derivative rule
- **Required context**: operation name, ValueId
- **Example**: `E5001: Autodiff unsupported operation 'CustomOp' at %25`

### E5002: Gradient verification failure
- **Trigger**: Generated gradient module fails IR verification
- **Required context**: specific verification error from E4xxx
- **Example**: `E5002: Gradient module verification failed: E4001 at instruction 15`

### E5003: Invalid axis in gradient
- **Trigger**: Reduction gradient has axis out of range
- **Required context**: operation, axis value, shape
- **Example**: `E5003: Sum gradient invalid axis 4 for shape [2, 3, 4]`

### E5004: Unsupported shape in gradient
- **Trigger**: Broadcasting or reduction shape not supported by autodiff engine
- **Required context**: operation, shapes involved
- **Example**: `E5004: Autodiff cannot compute gradient for broadcast [1, 5] → [3, 4, 5]`

### E5005: Non-differentiable input
- **Trigger**: Attempted to differentiate with respect to non-differentiable type
- **Required context**: ValueId, type
- **Example**: `E5005: Cannot differentiate with respect to i32 tensor at %10`

## E6xxx: Runtime and artifact-production errors

E6xxx errors occur during backend execution or while producing a runnable artifact.

### E6001: Out-of-bounds index
- **Trigger**: at run time, an index or a slice bound outside its axis ([Index bounds](./ir.md#index-bounds)), or
  an index function of the standard library with an index outside its container
  ([Library functions that check](./memory.md#library-functions-that-check)); the program makes the
  [defined stop](./memory.md#the-defined-stop)
- **Required context**: operation, indices, tensor shape
- **Example**: `E6001: Index out of bounds: [2, 5] for shape [3, 4]`

### E6002: Backend unavailable
- **Trigger**: Requested backend not available (e.g., GPU in CPU-only build)
- **Required context**: requested backend, available backends
- **Example**: `E6002: Backend 'Gpu' unavailable, available: [Cpu]`

### E6003: Unsupported operation on backend
- **Trigger**: Backend doesn't implement operation
- **Required context**: operation name, backend
- **Example**: `E6003: Operation 'Conv2d' not supported on backend 'Cpu'`

### E6004: Allocation failure
- **Trigger**: Failed to allocate tensor (out of memory, size too large)
- **Required context**: requested shape/dtype, backend, available memory (if applicable)
- **Example**: `E6004: Failed to allocate tensor [10000, 10000, f32] on Gpu: out of memory`

### E6005: Numeric overflow
- **Trigger**: no operation of Core v1: integer overflow wraps in two's complement
  ([Numeric precision](./stdlib.md#numeric-precision)), and a floating-point overflow gives an infinity (IEEE 754)
- **Required context**: operation, operands (summary), result

### E6006: Invalid numeric value
- **Trigger**: no operation of Core v1: a floating-point operation gives the value that IEEE 754 gives, NaN and the
  infinities included ([Exponential and logarithmic](./stdlib.md#exponential-and-logarithmic))
- **Required context**: operation, operands (summary)

### E6007: Execution timeout
- **Trigger**: Operation exceeded allowed execution time
- **Required context**: operation, timeout limit
- **Example**: `E6007: Operation 'MatMul' exceeded timeout of 30s`

### E6008: Device error
- **Trigger**: Device-specific error (GPU kernel failure, driver error)
- **Required context**: device, operation, device-specific error code
- **Example**: `E6008: GPU kernel failed for Conv2d: CUDA error 77 (illegal memory access)`

### E6009: Compiler materialization refusal
- **Trigger**: Compiler-side aggregate expansion exceeds a deterministic
  materialization limit, its accounting overflows, or an accepted aggregate
  operation has no valid representation in the runnable lowering ABI (including
  a nested `[Struct; N]` element-field receiver)
- **Required context**: the exceeded resource and attempted/limit values, or
  the unsupported/invalid lowering operation and source location
- **Artifact contract**: Compilation MUST terminate with a non-zero status and
  MUST NOT publish a partial runnable artifact
- **Example**: `E6009: Compiler materialization payload 2097160 bytes exceeds limit 2097152`

### E6010: Invalid manifest export
- **Trigger**: A `Mind.toml [exports] c_abi` entry is empty, exceeds the
  manifest export bound, or is not a C-style identifier
- **Required context**: the invalid entry and the validation reason
- **Artifact contract**: Compilation MUST terminate with a non-zero status;
  this user configuration error MUST NOT be classified as backend capability
- **Example**: ``E6010: invalid Mind.toml [exports] c_abi entry `bad name`: export name must be ASCII alphanumeric or underscore``

## Diagnostic requirements

All error messages MUST include:

1. **Error code**: The E-code from this catalog
2. **Message**: Human-readable description
3. **Source location**: File, line, column (when applicable)
4. **Context**: Specific values mentioned in "Required context" above

A message shows source text in backticks, writes "end of file" at the end of the input, and names a character
that does not print as `U+XXXX` with its Unicode name; it never shows an internal form of an implementation, such as
`Some('x')` or `Ident("A")`. A form that a later edition specifies gets one message that names its status. An item
form inside a block is refused at its first word, and a fault at module level says "expected an item".

Implementations SHOULD provide:

- **Suggestion**: How to fix the error (when applicable)
- **Note**: Additional explanatory information
- **Related locations**: Secondary locations involved in the error

### Error message format

Recommended format for CLI output:

```text
error[E3001]: Broadcasting failed at dimension 1
  --> src/model.mind:42:15
   |
42 |     let z = x + y;
   |               ^ shape [3, 4] incompatible with [3, 5]
   |
   = note: operand shapes: x=[3, 4], y=[3, 5]
   = help: ensure dimension 1 has extent 4 or 1 in both operands
```

### Programmatic error representation

Implementations SHOULD provide structured error data suitable for tooling:

```rust
// Not MIND source: the shape of the error data of an implementation, written in Rust
pub struct CompilerError {
    pub code: ErrorCode,        // E.g., E3001
    pub message: String,
    pub span: SourceSpan,       // File, line, column range
    pub severity: Severity,     // Error, Warning, Note
    pub context: HashMap<String, Value>,
    pub related: Vec<RelatedInfo>,
}
```

The record of a diagnostic whose code has the fix class EXACT or TYPED also carries its edit: the start and the end
of the replaced text and the new text ([Code table](#code-table)). A CHOICE diagnostic carries its two edits in the
fixed order, and a NONE diagnostic carries none.

## Error recovery

Each top-level item gets at most one lexical or syntax diagnostic, at its first fault, and the parser continues at the
next token in column 1 that can start an item ([Diagnostics](./lexical.md#diagnostics)). An item with such a fault
gets no type diagnostic, and no other item gets a diagnostic whose cause is a name of that item. Implementations MAY
attempt error recovery to report multiple type errors, but MUST NOT:

- Execute IR after verification failure
- Continue execution after runtime error
- Silently ignore errors

Recovery is ONLY permitted for type errors during compilation to improve diagnostics.

## Stability guarantees

Error codes in this catalog are **stable across Core v1 versions**:

- Adding new error codes is permitted
- Changing error messages is permitted (messages are not part of stability guarantee)
- Renumbering or removing error codes is NOT permitted without major version change; a code that a decision
  withdraws stays in the [code table](#code-table) with its history and is never given another meaning
- Context requirements MAY be expanded but MUST NOT be reduced

## Reference implementation (`star-ga/mind`) (informative)

The headings of this catalog define the codes; this section defines nothing. It lists the codes where the
reference compiler v0.10.4 differs from the catalog, each as a reference gap, measured on 2026-11-25 with the
release binary (`mindc check --no-fmt --no-lint` on a probe source, or the command that the row names).

| Code | Catalog | Measured in the reference | Probe |
|------|---------|---------------------------|-------|
| `E1001` | Invalid UTF-8 sequence | The code of a parse error: ``unexpected `;`, expected an expression`` | `return 1 +;` |
| `E1001` | Invalid UTF-8 sequence | A source with an ill-formed UTF-8 sequence is refused with no code: `stream did not contain valid UTF-8` | the bytes `0xFF 0xFE` in a name |
| `E2015` | No entry; an integer literal where a floating-point type is expected, and the reverse, is `E2001` | The code of that fault: `no implicit int↔float conversion (RFC 0011)` | `let y: f64 = 1;` and `let z: i64 = 1.5;` |
| `E2101` | No entry; a broadcasting failure is `E3001` | The code of a broadcasting failure: ``cannot broadcast shapes (3,4) and (3,5) for `+` `` | `a + b` with `Tensor<f32, [3, 4]>` and `Tensor<f32, [3, 5]>` |
| `E2620` | No entry; a pattern that does not fit its value is `E2001` (DN-36) | The code of that fault: `binder count must match the tuple arity` (measured on 2026-11-26) | `let (a, b, c) = (1, 2);` |
| `E2621` | No entry; an index outside its axis is `E3011` where it is an integer literal and the type gives the extent, and the [defined stop](./memory.md#the-defined-stop) otherwise | The code of a check-time refusal of `xs[2]` after a call that pushes to a copy of the parameter: `index 2 out of bounds for array of length 2` (the measurement of [Decision Notes, part 2](../../design/rfcs/decision-notes-2.md)) | `let xs: Vec<i64> = [1, 2];`, a call that pushes to `let mut w = p;`, then `xs[2]` |
| `E3003` | Dimension mismatch | A `matmul` whose contracting dimensions differ is accepted with no code (exit status 0) | `matmul(a, b)` with `a: Tensor<f32, [2, 3]>` and `b: Tensor<f32, [4, 2]>` |
| `E4001` | SSA violation (use before definition) | The code of an autodiff failure: `function 'f' not found in module (only 'main' is supported)` | `mindc FILE --autodiff --func f --emit-grad-ir` |

No probe of this measurement reached `E3001`, `E4002` or `E4003`: `--autodiff` without `--func` is refused with
no code (`--autodiff requires --func <name>`), and the release binary has the autodiff feature. This list makes
no claim about the codes that it does not name.
