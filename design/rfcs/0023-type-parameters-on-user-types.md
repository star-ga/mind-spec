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

# RFC 0023: Type parameters on `struct`, `enum`, `trait` and `type`, and type arguments on user types

| Field | Value |
|-------|-------|
| State | Draft (2026-11-24). Not yet accepted. |
| Number | Provisional. The specification owner assigns the final number. |
| Changes | `grammar-syntax.ebnf` (replaces `TypeParameters` and `TypeParameter` by the plain `TypeParameterList` on four declarations and unmarks it, adds `TypeArguments` and `TraitRef`), `types.md`, `errors.md` (three new codes, `E2038` to `E2040`) |
| Depends on | none. Bounds, supertraits and `where` are in [RFC 0027](./0027-function-generics.md), not here. |
| Related | [RFC 0025](./0025-patterns.md) (record literal), [RFC 0024](./0024-impl-forms.md) (methods of a generic type; `impl` of a trait that has parameters), [RFC 0027](./0027-function-generics.md) |

## Problem

The syntax grammar defines `TypeParameters` on `struct`, `enum`, `trait` and `type`, and type arguments
with several entries on any named type (`IdentifierType = Identifier , [ "<" , TypeList , ">" ]`).
[Core v1 form status](../../spec/v1.0/core-v1-forms.md) marks these forms NOT IN CORE v1, because
the reference compiler v0.10.4 does not implement them. A program therefore cannot declare a pair, an
optional value, a result with two types or a container of its own element type. The standard library
has `Option<T>` and `Result<T, E>`, and no user can write a type of the same kind.

Measured with the reference compiler v0.10.4 (`mindc check --no-fmt`):

| Source | Result |
|--------|--------|
| `struct Box<T> { v: T, }` | `E1001`, ``expected `{` after struct name`` (1:11) |
| `struct Pair<A, B> { a: A, b: B, }` | `E1001`, same text (1:12) |
| `enum Opt<T> { Some1(T), None1, }` | `E1001`, ``expected `{` after enum name`` (1:9) |
| `type Wrap<T> = T;` | `E1001`, ``expected `=` in type alias`` (1:10) |
| `trait T<X> { }` | `E1001`, ``expected '{', found Some('<')`` (1:8) |
| `trait T<X, Y> { }` | `E1001`, same text (1:8) |
| `fn f(b: Box<i64>)` with `struct Box { v: i64, }` | accepted without a check of the argument |
| `fn f(r: Result<i64, i64>)` | accepted (built-in type) |

## Grammar change

Replace `TypeParameters` of the four declarations by a list of plain names. A bound is not part of this
RFC. The grammar of the other forms is unchanged.

```ebnf
StructDeclaration = "struct" , Identifier , [ TypeParameterList ] , "{" , [ FieldList ] , "}" ;
EnumDeclaration   = "enum"   , Identifier , [ TypeParameterList ] , "{" , [ EnumVariantList ] , "}" ;
TypeDeclaration   = "type"   , Identifier , [ TypeParameterList ] , "=" , Type , ";" ;
TraitDeclaration  = "trait"  , Identifier , [ TypeParameterList ] , "{" , { TraitItem } , "}" ;

TypeParameterList = "<" , Identifier , { "," , Identifier } , [ "," ] , ">" ;

IdentifierType    = Identifier , [ TypeArguments ] ;
TypeArguments     = "<" , Type , { "," , Type } , [ "," ] , ">" ;
TraitRef          = Identifier , [ TypeArguments ] ;
```

The `trait` item stays marked NOT IN CORE v1 until [RFC 0024](./0024-impl-forms.md) is accepted; the rows below
that declare a trait are valid together with that RFC. `TraitRef` is the name of a trait with its arguments. [RFC 0024](./0024-impl-forms.md) uses it in the head of
an `impl`. This draft removes the productions `TypeParameters` and `TypeParameter` of the current grammar: a
type parameter of a declaration is a plain name, and a bound on it is not defined (the bound of a function
parameter is in [RFC 0027](./0027-function-generics.md)). The supertrait list of `TraitDeclaration` (`trait B: A`)
is owned by RFC 0027, which adds `[ ":" , TraitBounds ]` to the `TraitDeclaration` production above; `TraitBounds`
and `TraitBound` stay marked NOT IN CORE v1 until RFC 0027 is accepted. `FunctionTypeParameters` (one unbounded
name) is unchanged here; RFC 0027 widens it.

