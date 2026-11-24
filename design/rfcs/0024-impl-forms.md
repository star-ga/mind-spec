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

# RFC 0024: `trait` and `impl` blocks (an implementation of a type, of a trait for a type, and the associated items of a trait)

| Field | Value |
|-------|-------|
| State | Draft (2026-11-24). Not yet accepted. |
| Number | Provisional. The specification owner assigns the final number. |
| Changes | `grammar-syntax.ebnf` (new `ImplDeclaration`; unmarks `TraitDeclaration`, `TraitItem` and `FunctionSignature`; associated constants and types; `Self`), `types.md` (Traits and generics), `errors.md` (codes of the impl checks) |
| Depends on | none. The trait part of the grammar uses `TraitRef` and `TypeParameterList` of [RFC 0023](./0023-type-parameters-on-user-types.md); without that RFC, read `TraitRef` as one identifier and omit the parameter list. |
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

The codes `E2701`, `E2702`, `E2703` and `E2707` are in the [Error Catalog](../../spec/v1.0/errors.md#e2701-impl-of-an-undeclared-trait)
as a record of the released behaviour. This RFC specifies the `impl` forms, the trait declaration and the
associated items, so that the grammar, the catalog and the reference agree.

## Grammar change

```ebnf
ModuleItem        = … | TraitDeclaration | ImplDeclaration ;

TraitDeclaration  = "trait" , Identifier , [ TypeParameterList ] , "{" , { TraitItem } , "}" ;
TraitItem         = FunctionSignature | TraitConst | TraitType ;
FunctionSignature = "fn" , Identifier , "(" , [ ParameterList ] , ")" , [ "->" , Type ] , ";" ;
TraitConst        = "const" , Identifier , ":" , Type , ";" ;
TraitType         = "type" , Identifier , ";" ;

ImplDeclaration   = InherentImpl | TraitImpl ;
InherentImpl      = "impl" , IdentifierType , "{" , { ImplItem } , "}" ;
TraitImpl         = "impl" , TraitRef , "for" , Type , "{" , { ImplItem } , "}" ;
ImplItem          = FunctionDeclaration | ImplConst | ImplType ;
ImplConst         = "const" , Identifier , ":" , Type , "=" , Expression , ";" ;
ImplType          = "type" , Identifier , "=" , Type , ";" ;

Type              = … | AssociatedType ;
AssociatedType    = ( "Self" | Identifier ) , "::" , Identifier ;
PrimaryExpression = … | AssociatedValue ;
AssociatedValue   = ( "Self" | Identifier ) , "::" , Identifier ;
```

This RFC unmarks `TraitDeclaration`, `TraitItem` and `FunctionSignature`. The supertrait list of the old
`TraitDeclaration` (`trait B: A`) and the trait bounds are owned by [RFC 0027](./0027-function-generics.md), which adds
`[ ":" , TraitBounds ]` to the production above. They stay NOT IN CORE v1 until RFC 0027 is accepted. `trait` and `impl` are `ModuleItem`s; a module block ([RFC 0026](./0026-module-items.md)) MAY hold
them.

`Self` is not a new keyword. It is an ordinary identifier with one predeclared meaning: inside a trait
declaration it names the type that implements the trait, and inside an `impl` it names the type of the block.
Outside a trait and an `impl` it is an unknown name. A declaration that gives the name `Self` to a type, a
function or a value is refused with `E2715`.

`Name::Item` has the same spelling as the variant path of an enum ([RFC 0025](./0025-patterns.md)). The
resolver reads it as a variant when `Name` is an enum that has a variant `Item`, and as an associated item
otherwise. An enum with a variant and an associated item of the same name is refused with `E2711`.

`Type` after an inherent `impl` MUST be a user-declared `struct` or `enum` type, or an instance of one
([RFC 0023](./0023-type-parameters-on-user-types.md)). The reference's untyped `self` parameter is not
adopted: a method names its receiver with a first parameter of the type `Self`, or of the type that it
implements (open question 2).

## Static rules

1. **Method and associated function.** A function of an `impl` block whose first parameter has the type of
   the block (or `Self`) is a method. Another function of the block is an associated function. A method is
   called as `x.m(args)`; an associated function is called as `Type::f(args)`.
2. **Unique names.** Two items of the inherent blocks of one type MUST NOT have the same name (`E2711`).
3. **Trait block.** The block MUST define every function, constant and type that the trait declares, and
   MUST NOT define an item that the trait does not declare. A missing item is refused with `E2707` (the
   reference uses it for a missing method; this RFC extends it to constants and types). An extra function is
   refused with `E2703` (existing). An extra constant or type is refused with `E2714`.
4. **Signatures.** After `Self` is replaced by the type of the block, and each parameter of the trait by its
   argument, a function of the block MUST have the parameter types and the result type of the trait's
   signature. A difference is refused with `E2713`. (The reference accepts a difference today.)
5. **Constants and types.** An associated constant of a block MUST have the type that the trait declares, and
   its value MUST be a constant expression (the rule of `ConstDeclaration`). A wrong type is refused with
   `E2001`. An associated type MAY name any `Type` except `unit`; the type of the trait item is only a name
   for it, so a trait item has no bound in this RFC (open question 7).
6. **Coherence.** For a trait (with its arguments) and a type there MUST be at most one `impl` in the program,
   and in the modules that it imports ([Types](../../spec/v1.0/types.md#traits-and-generics)). A second one is
   refused with `E2702` (existing).
7. **Names.** The trait named in an `impl` MUST be declared and visible; an unknown trait is refused with
   `E2701` (existing). The type of the block MUST be declared and visible; an unknown type is refused with
   `E2710`. (The reference accepts an unknown type today.) An unknown name elsewhere keeps `E2002`. The type of
   a trait impl is a user-declared `struct` or `enum` type, an instance of one, or a primitive type: `impl T for
   i64` is valid, and its canonical name uses `i64`. Any other type (a tuple, an array, a tensor, a `diff` type)
   is refused with `E2710`. The type of an inherent block is a user-declared type only.
8. **Resolution.** `x.m(args)` where the type of `x` is `Type` calls the method `m` of the inherent block of
   `Type`, or of the trait impl of `Type` whose trait declares `m`. If both exist, the inherent method wins.
   If two trait impls of `Type` declare `m`, the call is refused as ambiguous (`E2712`).
   `Type::K` and `Type::f(args)` look in the same blocks in the same order. `Self::Item` in a trait
   signature names the associated type of the implementing type; in a block it names the type that the block
   gives to `Item`.
9. **No dynamic dispatch.** A call is resolved at compile time from the static type of the receiver. `dyn
   Trait` stays NOT IN CORE v1.

Codes that the reference already uses, now in the catalog: `E2701` trait not declared, `E2702` duplicate impl,
`E2703` method that the trait does not declare, `E2707` trait item missing in an impl. Codes reserved for this
draft by the specification owner (`E2710` to `E2715`): `E2710` unknown or unsupported type in an impl, `E2711`
duplicate name, `E2712` ambiguous method, `E2713` signature differs from the trait, `E2714` associated constant
or type that the trait does not declare, `E2715` the name `Self` declared by the program.

## Meaning as a desugaring

An `impl` block is a set of top-level items with a canonical name, and a method call is a call of one of
them. Nothing else is added to the Core IR. A trait declaration has no run-time form: it supplies the names and
signatures that rules 3 to 5 check, and it disappears.

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

is the program

```mind
struct P { x: i64, }
fn P__get(p: P) -> i64 { return p.x; }
fn main() -> i64 {
    let p = P { x: 4 };
    return P__get(p);
}
```

For a trait impl the item name is `Trait__Type__item`, where `Trait` and `Type` are written as the canonical
instance names of [RFC 0023](./0023-type-parameters-on-user-types.md) (`Conv__f64__P__conv` for the function
`conv` of `impl Conv<f64> for P`). A call `x.m(a)` becomes the call `Name(x, a)` of the function that rule 8
selects. This is the reading that the standard library already uses for the collection methods (`v.push(x)` for
`vec_push(v, x)`, see [STATUS](../../STATUS.md)). An associated constant `K` becomes the top-level constant
`Trait__Type__K` (`Type__K` in an inherent block); an associated type `Item` becomes the alias
`type Trait__Type__Item = …;` (`Type__Item` in an inherent block). `Self` and `Self::Item` are replaced by the
type and by the alias. The desugaring is the oracle for the equality test of the parser rows: the bytes of the
program with `impl` equal the bytes of the written-out program.

## Proposed conformance rows

Proposals. The reference refuses the inherent row, the rows that use `;` in a trait signature, and every row
that uses an associated item or `Self` as a checked name. For the reject rows with `E2701`, `E2702` and
`E2703` the reference gives the code and the text that the row names, measured with v0.10.4 on the same
program with the trait signature written without `;`. `E2707` is measured in the same way (the text of the
reference says "method"). The codes `E2710`, `E2713`, `E2714` and `E2038` are reserved for these drafts and
no compiler gives them today. The trait signatures
of the rows use the `;` of this draft's grammar. Rows that build a record use the record literal of
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
| Front end, parser | the `trait` item with the `;` form and the two associated items; the `impl` item with both forms and the two associated items; `Name::Item` in a type and in an expression. The inherent form and the `;` form are new; the other forms exist in the reference. | medium |
| Front end, checker | the nine rules; method resolution by receiver type; signature comparison with `Self` and the trait arguments; the code table | medium |
| Front end, desugaring | the canonical names and the call rewrite, one pass | small |
| Native lowering | none after the pass. A struct or enum receiver needs the admission of `struct` and `enum` items in the native lane (`lane.source.top_level` today). | large (prerequisite, shared with RFC 0023) |
| Tests | rows above; desugar parity; the four codes that already exist keep their text | small |

## Open questions for the specification owner

1. **Spelling of the trait item.** The grammar has `fn …;` in a trait. The reference refuses that form and
   accepts the form without `;`. Does the reference change (the form with `;` is then the only one), or does
   the grammar accept both for one edition? This draft keeps the `;`.
2. **Receiver spelling.** First parameter of type `Self` or of the implementing type (this draft), or a
   reserved `self` keyword? A `self` keyword needs a change of the keyword list in
   [Lexical Structure](../../spec/v1.0/lexical.md#keywords).
3. **Default items.** May a trait give a default body for a function or a default value for a constant?
   This draft has none.
4. **Generic blocks.** `impl<T> Box<T> { … }` needs the type-parameter list of RFC 0023 on the block.
5. **Visibility.** Whether a method of a type in one module is callable from another module without an
   export of the type (see [RFC 0026](./0026-module-items.md)), and whether a module MAY implement a trait that
   it imports for a type that it imports (both declared in other modules).
6. **Codes (settled).** `E2701`, `E2702`, `E2703` and `E2707` are in the catalog as released behaviour.
   `E2710` to `E2715` are reserved for this draft.
7. **Bounds on an associated type.** `type Item;` has no bound, so a generic function cannot do more with
   `T::Item` than move it. Bounds on associated types need [RFC 0027](./0027-function-generics.md).
8. **`Self` as an identifier.** The draft gives `Self` a predeclared meaning and adds no keyword. Reserve it
   in the lexical chapter instead?
