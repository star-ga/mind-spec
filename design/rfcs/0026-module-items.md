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

# RFC 0026: Module items (`module`, visibility and `export`, import alias, attributes, version attribute)

| Field | Value |
|-------|-------|
| State | Draft (2026-11-24). Not yet accepted. The specification owner decided the questions of this draft on 2026-11-24 (see [Questions](#questions-for-the-specification-owner)). |
| Number | Provisional. The specification owner assigns the final number. |
| Changes | `grammar-syntax.ebnf` (`ModuleItem`, `ModuleDeclaration`, `ExportDeclaration` in the list form only, `ImportDeclaration`, `AttributeArg`, `AttributedItem` without the function declaration), `language.md` (Modules and imports; Attributes: the list of rule 7, and an attribute before an item that is not a function declaration is derived), `types.md` (a module block is a namespace; the text on transparent blocks goes), `versioning.md` (the `requires` attribute; the example of a version declaration becomes a `mind` block again, and the sentence that calls it an extension in Core v1 goes), `core-v1-forms.md` (the rows of the module items and of an attribute before an item), `errors.md` (`E2720` to `E2725`, `E2728` and `E2729`) |
| Depends on | [RFC 0024](./0024-impl-forms.md): `TraitDeclaration` and `ImplDeclaration` are listed in `ModuleItem` below, and a module block MAY hold them. |
| Related | [RFC 0024](./0024-impl-forms.md) (visibility of methods), [RFC 0023](./0023-type-parameters-on-user-types.md) (the declaration name of a member of a module block) |

## Problem

The `ModuleItem` of the syntax grammar lists six items. The candidate block adds `const`, `enum`, a module block, `use`
and attributes before an item other than a function declaration (an attribute before a function declaration is part of
Core v1, [Attributes](../../spec/v1.0/language.md#attributes)). The text of the specification and the reference compiler
use more forms than that, and they do not agree on their meaning.

Measured with the reference compiler v0.10.4 (`mindc check --no-fmt`, and `mindc build --backend native`):

| Source | Check | Native backend |
|--------|-------|----------------|
| `module m;` | accepted | refused, `lane.source.top_level` |
| `module m { fn f() -> i64 { return 1; } }` | accepted | refused, `lane.source.top_level` |
| a module block inside a module block | accepted | refused, `lane.source.top_level` |
| `pub fn f() -> i64 { … }` | accepted | builds |
| `pub struct S { … }`, `pub const K: i64 = 1;` | accepted | refused (`lane.source.top_level`; `unsupported construct`) |
| `static X: i64 = 1;` | `E1001`, ``unexpected `:`, expected an expression`` | not reached |
| `export f;` (the grammar's form) | accepted | refused, `unsupported construct` |
| `export { f }` (not in the grammar; the formatter writes it for `export f;`) | accepted | builds |
| `import std.io as q;`, `use std.io as q;` | accepted | refused, `lane.source.top_level` |
| `#[test]` before `module m;` | accepted | refused, `lane.source.top_level` |
| `#[requires(mind_spec = "1.2")]` before `module m;` (the example of [Versioning](../../spec/v1.0/versioning.md#in-source-code)) | `E1001`, ``unexpected `#`, expected an expression`` (1:1) | not reached |
| `#[name("x")]` (a string argument) | `E1001`, ``unexpected `#`, expected an expression`` | not reached |

[Types](../../spec/v1.0/types.md#module-qualified-type-ownership) states that inline module blocks "are transparent
syntax containers in the current parser": a project loader flattens the declarations of a block into the file, and
the block does not create a module-table owner. The text of
[Language](../../spec/v1.0/language.md#module-qualified-references) gives a qualifier rule for imports and none for
blocks. The grammar's `ModuleBlock` needs braces, and the version example uses
`module my_program;` without them.

## Grammar change

```ebnf
ModuleItem          = FunctionDeclaration | TypeDeclaration | StructDeclaration
                    | EnumDeclaration | ConstDeclaration | TraitDeclaration | ImplDeclaration
                    | ModuleDeclaration | ImportDeclaration | ExportDeclaration
                    | UseDeclaration | AttributedItem ;

ModuleDeclaration   = "module" , Identifier , ( ";" | "{" , { ModuleItem } , "}" ) ;

ImportDeclaration   = "import" , ImportPath , [ "as" , Identifier ] , ";" ;

ExportDeclaration   = "export" , "{" , Identifier , { "," , Identifier } , [ "," ] , "}" ;

AttributeArg        = Identifier | Literal | Identifier , "=" , Literal ;

AttributedItem      = Attribute , { Attribute } , AttributableItem ;
AttributableItem    = TypeDeclaration | StructDeclaration | EnumDeclaration | ConstDeclaration
                    | TraitDeclaration | ImplDeclaration | ModuleDeclaration | ImportDeclaration
                    | ExportDeclaration | UseDeclaration ;
```

An attribute before a function declaration is the `{ Attribute }` of `FunctionDeclaration`
([Attributes](../../spec/v1.0/language.md#attributes)). `AttributedItem` takes every other item and no `AttributedItem`,
so `#[a] fn f() { }` and `#[a] #[b] struct S { }` have one derivation each (a check then refuses both, because no
chapter defines the names `a` and `b`, rule 7). The `AttributedItem` of
[`grammar-syntax.ebnf`](../../spec/v1.0/grammar-syntax.ebnf) takes the alternatives of its `ModuleItem` except
`FunctionDeclaration`; `AttributableItem` is the same rule over the `ModuleItem` of this draft.

`TraitDeclaration` and `ImplDeclaration` are the productions of [RFC 0024](./0024-impl-forms.md); the supertrait
list is owned by [RFC 0027](./0027-function-generics.md). `ExportDeclaration` has one form, the list form
`export { f, g }`, with no `;` after the brace; this is the form that formatted sources hold today. `pub` and
`static` are not added. A `Literal` of `AttributeArg` includes a string literal. The form `import a.b as c;` is the
extension that [Language](../../spec/v1.0/language.md#executable-subset-status-informative) already documents.

## Static rules

1. **File module.** `module m;` names the module of the file in which it stands. It MUST be the first
   item of the file, after attributes, and MUST appear at most once; a `module m;` that is not the first item, and a
   second one, are refused with `E2721`. When the file belongs to a project, the name `m` MUST equal the name that
   the project file gives to the file; a mismatch is refused with `E2722`. A file outside a project has no such
   name, and the declaration only names the file.
2. **Module block.** `module m { … }` introduces the namespace `m` inside the enclosing module. A member
   `f` of `m` is referred to as `m.f` from outside the block and as `f` inside it. This is the qualifier rule
   of [Language](../../spec/v1.0/language.md#module-qualified-references) applied to a block. The rule is for a name
   in an expression: a type position takes one identifier (`IdentifierType`), so a type of a block is named only
   inside the block in this draft ([Open](#open)). A block is not
   flattened into the file in any edition: two blocks with members of the same name are two namespaces.
3. **Names.** Two items of one namespace MUST NOT have the same name. A module block and a function of
   the same enclosing namespace MUST NOT have the same name. The qualified name of a module block is the module
   path of its file module, then the names of the blocks around it, outermost first, then its own name, joined by
   `.` (the declaration name `D` of [RFC 0023](./0023-type-parameters-on-user-types.md#instance-names)). In a
   project, the qualified name of a module block MUST NOT equal the module path of a module of the project: a block
   `defs` in the file module `nested` and the project module `nested.defs` would give the one name
   `nested.defs.Color` to two declarations, and the reference `nested.defs.Color` would have two meanings. A
   violation of this rule is refused with `E2720`.
4. **Export.** `export` is the only visibility mechanism. An item is visible to another module only if it is
   exported. A module block is a namespace of its module and not another module: a member of a block is visible in
   the whole module that holds the block, by its qualified name (rule 2), with no export. `export { f, g }` exports
   the named items of the module in which it stands. An export of a name that
   is not declared in that module is refused with `E2002`, at each place where it stands. A name that the module
   declares and that stands twice in its export lists, in one list or in two, is refused with `E2729`; no warning
   comes first. A method and an
   associated item are exported with their type ([RFC 0024](./0024-impl-forms.md), rule 10), and an export list
   does not name them.
5. **Forms that are not in the language.** The grammar does not derive them, and a check refuses each one with
   its own code and a message that names the replacement:
   - `pub` before an item is refused with `E2723`; the message names `export { … }`.
   - A `static` item is refused with `E2724`; the message names `const`, which holds constants.
   - An export in another form than `export { … }` (`export f;`, `export { f };`) is refused with `E2725`; the
     message names the list form.
6. **Import alias.** `import a.b as c;` binds the qualifier `c` and not `b`. The reference registers both
   (language.md); this RFC makes the alias the only qualifier of that import.
7. **Attributes.** An attribute is defined by a chapter of the specification, by its name and by the item that it
   stands before. The defined attributes are exactly those that a chapter defines by name and position. A search of
   every file of the repository for the forms `#[` and `#![` finds three that a chapter defines:
   - `raw_memory`, with no argument or the one argument `sealed`, before a function declaration
     ([Raw memory](../../spec/v1.0/memory.md#raw-memory)). It is part of Core v1. A function of an `impl` block
     ([RFC 0024](./0024-impl-forms.md)) is a function declaration too.
   - `requires`, with the one argument `mind_spec = "M.N"`, before the file module declaration `module m;`
     ([Versioning](../../spec/v1.0/versioning.md#in-source-code); rule 8 gives the form and the meaning of the
     value).
   - `repr(C)`, with the one argument `C`, before a `struct` declaration. The FFI chapter defines its name, its
     position and its meaning: the layout of the struct in memory, the field types that have a layout, and the
     refusal of another field type with `E2407`
     ([Struct layout attribute](../../spec/v1.0/ffi.md#struct-layout-attribute)).
     [MLIR Lowering](../../spec/v1.0/mlir-lowering.md) names such a struct a `#[repr(C)]` struct.

   No attribute name is defined for a module block. An attribute whose name is not in the list, a listed attribute
   with an argument form that the list does not give (`#[repr(packed)]`, `#[raw_memory(open)]`,
   `#[requires(mind_lang = "1.0")]`), and a listed attribute before an item for which its name is not defined
   (`#[repr(C)]` before a function, `#[raw_memory]` before a `struct`) are refused with
   [`E2502`](../../spec/v1.0/errors.md#e2502-invalid-attribute), the one code of the catalog for an invalid attribute,
   as [Attributes](../../spec/v1.0/language.md#attributes) refuses them. No attribute is an exception. A chapter or an
   RFC that defines an attribute adds it to the list.

   The other hits of the search define no attribute:
   - The syntactic grammar, the lexical chapter, the language chapter and the changelog (`docs/changelog.md`) write the
     general forms `#[name]` and `#[name(arg, ...)]`, and a comment of the syntactic grammar writes `#[a] fn f() { }`:
     the syntax of an attribute, not a name.
   - [Core v1 forms](../../spec/v1.0/core-v1-forms.md), [Attributes](../../spec/v1.0/language.md#attributes), the
     conformance rows `attribute_reject_unknown_name` and `attribute_reject_unknown_name_before_struct` and the
     [decision notes](./decision-notes-2.md) write `#[fast]`, a name that no chapter defines, before a function
     declaration and before a `struct` declaration; this rule refuses it with `E2502`. The forms page, the conformance
     rows `rawmem_reject_attr_argument` and `rawmem_reject_attr_on_struct` and the decision notes write
     `#[raw_memory(open)]` and `#[raw_memory] struct S { a: i64, }`, a use with another argument and a use before
     another item, which this rule refuses with `E2502` too.
   - [Future Extensions](../../spec/v1.0/future-extensions.md) writes `#[profile(default)]` and
     `#[profile(default | systems)]` in a design for a later edition and `#[cfg(profile = "ai")]` in a design that
     it rejects, and it names `#![no_std]` as a feature of another language. It defines none of them, and this rule
     refuses each of their names with `E2502`.
   - The example `examples/ffi/c_bindings.mind` writes `#[extern("C")]`, `#[export("C")]` and `#[unsafe]` before a
     function. The FFI and MLIR chapters write an external function as `extern "C"`, not as an attribute. The
     example is not a valid program under this RFC until a chapter or an RFC defines these names ([Open](#open)).
   - The changelog names the compiler attributes `#[deterministic]`, `#[target(...)]` and `#[q16]`, and
     `#[cfg(feature = "std-surface")]`, a gate in the source code of the compiler. This rule refuses each of their
     names with `E2502`.
8. **Version attribute.** In `#[requires(mind_spec = "M.N")]` before `module m;`, `mind_spec` is the only key. Its
   value is a string literal that holds a version `major.minor`: two decimal numbers joined by one `.`. Another key, a
   second argument, or a value that is not `major.minor` is an argument form that the definition does not give, and is
   refused with `E2502` (rule 7). An implementation compares a well-formed value with its own specification version.
   Another major, or the same major with a higher minor than its own, is a version that the implementation does not
   provide, and is refused with `E2728`. `E2728` applies only to a well-formed version attribute before `module m;`.
   Before another item, `requires` stands at a position that its definition does not give, so it is refused with
   `E2502` (rule 7) and its value is not compared: `#[requires(mind_spec = "9.0")] fn f() -> i64 { return 0; }` gets
   `E2502` only. The two refusals do not overlap: `E2502` is about the form and the position of the attribute, and
   `E2728` is about the version of a well-formed one before `module m;`.

## Meaning as a desugaring

**Module block.** A module block is a prefix on the names of its members. The item name of a member is its qualified
spelling, as in the declaration name `D` of [RFC 0023](./0023-type-parameters-on-user-types.md#instance-names):

```text
// Not Core v1: a source in the form that this RFC proposes
module m {
    fn f() -> i64 { return 1; }
}
fn main() -> i64 { return m.f(); }
```

has the written-out form below (not source text, because `m.f` in a declaration is not an identifier):

```text
// Not Core v1: the written-out form, not source text (a name in it is not an identifier)
fn m.f() -> i64 { return 1; }
fn main() -> i64 { return m.f(); }
```

with a reference `m.f` read as the prefixed name and a reference `f` inside the block rewritten to it. A nested block
adds one prefix with one `.` for each level (`a.b.f`). An item name holds `.`, which no identifier holds, so it never
equals a name of the program. The equality test of
[RFC 0023](./0023-type-parameters-on-user-types.md#meaning-as-a-desugaring) is the oracle.

**File module and export.** `module m;` has no desugaring: it is a declaration of the module name
that the project loader reads. `export { f, g }` has no desugaring: it marks `f` and `g` as visible.

**Import alias.** `import a.b as c;` is `import a.b;` with the qualifier `b` renamed to `c` in the file.

## Proposed conformance rows

Proposals. The reference accepts the text `module app;` and refuses the version attribute (measured above).
The other rows were not measured. The codes `E2720` to `E2722` are assigned to this draft, `E2723` to `E2725`,
`E2728` and `E2729` are proposed by it, and `E2002` and `E2502` exist.

```yaml
description: "A file module declaration and a module block"
category: syntax
profile: cpu
input:
  source: |
    module app;

    module util {
        fn twice(x: i64) -> i64 {
            return x + x;
        }
    }
    fn main() -> i64 {
        return util.twice(2);
    }
expected:
  status: success
  output: { result: { dtype: i64, shape: [], values: 4 } }
```

```yaml
description: "A module declaration that is not the first item is refused"
input:
  source: |
    fn main() -> i64 {
        return 0;
    }
    module app;
expected:
  status: error
  error: { code: E2721, message_contains: "first item" }
```

```yaml
description: "A member of a module block is not visible without its qualifier"
input:
  source: |
    module util {
        fn twice(x: i64) -> i64 {
            return x + x;
        }
    }
    fn main() -> i64 {
        return twice(2);
    }
expected:
  status: error
  error: { code: E2002, message_contains: "twice" }
```

```yaml
description: "An export of a name that is not declared is refused"
input:
  source: |
    fn main() -> i64 {
        return 0;
    }
    export { missing }
expected:
  status: error
  error: { code: E2002, message_contains: "missing" }
```

```yaml
description: "An export without the list form is refused"
input:
  source: |
    fn f() -> i64 {
        return 1;
    }
    fn main() -> i64 {
        return 0;
    }
    export f;
expected:
  status: error
  error: { code: E2725, message_contains: "export {" }
```

```yaml
description: "A name that stands twice in the export lists of one module is refused"
input:
  source: |
    fn area() -> i64 {
        return 1;
    }
    fn main() -> i64 {
        return 0;
    }
    export { area }
    export { area }
expected:
  status: error
  error: { code: E2729, message_contains: "area" }
```

```yaml
description: "pub is refused and the message names export"
input:
  source: |
    pub fn f() -> i64 {
        return 1;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2723, message_contains: "export" }
```

```yaml
description: "static is refused and the message names const"
input:
  source: |
    static X: i64 = 1;
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2724, message_contains: "const" }
```

```yaml
description: "The version attribute with a string value"
input:
  source: |
    #[requires(mind_spec = "1.0")]
    module app;
    fn main() -> i64 {
        return 0;
    }
expected:
  status: success
```

```yaml
description: "A version attribute with another major is refused"
input:
  source: |
    #[requires(mind_spec = "2.0")]
    module app;
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2728, message_contains: "mind_spec" }
```

```yaml
description: "A version attribute with an unknown key is refused"
input:
  source: |
    #[requires(mind_lang = "1.0")]
    module app;
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2502, message_contains: "mind_lang" }
```

```yaml
description: "An attribute name that is not defined is refused"
input:
  source: |
    #[test]
    module app;
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2502, message_contains: "test" }
```

```yaml
description: "repr(C) before a struct is a defined attribute"
input:
  source: |
    #[repr(C)]
    struct P {
        x: i64,
        y: i64,
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: success
```

```yaml
description: "repr(C) before a function is refused"
input:
  source: |
    #[repr(C)]
    fn f() -> i64 {
        return 1;
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2502, message_contains: "repr" }
```

```yaml
description: "Two modules with the same name in one namespace are refused"
input:
  source: |
    module util {
    }
    module util {
    }
    fn main() -> i64 {
        return 0;
    }
expected:
  status: error
  error: { code: E2720, message_contains: "util" }
```

## Cost for the compiler

| Part | Work | Size |
|------|------|------|
| Front end, parser | `module m;`; the list form of `export`; import alias; the attribute argument `key = literal` and string literals | small |
| Front end, resolver | a real namespace for a module block (the reference flattens a block today); the qualifier rule for members; the export rule; the refusals of rule 5; the attribute and version rules | medium |
| Front end, desugaring | the prefixed names | small |
| Native lowering | none after the prefixing. The native backend refuses every module item (`lane.source.top_level`); the prefixed form is plain functions, so the work is the admission of `module`, `import … as` and `export` items. | small to medium |
| Tests | rows above; parity of the module block against the written-out form | small |

## Questions for the specification owner

### Decided by the specification owner (2026-11-24)

1. **Transparent block or namespace.** A module block is a namespace (rule 2). No edition flattens it.
2. **`module m;` and the project.** The file module name MUST equal the name from the project file (rule 1,
   `E2722`).
3. **`pub`.** `export` is the only visibility mechanism. `pub` is refused (rule 5, `E2723`).
4. **`static`.** `static` is refused for good (rule 5, `E2724`). `const` holds constants.
5. **Export spelling.** There is ONE export form, the list form `export { f }`, which formatted sources hold today.
   The grammar changes to it, and another form is refused (rule 5, `E2725`).
6. **Version attribute.** `mind_spec` is the only key. The value is parsed as `major.minor`. An implementation
   refuses another major and a higher minor than its own (`E2728`). An unknown key is an argument form that the
   definition does not give, and is refused with `E2502` (rule 8).
7. **Attribute on a module block and on a method.** This draft defines no attribute name for a module block or a
   method. The attribute `raw_memory`, which [Raw memory](../../spec/v1.0/memory.md#raw-memory) defines before every
   function declaration, stands before a method too. Another attribute there is refused (`E2502`) until an RFC
   defines one (rule 7).
8. **Code allocation.** The three codes are assigned, because they are free in the catalog: `E2720` (a name that is not
   unique in its namespace: two items of one namespace with the same name, or a module block whose qualified name equals
   the module path of a project module, rule 3), `E2721` (`module m;` not first or repeated), `E2722` (module name
   differs from the project). The decisions of questions 3 to 6 and the export rule (rule 4) need five more codes: this
   draft proposes `E2723`, `E2724`, `E2725`, `E2728` and `E2729` from the same block, which the catalog does not define;
   they are not yet assigned. Their labels: `E2723` (`pub` before an item, rule 5), `E2724` (a `static` item, rule 5),
   `E2725` (an export in another form than the list form `export { … }`, rule 5), `E2728` (a well-formed version
   attribute before `module m;` with another major, or the same major and a higher minor, rule 8) and `E2729` (a name
   that the module declares and that stands twice in its export lists, rule 4). An invalid attribute, also a malformed
   version attribute or one before another item, has the code `E2502` of the catalog (rule 7), so this draft gives it no
   code of its own.

### Open

- **FFI attribute names of the example.** Whether the FFI chapter defines `extern("C")`, `export("C")` and `unsafe`
  as attributes is not decided. Until a chapter or an RFC defines them, they are refused with `E2502` (rule 7).
- **Export of a module block.** Whether an export list can make the members of a module block visible to another
  module (for example by naming the block) is not decided.
- **Qualified type names.** [Types](../../spec/v1.0/types.md#module-qualified-type-ownership) writes a type of another
  module with its import qualifier (`defs.Color` after `import nested.defs;`) and says that a qualified type is an
  extension of Core v1: `IdentifierType` and `TraitRef` take one identifier, so no type position derives `m.T`. How a
  type or a trait of a block is named from outside the block is not decided; a later change that adds qualified names
  to these productions decides it, also for the head of an impl ([RFC 0024](./0024-impl-forms.md#open)).
- **`requires` before another item.** This edition defines `requires` only before `module m;` (rule 7). Whether it
  MAY stand before another item is not decided; until then it is refused there with `E2502`.
