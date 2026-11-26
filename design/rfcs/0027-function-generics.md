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

# RFC 0027: Function generics (several type parameters, bounds, `where`, explicit type arguments at a call)

| Field | Value |
|-------|-------|
| State | Draft (2026-11-24). Not yet accepted. The specification owner decided the questions of this draft on 2026-11-24 (see [Questions](#questions-for-the-specification-owner)). |
| Number | Provisional. The specification owner assigns the final number. |
| Edition | Core v1.1, one edition together with [RFC 0023](./0023-type-parameters-on-user-types.md) and [RFC 0024](./0024-impl-forms.md). |
| Changes | `grammar-syntax.ebnf` (`FunctionDeclaration` gets `[ GenericParameters ]` and `[ WhereClause ]`; `GenericParameters`, `WhereClause`, `GenericFunctionRef`, the supertrait list of `TraitDeclaration` and the bounds of `TraitType` added; `TraitBounds` and `TraitBound` unmarked), `types.md` (Traits and generics, Type inference, the predeclared numeric bounds), `errors.md` (the trigger of `E2701`, whose heading [RFC 0024](./0024-impl-forms.md) makes "Trait name that names no trait that the program declares", also covers a bound, a `where` predicate and a supertrait that name neither a trait that the program declares nor a predeclared bound; the trigger of `E2037` also covers a `GenericFunctionRef` that no call follows; the new code `E2716`) |
| Owns | Bounds, the `where` clause, explicit type arguments at a call, **supertraits** (`trait B: A`), the predeclared numeric bounds and the bounds of an associated type. No other draft defines them. |
| Depends on | [RFC 0024](./0024-impl-forms.md) (a bound names a trait; the meaning of a method call on a bounded value). The plain parameter list and the instance names of [RFC 0023](./0023-type-parameters-on-user-types.md) are used here. |
| Related | [RFC 0023](./0023-type-parameters-on-user-types.md), [RFC 0025](./0025-patterns.md) |

## Problem

The grammar has no type parameter on a function: `FunctionDeclaration` is `{ Attribute } , "fn" , Identifier ,
"(" , [ ParameterList ] , ")" , [ "->" , Type ] , Block`. [Core v1 form status](../../spec/v1.0/core-v1-forms.md) gives
`fn f<T>(x: T) -> T { }` the status Extension, and [Types](../../spec/v1.0/types.md#traits-and-generics) records that
the reference ships "generics limited to a single type parameter over scalar types". The text of
[Types](../../spec/v1.0/types.md#traits-and-generics) also specifies trait bounds in a `where` clause, while the
grammar writes a bound inside the angle brackets of a type declaration (`TypeParameter`, `<T: Bound>`, marked NOT IN
CORE v1). The grammar has no `where` clause and no explicit type argument at a call, and the two spellings of a bound
do not agree. A function therefore cannot take a type parameter in the grammar, cannot require that a parameter has
a trait, and cannot name a type argument that no argument fixes.

Measured with the reference compiler v0.10.4 (`mindc check --no-fmt`):

| Source | Result |
|--------|--------|
| `fn id<T>(x: T) -> T` | accepted |
| `fn first<A, B>(a: A, b: B) -> A` and `fn id<T,>(…)` | accepted (an extension: the grammar has no type parameter on a function) |
| `fn id<>(x: i64) -> i64` | accepted |
| `fn id<T: Num>(x: T) -> T` | `E1001`, ``expected '>', found Some(':')`` (1:8) |
| `fn id<T>(x: T) -> T where T: Num { … }` | `E1001`, ``expected '{', found Some('w')`` (1:21) |
| `id<i64>(5)` | `E2037`, `` `id` is a function, not a value: first-class functions are not yet supported `` (the call is read as a comparison) |
| `id::<i64>(5)` | `E1001`, ``unexpected `:`, expected an expression`` (6:14) |
| `fn z<T>(x: i64) -> i64` called as `z(1)` | accepted: the parameter `T` is fixed by nothing |
| `fn pick<T>(x: T, y: T) -> T` called as `pick(5, 1.5)` | accepted: one parameter gets two types |
| a generic function, native backend | refused, `lane.source.function_contract` |

## Grammar change

```ebnf
FunctionDeclaration = { Attribute } , "fn" , Identifier , [ GenericParameters ] , "(" , [ ParameterList ] , ")" ,
                      [ "->" , Type ] , [ WhereClause ] , Block ;

GenericParameters   = "<" , GenericParameter , { "," , GenericParameter } , [ "," ] , ">" ;
GenericParameter    = Identifier , [ ":" , TraitBounds ] ;
TraitBounds         = TraitBound , { "+" , TraitBound } ;
TraitBound          = TraitRef ;

WhereClause         = "where" , WherePredicate , { "," , WherePredicate } , [ "," ] ;
WherePredicate      = Identifier , ":" , TraitBounds ;
(* Replaced by DN-68: no where clause; "where" stays reserved. *)

GenericFunctionRef  = Identifier , "::" , TypeArguments ;
PrimaryExpression   = … | GenericFunctionRef ;
```

`FunctionDeclaration` of the grammar has no type parameter today; this RFC adds `[ GenericParameters ]` to it, so in the
edition of this RFC `fn f<T>(x: T) -> T { }` is part of the language and no longer an extension. `GenericParameters`
does not touch the `TypeParameterList` of [RFC 0023](./0023-type-parameters-on-user-types.md): the type parameters of
`struct`, `enum`, `trait`, `type` and of an `impl` block stay plain names, and this edition has no bound on them (rule
14). The `where` clause is added to `FunctionDeclaration` only. `TraitRef` and `TypeArguments` are the productions of
RFC 0023. `GenericParameters` ends with the token `>`, as the type parameters of a declaration do. The closing angle
rule of [Lexical Structure](../../spec/v1.0/lexical.md#tokens) is for the `>` that closes a type-argument list
(`TypeArguments`): in `fn f<T: Conv<i64>>(x: T)` the first `>` of `>>` closes the arguments of `Conv`, and the rest
of the token, read again, is the `>` of `GenericParameters`; `id::<Box<i64>>(b)` ends two type-argument lists.
`where` is already in the keyword list.
*The `where` clause is replaced by [DN-68](./decision-notes-3.md#dn-68-no-where-clause-type-arguments-of-a-method): a bound is written in the parameter list only.*

The supertrait list is a bound on the implementing type, and a bound on an associated type is a bound on the type
that an impl gives to it. Both are added to the productions of RFC 0023 and [RFC 0024](./0024-impl-forms.md):

```ebnf
TraitDeclaration    = "trait" , Identifier , [ TypeParameterList ] , [ ":" , TraitBounds ] ,
                      "{" , { TraitItem } , "}" ;
TraitType           = "type" , Identifier , [ ":" , TraitBounds ] , ";" ;
```

A `GenericFunctionRef` MUST be followed at once by a `CallOperator`: `id::<i64>(5)` is a call, and `id::<i64>` alone is
refused (a function is not a value in Core v1,
[`E2037`](../../spec/v1.0/errors.md#e2037-function-name-used-as-a-value)). The spelling `id<i64>(5)` is not part of the
grammar, because `<` is the comparison operator. The token `::` is already in the operator list; `Identifier "::" "<"`
cannot be read as the variant path or the associated item path of [RFC 0024](./0024-impl-forms.md), which have an
identifier after `::`. A placeholder `_` is not a `Type`, so `f::<_, i64>(x)` is not derived.

## Static rules

1. **Parameters.** The names of one `GenericParameters` MUST be pairwise different (`E2039` of RFC 0023). A
   type parameter is in scope in the parameter list, the result type, the `where` clause and the body. It is a
   type, not a value. The list has at least one name: `fn id<>(…)` is not derived (the reference accepts it).
2. **Bounds.** A `TraitBound` MUST name a declared trait or a predeclared bound (rule 4) with the right number of
   arguments (`E2701` for an unknown trait, `E2038` for the argument count). A `WherePredicate` MUST name a type
   parameter of the same function: its name is looked up among the type parameters of the function only, so another
   name is an unresolved name there (`E2002`). `T: A + B` and `where T: A, T: B` mean the same. A type
   parameter that has no bound MAY be moved (passed, returned, bound to a name) and nothing else.
   *The `where` forms of this rule are replaced by [DN-68](./decision-notes-3.md#dn-68-no-where-clause-type-arguments-of-a-method).*
3. **What a bounded value can do.** A value of type `T` with the bound `B` supports the method calls
   `x.m(args)` where `m` is a method of `B`. An operator is defined on a value of type `T` only through a
   predeclared numeric bound (rule 4). Traits that a program declares for operators come in a later RFC. A call of a
   method that no bound declares is refused with `E2716` (rule 8).
4. **Predeclared numeric bounds.** `Numeric`, `Integer` and `Float` are predeclared trait names. Each one is a
   closed set of the numeric primitive types of [Types](../../spec/v1.0/types.md#type-formation) and of
   `PrimitiveType`:

   | Bound | Set of types | A value of type `T` with the bound supports |
   |-------|--------------|----------------------------------------------|
   | `Numeric` | `i32`, `i64`, `f32`, `f64` | unary `-`; `+`, `-`, `*`, `/`, `%`; `==`, `!=`, `<`, `<=`, `>`, `>=`; the compound assignments `+=`, `-=`, `*=`, `/=`, `%=`; a cast `e as T` from a numeric primitive type, and a cast `x as U` to a numeric primitive type `U` |
   | `Integer` | `i32`, `i64` | what `Numeric` supports, and `&`, `\|`, `^`, `<<`, `>>` with their compound assignments `&=`, `\|=`, `^=`, `<<=`, `>>=`, with the rules of [Bitwise and shift operators](../../spec/v1.0/language.md#bitwise-and-shift-operators) |
   | `Float` | `f32`, `f64` | what `Numeric` supports |

   A set holds the types of its row and no other type: a program cannot add one (an `impl` of a predeclared bound is
   refused with `E2701`, [RFC 0024](./0024-impl-forms.md) rule 7), and a declaration cannot take one of the three
   names (`E2042`, [RFC 0023](./0023-type-parameters-on-user-types.md) rule 9). A bound is satisfied by a type of
   its set, and a parameter with the bound `Integer` or `Float` satisfies a bound `Numeric`. Both operands of a
   binary operator, and the two sides of a compound assignment, MUST have the same type `T`, except the right operand of
   `<<` and `>>` (and of `<<=` and `>>=`): it is the shift count and MAY have any integer type, as [Bitwise and shift
   operators](../../spec/v1.0/language.md#bitwise-and-shift-operators) gives. A type parameter is not an integer or a
   floating-point type in the sense of [Type of a literal](../../spec/v1.0/types.md#type-of-a-literal), so a literal
   never takes the type `T`: in `x + 1` the literal has the type `i64`, the two operands have two types, and the source
   is refused with `E2004` (dtype mismatch in binary operation), the code that [Language](../../spec/v1.0/language.md)
   gives to two operands of different types of `%`, of `&`, `|` and `^`, and of an elementwise operator; `x + (1 as T)`
   is valid. A type parameter is not a primitive type name, so by the reading rule of
   [Casts](../../spec/v1.0/language.md#casts) a `<` after `x as T` opens a type-argument list: a comparison of such a
   cast is written `(x as T) < y`. The elementwise operators `.*`, `./`, `.+` and `.-` are not in the table
   ([Open](#open)). An arithmetic or bitwise operator gives a `T`, and a comparison gives a `bool`. In each instance an
   operator has the meaning that it has for the argument type, `%` on a float included ([Floating-point
   remainder](../../spec/v1.0/language.md#floating-point-remainder)), and a cast has the meaning that the cast rule
   ([Casts](../../spec/v1.0/language.md#casts)) gives for the two types of the instance. The standard library signatures
   that use `Numeric` and `Float` ([Standard Library](../../spec/v1.0/stdlib.md)) name these bounds.
5. **Inference.** At a call `f(args)` each type parameter is bound from the types of the arguments by
   structural matching of the parameter types. A parameter that two arguments bind to different types is refused
   with `E2001`. A parameter that no argument binds is refused with `E2003` (cannot infer type) unless the call
   names it with rule 6. No default type is chosen.
6. **Explicit arguments.** `f::<A, B>(args)` gives every type parameter of `f` in order. The count MUST equal
   the number of parameters (`E2038`). There is no partial list and no placeholder: a shorter list is refused with
   `E2038`, and `_` is not derived. An argument that rule 5 would infer to another type is refused with `E2001`.
7. **Bound satisfaction.** After inference, each bound of each parameter MUST be satisfied: the type that the
   parameter gets MUST have an `impl` of the trait ([RFC 0024](./0024-impl-forms.md), rule 6), or, for a
   predeclared bound, be a type of its set. A bound that is not satisfied is refused with `E2006` (trait bound not
   satisfied, existing).
8. **Method on a type parameter.** A call `x.m(args)` where `x` has a type parameter type and no bound of that
   parameter declares `m` (directly or through a supertrait, rule 12) is refused with `E2716`. (A call on a type that
   is known resolves by RFC 0024, rule 8.)
9. **Compatibility.** Core v1 has no generic function: `fn id<T>(x: T) -> T` is an extension
   ([Core v1 forms](../../spec/v1.0/core-v1-forms.md)). Under this RFC it has the meaning: one parameter, no bound,
   inferred at each call. A program that uses the extension and whose calls fix every type argument by an argument
   is valid under this RFC. A call whose type argument no argument fixes is an error (`E2003`); the specification owner
   decided this in
   [decision note DN-13](./decision-notes.md#dn-13-a-generic-call-whose-type-argument-is-not-fixed) (option A),
   and [Types](../../spec/v1.0/types.md#type-inference) already states that a generic function MUST infer its
   type parameters when the arguments give enough information. There is no warning
   period: the refusal comes in one step.
10. **Supertraits.** Each `TraitBound` of a supertrait list MUST name a declared trait or a predeclared bound with
    the right number of arguments (`E2701` for an unknown trait, `E2038` for the argument count). A trait MUST NOT be
    its own supertrait, directly or through other traits, and it MUST NOT name itself in the arguments of a
    supertrait (`trait B: A<B>`). A violation is refused with `E2040` (the code of
    [RFC 0023](./0023-type-parameters-on-user-types.md), rule 7, for a declaration that contains itself). The names
    of the supertrait list are not type parameters: `Self` is the only type that it constrains. The supertrait list
    is the only form of a supertrait; there is no `where Self: A` form.
11. **Impl of a trait with supertraits.** `impl B for S` MUST be accompanied by `impl A for S` for every
    supertrait `A` of `B`, in the program or in the modules that it imports. For a predeclared supertrait `A`, `S`
    MUST be a type of the set of `A`. A missing one is refused with `E2006` (trait bound not satisfied) at the
    `impl B` block.
12. **Supertrait use.** A value whose type parameter has the bound `B` supports the methods of `B` and of every
    supertrait of `B` (rule 3 extends to them), and satisfies a bound `A` of a call.
13. **Bounds on an associated type.** `type Item: C;` in a trait gives the associated type `Item` the bounds `C`.
    The type that an impl gives to `Item` MUST satisfy each bound (`E2006`). In the signatures of the trait,
    `Self::Item` supports what the bounds `C` allow (rules 3 and 4). In a function whose type parameter `T` has a
    bound that declares `Item`, `T::Item` names the type that the argument type gives to `Item`, and it supports what
    the bounds `C` allow. `T::Item` needs exactly one bound of `T` that declares `Item`: none is refused with
    `E2002`, and two are refused as ambiguous with `E2712` ([RFC 0024](./0024-impl-forms.md), rule 8).
14. **No bounds on the parameters of a type.** A bound on a type parameter of a `struct`, an `enum`, a `type`, a
    `trait` or an `impl` block is not part of this edition: `TypeParameterList` holds plain names, and a `where`
    clause follows a function only.

**Codes.** `E2001`, `E2002`, `E2003`, `E2004` and `E2006` exist. `E2038`, `E2039`, `E2040` and `E2042` are the codes of
[RFC 0023](./0023-type-parameters-on-user-types.md); this draft uses them as RFC 0023 defines them, and `E2040` for a
trait that names itself in its supertrait list. `E2701` (a trait name that names no trait that the program declares) and
`E2712` (ambiguous method or associated item) are the codes of [RFC 0024](./0024-impl-forms.md), with the headings that
it gives them. This draft proposes one code, `E2716`: a method call on a value of a type parameter whose bounds declare
no such method (rule 8). It is free in the catalog, and it is the next code after the codes of RFC 0024.

## Meaning as a desugaring

A bound and a supertrait list are checks and have no run-time form. A generic call is a call of a plain function,
one for each distinct list of arguments, in the way that [RFC 0023](./0023-type-parameters-on-user-types.md) gives for
types.

```text
// Not Core v1: a source in the form that this RFC proposes
trait Zero {
    fn zero(s: Self) -> i64;
}
struct P { x: i64, }
impl Zero for P {
    fn zero(s: P) -> i64 { return 0; }
}
fn first<A, B: Zero>(a: A, b: B) -> A where A: Zero {
    return a;
}
fn main() -> i64 {
    let p = P { x: 1 };
    let r = P { x: 2 };
    let q = first::<P, P>(p, r);
    return q.x;
}
```

has the written-out form below (not source text, because an instance name and an item name are not identifiers):

```text
// Not Core v1: the written-out form, not source text (a name in it is not an identifier)
struct P { x: i64, }
fn P::Zero::zero(s: P) -> i64 { return 0; }
fn first<P,P>(a: P, b: P) -> P {
    return a;
}
fn main() -> i64 {
    let p = P { x: 1 };
    let r = P { x: 2 };
    let q = first<P,P>(p, r);
    return q.x;
}
```

The instance name of a function is `D(f)` followed by the argument list, in the scheme of
[RFC 0023](./0023-type-parameters-on-user-types.md#instance-names): `first<P,P>`. A call `x.m(args)` on a value of a
type parameter type is, in the instance, the call that [RFC 0024](./0024-impl-forms.md) rule 8 selects for the
argument type, and an operator on a value with a predeclared bound is, in the instance, the operator of the argument
type. The explicit form `f::<A>(x)` and the inferred form `f(x)` give the same instance. The equality test of
RFC 0023 is the oracle.

## Proposed conformance rows

Proposals. No compiler accepts the accept rows today. The rows that declare a trait use the `;` of the grammar of
[RFC 0024](./0024-impl-forms.md), and the rows that build a record use the record literal of
[RFC 0025](./0025-patterns.md#record-literal).

```yaml
description: "Two type parameters, a bound, a where clause and an explicit call"
category: syntax
profile: cpu
input:
  source: |
    trait Zero {
        fn zero(s: Self) -> i64;
    }
    struct P {
        x: i64,
    }
    impl Zero for P {
        fn zero(s: P) -> i64 {
            return 0;
        }
    }
    fn first<A, B: Zero>(a: A, b: B) -> A where A: Zero {
        return a;
    }
    fn main() -> i64 {
        let p = P { x: 1 };
        let r = P { x: 2 };
        let q = first::<P, P>(p, r);
        return q.x;
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 1 } }
```

```yaml
description: "A predeclared numeric bound allows an operator"
input:
  source: |
    fn add<T: Numeric>(a: T, b: T) -> T {
        return a + b;
    }
    fn main() -> i64 {
        let a: i64 = 2;
        let b: i64 = 3;
        return add(a, b);
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 5 } }
```

```yaml
description: "A type outside the set of a predeclared bound is refused"
input:
  source: |
    fn add<T: Numeric>(a: T, b: T) -> T {
        return a + b;
    }
    fn main() -> i64 {
        let t = add(true, false);
        return 0;
    }
expected:
  status: error
  error: { code: E2006, message_contains: "Numeric" }
```

```yaml
description: "A literal is not a value of the type parameter"
input:
  source: |
    fn inc<T: Numeric>(a: T) -> T {
        return a + 1;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2004, message_contains: "T" }
```

```yaml
description: "A bound that the argument type does not satisfy is refused"
input:
  source: |
    trait Zero {
        fn zero(s: Self) -> i64;
    }
    struct P {
        x: i64,
    }
    fn need<T: Zero>(a: T) -> i64 {
        return 0;
    }
    fn main() -> i64 {
        let p = P { x: 1 };
        return need(p);
    }
expected:
  status: error
  error: { code: E2006, message_contains: "implement" }
```

```yaml
description: "A method that no bound of the type parameter declares is refused"
input:
  source: |
    trait Zero {
        fn zero(s: Self) -> i64;
    }
    fn one<T: Zero>(a: T) -> i64 {
        return a.size();
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2716, message_contains: "size" }
```

```yaml
description: "A call with the wrong number of explicit type arguments is refused"
input:
  source: |
    fn id<T>(x: T) -> T {
        return x;
    }
    fn main() -> i64 {
        return id::<i64, i64>(5);
    }
expected:
  status: error
  error: { code: E2038, message_contains: "type arguments" }
```

```yaml
description: "A type parameter that no argument fixes is refused"
input:
  source: |
    fn mk<T>() -> i64 {
        return 1;
    }
    fn main() -> i64 {
        return mk();
    }
expected:
  status: error
  error: { code: E2003, message_contains: "infer" }
```

```yaml
description: "One type parameter that gets two types is refused"
input:
  source: |
    fn pick<T>(x: T, y: T) -> T {
        return x;
    }
    fn main() -> i64 {
        let a = pick(5, 1.5);
        return 0;
    }
expected:
  status: error
  error: { code: E2001, message_contains: "T" }
```

```yaml
description: "Two type parameters of one function with the same name are refused"
input:
  source: |
    fn dup<T, T>(x: T) -> T {
        return x;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2039, message_contains: "duplicate type parameter" }
```

```yaml
description: "A where clause that names a name that is not a type parameter is refused"
input:
  source: |
    trait Zero {
        fn zero(s: Self) -> i64;
    }
    fn f<T>(x: T) -> T where U: Zero {
        return x;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2002, message_contains: "U" }
```

```yaml
description: "A trait with a supertrait and an impl of both"
input:
  source: |
    trait A {
        fn a(s: Self) -> i64;
    }
    trait B: A {
        fn b(s: Self) -> i64;
    }
    struct P {
        x: i64,
    }
    impl A for P {
        fn a(s: P) -> i64 {
            return 1;
        }
    }
    impl B for P {
        fn b(s: P) -> i64 {
            return 2;
        }
    }
    fn both<T: B>(t: T) -> i64 {
        return t.a() + t.b();
    }
    fn main() -> i64 {
        let p = P { x: 0 };
        return both(p);
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 3 } }
```

```yaml
description: "An impl of a trait without the impl of its supertrait is refused"
input:
  source: |
    trait A {
        fn a(s: Self) -> i64;
    }
    trait B: A {
        fn b(s: Self) -> i64;
    }
    struct P {
        x: i64,
    }
    impl B for P {
        fn b(s: P) -> i64 {
            return 2;
        }
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2006, message_contains: "implement" }
```

```yaml
description: "A trait that is its own supertrait is refused"
input:
  source: |
    trait A: A {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2040, message_contains: "contains itself" }
```

```yaml
description: "A trait that names itself in the arguments of its supertrait is refused"
input:
  source: |
    trait A<X> {
        fn a(s: Self) -> X;
    }
    trait B: A<B> {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2040, message_contains: "contains itself" }
```

```yaml
description: "A supertrait that is not declared is refused"
input:
  source: |
    trait B: Nope {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2701, message_contains: "Nope" }
```

## Cost for the compiler

| Part | Work | Size |
|------|------|------|
| Front end, parser | `GenericParameters` with bounds (the reference parses a list of names and stops at `:`); the `where` clause; `Identifier :: TypeArguments` before a call; the bounds of `TraitType`. Both front ends change. | small |
| Front end, checker | inference by structural matching (one binding per parameter); the conflict and the unfixed-parameter errors; bound lookup in the impl table of RFC 0024 and in the sets of the predeclared bounds; operators and method calls on a bounded value; associated types with bounds; `E2038`, `E2039` | large |
| Front end, desugaring | instance collection with the instance names of RFC 0023; a bounded method call becomes the call of the impl function in each instance | medium |
| Native lowering | none after the pass. The native backend refuses every generic function today (`lane.source.function_contract`); the instances are plain functions. | medium (prerequisite: the native backend admits the plain forms that the instances use) |
| Tests | rows above; a parity row (the equality test of RFC 0023); a determinism row for the instance order | small |

## Questions for the specification owner

### Decided by the specification owner (2026-11-24)

1. **Spelling of the explicit argument.** `f::<A>(x)`.
2. **Bounds on types.** There are no bounds on the type parameters of types in this edition (rule 14).
3. **Operators on a bounded value.** The built-in numeric bounds are in this RFC: `Numeric`, `Integer` and `Float`,
   predeclared trait names for closed sets of the numeric types (rule 4). Traits that a program declares for
   operators come in a later RFC.
4. **Supertrait spelling.** The supertrait list is enough; there is no `where Self: A` form. A trait that names
   itself with arguments (`trait B: A<B>`) is refused with `E2040` (rule 10).
5. **Partial and placeholder arguments.** There are no partial and no placeholder arguments (rule 6).
6. **Unfixed argument (rule 5).** Option A of DN-13 is decided, and no release warns first (rule 9).
7. **Defaults and const parameters.** As [RFC 0023](./0023-type-parameters-on-user-types.md), question 7: no
   defaults; const parameters get their own RFC.
8. **Code allocation.** `E2001`, `E2002`, `E2003`, `E2004` and `E2006` exist. `E2038` to `E2042` are
   assigned to RFC 0023 by the specification owner; this draft uses them as RFC 0023
   defines them, and `E2040` for a trait that names itself in its supertrait list. A call of a method that no bound
   declares gets its own code, `E2716` (rule 8), not `E2006`: `E2006` is a bound that a type does not satisfy, and
   rule 8 is a method that no bound declares. `E2716` is proposed by this draft and not yet assigned.

Bounds on an associated type (rule 13) come here by the decision of [RFC 0024](./0024-impl-forms.md), question 7.

### Open

- **Explicit type arguments of a method call and of a function of a generic block.** `GenericFunctionRef` takes one
  identifier, so `x.m(…)` and `Box::new(…)` infer their type arguments and have no explicit form.
- **Elementwise operators on a type parameter.** [Tensor operations](../../spec/v1.0/language.md#tensor-operations)
  gives `.*`, `./`, `.+` and `.-` the operand rule of the arithmetic operators, and on two scalar operands of one
  numeric type the value of the plain operator. Whether a value of a bounded type parameter supports them is not
  decided; until then they are not in the table of rule 4.
- **Other bound names of the standard library.** [Standard Library](../../spec/v1.0/stdlib.md) names `Ord`,
  `Display` and `Debug` as bounds. This RFC does not define them.
