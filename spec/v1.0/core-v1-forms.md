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

This chapter lists the forms of the surface grammar ([`grammar-syntax.ebnf`](./grammar-syntax.ebnf),
[`grammar-lexical.ebnf`](./grammar-lexical.ebnf)) with the status of each form in Core v1. It adds no rule:
the rules are in the grammar and in the chapters that it names. If this table and the grammar differ, the
grammar decides.

## Status words

| Status | Meaning |
|--------|---------|
| **Core v1** | The grammar defines the form and Core v1 requires it. |
| **Not in Core v1** | The grammar marks the form "NOT IN CORE v1". A conforming implementation refuses it or documents it as an extension. |
| **Extension** | The grammar does not define the form and no normative sentence forbids it. Core v1 neither requires nor forbids it. A program that uses it is not a Core v1 program. |
| **Open** | The text does not decide the meaning of the form. |

The forms of the "v1.1 candidate additions" block of the syntax grammar (`enum`, `const`, `module` blocks, `use`,
attributes, `assert`, `as` and the bitwise operators) keep the status that the block gives: an implementation that
claims v1.0 MAY parse them, and an implementation that claims v1.1 MUST. They are not listed here.

## Declarations

| Form | Status |
|------|--------|
| `fn name(params) -> T { }` | Core v1 |
| `fn name<T>(x: T) -> T` (one type parameter; see [Generics in Core v1](./types.md#generics-in-core-v1)) | Core v1 |
| `fn name<A, B>(...)` (a second type parameter) | Not in Core v1 |
| `fn name<T: Bound>(...)` and a `where` clause | Not in Core v1 |
| `id::<i64>(5)` (an explicit type argument at a call) | Not in Core v1 |
| `fn name<T,>(...)`, `fn name<>(...)` | Extension |
| `fn main() -> f64`, `fn main() { }` | Open |
| `type X = T;` | Core v1 |
| `type X<T> = T;` | Not in Core v1 |
| `struct S { f: T, }` | Core v1 |
| `struct S<T> { ... }`, `enum E<T> { ... }` | Not in Core v1 |
| `trait T { ... }`, `trait T<X> { ... }`, `trait B: A { ... }` | Not in Core v1 |
| `import a.b;`, `export f;` | Core v1 |
| `import a.b as c;`, `use a.b as c;`, `export { f }` | Extension |
| `module m;` | Open |
| `pub fn`, `pub struct`, `pub const`, `pub trait`, `static X: T = e;` | Open |
| `impl T for S { }`, `impl S { }` | Open |

## Types

| Form | Status |
|------|--------|
| `i32`, `i64`, `f32`, `f64`, `bool`, `unit` | Core v1 |
| `Tensor<dtype, [dims]>`, `(T, U)`, `[T; n]` | Core v1 |
| `diff T` | Core v1 |
| `Option<T>`, `Result<T, E>` | Core v1 |
| `(T) -> U` (a function type) in any type position | Not in Core v1 |
| `dyn Trait` in any type position | Not in Core v1 |
| `Name<A, B>` on a user-declared type | Not in Core v1 |
| `tensor<f32[2, 3]>` (lower case), `Tensor<f32>` (no shape), `diff tensor<f64[2]>` | Extension |

## Statements

| Form | Status |
|------|--------|
| `let x = e;`, `let x: T = e;`, `let _ = e;` | Core v1 |
| `let (a, b) = e;`, `let (a, b): (T, U) = e;`, `let ((a, b), c) = e;` | Core v1 |
| `let mut x = e;` | Extension |
| `return e;`, `return;`, `defer { ... }`, `expr;` | Core v1 |
| `break`, `continue` in a loop ([Loop exits](./language.md#loop-exits)) | Core v1 |
| `break`, `continue` outside every loop; `loop { }` | Open |
| `a = b`, `x += e`, `-=`, `*=`, `/=` | Core v1 |
| `x := e` | Open |
| `x %= e`, `<<=`, `>>=`, `&=`, `\|=`, `^=` | Extension |
| A missing `;` after `let` or after an expression statement, a missing `,` after the expression of a `match` arm | Open |

## Expressions

| Form | Status |
|------|--------|
| Integer, float, string and boolean literals | Core v1 |
| `+ - * / %`, comparisons, `&& \|\|`, unary `- !` | Core v1 |
| `1.0^` (a differentiable literal) | Open |
| `if a > b { } else { }`, `else if`, `while c { }` | Core v1 |
| `for v in xs { }`, `for (a, b) in xs { }` | Core v1 |
| `for i in a..b { }` (a range) | Extension |
| `match e { arms }`, `{ e }` and `{ s; e }` as a value | Core v1 |
| `t[i]`, `f(x)`, `x.f`, `x.m(a)`, `t[a:b]` | Core v1 |
| `a[1..3]` (a range index), `t.1` (a tuple index) | Extension |
| `tensor(e)`, `tensor(e, dtype: f64)` | Core v1 |
| `(a, b)`, `[a, b]` | Core v1 |
| `()` | Open |
| `fn(x: T) -> U { }` (a function expression) | Not in Core v1 |
| Patterns `&p` and `x @ p` in a match arm; the guard `p if g` | Open |
| `P { x: 1 }` (a record literal) | Extension |

## Lexical forms

| Form | Status |
|------|--------|
| Decimal, float, string, boolean literals; `0x`, `0b`, `0o` integers; a sign `+` or `-`; `_` inside a digit run | Core v1 |
| The escapes `\n \r \t \0 \\ \' \"` and `\u{HEX}` | Core v1 |
| Line comment `//`, block comment `/* */`, byte order mark, a Unicode identifier | Core v1 |
