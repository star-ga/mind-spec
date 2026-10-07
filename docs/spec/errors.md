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

﻿# Errors & Diagnostics

> **Status:** Core v1 normative catalog
>
> **Last updated:** 2026-10-07
>
> **MIND Spec Section**

The canonical error-code assignments and stability rules are maintained in
[Error Catalog (Normative)](../../spec/v1.0/errors.md). Diagnostic codes remain
stable within Core v1; adding a code requires a minor specification release,
while renumbering or reusing an existing code requires a major release.

Two E2xxx entries are pending compiler integration and targeted for
specification 1.7.0: `E2036` (a proven non-integer or opaque-handle value stored
into an `i8`, `u8`, `i16` or `u16` array element) and `E2037` (a function name
used as a value). The `E2002` entry is also clarified to cover a bare-headed
`Enum::Variant` value path or `match` pattern that names another project
module's enum when no import exports a type of that name, several imports
export one, or the single imported enum lacks the variant. The reference checks
this only in compiler builds with the non-default `cross-module-imports`
feature, and only when several source modules are checked or built together (a
project build, a single-file entry that imports modules of its manifest
project, or `mindc check` over several files or a directory), and that
resolution is pending compiler integration as well.
The entries, their limits and the reference commits are in the
[Error Catalog (Normative)](../../spec/v1.0/errors.md). This does not declare
the 1.7.0 release or promote an unreleased compiler artifact.

The E6xxx catalog distinguishes these current compilation refusals:

- `E6002` means the requested backend is unavailable.
- `E6009` means compiler-side aggregate materialization exceeded a deterministic
  limit or reached an operation that cannot be represented by the runnable ABI.
  The current reference profile executes fixed-array struct fields whose cells
  are `i64` or `f64`; nested `[Struct; N]` element-field receivers remain
  unsupported and must receive the same structured refusal.
- `E6010` means a `Mind.toml [exports] c_abi` entry failed manifest validation;
  it remains an ordinary user configuration error and cannot represent backend
  capability.

An `E6009` refusal terminates compilation with a non-zero status and does not
publish a partial runnable artifact. It does not imply that the source is
ill-typed.

---

[ Back to Spec Index](index.md)
