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

# RFC 0024: `trait` and `impl` blocks (implementations of a type and of a trait, associated items)

| Field | Value |
|-------|-------|
| State | Draft (2026-11-24). Not yet accepted. The specification owner decided the questions of this draft on 2026-11-24 (see [Questions](#questions-for-the-specification-owner)). |
| Number | Provisional. The specification owner assigns the final number. |
| Edition | Core v1.1, together with [RFC 0023](./0023-type-parameters-on-user-types.md) and [RFC 0027](./0027-function-generics.md). |
| Changes | `grammar-syntax.ebnf` (new `ImplDeclaration` with an optional `TypeParameterList`; unmarks `TraitDeclaration`, `TraitItem` and `FunctionSignature`; associated constants and types; `SelfType`), `lexical.md` and `grammar-lexical.ebnf` (`Self` joins the keyword list; `impl` joins the contextual words), `language.md` (the list of words that the grammar spells out), `types.md` (Traits and generics), `errors.md` (the headings of `E2701`, `E2702`, `E2703` and `E2707` become "Trait name that names no trait that the program declares", "Duplicate or overlapping impl", "Function that the trait does not declare" and "Trait item missing from an impl", and their triggers cover the uses of the [Codes](#static-rules) paragraph; the new codes `E2710` to `E2715`) |
| Depends on | [RFC 0023](./0023-type-parameters-on-user-types.md) (`TraitRef`, `TypeParameterList`, the rules of type parameters and the instance names), in the same edition. |
| Related | [RFC 0023](./0023-type-parameters-on-user-types.md), [RFC 0025](./0025-patterns.md), [RFC 0026](./0026-module-items.md), [RFC 0027](./0027-function-generics.md) (bounds) |

## Problem

The syntax grammar has no production for an `impl` block, and it marks `trait` as NOT IN CORE v1.
[Types](../../spec/v1.0/types.md#traits-and-generics) speaks of trait implementations ("for any type and trait
pair there MAY be at most one implementation in scope") and of "associated functions, types, and laws", and
gives no syntax. The reference compiler v0.10.4 accepts one `impl` form and refuses the other, and it accepts
a trait item only in a spelling that the grammar does not have, so the language has forms that its
specification does not define.

Measured with the reference compiler v0.10.4 (`mindc check --no-fmt`; a `struct P { x: i64, }` is declared):

| Source | Result |
|--------|--------|
| `trait T { fn get(p: i64) -> i64 }` (no `;`) and `impl T for P { fn get(p: i64) -> i64 { … } }` | accepted; the native backend refuses the first item, `lane.source.top_level` |
| the same trait with `fn get(p: i64) -> i64;` | `E1001`, ``expected `fn` method signature in trait body`` |
| `impl P { fn get(p: P) -> i64 { … } }` | `E1001`, ``expected `for` in `impl Trait for Type` `` (5:8) |
| `impl Nope for P { }` (no trait `Nope`) | `E2701`, `` `impl Nope for P`: trait `Nope` is not declared `` |
| two blocks `impl T for P { }` | `E2702`, ``duplicate `impl T for P` `` |
| `impl T for P { fn extra(p: P) -> i64 { … } }` when `T` does not declare `extra` | `E2703`, ``method `extra` is not declared in trait `T` `` (9:5) |
| `impl T for P { }` when `T` has a method that the block lacks | `E2707`, `` `impl T for P` is missing method `put` `` |
| `impl T for P { fn get(p: f64) -> f64 { … } }` when `T` declares `get(p: i64) -> i64` | accepted: the signature is not compared |
| `impl T for Nope { }` (no type `Nope`) | accepted without a diagnostic |
| `fn get(p: Self)` in a trait and in its impl | accepted (`Self` is an unknown type name and is not checked) |
| `impl T for P { fn get(self) -> i64 { … } }` | accepted (an untyped `self` parameter) |
| `trait T { const K: i64; }`, `trait T { type Item; }` | `E1001`, ``expected `fn` method signature in trait body`` (2:5) |
| `impl T for P { const K: i64 = 3; }`, `impl T for P { type Item = i64; }` | `E1001`, ``expected `fn` method in impl body`` (9:5) |
| `get(1)` for a function declared only inside `impl T for P` | `E2003`, ``unsupported call to `get` `` |
| `p.get()` with such a function | accepted |

The codes `E2701`, `E2702`, `E2703` and `E2707` are in the
[Error Catalog](../../spec/v1.0/errors.md#e2701-impl-of-an-undeclared-trait) as a record of the released behaviour. This
RFC specifies the `impl` forms, the trait declaration and the associated items, so that the grammar, the catalog and the
reference agree.

## Grammar change

```ebnf
ModuleItem        = … | TraitDeclaration | ImplDeclaration ;

TraitDeclaration  = "trait" , Identifier , [ TypeParameterList ] , "{" , { TraitItem } , "}" ;
TraitItem         = FunctionSignature | TraitConst | TraitType ;
FunctionSignature = "fn" , Identifier , "(" , [ ParameterList ] , ")" , [ "->" , Type ] , ";" ;
TraitConst        = "const" , Identifier , ":" , Type , ";" ;
TraitType         = "type" , Identifier , ";" ;

ImplDeclaration   = InherentImpl | TraitImpl ;
InherentImpl      = "impl" , [ TypeParameterList ] , IdentifierType , "{" , { ImplItem } , "}" ;
TraitImpl         = "impl" , [ TypeParameterList ] , TraitRef , "for" , Type , "{" , { ImplItem } , "}" ;
ImplItem          = FunctionDeclaration | ImplConst | ImplType ;
ImplConst         = "const" , Identifier , ":" , Type , "=" , Expression , ";" ;
ImplType          = "type" , Identifier , "=" , Type , ";" ;

Type              = … | SelfType | AssociatedType ;
SelfType          = "Self" ;
AssociatedType    = ( "Self" | Identifier ) , "::" , Identifier ;
PrimaryExpression = … | AssociatedValue ;
AssociatedValue   = ( "Self" | Identifier ) , "::" , Identifier ;
```

The lexical grammar adds `"Self"` to `Keyword`, and [Lexical Structure](../../spec/v1.0/lexical.md#keywords) adds
`Self` to the keyword list. It adds `"impl"` to `ContextualWord`: like the item words `const`, `enum`, `module` and
`use`, `impl` is not reserved, and a source is read by the rule of
[Words that the grammar spells out](../../spec/v1.0/language.md#words-that-the-grammar-spells-out), which then lists
`impl` too. Where an item starts, no production derives an `Identifier`, so `impl` there begins an
`ImplDeclaration`, and `let impl = 1;` binds a name.

This RFC unmarks `TraitDeclaration`, `TraitItem` and `FunctionSignature`. The supertrait list of the old
`TraitDeclaration` (`trait B: A`), the trait bounds and the bounds of an associated type are owned by
[RFC 0027](./0027-function-generics.md), which adds `[ ":" , TraitBounds ]` to the `TraitDeclaration` and
`TraitType` productions above, in the same edition. `trait` and `impl` are `ModuleItem`s; a module block
([RFC 0026](./0026-module-items.md)) MAY hold them.

**One trait item form.** A function of a trait is a `FunctionSignature`, which ends with `;`. A trait item without
the `;`, and a trait item with a body or a value, are not derived: a trait has no default items in this edition.

**`Self`.** `Self` is a keyword. Inside a trait declaration it names the type that implements the trait, and inside
an `impl` block it names the type of the block. Outside a trait declaration and an `impl` block, `Self` is refused
with `E2002`. A declaration cannot take the name `Self`, because a keyword is not an identifier.

`Name::Item` has the same spelling as the variant path of an enum ([RFC 0025](./0025-patterns.md)). The
resolver reads it as a variant when `Name` is an enum that has a variant `Item`, and as an associated item
otherwise. An enum with a variant and an associated item of the same name is refused with `E2711`.

`Type` after an inherent `impl` MUST be a user-declared `struct` or `enum` type, or an instance of one
([RFC 0023](./0023-type-parameters-on-user-types.md)).

**Receiver.** A method names its receiver with its first parameter, whose type is `Self` or the type of the block.
There is no `self` keyword: a parameter named `self` is an ordinary parameter and needs a type like any other.

**Generic blocks.** A block MAY declare type parameters: `impl<T> Box<T> { … }`. The rules of
[RFC 0023](./0023-type-parameters-on-user-types.md) apply to the list: the names are pairwise different (`E2039`),
and each name MUST be used in the head of the block, in the type after `impl` or after `for` or in the arguments of
the trait (`E2041`). A parameter is in scope in the head and in the items of the block. A parameter of a block has
no bound in this edition ([RFC 0027](./0027-function-generics.md) defines bounds on the parameters of a function
only), so a value of its type can only be moved. The functions of a generic block are generic functions: their type
parameters are the parameters of the block, then their own, and they are instantiated for each distinct list of
arguments ([RFC 0027](./0027-function-generics.md)).

## Static rules

1. **Method and associated function.** A function of an `impl` block whose first parameter has the type of
   the block (or `Self`) is a method. Another function of the block is an associated function. A method is
   called as `x.m(args)`; an associated function is called as `Type::f(args)`. `x.m(args)` is the method call of the
   grammar (`MethodCallOperator`,
   [Field access and method calls](../../spec/v1.0/language.md#field-access-and-method-calls)), its one derivation;
   `(x.m)(args)` is the call of the value of a field `m` and never calls a method.
2. **Unique names.** Two items of the inherent blocks of one type MUST NOT have the same name. This also holds for
   two generic blocks that have an instance in common (`impl<T> Box<T>` and `impl Box<i64>`). A violation is
   refused with `E2711`. The items of the blocks of a type are named through the type, and they are not items of a
   namespace of [RFC 0026](./0026-module-items.md) (rule 3), so `E2720` does not apply to them.
3. **Trait block.** The block MUST define every function, constant and type that the trait declares, and
   MUST NOT define an item that the trait does not declare. A missing item is refused with `E2707` (the
   reference uses it for a missing method; this RFC extends it to constants and types). An extra function is
   refused with `E2703` (existing). An extra constant or type is refused with `E2714`.
4. **Signatures.** After `Self` is replaced by the type of the block, and each parameter of the trait by its
   argument, a function of the block MUST have the parameter types and the result type of the trait's
   signature. A difference is refused with `E2713`. (The reference accepts a difference today.)
5. **Constants and types.** An associated constant of a block MUST have the type that the trait declares, and
   its value MUST be a constant expression (the rule of `ConstDeclaration`). A wrong type is refused with
   `E2001`. An associated type MAY name any `Type`, `unit` included. A bound on an associated type is defined by
   [RFC 0027](./0027-function-generics.md) in the same edition.
6. **Coherence.** For a trait (with its arguments) and a type there MUST be at most one `impl` in the program,
   and in the modules that it imports ([Types](../../spec/v1.0/types.md#traits-and-generics)). Two generic impls
   also conflict when one instance of the type and of the trait arguments matches both heads. A second one is
   refused with `E2702` (existing).
7. **Names.** The trait named in an `impl` MUST be a trait that the program declares, and it MUST be visible.
   Another name, a predeclared bound of [RFC 0027](./0027-function-generics.md) (`Numeric`, `Integer`, `Float`)
   included, is refused with `E2701` (existing). The type of the block MUST be declared and visible; an unknown type
   is refused with `E2710`. (The reference accepts an unknown type today.) An unknown name elsewhere keeps `E2002`.
   The type of a trait impl is a user-declared `struct` or `enum` type, an instance of one, or a primitive type:
   `impl T for i64` is valid. A bare type parameter of the block (`impl<T> Zero for T`) and any other type (a tuple,
   an array, a tensor, a `diff` type) are refused with `E2710`. The type of an inherent block is a user-declared
   type only.
8. **Resolution.** `x.m(args)` where the type of `x` is `Type` calls the method `m` of the inherent block of
   `Type`, or of the trait impl of `Type` whose trait declares `m`. If both exist, the inherent method wins.
   If two trait impls of `Type` declare `m`, the call is refused as ambiguous (`E2712`).
   `Type::K` and `Type::f(args)` look in the same blocks in the same order, and an ambiguity there is refused with
   `E2712` too. `Self::Item` in a trait signature names the associated type of the implementing type; in a block it
   names the type that the block gives to `Item`.
9. **No dynamic dispatch.** A call is resolved at compile time from the static type of the receiver. `dyn
   Trait` stays NOT IN CORE v1.
10. **Visibility.** A method and an associated item are visible wherever their type is visible: an export of the
    type makes them visible, and an export list does not name them ([RFC 0026](./0026-module-items.md)). An impl of
    a trait for a type MUST stand in a module that declares the trait or the type. For an impl that stands in a
    module block ([RFC 0026](./0026-module-items.md)), the module of this rule is the innermost module block that
    holds the impl; for an impl outside every module block, it is the file module. A declaration counts only for the
    module or the block in which it stands directly: with `trait T` and `struct S` declared outside every block,
    `module m { impl T for S { } }` is refused. A primitive type is declared by no module, so `impl T for i64` stands
    in the module or the block that declares `T`. A violation is refused with `E2715`.

**Codes.** Codes that the reference already uses, now in the catalog: `E2701` (a trait name that names no trait that the
program declares: here the trait of an impl, rule 7; [RFC 0027](./0027-function-generics.md) gives the same code to a
bound, a `where` predicate and a supertrait), `E2702` (duplicate or overlapping impl, rule 6), `E2703` (function that
the trait does not declare, rule 3), `E2707` (trait item missing from an impl: a function, a constant or a type, rule
3). This draft changes the catalog headings of all four so that each heading covers every use: `E2701` "Trait name that
names no trait that the program declares", `E2702` "Duplicate or overlapping impl", `E2703` "Function that the trait
does not declare" (a method or an associated function, rule 1), `E2707` "Trait item missing from an impl". Codes
reserved for this draft by the specification owner: `E2710` unknown or unsupported type in an impl, `E2711` duplicate
name, `E2712` ambiguous method or associated item, `E2713` signature differs from the trait, `E2714` associated constant
or type that the trait does not declare, `E2715` trait impl in a module that declares neither the trait nor the type.
The published catalog does not define `E2715`, so it has no other meaning. Codes of [RFC
0023](./0023-type-parameters-on-user-types.md) that this draft uses: `E2038` (number of type arguments), `E2039`
(duplicate parameter of a block), `E2041` (unused parameter of a block); all three are assigned there.

## Meaning as a desugaring

An `impl` block is a set of top-level items with a canonical name, and a method call is a call of one of
them. Nothing else is added to the Core IR. A trait declaration has no run-time form: it supplies the names and
signatures that rules 3 to 5 check, and it disappears.

**Item names.** The name of an item `item` of an inherent block for `Type` is `C(Type)::item`, where `C` is the
canonical spelling of [RFC 0023](./0023-type-parameters-on-user-types.md#instance-names): `P::get`, and
`Box<i64>::get` for the instance `Box<i64>` of a generic block. The name of an item of a trait impl is
`C(Type)::C(Trait)::item`, where `C(Trait)` is `D(Trait)` with the trait arguments in the same form:
`P::Conv<f64>::conv` for the function `conv` of `impl Conv<f64> for P`. An item name holds `::`, which no identifier
holds, so it never equals a name of the program; an inherent name has one `::` and a trait impl name has two.
A function of an inherent block that has type parameters of its own ([RFC 0027](./0027-function-generics.md)) has one
instance for each list of its own arguments, named by the item name followed by those arguments in the form of
[RFC 0023](./0023-type-parameters-on-user-types.md#instance-names): `Box<i64>::map<f64>` for `fn map<U>` of
`impl<T> Box<T>` with `T` = `i64` and `U` = `f64`. A function of a trait impl has no type parameters of its own,
because a `FunctionSignature` has none (rule 4).

```mind
struct P { x: i64, }
impl P {
    fn get(p: P) -> i64 { return p.x; }
}
fn main() -> i64 {
    let p = P { x: 4 };
    return p.get();
}
```

has the written-out form below (not source text, because `P::get` in a declaration is not an identifier):

```text
struct P { x: i64, }
fn P::get(p: P) -> i64 { return p.x; }
fn main() -> i64 {
    let p = P { x: 4 };
    return P::get(p);
}
```

A call `x.m(a)` becomes the call `Name(x, a)` of the item that rule 8 selects. This is the reading that the
standard library already uses for the collection methods (`v.push(x)` for `vec_push(v, x)`, see
[STATUS](../../STATUS.md)). An associated constant `K` becomes the top-level constant `C(Type)::C(Trait)::K`
(`C(Type)::K` in an inherent block); an associated type `Item` becomes an alias with the name
`C(Type)::C(Trait)::Item` (`C(Type)::Item` in an inherent block). `Self` and `Self::Item` are replaced by the type
and by the alias. The equality test of [RFC 0023](./0023-type-parameters-on-user-types.md#meaning-as-a-desugaring)
is the oracle for the parser rows.

## Proposed conformance rows

Proposals. The reference refuses the inherent row, the rows that use `;` in a trait signature, and every row
that uses an associated item or `Self` as a checked name. For the reject rows with `E2701`, `E2702` and
`E2703` the reference gives the code and the text that the row names, measured with v0.10.4 on the same
program with the trait signature written without `;`. `E2707` is measured in the same way (the text of the
reference says "method"). The codes `E2710` to `E2715` are reserved for this draft, and `E2038` and `E2041` are
codes of [RFC 0023](./0023-type-parameters-on-user-types.md). The trait signatures of the rows use the `;` of this
draft's grammar. Rows that build a record use the record literal of
[RFC 0025](./0025-patterns.md#record-literal).

```yaml
description: "An inherent impl and a method call"
category: syntax
profile: cpu
input:
  source: |
    struct P {
        x: i64,
    }
    impl P {
        fn get(p: P) -> i64 {
            return p.x;
        }
    }
    fn main() -> i64 {
        let p = P { x: 4 };
        return p.get();
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 4 } }
```

```yaml
description: "A trait with an associated constant and type, and its impl"
input:
  source: |
    trait Shape {
        const SIDES: i64;
        type Unit;
        fn area(s: Self) -> i64;
    }
    struct Sq {
        x: i64,
    }
    impl Shape for Sq {
        const SIDES: i64 = 4;
        type Unit = i64;
        fn area(s: Sq) -> Self::Unit {
            return s.x * s.x;
        }
    }
    fn main() -> i64 {
        let s = Sq { x: 3 };
        return s.area() + Sq::SIDES;
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 13 } }
```

```yaml
description: "A generic inherent block and a method call on an instance"
input:
  source: |
    struct Box<T> {
        v: T,
    }
    impl<T> Box<T> {
        fn get(b: Box<T>) -> T {
            return b.v;
        }
    }
    fn main() -> i64 {
        let b = Box { v: 4 };
        return b.get();
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 4 } }
```

```yaml
description: "A parameter of a block that the head does not use is refused"
input:
  source: |
    struct P {
        x: i64,
    }
    impl<T> P {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2041, message_contains: "unused type parameter" }
```

```yaml
description: "An impl of an unknown trait is refused"
input:
  source: |
    struct P {
        x: i64,
    }
    impl Nope for P {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2701, message_contains: "is not declared" }
```

```yaml
description: "An impl of a predeclared bound is refused"
input:
  source: |
    struct P {
        x: i64,
    }
    impl Numeric for P {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2701, message_contains: "Numeric" }
```

```yaml
description: "An impl that lacks a trait method is refused"
input:
  source: |
    trait T {
        fn get(p: i64) -> i64;
        fn put(p: i64) -> i64;
    }
    struct P {
        x: i64,
    }
    impl T for P {
        fn get(p: i64) -> i64 {
            return 1;
        }
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2707, message_contains: "missing" }
```

```yaml
description: "An impl that lacks an associated constant is refused"
input:
  source: |
    trait T {
        const K: i64;
    }
    struct P {
        x: i64,
    }
    impl T for P {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2707, message_contains: "missing" }
```

```yaml
description: "An associated constant of the wrong type is refused"
input:
  source: |
    trait T {
        const K: i64;
    }
    struct P {
        x: i64,
    }
    impl T for P {
        const K: f64 = 1.5;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2001, message_contains: "K" }
```

```yaml
description: "A function whose signature differs from the trait is refused"
input:
  source: |
    trait T {
        fn get(p: i64) -> i64;
    }
    struct P {
        x: i64,
    }
    impl T for P {
        fn get(p: f64) -> f64 {
            return p;
        }
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2713, message_contains: "signature" }
```

```yaml
description: "A function that the trait does not declare is refused"
input:
  source: |
    trait T {
    }
    struct P {
        x: i64,
    }
    impl T for P {
        fn extra(p: P) -> i64 {
            return 1;
        }
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2703, message_contains: "not declared in trait" }
```

```yaml
description: "Two impls of one trait for one type are refused"
input:
  source: |
    trait T {
    }
    struct P {
        x: i64,
    }
    impl T for P {
    }
    impl T for P {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2702, message_contains: "duplicate" }
```

```yaml
description: "An impl for an unknown type is refused"
input:
  source: |
    trait T {
    }
    impl T for Nope {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2710, message_contains: "unknown type" }
```

```yaml
description: "A trait impl for a primitive type and a method call on a value of that type"
input:
  source: |
    trait Zero {
        fn zero(s: Self) -> i64;
    }
    impl Zero for i64 {
        fn zero(s: i64) -> i64 {
            return 0;
        }
    }
    fn main() -> i64 {
        let x = 5;
        return x.zero();
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 0 } }
```

```yaml
description: "A trait impl for a tuple type is refused"
input:
  source: |
    trait Zero {
        fn zero(s: Self) -> i64;
    }
    impl Zero for (i64, i64) {
        fn zero(s: (i64, i64)) -> i64 {
            return 0;
        }
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2710, message_contains: "type" }
```

```yaml
description: "An impl of a trait with one parameter that gives two arguments is refused"
input:
  source: |
    trait Conv<X> {
        fn conv(a: i64) -> X;
    }
    struct P {
        x: i64,
    }
    impl Conv<i64, i64> for P {
        fn conv(a: i64) -> i64 {
            return a;
        }
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2038, message_contains: "type arguments" }
```

## Cost for the compiler

| Part | Work | Size |
|------|------|------|
| Front end, parser | the `trait` item with the `;` form and the two associated items; the `impl` item with both forms, the optional parameter list and the two associated items; `Self` as a keyword and as a type; `Name::Item` in a type and in an expression. The inherent form, the parameter list and the `;` form are new; the other forms exist in the reference. | medium |
| Front end, checker | the ten rules; method resolution by receiver type; signature comparison with `Self` and the trait arguments; overlap of generic blocks; the module rule of rule 10; the code table | medium |
| Front end, desugaring | the item names and the call rewrite, one pass, shared with the instance pass of RFC 0023 | small |
| Native lowering | none after the pass. A struct or enum receiver needs the admission of `struct` and `enum` items in the native lane (`lane.source.top_level` today). | large (prerequisite, shared with RFC 0023) |
| Tests | rows above; desugar parity; the four codes that already exist keep their text | small |

## Questions for the specification owner

### Decided by the specification owner (2026-11-24)

1. **Spelling of the trait item.** `fn …;` with the `;` is the only trait item form. The reference changes to it.
2. **Receiver spelling.** The receiver is the first parameter, of type `Self` or of the implementing type. There
   is no `self` keyword.
3. **Default items.** A trait has no default items in this edition: no default body and no default value.
4. **Generic blocks.** `impl<T> Box<T> { … }` is in this RFC, with the parameter rules of
   [RFC 0023](./0023-type-parameters-on-user-types.md), in the same edition.
5. **Visibility.** A method is visible where its type is visible. A module MAY implement a trait for a type only
   when it declares the trait or the type (rule 10, `E2715`).
6. **Codes (settled).** `E2701`, `E2702`, `E2703` and `E2707` are in the catalog as released behaviour; this draft
   widens the headings of `E2701`, `E2702`, `E2703` and `E2707` to their uses (the Codes paragraph of the static
   rules).
   `E2710` to `E2715` are reserved for this draft.
7. **Bounds on an associated type.** They come with the bounds of [RFC 0027](./0027-function-generics.md), in the
   same edition.
8. **`Self` as an identifier.** `Self` is reserved in the lexical chapter: it is a keyword.

### Open

- **Inherent blocks in another module.** Rule 10 covers trait impls. Whether an inherent block MAY stand in a module
  that does not declare its type is not decided.
- **Qualified names in the head of an impl.** `TraitRef` and `IdentifierType` take one identifier, so an impl
  cannot yet name a trait or a type of another module. Rule 10 applies to such heads once a later change adds
  qualified names there.
