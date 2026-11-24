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
| State | Draft (2026-11-24). Not yet accepted. |
| Number | Provisional. The specification owner assigns the final number. |
| Changes | `grammar-syntax.ebnf` (`FunctionTypeParameters` replaced by `GenericParameters`; `WhereClause`, `GenericFunctionRef` and the supertrait list of `TraitDeclaration` added; `TraitBounds` and `TraitBound` unmarked), `types.md` (Generics in Core v1, Traits and generics), `errors.md` |
| Owns | Bounds, the `where` clause, explicit type arguments at a call, and **supertraits** (`trait B: A`). No other draft defines them. |
| Depends on | [RFC 0024](./0024-impl-forms.md) (a bound names a trait; the meaning of a method call on a bounded value). The plain parameter list of [RFC 0023](./0023-type-parameters-on-user-types.md) is widened here. |
| Related | [RFC 0023](./0023-type-parameters-on-user-types.md), [RFC 0025](./0025-patterns.md) |

## Problem

Core v1 admits one unbounded type parameter on a function: `FunctionTypeParameters = "<" , Identifier , ">"`
([Types](../../spec/v1.0/types.md#generics-in-core-v1)). The text of [Types](../../spec/v1.0/types.md#traits-and-generics)
also specifies trait bounds and a `where` clause, and the old grammar had a bound inside the angle brackets
(`<T: Bound>`). The grammar has no `where` clause and no explicit type argument at a call, and the two spellings of
a bound do not agree. A function therefore cannot take two type parameters in the grammar, cannot require that a
parameter has a trait, and cannot name a type argument that no argument fixes.

Measured with the reference compiler v0.10.4 (`mindc check --no-fmt`):

| Source | Result |
|--------|--------|
| `fn id<T>(x: T) -> T` | accepted |
| `fn first<A, B>(a: A, b: B) -> A` and `fn id<T,>(…)` | accepted (an extension: the grammar has one name) |
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
FunctionDeclaration = "fn" , Identifier , [ GenericParameters ] , "(" , [ ParameterList ] , ")" ,
                      [ "->" , Type ] , [ WhereClause ] , Block ;

GenericParameters   = "<" , GenericParameter , { "," , GenericParameter } , [ "," ] , ">" ;
GenericParameter    = Identifier , [ ":" , TraitBounds ] ;
TraitBounds         = TraitBound , { "+" , TraitBound } ;
TraitBound          = TraitRef ;

WhereClause         = "where" , WherePredicate , { "," , WherePredicate } , [ "," ] ;
WherePredicate      = Identifier , ":" , TraitBounds ;

GenericFunctionRef  = Identifier , "::" , TypeArguments ;
PrimaryExpression   = … | GenericFunctionRef ;
```

`GenericParameters` replaces `FunctionTypeParameters`. It does not touch the `TypeParameterList` of
[RFC 0023](./0023-type-parameters-on-user-types.md): the type parameters of `struct`, `enum`, `trait` and `type`
stay plain names, and a bound on them is not defined by any draft (open question 2). The `where` clause is added
to `FunctionDeclaration` only. `TraitRef` and `TypeArguments` are the productions of RFC 0023. `where` is
already in the keyword list.

The supertrait list is a bound on the implementing type. It is added to the `TraitDeclaration` of RFC 0023 and
[RFC 0024](./0024-impl-forms.md):

```ebnf
TraitDeclaration    = "trait" , Identifier , [ TypeParameterList ] , [ ":" , TraitBounds ] ,
                      "{" , { TraitItem } , "}" ;
```

A `GenericFunctionRef` MUST be followed at once by a `CallOperator`: `id::<i64>(5)` is a call, and `id::<i64>`
alone is refused (a function is not a value in Core v1, [`E2037`](../../spec/v1.0/errors.md#e2037-function-name-used-as-a-value)).
The spelling `id<i64>(5)` is not part of the grammar, because `<` is the comparison operator. The token `::` is
already in the operator list; `Identifier "::" "<"` cannot be read as the variant path or the associated item
path of [RFC 0024](./0024-impl-forms.md), which have an identifier after `::`.

## Static rules

1. **Parameters.** The names of one `GenericParameters` MUST be pairwise different (`E2039` of RFC 0023). A
   type parameter is in scope in the parameter list, the result type, the `where` clause and the body. It is a
   type, not a value. The list has at least one name: `fn id<>(…)` is refused (the reference accepts it).
2. **Bounds.** A `TraitBound` MUST name a declared trait with the right number of arguments (`E2701` for an
   unknown trait, `E2038` for the argument count). A `WherePredicate` MUST name a type parameter of the same
   function (`E2002` otherwise). `T: A + B` and `where T: A, T: B` mean the same. A type parameter that has no
   bound MAY be moved (passed, returned, bound to a name) and nothing else.
3. **What a bounded value can do.** A value of type `T` with the bound `B` supports the method calls
   `x.m(args)` where `m` is a method of `B`. It does not support an operator: `+`, `<` and `==` need operator
   traits that this RFC does not define (open question 3). A call of a method that no bound declares is refused
   (rule 7).
4. **Inference.** At a call `f(args)` each type parameter is bound from the types of the arguments by
   structural matching of the parameter types. A parameter that two arguments bind to different types is refused
   with `E2001`. A parameter that no argument binds is refused with `E2003` (cannot infer type) unless the call
   names it with rule 5. No default type is chosen.
5. **Explicit arguments.** `f::<A, B>(args)` gives every type parameter of `f` in order. The count MUST equal
   the number of parameters (`E2038`). A partial list and a placeholder are not part of this RFC. An argument
   that rule 4 would infer to another type is refused with `E2001`.
6. **Bound satisfaction.** After inference, each bound of each parameter MUST be satisfied: the type that the
   parameter gets MUST have an `impl` of the trait ([RFC 0024](./0024-impl-forms.md), rule 6). A missing impl is
   refused with `E2006` (trait bound not satisfied, existing).
7. **Method on a type parameter.** A call `x.m(args)` where `x` has a type parameter type and no bound declares
   `m` is refused with `E2006`. (A call on a type that is known resolves by RFC 0024, rule 8.)
8. **Compatibility.** `fn id<T>(x: T) -> T` keeps its meaning: one parameter, no bound, inferred at each call.
   A program that is valid under Core v1 and gives a type argument that is fixed by an argument is valid
   under this RFC. A call that the reference accepts today and whose argument no argument fixes becomes an
   error (`E2003`); the specification owner decided this in
   [decision note DN-13](./decision-notes.md#dn-13-a-generic-call-whose-type-argument-is-not-fixed) (option A),
   and [Types](../../spec/v1.0/types.md#generics-in-core-v1) already states it for Core v1.
9. **Supertraits.** Each `TraitBound` of a supertrait list MUST name a declared trait with the right number of
   arguments (`E2701` for an unknown trait, `E2038` for the argument count). A trait MUST NOT be its own
   supertrait, directly or through other traits; a cycle is refused with `E2040` (the code of
   [RFC 0023](./0023-type-parameters-on-user-types.md), rule 7, for a type that contains itself). The names of
   the supertrait list are not type parameters: `Self` is the only type that it constrains.
10. **Impl of a trait with supertraits.** `impl B for S` MUST be accompanied by `impl A for S` for every
    supertrait `A` of `B`, in the program or in the modules that it imports. A missing one is refused with
    `E2006` (trait bound not satisfied) at the `impl B` block.
11. **Supertrait use.** A value whose type parameter has the bound `B` supports the methods of `B` and of every
    supertrait of `B` (rule 3 extends to them), and satisfies a bound `A` of a call.

## Meaning as a desugaring

A bound and a supertrait list are checks and have no run-time form. A generic call is a call of a plain function, one for each distinct
list of arguments, in the way that [RFC 0023](./0023-type-parameters-on-user-types.md) gives for types.

```mind
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

is the program

```mind
struct P { x: i64, }
fn Zero__P__zero(s: P) -> i64 { return 0; }
fn first__P__P(a: P, b: P) -> P {
    return a;
}
fn main() -> i64 {
    let p = P { x: 1 };
    let r = P { x: 2 };
    let q = first__P__P(p, r);
    return q.x;
}
```

The instance name is the function name, then `__` and the canonical spelling of each argument, joined by `__`.
A call `x.m(args)` on a value of a type parameter type is, in the instance, the call that
[RFC 0024](./0024-impl-forms.md) rule 8 selects for the argument type. The explicit form `f::<A>(x)` and the
inferred form `f(x)` give the same instance. The written-out program is the oracle for the equality test: the
bytes of the generic program equal the bytes of the written-out program.

## Proposed conformance rows

Proposals. No compiler accepts the accept row today. Of the reject rows, the reference gives the stated result
only for the rows marked "measured" (`E1001` is its own code for the form, not the proposed code). The rows
that declare a trait use the `;` of the grammar of [RFC 0024](./0024-impl-forms.md), and the rows that build a
record use the record literal of [RFC 0025](./0025-patterns.md#record-literal).

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
| Front end, parser | `GenericParameters` with bounds (the reference parses a list of names and stops at `:`); the `where` clause; `Identifier :: TypeArguments` before a call. Both front ends change. | small |
| Front end, checker | inference by structural matching (one binding per parameter); the conflict and the unfixed-parameter errors; bound lookup in the impl table of RFC 0024; method calls on a bounded value; `E2038`, `E2039` | large |
| Front end, desugaring | instance collection with a canonical name, shared with RFC 0023; a bounded method call becomes the call of the impl function in each instance | medium |
| Native lowering | none after the pass. The native lane refuses every generic function today (`lane.source.function_contract`); the instances are plain functions. | medium (prerequisite: the lane admits the plain forms that the instances use) |
| Tests | rows above; a parity row (generic program equals the written-out program); a determinism row for the instance order | small |

## Open questions for the specification owner

1. **Spelling of the explicit argument.** `f::<A>(x)` (this draft) or another form. `f<A>(x)` is ambiguous with
   comparison; the reference reads it as one.
2. **Bounds on types.** This draft defines bounds and `where` for functions only. The parameters of a `struct`,
   an `enum`, a `type` and a `trait` are plain names (RFC 0023), so a bound on them, and a `where` clause after
   such a declaration, are not defined. Wanted? A bound on a type parameter needs a rule for the check at each
   use `S<i64>` and for what the bound allows inside the declaration.
3. **Operators on a bounded value.** `a + b` for `T: Add` needs operator traits and their names. Define them
   here, in a later RFC, or define the numeric types as built-in bounds?
4. **Supertrait spelling.** This draft owns `trait B: A + C`. Is the list enough, or is a `where Self: A` form
   wanted too? Is a trait that names itself with arguments (`trait B: A<B>`) allowed?
5. **Partial and placeholder arguments.** `f::<_, i64>(x)`: wanted?
6. **Unfixed argument (rule 4).** Option A of DN-13 is decided. A refusal changes programs that the
   reference accepts today; one release with a warning first?
7. **Defaults and const parameters.** Out of scope, as in RFC 0023.
8. **Code allocation (settled).** `E2001`, `E2002`, `E2003` and `E2006` exist. `E2038`, `E2039` and `E2040` are
   reserved for RFC 0023 by the specification owner; this draft uses `E2038` and `E2039` as RFC 0023 defines them,
   and `E2040` for a supertrait cycle. It adds no code.
