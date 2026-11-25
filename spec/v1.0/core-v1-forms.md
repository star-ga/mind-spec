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

# Core v1 Forms

This chapter lists forms of the surface grammar ([`grammar-syntax.ebnf`](./grammar-syntax.ebnf),
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf)) with the status of each form in Core v1. It adds no rule:
the status of a form follows from the grammar and from the normative chapters that the table links. If this
table and the grammar or a normative chapter differ, the grammar and the chapter decide.

- **Core v1**: the grammar derives the form, does not mark it, and no normative sentence forbids it.
- **Core v1 refuses**: a normative sentence forbids the form, whether the grammar derives it or not. A
  conforming implementation MUST refuse it.
- **Not in Core v1**: the grammar derives the form and marks it "NOT IN CORE v1". A conforming implementation
  refuses it or documents it as an extension.
- **Extension**: the grammar does not derive the form and no normative sentence forbids it. Core v1 neither
  requires it nor forbids it. A program that uses it is not a Core v1 program.
- **Open**: the grammar derives the form and no sentence of this specification gives it a meaning.

**Reference gap (informative).** The mark "reference gap" after a status records that the reference compiler
v0.10.4 does not yet follow the status, and the words in parentheses say what was measured. The release binary
was run on 2026-11-24 with `mindc check --no-fmt --no-lint` on each probe source, and with
`mindc build --backend native` and a run of the image where the mark names the native backend or an image. A gap
is work for the compiler; it does not change the status. A row without the mark makes no claim about the
reference.

