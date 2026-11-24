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
the status of a form follows from the grammar. If this table and the grammar differ, the grammar decides.

- **Core v1**: the grammar derives the form and does not mark it.
- **Not in Core v1**: the grammar derives the form and marks it "NOT IN CORE v1". A conforming implementation
  refuses it or documents it as an extension.
- **Extension**: the grammar does not derive the form. Core v1 neither requires it nor forbids it. A program
  that uses it is not a Core v1 program.
- **Open**: the grammar derives the form and no sentence of this specification gives it a meaning.

| Form | Status |
|------|--------|
| `fn name(params) -> T { }`, `type X = T;`, `struct S { f: T, }`, `import a.b;`, `export f;` | Core v1 |
| `Tensor<dtype, [dims]>`, `(T, U)`, `[T; n]`, `diff T` | Core v1 |
| `let x = e;`, `let x: T = e;`, `let _ = e;`, `let (a, b) = e;` | Core v1 |
| `return e;`, `return;`, `defer { }`, `a = b;`, `a += b;` | Core v1 |
| `break`, `continue` in the body of a loop ([Loop exits](./language.md#loop-exits)) | Core v1 |
| `if a > b { } else { }`, `while c { }`, `for v in xs { }`, `match e { x => y, }` | Core v1 |
| `t[i]`, `t[a:b]`, `f(x)`, `x.m(a)`, `tensor(e)`, `tensor(e, dtype: f64)`, `(a, b)`, `[a, b]` | Core v1 |
| String escapes `\n \r \t \0 \\ \' \"` and `\u{HEX}` ([String escapes](./language.md#string-escapes)) | Core v1 |
| `trait T { }` | Not in Core v1 |
| `type X<T> = T;`, `struct S<T> { }` | Not in Core v1 |
| `P<A, B>` as a type, where `P` is a user-declared type | Not in Core v1 |
| `(T) -> U` as a type, `dyn Trait` as a type | Not in Core v1 |
| `fn(x: T) -> U { }` as an expression | Not in Core v1 |
| `let mut x = e;`, `loop { }`, `for i in a..b { }` | Extension |
| `fn f<T>(x: T) -> T { }`, `import a.b as c;` | Extension |
| `module m;`, `pub fn f() { }`, `impl S { }` | Extension |
| `break`, `continue` outside the body of every loop | Open |
