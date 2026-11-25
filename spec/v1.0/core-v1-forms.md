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

**Reference verdict (informative).** The mark "reference gap" after a status records that the reference
compiler v0.10.4 does not yet follow the status, the mark "reference conforms" records that it follows the
status for the sources measured, and the words in parentheses say what was measured. The release binary was run
on 2026-11-25 with `mindc check --no-fmt --no-lint` on each probe source, and with `mindc build --backend native`
and a run of the image where the mark names the native backend or an image. A gap is work for the compiler; it
does not change the status. A row without a mark makes no claim about the reference.

| Form | Status |
|------|--------|
| `fn name(params) -> T { }`, `type X = T;`, `struct S { f: T, }`, `import a.b;`, `export f;` | Core v1 |
| `fn main() -> i64 { }`, `fn main() { }`, `fn main() -> unit { }` ([Entry function](./language.md#entry-function)) | Core v1; reference gap (the native backend refuses `fn main() -> unit` with `lane.type.named`, and the image of `fn main() { let x = 1; }` exits with the status 1, and with 7 for `let x = 7;`, not 0) |
| `fn main() -> f64 { }`, `fn main(n: i64) -> i64 { }`: an entry function with another result type or a parameter | Core v1 refuses; reference gap (`mindc check` accepts both) |
| `Tensor<dtype, [dims]>`, `(T, U)`, `[T; n]`, `diff T` | Core v1 |
| `struct N { next: N, }`, and `struct A { b: B, }` with `struct B { a: A, }`: a struct that holds itself ([Type formation](./types.md#type-formation)) | Core v1 refuses; reference gap (`mindc check` accepts both) |
| `let x = e;`, `let x: T = e;`, `let _ = e;`, `let (a, b) = e;`, `let mut x = e;` | Core v1 |
| `let x = 1; let x = 2;`: a later `let` of the same name is a new binding ([Bindings and assignment](./language.md#bindings-and-assignment)) | Core v1; reference conforms (`mindc check` accepts it, and the image of `let x = 1; let x = 2; return x;` exits with the status 2) |
| `return e;`, `return;` | Core v1 |
| `defer { }` (no sentence of this specification gives a `defer` statement a meaning) | Open |
| `defer { };`: a `;` after the block of a `defer` ([Block-like statements](./language.md#block-like-statements)) | Core v1 refuses; reference gap (`mindc check` accepts it) |
| `a = b;`, `a += b;`, `a -= b;`, `a *= b;`, `a /= b;`, `a[i] = b;`, `t.0 = b;` where the root of the place is bound by `let mut` ([Bindings and assignment](./language.md#bindings-and-assignment)) | Core v1; reference gap (the native backend refuses `a[i] = b;` with `lane.source.index_store` and `t.0 = b;` as a struct field assignment) |
| `a %= b;`, `a <<= b;`, `a >>= b;`, `a &= b;`, `a \|= b;`, `a ^= b;` where the root of `a` is bound by `let mut` | Core v1; reference gap (the native backend builds `%=` and refuses the other five) |
| An assignment or a compound assignment to a place whose root is not declared with `let mut` (a `let` without `mut`, a parameter, a `for` pattern or a `match` arm binds it) | Core v1 refuses; reference gap (`mindc check` accepts `let x = 1; x = 2;`, `x += 1` on such an `x`, `let a = [1, 2, 3]; a[0] = 5;`, and an assignment to a parameter, to a `for` variable and to a `match` arm binding) |
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
| `break` or `continue` where the grammar needs a name or an expression: `let break = 4;`, `let continue = 1;`, `break - 1;`, `break = 5;` (`break` and `continue` are keywords, [Loop exits](./language.md#loop-exits)) | Core v1 refuses; reference gap (`mindc check` accepts `let break = 4;` and `let continue = 1;`, and the image of `let break = 4; return break;` exits with the status 4; in a loop it reads `break - 1;` as the loop exit; it refuses `break = 5;` with `E1001`) |
| `loop { }` where a statement can start: the name `loop` directly followed by `{` ([Loop exits](./language.md#loop-exits)) | Core v1 refuses; reference gap (`mindc check` accepts it; with an empty block the native build also builds it, and the image runs on past it: `loop { } return 7;` exits with the status 7) |
| `let loop = false; while loop { } return 3;`: in every other place `loop` is a name, here the condition of a `while` ([Loop exits](./language.md#loop-exits)) | Core v1; reference gap (`mindc check` refuses it with `E1001`, "expected '{', found Some('r')") |
| A missing `;` after a `let`, a `return`, a loop exit (`while c { break }`) or an expression statement; a missing `,` after an expression arm of a `match` ([Statement separators](./language.md#statement-separators)) | Core v1 refuses; reference gap (`mindc check` accepts a missing `;` after a `let`, an expression statement, a `return` and a loop exit, and a missing `,`; it reads `while c { break }` as the loop exit) |
| `if a > b { } else { }`, `match e { x => y, }`, `match e { x => { y } }` | Core v1 |
| `t[i]`, `f(x)`, `x.m(a)`, `tensor(e)`, `tensor(e, dtype: f64)`, `(a, b)`, `[a, b]` | Core v1 |
| `(o.unwrap_or)(0)` on an `Option<i64>`: a field access whose name is not a field of the type, then a call ([Field access and method calls](./language.md#field-access-and-method-calls)) | Core v1 refuses; reference gap (`mindc check` accepts it) |
| `t[a:b]`, the slice form ([Tuple index](./language.md#tuple-index)) | Core v1; reference gap (`mindc check` refuses `let b = a[1:3];` on the array `[1, 2, 3, 4]` with `E1001`, "expected `]` to close index expression") |
| `a[:e2]`, `a[e1:]`, `a[:]`, `a[e1:e2:e3]`: an omitted start is 0, an omitted end is the length of the axis, and an omitted step is 1 ([Tuple index](./language.md#tuple-index)) | Core v1; reference gap (`mindc check` refuses each of `a[:2]`, `a[1:]`, `a[:]` and `a[0:4:2]` with `E1001`) |
| `a[0:4:0]`: a slice with the step 0 ([Indexing and slicing](./ir.md#indexing-and-slicing)) | Core v1 refuses; reference gap (`mindc check` refuses it with `E1001`, "expected `]` to close index expression", not with `E4008`) |
| `t.0`, `t.0.1` on a tuple ([Tuple index](./language.md#tuple-index)) | Core v1; reference gap (the native backend refuses tuples with `lane.source.tuple`) |
| `t.0.1e0` (a float literal with an exponent after an access dot, [Tuple index](./language.md#tuple-index)) | Core v1 refuses; reference conforms (`mindc check` refuses it with `E2002`, as the unknown identifier `e0`) |
| `x.0` where `x` is not a tuple, `t.N` with `N` not less than the number of elements, `t[0]` on a tuple | Core v1 refuses; reference gap (`mindc check` accepts all three) |
| `a[1..3]` (a range index) | Core v1 refuses; reference gap (`mindc check` accepts it) |
| `()`, the value of type `unit` ([The unit value](./types.md#the-unit-value)) | Core v1; reference gap (the native backend refuses it with `lane.source.tuple`) |
| `()` where another type is expected (`let n: i64 = ();`) | Core v1 refuses; reference gap (`mindc check` accepts it, also as an argument for an `i64` parameter) |
| `a % b` on two `f32` or two `f64` operands ([Floating-point remainder](./language.md#floating-point-remainder)) | Core v1; reference gap (the native backend refuses it with `lane.type.mismatch`) |
| `a % b` and `a %= b` with an `f32` and an `f64` operand ([Floating-point remainder](./language.md#floating-point-remainder)) | Core v1 refuses; reference gap (`mindc check` accepts both) |
| The precedence of `as`: `a * b as f64` is `a * (b as f64)` ([Operator precedence](./language.md#operator-precedence-and-associativity)) | Core v1 |
| `e as T` for a pair of types of the cast table ([Casts](./language.md#casts)) | Core v1; reference gap (the native backend refuses `i64 as i32` and `i32 as i64` with `lane.type.int_width`, `f64 as i32` and `f64 as f32` with `lane.source.cast`, and `f32 as f64` with `lane.type.non_f64_float`) |
| A cast that the table does not list (`1 as bool`, `true as f64`, `x as Option<i64>> z`) | Core v1 refuses; reference gap (`mindc check` accepts `true as f64` and `x as Option<i64>> z`; it refuses a cast to `bool` with `E2016`) |
| `x as i64 < y`: a primitive type name ends the type of a cast, and `<` compares ([Casts](./language.md#casts)) | Core v1; reference conforms (`mindc check` accepts it) |
| `let b = x as Option < y;`: after a type name that is not a primitive type, `<` opens a type-argument list, here one that is not closed ([Casts](./language.md#casts)) | Core v1 refuses; reference gap (`mindc check` accepts it) |
| `a & b`, `a \| b`, `a ^ b` on two operands of the same integer type; `a << c`, `a >> c` with integer operands; `20 - 17 >> 2` is `20 - (17 >> 2)` ([Bitwise and shift operators](./language.md#bitwise-and-shift-operators)) | Core v1; reference gap (the native backend refuses `<<` on `i32` operands, and an `i32` count of an `i64` shift, with `lane.type.int_width`); the `i64` values conform (the native images give `12 & 10` 8, `12 \| 3` 15, `12 ^ 5` 9, `1 << 64` 1, `1 << 65` 2, `40 >> 66` 10, `1 << (0 - 63)` 2, `64 >> (0 - 61)` 8, `(0 - 17) >> 2` -5, `(1 << 63) >> 63` -1, `20 - 17 >> 2` 16 and `6 + 5 & 3` 7) |
| `&`, `\|` or `^` with an `i32` and an `i64` operand; an operand of `&`, `\|`, `^`, `<<` or `>>` that is not of an integer type (`true & false`, `1.5 \| 2.5`, `x << 2` with `x: f64`) | Core v1 refuses; reference gap (`mindc check` accepts all of them; the image of `true & false` builds and exits with the status 0; the native backend refuses the float operands with `lane.type.mismatch` and the mixed widths with `lane.type.int_width`) |
| `let o: Option<Option<i64>>= p;`: the first `>` of `>>=` closes a type argument list ([Tokens](./lexical.md#tokens)) | Core v1; reference gap (the native backend refuses the type `Option<Option<i64>>` with `lane.type.generic`, also with a space before `=`); `mindc check` accepts it |
| `let o: Option<i64>>= p;`: a `>` that closes no open list | Core v1 refuses; reference conforms (`mindc check` refuses it with `E1001`) |
| `a .* b`, `a ./ b`, `a .+ b`, `a .- b`: the elementwise operators, with the operand rule of the arithmetic operators ([Tensor operations](./language.md#tensor-operations)) | Core v1; reference gap (`mindc check` accepts the four on two `i64` scalars; the native backend refuses each with `lane.source.tensor`) |
| `a .* b` with an `f64` and an `i64` operand: operands of two different dtypes | Core v1 refuses; reference gap (`mindc check` accepts it) |
| `tensor([[1, 2], [3, 4]])` (shape `[2, 2]`, dtype `i64`), `tensor(3, dtype: f32)`: the tensor constructor ([Tensor operations](./language.md#tensor-operations)) | Core v1; reference gap (`mindc check` refuses the first with `E2003`, "unsupported call to `tensor`", and the second with `E1001`, "expected ')', found Some(':')") |
| `tensor(true, dtype: f32)` (no cast from `bool` to `f32`), `tensor(true)` (`bool` is not a dtype) | Core v1 refuses; reference gap (`mindc check` refuses the first with `E1001` and the second with `E2003`, not with `E2016` and `E2005`) |
| `1.0^` (a literal with the suffix `^`, [Lexical Structure](./lexical.md#literals)) | Core v1 refuses |
| `fn echo(s: String) -> String { }`, `let t: String = "a";`: the string type `String`, the type of a string literal ([Type formation](./types.md#type-formation)) | Core v1; reference gap (`mindc check` accepts it; the native backend refuses a `String` result with `lane.string.result`) |
| `let n: i64 = "a";`: a string literal where another type is expected | Core v1 refuses; reference gap (`mindc check` accepts it) |
| String escapes `\n \r \t \0 \\ \' \"` and `\u{HEX}` ([String escapes](./language.md#string-escapes)) | Core v1 |
| `trait T { }` | Not in Core v1 |
| `type X<T> = T;`, `struct S<T> { }` | Not in Core v1 |
| `P<A, B>` as a type, where `P` is a user-declared type | Not in Core v1 |
| `(T) -> U` as a type, `dyn Trait` as a type | Not in Core v1 |
| `fn(x: T) -> U { }` as an expression | Not in Core v1 |
| `for i in a..b { }` | Extension |
| `fn f<T>(x: T) -> T { }`, `import a.b as c;` | Extension |
| `module m;`, `pub fn f() { }`, `impl S { }` | Extension |
| `#[repr(C)] struct S { a: i32, }`, `#[requires(mind_spec = "1.2")] module m;`: an attribute before an item that is not a function declaration (`AttributedItem`, which `Module` does not reach; [Attributes](./language.md#attributes)) | Extension |
| `#[raw_memory] fn f(p: i64) -> i64 { }`, `#[raw_memory(sealed)] fn g() -> i64 { }` ([Raw memory](./language.md#raw-memory)) | Core v1; reference gap (`mindc check` accepts both; the native backend refuses an attributed function with `lane.source.function_contract`) |
| A call of a raw memory function in a function without the attribute, outside the standard library (`fn r(p: i64) -> i64 { return __mind_load_i64(p); }`, `vec_addr(v)` in an unmarked `main`, a call of a `#[raw_memory]` function from an unmarked `main`) | Core v1 refuses; reference gap (`mindc check` accepts all three; the native backend builds the first, and its image exits with the status 0) |
| `#[raw_memory] struct S { a: i64, }`, `#[raw_memory(open)] fn f() { }`: the attribute `raw_memory` before another item or with another argument | Core v1 refuses; reference gap (`mindc check` accepts both) |
| `#[fast] fn f() { }`: an attribute name that this specification does not define, before a function declaration ([Attributes](./language.md#attributes)) | Core v1 refuses; reference gap (`mindc check` accepts it) |
