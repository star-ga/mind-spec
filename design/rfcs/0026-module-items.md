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

# RFC 0026: Module items (`module`, visibility, `export`, `static`, import alias, version attribute)

| Field | Value |
|-------|-------|
| State | Draft (2026-11-24). Not yet accepted. |
| Number | Provisional. The specification owner assigns the final number. |
| Changes | `grammar-syntax.ebnf` (`ModuleItem`, `ModuleDeclaration`, `ExportDeclaration`, `ImportDeclaration`, `AttributeArg`), `language.md` (Modules and imports), `versioning.md` |
| Depends on | [RFC 0024](./0024-impl-forms.md): `TraitDeclaration` and `ImplDeclaration` are listed in `ModuleItem` below, and a module block MAY hold them. |
| Related | [RFC 0024](./0024-impl-forms.md) (visibility of methods), [RFC 0023](./0023-type-parameters-on-user-types.md) |

## Problem

The `ModuleItem` of the syntax grammar lists six items. The candidate block adds `const`, `enum`, a
module block, `use` and attributes. The text of the specification and the reference compiler use more
forms than that, and they do not agree on their meaning.

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

[Types](../../spec/v1.0/types.md) states that an inline module block is today "a transparent syntax
container": its declarations are flattened into the file, and the block does not create a module-table
owner. The text of [Language](../../spec/v1.0/language.md#module-qualified-references) gives a qualifier
rule for imports and none for blocks. The grammar's `ModuleBlock` needs braces, and the version example uses
`module my_program;` without them.

## Grammar change

```ebnf
ModuleItem          = FunctionDeclaration | TypeDeclaration | StructDeclaration
                    | EnumDeclaration | ConstDeclaration | TraitDeclaration | ImplDeclaration
                    | ModuleDeclaration | ImportDeclaration | ExportDeclaration
                    | UseDeclaration | AttributedItem ;

ModuleDeclaration   = "module" , Identifier , ( ";" | "{" , { ModuleItem } , "}" ) ;

ImportDeclaration   = "import" , ImportPath , [ "as" , Identifier ] , ";" ;

ExportDeclaration   = "export" , ( Identifier | "{" , Identifier , { "," , Identifier } , [ "," ] , "}" ) , [ ";" ] ;

AttributeArg        = Identifier | Literal | Identifier , "=" , Literal ;
```

`TraitDeclaration` and `ImplDeclaration` are the productions of [RFC 0024](./0024-impl-forms.md); the supertrait
list is owned by [RFC 0027](./0027-function-generics.md) and stays NOT IN CORE v1. `static` is not added (open
question 4). `pub` is not added (open question 3). A `Literal` of `AttributeArg` includes a string literal.
The form `import a.b as c;` is the extension that
[Language](../../spec/v1.0/language.md#executable-subset-status-informative) already documents.

## Static rules

1. **File module.** `module m;` names the module of the file in which it stands. It MUST be the first
   item of the file, after attributes, and MUST appear at most once; a `module m;` that is not the first item, and a second one, are refused with `E2721`.
   The name `m` MUST be the file's module name if the file belongs to a project that names its modules; a
   mismatch is refused with `E2722`. Without a project, the declaration only names the file.
2. **Module block.** `module m { … }` introduces the namespace `m` inside the enclosing module. A member
   `f` of `m` is referred to as `m.f` from outside the block and as `f` inside it. This is the qualifier rule
   of [Language](../../spec/v1.0/language.md#module-qualified-references) applied to a block.
3. **Names.** Two items of one namespace MUST NOT have the same name. A module block and a function of
   the same enclosing namespace MUST NOT have the same name. A violation is refused with `E2720`.
4. **Export.** An item is visible to another module only if it is exported. `export f;` and `export { f, g };`
   export the named items of the module in which they stand. An export of a name that is not declared in
   that module is refused with `E2002`. One export of the same name twice is a warning.
5. **Import alias.** `import a.b as c;` binds the qualifier `c` and not `b`. The reference registers both
   (language.md); this RFC makes the alias the only qualifier of that import.
6. **Attribute arguments.** `#[name(key = "value")]` is accepted by the grammar. The meaning of an attribute
   name is defined where the name is used. The attribute `requires` is defined in
   [Versioning](../../spec/v1.0/versioning.md#in-source-code): its key `mind_spec` has a string value
   that names a specification version.

## Meaning as a desugaring

**Module block.** A module block is a prefix on the names of its members. This is the written-out form:

```mind
module m {
    fn f() -> i64 { return 1; }
}
fn main() -> i64 { return m.f(); }
```

is

```mind
fn m__f() -> i64 { return 1; }
fn main() -> i64 { return m__f(); }
```

with a reference `m.f` rewritten to the prefixed name and a reference `f` inside the block rewritten in the
same way. A nested block uses one `__` for each level. The prefixed name is not visible to the user.

**File module and export braces.** `module m;` has no desugaring: it is a declaration of the module name
that the project loader reads. `export { f, g };` is `export f; export g;`.

**Import alias.** `import a.b as c;` is `import a.b;` with the qualifier `b` renamed to `c` in the file.

## Proposed conformance rows

Proposals. The reference accepts the text `module app;` and refuses the version attribute (measured above).
The other rows were not measured. The codes `E2720`, `E2721` and `E2722` are proposed by this draft (open
question 8); `E2002` exists.

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
    export missing;
expected:
  status: error
  error: { code: E2002, message_contains: "missing" }
```

```yaml
description: "The version attribute with a string value"
input:
  source: |
    #[requires(mind_spec = "1.2")]
    module app;
    fn main() -> i64 {
        return 0;
    }
expected:
  status: success
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
| Front end, parser | `module m;`; export braces; import alias; the attribute argument `key = literal` and string literals | small |
| Front end, resolver | a real namespace for a module block (the reference flattens a block today); the qualifier rule for members; the export rule | medium |
| Front end, desugaring | the prefixed names | small |
| Native lowering | none after the prefixing. The native lane refuses every module item (`lane.source.top_level`); the prefixed form is plain functions, so the work is the admission of `module`, `import … as` and `export` items. | small to medium |
| Tests | rows above; parity of the module block against the written-out form | small |

## Open questions for the specification owner

1. **Transparent block or namespace.** The reference flattens a module block (types.md). This draft makes it a
   namespace (rule 2). A project that has two blocks with a member of the same name changes meaning. Keep
   the flattening for one edition?
2. **`module m;` and the project.** Does the file module name have to equal the name from the project file?
   The reference accepts any name today.
3. **`pub`.** The reference accepts `pub` before several items and gives it no checked meaning. Is `export`
   the only visibility mechanism (this draft), or does `pub` join the language? If `pub` joins, `export`
   becomes redundant.
4. **`static`.** A module-level mutable value conflicts with a deterministic evaluation order. Refuse for
   good, allow only a constant (`const` already exists), or allow with a rule?
5. **Export spelling.** The reference formatter rewrites `export f;` to `export { f }`. This draft accepts
   both. Should the formatter write the grammar's form instead?
6. **Version attribute.** Is `mind_spec` the only key? Is the value compared as a string or parsed as a
   version? What does an implementation do with an unknown key?
7. **Attribute on a module block** and on a method of an impl: allowed by `AttributedItem`; is any attribute
   name defined for them?
8. **Code allocation.** `E2720` (duplicate name in one namespace), `E2721` (`module m;` not first or repeated) and
   `E2722` (module name differs from the project) are proposals in the range next to the reserved codes of
   [RFC 0024](./0024-impl-forms.md). Are the three codes free?
