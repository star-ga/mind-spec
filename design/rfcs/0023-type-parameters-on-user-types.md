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
| State | Draft (2026-11-24). Not yet accepted. The specification owner decided the questions of this draft on 2026-11-24 (see [Questions](#questions-for-the-specification-owner)). |
| Number | Provisional. The specification owner assigns the final number. |
| Edition | Core v1.1, one edition together with [RFC 0027](./0027-function-generics.md) and [RFC 0024](./0024-impl-forms.md). The order of the work is free. |
| Changes | `grammar-syntax.ebnf` (replaces `TypeParameters` and `TypeParameter` by the plain `TypeParameterList` on four declarations and unmarks it, adds `TypeArguments` and `TraitRef`), `types.md` (type parameters, instance names; a struct also holds itself through an enum payload and the type arguments of an instance), `errors.md` (five codes: `E2038` to `E2042` assigned to this RFC) |
| Depends on | none. Bounds, supertraits and `where` are in [RFC 0027](./0027-function-generics.md), not here. |
| Related | [RFC 0025](./0025-patterns.md) (record literal), [RFC 0024](./0024-impl-forms.md) (methods of a generic type; `impl` of a trait that has parameters), [RFC 0027](./0027-function-generics.md), [RFC 0026](./0026-module-items.md) (module blocks in a declaration name) |

## Problem

The syntax grammar defines `TypeParameters` on `struct`, `enum`, `trait` and `type`, and type arguments
with several entries on any named type (`IdentifierType = Identifier , [ "<" , TypeList , CloseAngle ]`).
The grammar marks these parts "NOT IN CORE v1", and [Core v1 form status](../../spec/v1.0/core-v1-forms.md) gives
the forms the status Not in Core v1. A program therefore cannot declare a pair, an
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
TypeArguments     = "<" , Type , { "," , Type } , [ "," ] , CloseAngle ;
TraitRef          = Identifier , [ TypeArguments ] ;
```

The `trait` item and the `impl` block are defined by [RFC 0024](./0024-impl-forms.md) in the same edition; the rows
below that declare a trait need that RFC. `TraitRef` is the name of a trait with its arguments.
[RFC 0024](./0024-impl-forms.md) uses it in the head of an `impl`. This draft removes the productions `TypeParameters`
and `TypeParameter` of the current grammar: a type parameter of a declaration is a plain name, and a bound on it is not
part of this edition ([RFC 0027](./0027-function-generics.md) defines the bounds of a function parameter only). The
supertrait list of `TraitDeclaration` (`trait B: A`) is owned by RFC 0027, which adds `[ ":" , TraitBounds ]` to the
`TraitDeclaration` production above. The grammar has no type parameter on a function (`FunctionDeclaration`; the form
`fn f<T>` is an extension, [Core v1 forms](../../spec/v1.0/core-v1-forms.md)); RFC 0027 adds `[ GenericParameters ]` to
`FunctionDeclaration`.

Closing angle: `TypeArguments` ends with `CloseAngle`, so the rule of
[Lexical Structure](../../spec/v1.0/lexical.md#tokens) for the `>` that closes a type-argument list applies to it.
Where a type-argument list is open and the next token starts with `>` (`>>`, `>=` or `>>=`), the first `>` closes the
list and the rest of the token is read again: `Pair<Box<i64>>` ends two lists, and `let p: Box<Box<i64>>= q;` is
derived. `TypeParameterList` ends with the token `>`, as the type parameters of a declaration do in the grammar
today, so the rule does not apply to it: `type X<T>= T;` holds the token `>=` and is not derived. Elsewhere `>>` is
the shift operator.

This RFC adds no type argument in an expression. The type arguments of a record literal are inferred from the
types of its fields; a parameter that the fields do not fix is refused with `E2003` (cannot infer type). A call of
a generic function takes explicit type arguments in the form `f::<A>(x)` of [RFC 0027](./0027-function-generics.md),
or infers them.

## Static rules

1. The names of one `TypeParameterList` MUST be pairwise different. A duplicate is refused with
   `E2039` ("duplicate type parameter").
2. A type parameter is in scope in the declaration that lists it, and nowhere else. It is a type, not a
   value. For a `trait` the scope is the signatures and the constant types of the trait items, its supertrait list
   and the bounds of its associated types ([RFC 0027](./0027-function-generics.md)). A use outside the scope is an
   unknown name (`E2002`).
3. Every type parameter MUST be used in its declaration: in a field type of a `struct`, in a payload type of an
   `enum`, in the right-hand side of a `type`, or, for a `trait`, in a parameter type, a result type or a constant
   type of a trait item, in its supertrait list or in a bound of an associated type. An unused parameter is refused
   with `E2041` ("unused type parameter"). A list that has a duplicate name is refused with `E2039` only.
4. A use of a declared type with parameters MUST give exactly as many type arguments as the declaration has
   parameters. A mismatch is refused with `E2038` ("wrong number of type arguments").
   The same rule applies to a `TraitRef` that names a trait with parameters.
5. A type alias with parameters MUST be applied in full wherever it is used. It is a transparent name: the
   alias and its right-hand side are the same type.
6. A type argument is any `Type`, `unit` included. Aggregate types, arrays and tensors are allowed. A field or a
   payload of type `unit` has size 0 and no storage.
7. A `struct` or `enum` MUST NOT contain itself by value: not directly, and not through the fields, payloads and type
   arguments of other types (a field of type `Option<Node<T>>` in `Node<T>` contains `Node<T>`).
   [Types](../../spec/v1.0/types.md#type-formation) refuses a struct that holds itself with `E2407` ("struct with no
   layout"); this draft extends the meaning of "holds" there to the payloads of an enum and to the type arguments of an
   instance, so a `struct` that contains itself in any of these ways is refused with `E2407`. An `enum` that contains
   itself by value, and a `type` declaration that names itself in its right-hand side, directly or through other aliases
   (`type L = Pair<L, i64>;`), because the replacement of [Instance names](#instance-names) would not end, are refused
   with `E2040` ("declaration contains itself"). A type that holds itself through a pointer comes with a later RFC on an
   owning pointer type. [RFC 0027](./0027-function-generics.md) uses `E2040` for a trait that names itself in its
   supertrait list.
8. A type argument on a type without parameters is refused with the code of rule 4. (The reference
   v0.10.4 accepts `Box<i64>` for a `Box` without parameters; in Core v1 a type argument on a user-declared type
   has the status Not in Core v1.)
9. The built-in types `Option<T>` and `Result<T, E>` follow the same rules, with one and with two parameters. A
   `struct`, `enum`, `type` or `trait` declaration MUST NOT take a predeclared type name: a name of
   `PrimitiveType` (`i32`, `i64`, `f32`, `f64`, `bool`, `unit`), `Tensor`, `Option`, `Result`, or a predeclared
   bound of [RFC 0027](./0027-function-generics.md) (`Numeric`, `Integer`, `Float`). Such a declaration is refused
   with `E2042` ("predeclared type or bound name"). A user type never shadows a predeclared one.

## Instance names

An instance is a generic `struct` or `enum` declaration, or `Option` or `Result`, together with one list of type
arguments. The canonical IR gives each instance a name, and that name is part of the artifact bytes, so its spelling
is normative. An instance name holds characters that no identifier can hold (`<`, `>`, `,`, `(`, `)`, `[`, `]`, `;`,
`.`), so it never equals an identifier of the program. No identifier spelling is reserved for it, in the lexical
chapter or elsewhere.

**Declaration name.** `D(N)` of a declaration `N` is its identifier, preceded by the module path that owns it
and by the names of the module blocks around it ([RFC 0026](./0026-module-items.md)), outermost first, each one
followed by `.`. For a manifest project the module path is the full module path of
[Types](../../spec/v1.0/types.md#module-qualified-type-ownership) (`nested.defs.Color`). A single source without a
project has no module path: `struct Pt` in the block `geo` has `D` = `geo.Pt`. `D` is unique in a program: two
items of one namespace have different names, and the qualified name of a module block never equals the module path
of a module of the project ([RFC 0026](./0026-module-items.md), rule 3). So two different declarations have two
different `D`, and two different instances have two different instance names.

**Aliases and parameters come first.** Before `C` is applied to a type, three kinds of names in it are replaced,
until none is left:

- a type parameter, by its argument of the instance;
- an associated type, by the type that the `impl` gives to it ([RFC 0024](./0024-impl-forms.md));
- an alias: a use of a `type` declaration without parameters, by its right-hand side, and a use `N<A1, …, An>` of a
  `type` declaration with parameters, by its right-hand side in which each parameter is replaced by its argument, as
  for a type parameter.

The replacement ends, because an alias does not name itself (rule 7). An alias is never an instance, and its name
never stands in an instance name: `Twice<i64>` with `type Twice<T> = Pair<T, T>;` is the type `Pair<i64, i64>`
(rule 5), and its spelling is `Pair<i64,i64>`.

**Canonical spelling of a type.** `C(T)` is written without a space, except the one space after `diff`. `T` holds no
alias, type parameter or associated type when `C` is applied:

| Type `T` | `C(T)` |
|----------|--------|
| a primitive type | its name: `i32`, `i64`, `f32`, `f64`, `bool`, `unit` |
| a declared `struct` or `enum` `N` without parameters | `D(N)` |
| `N<A1, …, An>`, an instance of a generic `struct` or `enum`, or of `Option` or `Result` | `D(N)` , `<` , `C(A1)` , `,` … `,` , `C(An)` , `>` (`Option` and `Result` have no module path) |
| a tuple type with the elements `T1, …, Tn`, `n` ≥ 1 | `(` , `C(T1)` , `,` … `,` , `C(Tn)` , `)` |
| `[T; n]` | `[` , `C(T)` , `;` , `n` , `]`, with `n` in decimal digits, without sign, prefix, `_` or leading zero |
| `Tensor<d, [s1, …, sk]>` | `Tensor<` , `d` , `,[` , `s1` , `,` … `,` , `sk` , `]>`, each dimension in decimal digits as for an array, or its identifier |
| `diff T` | `diff` , one space , `C(T)` |

A trailing `,` of the source is not written.

**Instance name.** The instance of `N` with the arguments `A1, …, An` has the name
`D(N)<C(A1),…,C(An)>`, which is `C(N<A1, …, An>)`. Nested arguments nest in the same way. Two uses whose arguments
are the same types after the replacement name one instance. An example:

```text
// Not Core v1: a source in the form that this RFC proposes
struct Box<T> { v: T, }
struct Pair<A, B> { a: A, b: B, }
fn f(p: Pair<Box<i64>, (f64, bool)>) -> i64 { return p.a.v; }
```

has the two instances `Box<i64>` and `Pair<Box<i64>,(f64,bool)>`. [RFC 0027](./0027-function-generics.md) names an
instance of a generic function in the same way (`first<P,P>`), and [RFC 0024](./0024-impl-forms.md) names the items
of an `impl` block with these spellings. A diagnostic writes the source spelling `Pair<Box<i64>, (f64, bool)>`.

With aliases:

```text
// Not Core v1: a source in the form that this RFC proposes
struct Box<T> { v: T, }
struct Pair<A, B> { a: A, b: B, }
type Num = i64;
type Twice<T> = Pair<T, T>;
fn g(b: Box<Num>, c: Box<i64>, d: Box<Twice<Num>>) -> i64 { return b.v + c.v + d.v.a; }
```

has the three instances `Box<i64>`, `Pair<i64,i64>` and `Box<Pair<i64,i64>>`. `Box<Num>` and `Box<i64>` are one
instance, because `Num` is replaced by `i64`. `Twice<Num>` is replaced by `Pair<i64, i64>`, so it is not an instance,
and the names `Num` and `Twice` stand in no instance name.

## Meaning as a desugaring

Every use of a generic type has a plain form. A conforming implementation MAY implement generics in any
way that keeps this equality: a program with generic types and the program in which every instance is
written out as a plain declaration under its instance name have the same behaviour and the same canonical IR
bytes.

```text
// Not Core v1: a source in the form that this RFC proposes
struct Pair<A, B> { a: A, b: B, }
type Twice<T> = Pair<T, T>;
fn first(p: Pair<i64, f64>) -> i64 { return p.a; }
fn both(t: Twice<i64>) -> i64 { return t.a + t.b; }
```

is the written-out form below. In it, `Pair<i64,f64>` is one name, not a use with arguments. The alias `Twice` has
no written-out declaration: its use `Twice<i64>` is replaced by `Pair<i64, i64>` ([Instance names](#instance-names)).
The written-out form is not source text, because an instance name is not an identifier.

```text
// Not Core v1: the written-out form, not source text (a name in it is not an identifier)
struct Pair<i64,f64> { a: i64, b: f64, }
struct Pair<i64,i64> { a: i64, b: i64, }
fn first(p: Pair<i64,f64>) -> i64 { return p.a; }
fn both(t: Pair<i64,i64>) -> i64 { return t.a + t.b; }
```

**Equality test.** The test compares the canonical IR of the generic program with the canonical IR of a plain
source program in which each instance is declared under a fresh identifier, after each instance name in the first
IR is replaced by that identifier. [RFC 0024](./0024-impl-forms.md), [RFC 0026](./0026-module-items.md) and
[RFC 0027](./0027-function-generics.md) use the same test for their written-out forms.

A generic function is instantiated in the same way ([RFC 0027](./0027-function-generics.md)): one plain function for
each distinct list of type arguments.

A `trait` with parameters is a family of signature lists. A trait has no value and no run-time form in Core
v1.1 (`dyn Trait` stays NOT IN CORE v1), so a trait declaration only supplies the signatures that an `impl`
is checked against. The use `Conv<f64>` in the head of an `impl` selects the signatures with `X` replaced by
`f64`, and the `impl` is written out with the item names of [RFC 0024](./0024-impl-forms.md), in which the trait part
is the spelling `Conv<f64>`. A trait with parameters adds no item to the program that the written-out form needs.

## Proposed conformance rows

Rows use the format of [Conformance](../../spec/v1.0/conformance.md#test-format). They are proposals: no compiler
accepts the accept rows today. The codes `E2038` to `E2042` are assigned to this draft, and `E2002` and `E2003` exist.
The fields `category: syntax` and `profile: cpu` are omitted after the first row. The rows that declare a trait write
the signature with the `;` of the grammar. The reference v0.10.4 refuses that form and accepts a trait item without `;`;
the specification owner decided that the form with `;` is the only one ([RFC 0024](./0024-impl-forms.md), question 1).

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
# accept: unit as a type argument
description: "unit is a valid type argument"
input:
  source: |
    struct Box<T> {
        v: T,
    }
    fn f(b: Box<unit>) -> i64 {
        return 1;
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
description: "A parameterised alias that is not applied in full is refused"
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
description: "A generic struct that contains itself by value is refused"
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
  error: { code: E2407, message_contains: "Node" }
```

```yaml
# reject 4b: an alias that names itself
description: "A type alias that names itself in its right-hand side is refused"
input:
  source: |
    struct Pair<A, B> {
        a: A,
        b: B,
    }
    type L = Pair<L, i64>;
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

```yaml
# reject 7: an unused type parameter
description: "A type parameter that no field uses is refused"
input:
  source: |
    struct Tag<T> {
        n: i64,
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2041, message_contains: "unused type parameter" }
```

```yaml
# reject 8: a user type with a predeclared name
description: "A struct with the name of a built-in type is refused"
input:
  source: |
    struct Option {
        v: i64,
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2042, message_contains: "Option" }
```

## Cost for the compiler

| Part | Work | Size |
|------|------|------|
| Front end, parser | `TypeParameterList` after the name of four declarations (the `trait` form is parsed today without it and refuses `<`); `TypeArguments` in a type; the `>>` split. The reference keeps two front ends in step; both change. | small |
| Front end, resolver and checker | scope of a type parameter; arity rule; the unused-parameter rule; the predeclared-name rule; alias expansion; inference of the arguments of a record literal and of a generic function from a struct argument; the new codes | medium |
| Front end, desugaring | instance collection and the instance names of this RFC; one pass before lowering, shared by the MLIR path and the native path | medium |
| Native lowering | none after the pass above. The native backend refuses `struct`, `enum` and `type` items today (`lane.source.top_level`); it MUST admit plain `struct` and `enum` first, and that work is a prerequisite and a separate item. | large (prerequisite) |
| Tests | accept and reject rows above; a parity row for the desugaring (the equality test above); a determinism row for the instance order and the instance names | small |

The desugaring is the oracle for the equality test. No other oracle is needed for the parser rows.

## Questions for the specification owner

### Decided by the specification owner (2026-11-24)

1. **Edition.** RFC 0023 and [RFC 0027](./0027-function-generics.md) land in one edition, Core v1.1. The order of
   the work is free. [RFC 0024](./0024-impl-forms.md) is in the same edition.
2. **`unit` as an argument.** `unit` is allowed as a type argument. A field or payload of type `unit` has size 0
   and no storage (rule 6).
3. **Instance names.** An instance name is formed with characters that no identifier can hold. The scheme is
   normative, because the name is part of the artifact bytes ([Instance names](#instance-names)). No spelling is
   reserved in the lexical chapter. An alias, with or without parameters, is replaced by its right-hand side applied to
   its arguments before the scheme is applied, as a type parameter is; an alias is never an instance.
4. **Recursive types.** Containment by value stays refused (rule 7): a struct with `E2407` of
   [Types](../../spec/v1.0/types.md#type-formation), an enum and an alias with `E2040`. A type that holds itself
   through a pointer comes with a later RFC on an owning pointer type.
5. **Marker parameters.** An unused type parameter is refused with `E2041` (rule 3).
6. **Codes.** `E2038` (wrong number of type arguments), `E2039` (duplicate type parameter), `E2040`
   (declaration contains itself: an enum by value or an alias in its right-hand side here, a trait in its own
   supertrait list in RFC 0027; a struct that holds itself keeps `E2407` of the catalog), `E2041`
   (unused type parameter) and `E2042` (predeclared type or bound name) are assigned to this draft.
   The published catalog does not define any of them.
7. **Defaults and const parameters.** There are no defaults (`struct Box<T = i64>`). Const parameters (`[T; N]`
   with a named `N`) get their own RFC, because shapes need them.
8. **Name of a user type equal to a built-in.** A user type with the name of a built-in type is refused with
   `E2042` (rule 9). It does not shadow the built-in type.

### Open

- **The empty tuple type.** The grammar derives the type `()` (`TupleType` without elements). Whether it is the
  type `unit` is not decided, so [Instance names](#instance-names) gives no spelling for it.
- **Instances across source modules.** Which source module's IR holds an instance whose declaration and arguments
  come from different source modules is not decided. The instance name itself does not depend on it.