Lexing: the token `>>` ends two nested argument lists in `Pair<Box<i64>>`. A parser MUST split `>>` into two
`>` tokens while it reads `TypeArguments` or `TypeParameterList`. Elsewhere `>>` is the shift operator.

There is no syntax for an explicit type argument in an expression. The type arguments of a generic
function call and of a record literal are inferred.

## Static rules

1. The names of one `TypeParameterList` MUST be pairwise different. A duplicate is refused with
   `E2039` ("duplicate type parameter"), a code reserved for this draft.
2. A type parameter is in scope in the declaration that lists it, and nowhere else. It is a type, not a
   value. For a `trait` the scope is the signatures of the trait items. A use outside the scope is an
   unknown name (`E2002`).
3. A type parameter MAY be unused in the declaration (a marker type). It then cannot be inferred and the
   program MUST name it with an annotation.
4. A use of a declared type with parameters MUST give exactly as many type arguments as the declaration has
   parameters. A mismatch is refused with `E2038` ("wrong number of type arguments"), a code reserved for this draft.
   The same rule applies to a `TraitRef` that names a trait with parameters.
5. A type alias with parameters MUST be applied in full wherever it is used. It is a transparent name: the
   alias and its right-hand side are the same type.
6. A type argument is any `Type` except `unit`. Aggregate types, arrays and tensors are allowed.
7. A struct or enum MAY NOT contain itself by value, with or without arguments. Indirect containment
   waits for a reference type RFC. A violation is refused with `E2040` ("type contains
   itself"), a code reserved for this draft. [RFC 0027](./0027-function-generics.md) uses the same code for a
   trait that is its own supertrait.
8. A type argument on a type without parameters is refused with the code of rule 4. (The reference
   v0.10.4 accepts `Box<i64>` for a `Box` without parameters; Core v1 would refuse it.)
9. The built-in types `Option` and `Result` follow the same rules. A user type MUST NOT take the name of a
   built-in type in the same module.

## Meaning as a desugaring

Every use of a generic type has a plain form. A conforming implementation MAY implement generics in any
way that keeps this equality: a program with generic types and the program in which every instance is
written out as a plain declaration have the same behaviour and the same canonical IR bytes.

```mind
struct Pair<A, B> { a: A, b: B, }
type Twice<T> = Pair<T, T>;
fn first(p: Pair<i64, f64>) -> i64 { return p.a; }
fn both(t: Twice<i64>) -> i64 { return t.a + t.b; }
```

is the program

```mind
struct Pair__i64__f64 { a: i64, b: f64, }
struct Pair__i64__i64 { a: i64, b: i64, }
fn first(p: Pair__i64__f64) -> i64 { return p.a; }
fn both(t: Pair__i64__i64) -> i64 { return t.a + t.b; }
```

The instance name is the declaration name, then one `__` and the canonical spelling of each argument
(`i64`, `f64`, a nested instance in the same form), joined by `__`. Two uses with equal arguments name one
instance. The instance names are not visible to the user: a diagnostic writes the source spelling
`Pair<i64, f64>`. A user identifier that contains `__` is refused when it could collide with an instance
name (open question 3).

A generic function whose parameter types name a generic type is instantiated in the same way, one plain
function for each distinct set of inferred arguments.

A `trait` with parameters is a family of signature lists. A trait has no value and no run-time form in Core
v1 (`dyn Trait` stays NOT IN CORE v1), so a trait declaration only supplies the signatures that an `impl`
is checked against. The use `Conv<f64>` in the head of an `impl` selects the signatures with `X` replaced by
`f64`, and the `impl` is written out with the canonical names of [RFC 0024](./0024-impl-forms.md), in which
the trait name is the instance name `Conv__f64`. A trait with parameters adds no item to the program that
the written-out form needs.

## Proposed conformance rows

Rows use the format of [Conformance](../../spec/v1.0/conformance.md#test-format). They are proposals: no
compiler accepts the accept rows today. The codes `E2038`, `E2039` and `E2040` are reserved for this draft; `E2002` exists. The fields `category: syntax`
and `profile: cpu` are omitted after the first row. The rows that declare a trait write the signature with the `;`
of the grammar. The reference v0.10.4 refuses that form and accepts a trait item without `;`; the draft keeps the
grammar (see [RFC 0024](./0024-impl-forms.md), open question 1).

```yaml
# accept: two instances of one declaration, a nested use and an alias
description: "A struct with two type parameters, used with two argument lists"
category: syntax
profile: cpu
input:
  source: |
    struct Pair<A, B> {
        a: A,
        b: B,
    }
    type Twice<T> = Pair<T, T>;
    fn first(p: Pair<i64, f64>) -> i64 {
        return p.a;
    }
    fn both(t: Twice<i64>) -> i64 {
        return t.a + t.b;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: success
```

```yaml
# reject 1: too few arguments
description: "A use of Pair with one argument is refused"
input:
  source: |
    struct Pair<A, B> {
        a: A,
        b: B,
    }
    fn f(p: Pair<i64>) -> i64 {
        return 0;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2038, message_contains: "type arguments" }
```

```yaml
# reject 2: duplicate parameter name
description: "Two type parameters with the same name are refused"
input:
  source: |
    struct Same<T, T> {
        a: T,
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2039, message_contains: "duplicate type parameter" }
```

```yaml
# reject 3: an alias used without its arguments
description: "A parametrised alias that is not applied in full is refused"
input:
  source: |
    type Wrap<T> = T;
    fn f(x: Wrap) -> i64 {
        return 0;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2038, message_contains: "type arguments" }
```

```yaml
# reject 4: self containment by value
description: "A struct that contains itself by value is refused"
input:
  source: |
    struct Node<T> {
        v: T,
        next: Node<T>,
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2040, message_contains: "contains itself" }
```

```yaml
# accept: a trait with a type parameter (declaration only; the impl rows are in RFC 0024)
description: "A trait with one type parameter that appears in a signature"
input:
  source: |
    trait Conv<X> {
        fn conv(a: i64) -> X;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: success
```

```yaml
# reject 5: a trait parameter used outside the trait
description: "The parameter of a trait is not in scope outside the trait"
input:
  source: |
    trait Conv<X> {
        fn conv(a: i64) -> X;
    }
    fn f(a: X) -> i64 {
        return 0;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2002, message_contains: "X" }
```

```yaml
# reject 6: duplicate trait parameter
description: "Two type parameters of a trait with the same name are refused"
input:
  source: |
    trait Bad<X, X> {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2039, message_contains: "duplicate type parameter" }
```

## Cost for the compiler

| Part | Work | Size |
|------|------|------|
| Front end, parser | `TypeParameterList` after the name of four declarations (the `trait` form is parsed today without it and refuses `<`); `TypeArguments` in a type; the `>>` split. The reference keeps two front ends in step; both change. | small |
| Front end, resolver and checker | scope of a type parameter; arity rule; alias expansion; inference of the arguments of a generic function from a struct argument; the new code | medium |
| Front end, desugaring | instance collection and the canonical instance name; one pass before lowering, shared by the MLIR path and the native path | medium |
| Native lowering | none after the pass above. The native lane refuses `struct`, `enum` and `type` items today (`lane.source.top_level`); it MUST admit plain `struct` and `enum` first, and that work is a prerequisite and a separate item. | large (prerequisite) |
| Tests | accept and reject rows above; a parity row for the desugaring (the generic program and its written-out form give equal bytes); a determinism row for the instance order | small |

The desugaring is the oracle for the equality test: the bytes of the generic program equal the bytes of
the written-out program. No other oracle is needed for the parser rows.

## Open questions for the specification owner

1. **Bounds and traits.** This RFC takes the plain parameter list for `trait` too. Bounds on function
   parameters, supertraits and `where` are in [RFC 0027](./0027-function-generics.md); a bound on a parameter of a
   `struct`, `enum`, `type` or `trait` is in no draft (RFC 0027, open question 2). This RFC has no operation on a `T` other than
   moving it (field access, passing, returning). Arithmetic on a `T` needs a bound. Should RFC 0027 be
   accepted before this one, so that both land in one edition?
2. **`unit` and zero-size types** as an argument: rule 6 refuses `unit`. Keep or allow?
3. **Instance names.** The `__` rule reserves a spelling. Reserve it in the lexical chapter, or mangle with a
   character that no identifier can contain?
4. **Recursive types** (rule 7): when does indirect containment arrive, and with which type?
5. **Marker parameters** (rule 3): allow, or refuse an unused parameter?
6. **Code allocation (settled).** The specification owner reserved `E2038` (wrong number of type arguments),
   `E2039` (duplicate type parameter) and `E2040` (type contains itself) for this draft.
7. **Defaults** (`struct Box<T = i64>`) and **const parameters** (`[T; N]` with a named `N`): out of scope here;
   the owner decides whether to open a later RFC.
8. **Name of a user type equal to a built-in** (rule 9): refuse (proposed) or shadow?
