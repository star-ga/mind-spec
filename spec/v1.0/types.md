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

# Type System (Normative)

The MIND type system enforces static correctness and enables efficient differentiation. This chapter
formalises type formation, typing judgements, inference constraints, and trait coherence. It aligns
with the reference notes in
[`star-ga/mind/docs/type-system.md`](https://github.com/star-ga/mind/blob/main/docs/type-system.md).

## Type formation

The following forms are part of the core language:

- **Primitive types**: `i32`, `f64`, `bool`, `unit`.
- **Composite types**: tuples `(T1, T2, ...)`, arrays `[T; n]`, and structs defined via `struct`.
- **Function types**: `(T1, ..., Tn) -> U`.
- **Trait objects**: `dyn Trait` for traits marked as object-safe *(specified for full v1.0; not
  yet implemented in the executable subset — see [Traits and generics](#traits-and-generics))*.
- **Differentiable wrappers**: `diff T` identifies values that participate in differentiation (see
  [Automatic differentiation](./autodiff.md)).

Implementations MAY extend the set of primitive types but MUST document the extensions.

> **Compiler integration update, pending release (informative).** The reference
> compiler source at `4fd65cfb` refuses an `iN` or `uN` annotation with `N`
> greater than 64 (`i128`, `u128`, `i256`, ...) during checking. The refusal covers
> `let` annotations, parameters, return types, `as` casts, `const` and extern
> `const` types, type-alias targets, struct fields, enum payloads, extern function
> signatures, closure and trait-method signatures, and the same annotations
> nested inside generic, tuple, array, reference and pointer types. Widths up to
> 64 (for example `u8`, `i16`, `u32`, `i64` and `u64`) still check, and tensor
> dtype strings are outside this check. Before this change such annotations were
> accepted outside extern function signatures, whose C-ABI check already refused
> them, and (as the commit records for a `let` binding) their values were computed
> in 64 bits. The check does not depend on a cargo feature. The compiler test
> `wide_integer_types` exercises the `let`, parameter and return positions; the
> other positions go through the same validation walk and have no dedicated
> control. This check refuses only widths greater than 64 that fit in 32 bits;
> an unrecognised width of 64 bits or less (for example `i24`) is not refused by
> this check and is not computed at its written width. This does not change the
> published v0.10.2 artifact.

## Typing judgements

Typing rules are written using natural deduction. The primary judgement `Γ ⊢ e : T` reads “under
context Γ, expression e has type T”. Implementations MUST reject programs that violate any
applicable rule. Selected core rules include:

- **Variable**: if `x : T ∈ Γ` then `Γ ⊢ x : T`.
- **Let binding**: if `Γ ⊢ e1 : T1` and `Γ, x : T1 ⊢ e2 : T2` then `Γ ⊢ let x = e1 in e2 : T2`.
- **Function abstraction**: if `Γ, x1 : T1, ..., xn : Tn ⊢ e : U` then `Γ ⊢ fn(x1 : T1, ..., xn : Tn) -> U { e } : (T1, ..., Tn) -> U`.

### Fixed-array literal cardinality

An array literal initializing an explicitly annotated `let` or `const` binding
of type `[T; n]` MUST contain exactly `n` elements. This rule applies at every
lexical depth, including function, branch, and loop bodies. Parentheses around
the literal do not change its cardinality. When `T` is itself a fixed-array
type, each nested array literal MUST satisfy its corresponding extent.

A cardinality mismatch MUST be rejected during static checking. The diagnostic
MUST identify the literal and report both the required and actual element
counts; execution failure at a later call site is not an adequate substitute.
This rule concerns literal cardinality; nonliteral initializers remain subject
to the ordinary type compatibility rules.

**Implementation coverage (informative, pending release).** The normative rule
above is limited to annotated `let` and `const` bindings. Compiler commit
`c4c7b034` additionally applies the cardinality check, and an element-type
check, to the value supplied for a struct-literal field whose declared type is
exactly `[i64; N]` (an array literal, or a non-literal value of known type;
module-local type aliases resolved). The checker reports `E2001` during checking
when:

- the literal does not have `N` elements;
- an element has a type known not to be `i64`, for example a float literal, a
  bool literal or a comparison or logical result, a record value, a call whose
  lexically nearest declaration returns a known type other than `i64`, a `for`
  range variable (typed `i32` by this check) used without `as i64`, or a local
  or parameter of another known type;
- a non-literal value has a known type other than `[i64; N]`.

An `if`/`else` expression or a block inside an element is checked branch by
branch through its tail, so a known-bad branch is not hidden by an unknown
sibling. The same commit also rejects, with `E2001`, a float literal reached
through an `if`/`else` branch or block tail of a fixed-array return whose
element type is an integer type. Fields whose element type is not `i64` are not
checked by this pass, a struct declared in another source has no schema for it,
and a fact the checker cannot prove (an unresolved identifier or a method call,
for example) is deferred rather than rejected. The pass runs in builds with the
`std-surface` feature, which the reference compiler enables by default. The
compiler controls are its `fixed_array_return_lengths` tests.

This coverage does not extend the normative rule to struct-literal fields;
whether it should become a rule is a decision pending for 1.7.0. It does not
change the published v0.10.2 artifact.

A comprehensive derivation catalogue is maintained in the implementation notes
([informative](https://github.com/star-ga/mind/blob/main/docs/type-system.md)).

## Record identity and fixed-array values

A value of a user-defined struct type denotes a record with identity. A new
struct literal creates a new record. Binding, assigning, passing or returning
an existing record value MUST preserve its identity; none of these operations
implicitly clones its fields. A field mutation through one reference MUST be
visible through other references to that record. Rebinding a variable changes
which record that variable denotes; it does not replace the record seen by
other references.

A fixed array `[T; n]` is a value container. Binding, assigning, passing,
returning or reading a fixed-array field copies the array's element values.
Replacing an element in the copy MUST NOT replace the corresponding element
in the original container. When `T` is a struct type, each element value is a
record reference: copying the container preserves those record identities,
not recursive copies of the records. Mutating a referenced record is therefore
visible through both containers. The same element-value rule applies at each
fixed-array nesting level that an implementation supports.

These rules distinguish the two operations below:

| Operation | Required observable behavior |
|---|---|
| Pass record `r` to a function that mutates one of its fields | The caller sees the field mutation through `r`. |
| Copy fixed array `a` to `b`, then replace `b[0]` | The element value stored in `a[0]` is unchanged. |
| Copy a fixed array of records, then mutate a record reached through the copy | Both arrays still refer to that mutated record. |
| Bind `c` to record `b`, then assign `c.xs[0]` where `xs` is a fixed-array field | The update is visible through `b.xs[0]`, because `b` and `c` denote one record. |
| Read `b.xs` into a separate fixed-array variable, then replace an element in that variable | The element stored in the record's `xs` field is unchanged. |

Record identity is a language property, not a numerical machine address.
Physical handles MAY implement references, but their carrier width MUST NOT
substitute for the record's semantic type. A backend MUST NOT serialize a
machine address as a canonical language-level identity. These rules do not add
an implicit record-to-integer conversion, prescribe record equality, or extend
permission to mutate through a restricted reference.

### Implementation coverage

The compiler source at
[`143bdd8f`](https://github.com/star-ga/mind/commit/143bdd8f8f85d0bb82e82d88cce0d0725c1998f5)
retains caller-visible record mutation and value-copy fixed-array containers
on its Rust/MLIR shared-library path. The
[`aggregate_const_run` controls](https://github.com/star-ga/mind/blob/143bdd8f8f85d0bb82e82d88cce0d0725c1998f5/tests/aggregate_const_run.rs)
execute record parameters and fixed arrays of record references. Declared
fixed-array returns now preserve the record element type for direct and local
receiver field reads, including aliases resolved in the defining module.
An unrelated caller alias cannot reinterpret an imported return. Conflicting
imported return schemas refuse before linking. Executing controls cover these
paths in
[`fixed_array_struct_field_run`](https://github.com/star-ga/mind/blob/143bdd8f8f85d0bb82e82d88cce0d0725c1998f5/tests/fixed_array_struct_field_run.rs)
and
[`cross_module_field_access_run`](https://github.com/star-ga/mind/blob/143bdd8f8f85d0bb82e82d88cce0d0725c1998f5/tests/cross_module_field_access_run.rs).
This source coverage is not a new published compiler artifact or evidence of
pure-MIND native-ELF support.

[Compiler PR #263](https://github.com/star-ga/mind/pull/263), merged at
[`1833f095`](https://github.com/star-ga/mind/commit/1833f095ce74b966287f27932c92733529c08b53),
extends reference record-field fixed arrays to `i8`, `u8`, `i16` and `u16`.
Executing shared-artifact controls preserve element width and signedness and
neighboring fields (`aa56de24`), and exactly-once receiver/index/right-hand-side
evaluation (`5a4e4b02`). Known non-integer values, such as floats, and known
opaque handles assigned to narrow elements are refused with
[`E2036`](./errors.md#e2036-non-integer-value-stored-into-a-narrow-integer-element)
(`0a8b34a5`), rather than truncated; an opaque handle would otherwise become an
address-dependent value. The eight-byte cell stride is this reference backend's
layout, not a new language-level layout mandate.

The pure-MIND native emitter has a separate, emitter-level, read-only slice for
record fields of type `[i64; N]` and `[u8; N]` with `1 <= N <= 4096` (a
capability bound of that emitter, not a language limit). The `i64` form landed
in `c4c7b034` and the `u8` form in `9b23e3fe`. The slice admits construction
from a direct array literal, whole-field reads and bounds-checked indexed
reads. Indexed write-back through the field, aliases, non-literal construction,
other element widths, aggregate cells and multi-module ownership are refused. The
slice is reachable only through the emitter's self-test entry, which takes a
caller-supplied trace hash. The emitter's other entry, which computes its own
canonical trace hash, returned no artifact for the `direct.mind` fixture, and the
standalone bootstrap also refuses that fixture; the canonical mic@3 trace path's
layout precondition fails closed for every record that has a fixed-array field
(`f7bba8c6` for field reads, `a80b67ea` for construction), so the slice is not
reachable through that path. The slice is therefore not native-profile support,
not standalone-compiler support, and is in no published artifact, including
v0.10.2.

Struct-owned fixed arrays of records remain unsupported: checking may succeed,
but shared-library emission refuses with `E6009` and leaves no artifact.
Interpreter field mutation is also explicitly unsupported. A backend that
cannot implement an operation under the identity and value rules MUST refuse
it; it MUST NOT silently choose deep-copy semantics, ignore a mutation, or
report a passing test that omitted the mutation. Cross-backend coverage remains
limited to the operations independently verified on each backend.

## Type inference

Implementations MUST support bidirectional type inference:

- Expressions without annotations are checked by propagating expected types from their context.
- When inference fails, diagnostics MUST include the expression span and the conflicting types.
- Generic functions MUST infer type parameters when sufficient information is available. Otherwise
  the caller MUST provide explicit type arguments.

Inference relies on unification with occurs checks. Implementations SHOULD emit informative error
messages when inference requires additional annotations.

### Struct literal bindings

A literal of a declared struct denotes that struct, including when its local
binding omits an annotation. Integer field initializers such as `0` MUST NOT
turn the aggregate binding into an `i32` scalar. Replacing a mutable binding
with a value of the same struct type MUST NOT produce an integer-narrowing
diagnostic merely because the replacement comes from a function.

The declared field widths govern field values. A genuine implicit `i64` to
`i32` scalar assignment still requires the narrowing diagnostic. A known
struct binding cannot be replaced with a numeric scalar; the implemented
confident-scalar check reports `E2026`. A fresh lexical binding shadows the
previous binding and does not inherit its struct identity.

Implementation status: pending compiler integration. The regression exercises
check/build agreement, full-width values and deterministic shared-library
emission. It does not promote full structural type inference or native-ELF
coverage beyond the independently verified backend subset.

### Core IR integration

The type checker participates directly in Core IR construction:

- **Symbol tables** feed module inputs. Each declared value is materialised as an `Input` instruction
  carrying its resolved tensor type so that the IR verifier can enforce the single-definition rule.
- **Shape validation** rejects tensors with zero or negative extents. Scalars (rank-0) are exempt and
  remain represented with an empty shape.
- **Operation typing** mirrors the IR instruction set. For arithmetic operations the operands MUST
  share a dtype; shape compatibility follows the broadcasting rules in
  [Shapes](./shapes.md#broadcasting). Scalar operands implicitly broadcast to the non-scalar
  operand's shape. Batched `MatMul` operations additionally broadcast leading dimensions and enforce
  that the contracting dimension matches.
- **Verification before emission**: translators are expected to reject programs with unknown dtypes,
  incompatible shapes, or undeclared symbols before emitting IR. This aligns the surface-language
  diagnostics with the invariants described in [Core IR](./ir.md#verification).

## Module-qualified type ownership

> **Compiler integration update, pending release.** The project-module source
> implementation under review resolves qualified imported types and enum
> variants as described here, and compiler commit `1def5dde` adds the
> bare-headed enum variant resolution described below. This does not change the
> published v0.10.2 artifact.

For a manifest project, the defining source module owns each enum, struct, and
type alias. A qualifier MUST resolve to the current module or to exactly one
imported module, and a type referenced from another module MUST be exported by
that owner. The terminal import alias (`defs.Color`), full module path
(`nested.defs.Color`), and crate-qualified path (`crate.nested.defs.Color`) all
retain the same defining owner. The rule applies recursively in reference,
fixed-array, tuple, generic-argument, raw-pointer, and external-function type
positions. Same-named types in different modules remain distinct.

An unknown, unimported, non-exported, or ambiguous owner MUST be refused with
`E2002` during both checking and artifact-producing builds. A refused build
MUST leave no artifact.

This clarifies the owner rule above for bare-headed enum variant paths. In a
manifest project, a bare-headed enum variant path whose enum is not
declared in the current module (`Table::Raw`, `Table.Raw`, or the same head in a
pattern) resolves through that module's imports. When exactly one import exports
a type of that name and that type is an enum, its module is the owner, and the
value, payload-constructor, dot-form and pattern spellings all denote the
owner's variant. A type declared in the current module keeps lexical
precedence. A bare-headed `Enum::Variant` value or pattern MUST be refused
with `E2002` during checking and artifact-producing builds, and a refused build
MUST leave no artifact, when its head names an enum declared by another project
module and (a) no import exports a type of that name, (b) several imports export
one, or (c) the single imported enum does not declare the variant. The dot
spelling `Enum.Variant` denotes a variant only when its head resolves to a
visible enum; with such a head, case (c) applies to it.

**Implementation coverage (informative, pending release).** Compiler commit
`1def5dde` implements this resolution, and the refusal with the gaps listed
below, for manifest projects in builds with the `cross-module-imports` feature,
which is not a default feature; a build without it does not perform them. The
resolution matters most when several project modules declare an enum of the same
name, because the reference keys each such enum by its owner. The reference
locates the diagnostic at the path, or at the match arm for a pattern.

Implementation gap: the reference check inspects a bare `Enum::Variant` used as
a plain value and in patterns, including payload patterns. It does not inspect a
payload-constructor call such as `Table::Text(9)` or a struct-variant literal
(`Table::Text { ... }`), and the name resolver accepts any `::`-qualified callee
and does not resolve a struct-literal name, so checking reports no `E2002` for
those spellings on another module's enum; no compiler control records what a
build then does with them. The parser rewrites `Table.Raw` to `Table::Raw` only
when the enum is visible to the module, so for the dot spelling the check
refuses an unknown variant of an imported enum but not an unimported or
ambiguous enum.

Coverage: the compiler control `cross_module_enum_variant_lowering` builds a
four-module project with colliding enum names and runs it when the MLIR
toolchain produces an artifact. It refuses the not-imported and unknown-variant
cases through both `mindc check` and `mindc build`, with no artifact left, and
the ambiguous case through `mindc check` only. Its refusal cases use
`::`-spelled value paths; no dedicated control asserts a refusal reported at a
pattern. The control is compiled only with the `mlir-build` and
`cross-module-imports` features on a unix host.

Inline `module name { ... }` blocks are transparent syntax containers in the
current parser. The parser accepts and preserves dotted type names and
qualified enum-pattern paths inside them, but an inline name does not create a
module-table owner. A project loader instead assigns the enclosing source
file's canonical module path and flattens a transparent block's declarations
into that file. Therefore parsing `config.Mode` in an inline block does not
establish `config` as a semantic owner; compiling that source without a
manifest-resolved module MUST refuse the qualified type and variants with
`E2002`.

The pending integration's executable coverage is the compiler-side
`qualified_enum_run` test together with the parser and single-source refusal
controls in `parse_match_and_ref`.

## Slice call implementation boundary

> **Compiler integration update, pending release.** The `std-surface` source
> implementation under review defines a bounded dynamic-array-to-slice call
> ABI. This describes the pending integration; it does not change the
> published v0.10.2 artifact.

A compatible `array<T>` value or array literal MAY be passed to `&[T]` or
`&mut [T]` parameters. Both use the existing `std.vec` Option-C dynamic-array
handle layout, an opaque handle to the `[addr, len, cap]` record. A mutable
slice parameter accepts an `array<T>` value or a mutable slice value; a
read-only parameter also accepts a mutable slice value. Read-only slices
permit indexing, `get`, and length queries. Mutable slices add indexed
assignment and `set`; ownership operations such as `push`, `free`, and
capacity access are unavailable through either slice form. Inferred aliases
retain their slice capabilities across branches, loop iterations, and loop
transfers, including `break` and `continue` paths.

The compiler MUST refuse an unproven or incompatible call-boundary layout
with `E2032` before artifact emission. This includes an unsupported element
form, an explicit slice-typed local binding, a scalar/map/opaque integer
argument, an incompatible array, and a slice or array result that is not
proven on every required path. The current ABI guard refuses floating-point,
tensor, fixed-array, and nested-slice element layouts. Opaque integer and map
handles cannot establish slice provenance merely by annotation.

Capability erasure, read-only mutation, borrowed values passed to non-slice
parameters, borrowed values returned through non-slice returns, and
slice-containing struct fields MUST produce `E2033`. A declared slice return
may preserve a compatible slice capability. General lifetime and
alias-exclusivity analysis remains outside this implementation. These limits
are separate from the general byte-slice design in [Future Extensions](./future-extensions.md#systems-programming-primitives).

For an owned `array<T>`, `push` returns the replacement owner handle. The
pending compiler accepts an explicit same-binding update such as
`xs = xs.push(value)` and rewrites a bare statement `xs.push(value)` to that
same owner-preserving form. A collection mutation used where its replacement
handle cannot be rebound, including assignment to a different binding or a
nested expression, MUST be refused with `E2300`. This rule follows the
receiver's collection type; a user-defined method with the same name on a
non-collection value is unaffected.

`set` has a different result contract: it updates existing storage and returns
a scalar status. Consequently `xs.set(index, value)` is valid as a statement
for an owned array or mutable slice, while `xs = xs.set(index, value)` cannot
replace an owned array and MUST be refused with `E2032`. Neither read-only nor
mutable borrowed slices provide `push`; attempts MUST be refused with `E2033`.

The pending integration's executable coverage is the compiler-side
`slice_call_abi_run` and `lowering_refusal_diagnostics_run` tests; they are not
yet shipped conformance artifacts.

## Traits and generics

> **Implementation status (v0.10.x, honest boundary).** The rules in this section specify the
> *full* v1.0 type system; they are **not yet implemented** in the reference implementation's
> executable subset. Shipped today: generics limited to a **single type parameter over scalar
> types** (a bounded slice — no multi-parameter generics, no generic containers, no `where`-clause
> bounds). **Not shipped:** `trait` declarations, trait implementations, `dyn Trait` objects, and
> closures / first-class function values. See
> [Future Extensions](./future-extensions.md#deferred-core-language-features) for the roadmap.
> None of these are required for Core v1 conformance.

- Traits declare associated functions, types, and laws. Implementations MUST enforce that all
  required items are provided by conforming types.
- Trait implementations MUST be coherent: for any type and trait pair there MAY be at most one
  implementation in scope.
- Generic type parameters use an explicit `where` clause to declare trait bounds.

Trait resolution strategies are implementation-defined but MUST respect lexical scoping. The reference
implementation uses a Rust-level trait-based plugin architecture internally for backend selection;
this is an implementation detail, not a MIND-language trait feature.

## Differentiable types

The `diff T` wrapper marks values that participate in automatic differentiation. Implementations
MUST track primal and tangent components as described in [Automatic differentiation](./autodiff.md).
Values of type `diff T` MAY be passed where `T` is expected only when an implicit projection rule is
available; otherwise an explicit conversion is required.

## Type soundness

The canonical proof of progress and preservation is maintained alongside the reference compiler
(informative). Implementations SHOULD aim to keep diagnostic examples synced with the canonical
proof obligations.