| Form | Status |
|------|--------|
| `fn name(params) -> T { }`, `type X = T;`, `struct S { f: T, }`, `import a.b;`, `export f;` | Core v1 |
| `fn main() -> i64 { }`, `fn main() { }`, `fn main() -> unit { }` ([Entry function](./language.md#entry-function)) | Core v1; reference gap (the native backend refuses `fn main() -> unit` with `lane.type.named`, and the image of `fn main() { let x = 1; }` exits with the status 1, and with 7 for `let x = 7;`, not 0) |
| `fn main() -> f64 { }`, `fn main(n: i64) -> i64 { }`: an entry function with another result type or a parameter | Core v1 refuses; reference gap (`mindc check` accepts both) |
| `Tensor<dtype, [dims]>`, `(T, U)`, `[T; n]`, `diff T` | Core v1 |
| `let x = e;`, `let x: T = e;`, `let _ = e;`, `let (a, b) = e;`, `let mut x = e;` | Core v1 |
| `return e;`, `return;`, `defer { }` | Core v1 |
| `a = b;`, `a += b;`, `a -= b;`, `a *= b;`, `a /= b;`, `a[i] = b;`, `t.0 = b;` where the root of the place is bound by `let mut` ([Bindings and assignment](./language.md#bindings-and-assignment)) | Core v1; reference gap (the native backend refuses `a[i] = b;` with `lane.source.index_store` and `t.0 = b;` as a struct field assignment) |
| `a %= b;`, `a <<= b;`, `a >>= b;`, `a &= b;`, `a \|= b;`, `a ^= b;` where the root of `a` is bound by `let mut` | Core v1; reference gap (the native backend builds `%=` and refuses the other five) |
| An assignment or a compound assignment to a place whose root a `let` without `mut`, a parameter or a `for` pattern binds | Core v1 refuses; reference gap (`mindc check` accepts `let x = 1; x = 2;`, `x += 1` on such an `x`, `let a = [1, 2, 3]; a[0] = 5;`, and an assignment to a parameter and to a `for` variable) |
| An assignment whose left operand is not a place (`x + 1 = 3;`) | Core v1 refuses; reference gap (`mindc check` refuses it with `E1001`, not `E2402`) |
| `x := e` (no operator `:=`, [Lexical Structure](./lexical.md#tokens)) | Core v1 refuses |
| `while c { }`, `for v in xs { }`: loops, expressions of the type `unit` ([Loops](./language.md#loops)) | Core v1 |
| A loop as a value (`let u = while c { };`) | Core v1; reference gap (`mindc check` refuses it with `E2002`, as an unknown identifier `while` or `for`) |
| `if c { }`, `match e { }`, a block, `while c { }` and `for v in xs { }` as statements with no `;` ([Block-like statements](./language.md#block-like-statements)) | Core v1; reference gap (`mindc check` refuses a block that holds a statement, `{ s = s + 1; }`, with `E1001`) |
| `while c { };`: a loop with `;` is an expression statement | Core v1; reference gap (the native backend refuses `while c { ... };` as an unsupported construct and builds the same loop without the `;`) |
| `if c { 1 } else { 2 }` and the other forms as the tail of a block; a block as a value (`let b = { let t = 3; t };`) | Core v1; reference gap (`mindc check` refuses a block that holds a statement also as a value, with `E1001`, and the native backend refuses `let b = { 4 };` with `lane.source.set`) |
| A block-like statement that is not the tail and whose type is not `unit` (`if c { 1 } else { 2 } return 0;`) | Core v1 refuses; reference gap (`mindc check` accepts it) |
| `break;`, `continue;` in the body of a loop ([Loop exits](./language.md#loop-exits)) | Core v1 |
| `break;`, `continue;` outside the body of every loop | Core v1 refuses; reference gap (`mindc check` accepts both) |
| `break 'a;`, `continue 'a;` (a label), `break 7;` (a value) | Core v1 refuses; reference gap (`mindc check` accepts `break 7;`) |
| `break - 1;`, `break = 5;`, `while c { break }`: `break` with no `;` directly after it is a name | Core v1; reference gap (`mindc check` reads the loop exit in `break - 1;` and in `while c { break }`, and refuses `break = 5;` with `E1001`) |
| `loop { }`: `loop` is a name, and a block follows it with no `;` | Core v1 refuses; reference gap (`mindc check` accepts it; with an empty block the native build also builds it, and the image runs on past it: `loop { } return 7;` exits with the status 7) |
| A missing `;` after a `let`, a `return`, a loop exit or an expression statement; a missing `,` after an expression arm of a `match` ([Statement separators](./language.md#statement-separators)) | Core v1 refuses; reference gap (`mindc check` accepts a missing `;` after a `let`, an expression statement and a `return`, and a missing `,`) |
| `if a > b { } else { }`, `match e { x => y, }`, `match e { x => { y } }` | Core v1 |
| `t[i]`, `t[a:b]`, `f(x)`, `x.m(a)`, `tensor(e)`, `tensor(e, dtype: f64)`, `(a, b)`, `[a, b]` | Core v1 |
| `t.0`, `t.0.1` on a tuple ([Tuple index](./language.md#tuple-index)) | Core v1; reference gap (the native backend refuses tuples with `lane.source.tuple`) |
| `t.0.1e0` (a float literal with an exponent after `.`) | Core v1 refuses |
| `x.0` where `x` is not a tuple, `t.N` with `N` not less than the number of elements, `t[0]` on a tuple | Core v1 refuses; reference gap (`mindc check` accepts all three) |
| `a[1..3]` (a range index) | Core v1 refuses; reference gap (`mindc check` accepts it) |
| `()`, the value of type `unit` ([The unit value](./types.md#the-unit-value)) | Core v1; reference gap (the native backend refuses it with `lane.source.tuple`) |
| `()` where another type is expected (`let n: i64 = ();`) | Core v1 refuses; reference gap (`mindc check` accepts it, also as an argument for an `i64` parameter) |
| `a % b` on two `f32` or two `f64` operands ([Floating-point remainder](./language.md#floating-point-remainder)) | Core v1; reference gap (the native backend refuses it with `lane.type.mismatch`) |
| `a % b` and `a %= b` with an `f32` and an `f64` operand | Core v1 refuses; reference gap (`mindc check` accepts both) |
| The precedence of `as`: `a * b as f64` is `a * (b as f64)` ([Operator precedence](./language.md#operator-precedence-and-associativity)) | Core v1 |
| `e as T` for a pair of types of the cast table ([Casts](./language.md#casts)) | Core v1; reference gap (the native backend refuses `i64 as i32` and `i32 as i64` with `lane.type.int_width`, `f64 as i32` and `f64 as f32` with `lane.source.cast`, and `f32 as f64` with `lane.type.non_f64_float`) |
| A cast that the table does not list (`1 as bool`, `true as f64`) | Core v1 refuses; reference gap (`mindc check` accepts `true as f64`; it refuses a cast to `bool` with `E2016`) |
| `1.0^` (a literal with the suffix `^`, [Lexical Structure](./lexical.md#literals)) | Core v1 refuses |
| String escapes `\n \r \t \0 \\ \' \"` and `\u{HEX}` ([String escapes](./language.md#string-escapes)) | Core v1 |
| `trait T { }` | Not in Core v1 |
| `type X<T> = T;`, `struct S<T> { }` | Not in Core v1 |
| `P<A, B>` as a type, where `P` is a user-declared type | Not in Core v1 |
| `(T) -> U` as a type, `dyn Trait` as a type | Not in Core v1 |
| `fn(x: T) -> U { }` as an expression | Not in Core v1 |
| `for i in a..b { }` | Extension |
| `fn f<T>(x: T) -> T { }`, `import a.b as c;` | Extension |
| `module m;`, `pub fn f() { }`, `impl S { }` | Extension |
