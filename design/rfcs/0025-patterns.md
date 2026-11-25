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

# RFC 0025: Patterns (binding patterns, literal, variant and record patterns, guards) and the record literal

| Field | Value |
|-------|-------|
| State | Draft (2026-11-24). Not yet accepted. The specification owner decided the questions of this draft on 2026-11-24 (see [Questions](#questions-for-the-specification-owner)). |
| Number | Provisional. The specification owner assigns the final number. |
| Changes | `grammar-syntax.ebnf` (`Pattern`, `MatchArm`, record literal), `language.md` (new section on patterns; exhaustiveness), `types.md` (removes the dot spelling `Enum.Variant` of a variant), `errors.md` (`E2310`, `E2311`, `W2312`, `E2313`, `E2314`) |
| Depends on | none. Enum variant patterns use the enum declaration of the candidate block. |
| Related | [RFC 0023](./0023-type-parameters-on-user-types.md), [RFC 0024](./0024-impl-forms.md) (the variant path `E::B` in an expression) |

## Problem

`Pattern` has three forms in the grammar: an identifier, a tuple of patterns and `_`. It is used by `let`,
by `for` and by the arms of `match`. The language needs more, and the reference compiler v0.10.4 and the
grammar disagree in both directions.

Measured with the reference compiler v0.10.4 (`mindc check --no-fmt`):

| Source | Result |
|--------|--------|
| `for (a, b) in xs { }` (the grammar derives it) | `E1001`, `expected loop variable name` (3:9) |
| `let (a, b): (i64, i64) = (1, 2);` (the grammar derives it) | `E1001`, ``expected '=', found Some(':')`` (2:15) |
| `match x { 0 => 1, _ => 2, }` (a literal pattern) | accepted; no production derives it |
| `match e { E::A => 1, E::B(v) => v, }` | accepted; no production derives it |
| `match p { P { x } => x, }` (a record pattern) | accepted; no production derives it |
| `match x { n if n > 1 => n, _ => 0, }` (a guard) | accepted; no production derives it |
| `match x { n @ 1 => n, _ => 0, }` | `E1001`, ``expected `=>` after match pattern`` (3:11) |
| `match x { &n => n, }` | `E1001`, `expected pattern` (3:9) |
| `match x { A => 1, _ => 2, }` where `A` names a variant of the scrutinee's enum (a bare identifier that is not the final arm) | refused, `E2301` ([Error Catalog](../../spec/v1.0/errors.md#e2301-non-final-enum-variant-binding-collision)) |
| `match x { n => 1, }` where `n` names a variant of the scrutinee's enum and is the only, final arm | accepted without a diagnostic (the name is a catch-all binding) |
| a `match` that omits a case (`match b { true => 1, }` for a `bool` `b`) | accepted: no exhaustiveness check |
| `P { x: 1 }` (a record literal) | accepted; no production derives it |
| `if b { }`, `while b { }`, `match x { }` with an identifier `b` or `x` | `E1001`, ``expected '{', found Some('r')`` (`Some('e')` for `if b { } else { }`; the reference appears to read `b { }` as a record literal) |

The native backend refuses `match` (`lane.source.match`), tuples (`lane.source.tuple`) and `for` over a
collection (`lane.source.for_each`). The grammar derives the first two of those forms.

## Grammar change

```ebnf
Pattern          = IdentifierPattern
                 | TuplePattern
                 | WildcardPattern
                 | LiteralPattern
                 | VariantPattern
                 | RecordPattern ;

LiteralPattern   = [ "-" ] , IntegerLiteral | BooleanLiteral | StringLiteral ;
VariantPattern   = Identifier , "::" , Identifier , [ "(" , [ PatternList ] , ")" ] ;
RecordPattern    = Identifier , "{" , [ FieldPatternList ] , "}" ;
FieldPatternList = FieldPattern , { "," , FieldPattern } , [ "," ] ;
FieldPattern     = Identifier , [ ":" , Pattern ] ;

MatchArm         = Pattern , [ "if" , Expression ] , "=>" , ( Expression , "," | Block ) ;

RecordLiteral    = Identifier , "{" , [ FieldInitList ] , "}" ;
FieldInitList    = FieldInit , { "," , FieldInit } , [ "," ] ;
FieldInit        = Identifier , ":" , Expression ;
PrimaryExpression = … | RecordLiteral ;
```

`FieldPattern = Identifier` alone binds the field to a variable of the same name. A float literal is not a
pattern (equality on floats in a pattern has no single meaning). The binding pattern `x @ p`, the reference
pattern `&p`, or-patterns (`1 | 2`), range patterns (`1..=3`) and `..` in a record pattern are not part of the
language; none of them is derived.

### Variant path

`E::B` is the only spelling of a variant, in a pattern (`VariantPattern`) and in an expression (`AssociatedValue` of
[RFC 0024](./0024-impl-forms.md)). This RFC removes the dot spelling `Enum.Variant` from
[Types](../../spec/v1.0/types.md#module-qualified-type-ownership). `E.B`, where `E` names an enum, is refused with
`E2002`, and the message names `E::B`.

### Tuple index

The tuple index is the form that [decision note DN-11](./decision-notes.md#dn-11-tuple-index-and-range-index)
decides. The normative text has it (`TupleIndexOperator` of
[`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf), [Tuple index](../../spec/v1.0/language.md#tuple-index)).
This RFC does not change it; its plain forms use it. `t.i`, with `i` a `DecimalInteger` with no sign and no prefix,
reads component `i` of a tuple value, counted from 0. It needs a tuple type and an index below the arity of that
type; otherwise it is refused with `E2404`. Where the parser expects the `DecimalInteger` of a tuple index and
the next token is a float literal of the form digits "." digits (no exponent, no suffix), the token is read as two
tuple indices: `t.0.1` means `(t.0).1`. `t[i]` on a tuple has no meaning and is refused with `E2404`, and the
diagnostic names the form `e.N`.

### Record literal

A record literal has the form `Name { f: e, … }` and builds a value of the declared `struct` `Name`.
The head of `if`, `while`, `for … in` and `match` is an `Expression` followed by a `Block`, so `b { }`
there is ambiguous. **Rule:** a record literal MUST NOT stand, unparenthesised, in the head expression of
`if`, `while`, `for … in` or `match`. In those positions an identifier followed by `{` always starts the
block. A record literal in the head needs parentheses: `if (P { x: 1 }).x > 0 { … }`.
This rule makes `if b { }` and `match x { }` valid, which the reference refuses today.

### For-loop pattern

`for Pattern in Expression Block` binds the pattern to **each element** of the iterable and destructures it.
A loop that needs an index and a value uses a library function that yields pairs, not a loop form.
`for (a, b) in xs { B }` needs `xs` to have tuple elements of arity two.

## Static rules

1. **Typing.** A pattern has the type of its scrutinee. A tuple pattern needs a tuple type of the same
   arity. A literal pattern needs a scrutinee of the type of the literal (`i64`-family, `bool`, `String`).
   A variant pattern needs a scrutinee of the named enum and the payload arity of that variant. A record
   pattern needs a scrutinee of the named `struct`, and every field it names MUST exist.
2. **Bindings.** A name is bound at most once in one pattern (`E2313`). A binding has the type of the
   part of the scrutinee that it matches. Its scope depends on the position of the pattern:
   in a `match` arm it is the guard and the arm body, and nowhere else; in a `let` it is the rest of the
   enclosing block, from the end of the `let` statement; in a `for` it is the body of the loop.
3. **Irrefutable positions.** The pattern of a `let` and of a `for` MUST be
   irrefutable: an identifier, `_`, a tuple of irrefutable patterns, or a record pattern whose field
   patterns are irrefutable. A refutable pattern there is refused with `E2310`.
4. **Exhaustiveness.** The arms of a `match` MUST cover every value of the scrutinee type. An arm with a
   guard does not count toward coverage. A `bool` needs both literals or a catch-all arm. An integer or
   string scrutinee needs a catch-all arm (`_` or an identifier). An enum needs every variant or a
   catch-all arm. A missing case is an error, refused with `E2311`. An arm that no value can reach is a warning
   (`W2312`), not an error.
5. **Variant against binding.** An unguarded arm whose pattern is a bare identifier equal to the name of a variant
   of the scrutinee's enum is refused. When the arm is not the final arm, the code is `E2301` (the existing rule of
   the [Error Catalog](../../spec/v1.0/errors.md#e2301-non-final-enum-variant-binding-collision)). When it is the
   final arm, the code is `E2314`. The message names the variant pattern `E::A` and the rename of the binding. An
   arm with a guard, `A if g => …`, is a binding and is not refused.
6. **Guards.** A guard is an `Expression` of type `bool`. It MAY read the bindings of its pattern. It MUST
   NOT assign. It MAY call a function; the effects of the call happen when the guard runs (rule 7).
7. **Order.** The arms are tried from the first to the last. For one arm the pattern is tested first, and the
   guard runs only when the pattern matched, at most once in one execution of the `match`. The first arm whose
   pattern matches and whose guard is true is chosen, and no guard of a later arm runs. A guard therefore has
   its effects in this order and in no other, which keeps the program deterministic.

## Meaning as a desugaring

Every form in this RFC has a plain form in the existing core.

**Tuple `let`.** `let (a, b) = e;` is `let t = e; let a = t.0; let b = t.1;` where `t` is a fresh name and
`t.i` is the tuple index.

**For-loop pattern.** `for P in c { B }` is `for e in c { let P = e; B }` with `e` fresh. With a tuple
pattern: `for (a, b) in c { B }` is `for e in c { let (a, b) = e; B }`.

**Match.** `match s { p1 if g1 => a1, p2 => a2, }` is an `if` chain on a fresh binding `t = s`:
`if test(p1, t) { bind(p1, t); if g1 { a1 } else { next } } else { next }`, where `next` is the rest
of the chain and the last `next` is a trap (no value reaches it after rule 4). `test` compares a literal,
compares the discriminant of an enum, or is `true` for an identifier, `_` and a record pattern; `bind` is the
sequence of `let` that read the matched parts. A literal integer arm list is a chain of `==` tests.

**Record literal.** `P { x: 1, y: 2 }` builds the value of `struct P` with the fields in the order of the
declaration. The order of the field initialisers in the source does not change the order in which the
expressions are evaluated: they run from the first to the last as written, then the record is built.

These plain forms are the parity oracle for the parser rows: the bytes of a program with the form equal the
bytes of the program with the plain form written out.

## Proposed conformance rows

Proposals. The reference refuses the first two accept rows today. The codes `E2310`, `E2311`, `W2312`, `E2313`
and `E2314` are the codes of this draft; `E2001`, `E2002` and `E2301` exist, and `E2404` is the code of the tuple index
([decision note DN-11](./decision-notes.md#dn-11-tuple-index-and-range-index)).

```yaml
description: "A tuple pattern as the for-loop variable destructures each element"
category: syntax
profile: cpu
input:
  source: |
    fn main() -> i64 {
        let xs = [(1, 2), (3, 4)];
        let mut s = 0;
        for (a, b) in xs {
            s = s + a * b;
        }
        return s;
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 14 } }
```

```yaml
description: "A typed tuple let"
input:
  source: |
    fn main() -> i64 {
        let (a, b): (i64, i64) = (1, 2);
        return a + b;
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 3 } }
```

```yaml
description: "A tuple index of a tuple index reads two components"
input:
  source: |
    fn main() -> i64 {
        let t = ((1, 2), 3);
        return t.0.1 + t.1;
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 5 } }
```

```yaml
description: "A tuple index at the arity of the tuple is refused"
input:
  source: |
    fn main() -> i64 {
        let t = (1, 2);
        return t.2;
    }
expected:
  status: error
  error: { code: E2404, message_contains: "tuple" }
```

```yaml
description: "The index operator on a tuple is refused"
input:
  source: |
    fn main() -> i64 {
        let t = (1, 2);
        return t[0];
    }
expected:
  status: error
  error: { code: E2404, message_contains: "tuple" }
```

```yaml
description: "A for-loop pattern of arity three over pairs is refused"
input:
  source: |
    fn main() -> i64 {
        let xs = [(1, 2)];
        for (a, b, c) in xs {
        }
        return 0;
    }
expected:
  status: error
  error: { code: E2001, message_contains: "arity" }
```

```yaml
description: "A for-loop pattern over scalar elements is refused"
input:
  source: |
    fn main() -> i64 {
        let xs = [1, 2];
        for (a, b) in xs {
        }
        return 0;
    }
expected:
  status: error
  error: { code: E2001, message_contains: "tuple" }
```

```yaml
description: "A match on an integer without a catch-all arm is refused"
input:
  source: |
    fn k(x: i64) -> i64 {
        return match x {
            0 => 1,
            1 => 2,
        };
    }
    fn main() -> i64 {
        return k(0);
    }
expected:
  status: error
  error: { code: E2311, message_contains: "not exhaustive" }
```

```yaml
description: "A refutable pattern in a let is refused"
input:
  source: |
    fn main() -> i64 {
        let 1 = 1;
        return 0;
    }
expected:
  status: error
  error: { code: E2310, message_contains: "refutable" }
```

```yaml
description: "A name bound twice in one pattern is refused"
input:
  source: |
    fn main() -> i64 {
        let (a, a) = (1, 2);
        return a;
    }
expected:
  status: error
  error: { code: E2313, message_contains: "bound twice" }
```

```yaml
description: "A final bare identifier arm with the name of a variant is refused"
input:
  source: |
    enum E {
        A,
        B,
    }
    fn k(e: E) -> i64 {
        return match e {
            E::A => 1,
            B => 2,
        };
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2314, message_contains: "E::B" }
```

```yaml
description: "An empty block after an identifier is a block, not a record literal"
input:
  source: |
    fn main() -> i64 {
        let b = true;
        if b {
        }
        return 0;
    }
expected:
  status: success
```

## Cost for the compiler

| Part | Work | Size |
|------|------|------|
| Front end, parser | `for` takes a `Pattern`; the typed tuple `let`; guard; literal, variant and record patterns; the record literal and the head rule; the tuple index and its reading rule. The reference keeps two front ends in step; both change. | medium |
| Front end, checker | pattern typing; irrefutable positions; exhaustiveness (a usefulness check over the constructors of the scrutinee type); duplicate bindings; the final-arm rule; five new diagnostics | large |
| Front end, desugaring | the four plain forms above | medium |
| Native lowering | `for` over a fixed array is an indexed `while`, which the native backend builds today. A tuple pattern is a replacement of one tuple by scalars (no tuple value crosses a call). An integer or wildcard `match` is an `if` chain, which the native backend builds. A variant `match` needs the enum admission of RFC 0023. | medium, in steps |
| Tests | the rows above; one desugar-parity row for each plain form; the mutation row that removes the exhaustiveness arm | medium |

## Questions for the specification owner

### Decided by the specification owner (2026-11-24)

1. **Exhaustiveness (rule 4).** A non-exhaustive `match` is an error (`E2311`) from the first edition that
   accepts this RFC. There is no warning edition.
2. **Binding and reference patterns.** `x @ p` and `&p` are not part of the language.
3. **Or-patterns and ranges.** `1 | 2` and `1..=3` are not in this RFC. One later RFC holds them, together with
   `..` in a record pattern (question 6).
4. **Variant path spelling.** `E::B` is the only variant path. The dot form leaves the Types text
   ([Variant path](#variant-path)).
5. **Float and `String` literal patterns.** A `String` literal pattern is allowed. A float literal pattern is not.
6. **Record pattern with `..`.** Not here. It comes with the later RFC of question 3.
7. **Tuple index.** The grammar defines `t.0` ([decision note DN-11](./decision-notes.md#dn-11-tuple-index-and-range-index),
   [Tuple index](../../spec/v1.0/language.md#tuple-index)).
   `t[0]` on a tuple is not defined. The plain form of the tuple `let` uses the tuple index.
8. **Codes.** The proposed codes are assigned, because they are free in the catalog: `E2310` (refutable pattern in
   `let` or `for`), `E2311` (`match` not exhaustive), `W2312` (arm that no value can reach), `E2313` (name bound
   twice). Question 9 takes `E2314` from the same block.
9. **A variant name as the final arm.** A final bare identifier arm whose name equals a variant of the matched
   enum is an error with its own code, `E2314`, not a warning (rule 5).

### Open

- **Record patterns that omit fields.** Rule 1 lets a record pattern name some of the fields of the `struct`.
  Whether it MUST name every field while `..` is not in the language is not decided.
