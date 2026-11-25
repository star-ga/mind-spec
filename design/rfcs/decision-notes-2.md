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

# Decision Notes, Part 2 (Informative)

This page continues [Decision Notes](./decision-notes.md) with the notes DN-14 to DN-21, which the specification
owner decided on 2026-11-25. The introduction of that page applies here: a note records the text, the measured
behaviour of the reference compiler v0.10.4, the options and the decision, and its **Form status** paragraph gives
the status of [Core v1 form status](../../spec/v1.0/core-v1-forms.md) to the same forms.

## DN-14. Raw memory and its mark

**Text before the decision.** [Standard Library](../../spec/v1.0/stdlib.md) gave the `__mind_*` intrinsics, which
take and give opaque `i64` addresses, and named `vec_addr` and the other functions that give the address of a buffer.
No sentence said how long an address stays valid, and any function could call the intrinsics. The determinism rule of
that chapter covered "any program written against these intrinsics", also a program that reads through an address of
freed memory. [Security](../../spec/v1.0/security.md#core-language-safety) said that the surface language inherits the
memory safety model of another language and that a use after a free and a buffer overflow are refused before IR
generation; no rule of the language did that. An attribute stood only in the "v1.1 candidate additions" block of the
grammar, which `Module` does not reach.

**Reference.** `mindc check` accepts every source of this note: a `#[raw_memory]` function that calls `__mind_load_i64`,
called from a `#[raw_memory]` `main`; a `#[raw_memory(sealed)]` function that calls the intrinsics, called from an
unmarked `main`; `vec_get` in an unmarked `main`; a call of `__mind_load_i64` in an unmarked function; a call of
`vec_addr` in an unmarked `main`; a call of a `#[raw_memory]` function from an unmarked `main`; `#[raw_memory]` before a
`struct`; `#[raw_memory(open)]` before a function; `#[fast]` before a function; `#[fast] struct S { a: i64, }`; and a
call of each index function with an index outside its container: `vec_get(v, 5)` and `vec_get(v, -1)` with
`v = vec_push(vec_new(), 7)`, `vec_set(v, 5, 1)`, `string_get_byte(s, 5)` with `let s: String = "ab";`, and
`map_key_at(m, 5)` and `map_value_at(m, 5)` with `m = map_insert(map_new(), 1, 2)`. The native backend refuses each
source with an attributed function with `lane.source.function_contract`, the source with `#[raw_memory]` before a
`struct` with `lane.source.top_level`, the source with `#[fast]` before a `struct` in the same way, and the sources that
call `vec_get`, `vec_addr` or another index function with `lane.call.unknown`. It builds the source with the unmarked
call of `__mind_load_i64`, and its image exits with the status 0. The MLIR backend builds `#[fast] struct S { a: i64, }`
and each source with an index outside the container, and no image of these sources stops with the status 77 of the
defined stop: the image of `#[fast] struct S` exits with the status 0, `vec_get(v, 5)` with 33, `vec_get(v, -1)` with
49, `vec_set(v, 5, 1)` and `string_get_byte(s, 5)` with 0, and `map_key_at(m, 5)` and `map_value_at(m, 5)` with 49; with
the value of `vec_get(v, 5)` or of `string_get_byte(s, 5)` not used, the image of `return 5;` exits with the status 5,
and `vec_get(v, 100000000)` ends with the signal SIGSEGV, status 139; with the index 0, `vec_get` gives 7 and
`map_value_at` gives 2. The MLIR backend also builds the sources with `#[raw_memory]` before a `struct`, with
`#[raw_memory(open)]` before a function and with `#[fast]` before a function, and each image exits with the status 0. It
accepts `#[raw_memory(open)] fn f(p: i64) -> i64 { return __mind_load_i64(p); }`; the native backend refuses that source
with `lane.source.function_contract`, and the MLIR backend builds it and its image exits with the status 0. It accepts a
false `assert(x == 2);` with `x = 1`; the native backend refuses that source with `lane.source.assert`, and the MLIR
backend builds it, and its image writes "assertion failed at source span 38..53" and ends with the signal SIGABRT,
status 134, not the status 77 of the defined stop.

**Options.** (A) Only a sentence on address validity. (B) An attribute on a function that allows raw memory uses in
its body; a use elsewhere is refused at check time. (C) A block form with a new keyword. (D) Raw memory uses only in
the standard library. (E) As (B), and a function of the standard library may make raw memory uses without the
attribute, while the library functions that give or take an address are raw memory functions themselves.

**Decision.** Option E, decided by the specification owner on 2026-11-25. The chapter
[Memory model](../../spec/v1.0/memory.md) holds the rules.

- Address validity ([Address validity](../../spec/v1.0/memory.md#address-validity)). An address that a function
  gives for the storage of a buffer (`vec_addr`, `string_addr`, `map_keys_addr`, `map_vals_addr`, `vec_zeroed`) is
  valid until the next operation that can grow, shrink or release that buffer. An address from `__mind_alloc` or
  `__mind_realloc` is valid until it is passed to `__mind_free` or `__mind_realloc`. A read or a write through an
  address that is not valid, and a read of memory that the program did not write after the allocation, is an error
  of the program. An implementation does not have to detect it, and this specification gives the value of such a
  read no meaning. A program that keeps the address rules and the rules of
  [Records and containers](../../spec/v1.0/memory.md#records-and-containers) (DN-15) MUST observe the same logical
  behaviour byte-for-byte given identical inputs.
- The mark ([Raw memory](../../spec/v1.0/memory.md#raw-memory)). A raw memory function is a function that the list of
  [raw memory functions](../../spec/v1.0/memory.md#raw-memory-functions) names, or a function declared with
  `#[raw_memory]`. An implementation that adds an external function as an extension treats one with a pointer type in
  its signature, or with the tag `unsafe fn`, as a raw memory function. A call of a raw memory function, and a region
  block (DN-15), is a raw memory use. A call of a raw memory function is allowed only in the body of a function declared
  with `#[raw_memory]` or `#[raw_memory(sealed)]`, or in a function of the standard library. A region block is allowed
  only in the body of a function declared with `#[raw_memory]` or `#[raw_memory(sealed)]`; a function of the standard
  library also needs the attribute for a region block. Any other raw memory use MUST be refused at check time with
  `E2501`, except in the body of a function whose attribute `raw_memory` `E2502` refuses (below).
  `#[raw_memory(sealed)]` states that no parameter and no result of the function carries an address and that the
  function keeps no address after it returns. A call of a sealed function is not a raw memory use. An implementation
  does not check this statement. The attribute `raw_memory` stands only directly before a function declaration and takes
  no argument or the one argument `sealed`. Any other use of the attribute `raw_memory`, before another item or with
  another argument, MUST be refused at check time with `E2502`. A function whose attribute `raw_memory` `E2502` refuses
  gets no `E2501`: a raw memory use in its body, a call or a region block, is not refused with `E2501`, and the source
  gets the one code `E2502`.
- Attributes ([Attributes](../../spec/v1.0/language.md#attributes)). `FunctionDeclaration` takes `{ Attribute }`
  before `fn`. An attribute before a function declaration is part of Core v1 when the specification defines its name
  for that position. An attribute before a function declaration whose name this specification does not define for
  that position MUST be refused at check time with `E2502`. Before another item, an attribute whose name this
  specification does not define for that position MUST be refused at check time with `E2502` too, for example
  `#[fast] struct S { a: i64, }`. A defined attribute with an argument form that its definition does not give MUST
  be refused at check time with `E2502`. `E2502` is the one code for an invalid attribute.
- The library is safe without the mark
  ([Library functions that check](../../spec/v1.0/memory.md#library-functions-that-check)). A function of the
  standard library that is not a raw memory function is safe for every argument: no argument makes it read or write
  memory outside the storage that its containers own. An index function (`vec_get`, `vec_set`, `string_get_byte`,
  `map_key_at`, `map_value_at`) MUST make the [defined stop](../../spec/v1.0/memory.md#the-defined-stop) when the
  index is not less than the length of the container or is negative, with `E6001`. A form of an index function that
  does not check the index has its own name and is declared with `#[raw_memory]`.
- [The defined stop](../../spec/v1.0/memory.md#the-defined-stop) is how a program ends when a check of the language or
  of the standard library fails at run time. The program ends at the failed check: no later step of the program runs and
  `main` returns no value. The implementation writes a diagnostic with the source location and, where the check has a
  code, that code. The process ends with the exit status 77, the same for every cause of the stop and on every
  substrate. The stop is at the same step of the program on every substrate.
- [Security](../../spec/v1.0/security.md#core-language-safety) says only what the language checks: no pointer type,
  the mark of raw memory uses, the stop of the index functions, index bounds and containers. It says that the
  address rules are not checked.
- What a value of a container that a program keeps sees after a change of the container is the container model of
  [DN-15](#dn-15-one-model-for-arrays-maps-and-strings).

**Form status.** `#[raw_memory] fn f(p: i64) -> i64 { }`, `#[raw_memory(sealed)] fn g() -> i64 { }`: Core v1; reference
gap (`mindc check` accepts both; the native backend refuses an attributed function with
`lane.source.function_contract`). A call of a raw memory function in a function without the attribute, outside the
standard library (`fn r(p: i64) -> i64 { return __mind_load_i64(p); }`, `vec_addr(v)` in an unmarked `main`, a call of a
`#[raw_memory]` function from an unmarked `main`): Core v1 refuses; reference gap (`mindc check` accepts all three; the
native backend builds the first, and its image exits with the status 0). `#[raw_memory] struct S { a: i64, }`,
`#[raw_memory(open)] fn f() { }`: Core v1 refuses; the code is `E2502`; reference gap (`mindc check` accepts both; the
native backend refuses them with `lane.source.top_level` and `lane.source.function_contract`; the MLIR backend builds
both and their images exit with the status 0). `#[fast] fn f() { }`: Core v1 refuses; the code is `E2502`; reference gap
(`mindc check` accepts it; the native backend refuses it with `lane.source.function_contract`; the MLIR backend builds
it and its image exits with the status 0). `#[repr(C)] struct S { a: i32, }`,
`#[requires(mind_spec = "1.2")] module m;`: Extension. `#[fast] struct S { a: i64, }`: Core v1 refuses; the code is
`E2502`; reference gap (`mindc check` accepts it; the MLIR backend builds it and its image exits with the status 0). An
index function of the standard library with an index outside its container
(`let v = vec_push(vec_new(), 7); return vec_get(v, 5);`, and `vec_set`, `string_get_byte`, `map_key_at`,
`map_value_at`): Core v1; the program makes the [defined stop](../../spec/v1.0/memory.md#the-defined-stop) with `E6001`;
reference gap (`mindc check` accepts all five; the native backend refuses each with `lane.call.unknown`; the MLIR
backend builds each and its image does not stop with the status 77 of the defined stop: `vec_get(v, 5)` exits with the
status 33, `vec_get(v, -1)` 49, `vec_set(v, 5, 1)` 0, `string_get_byte(s, 5)` 0, `map_key_at(m, 5)` and
`map_value_at(m, 5)` 49; with the value of `vec_get(v, 5)` or of `string_get_byte(s, 5)` not used, the image of
`return 5;` exits with the status 5, and `vec_get(v, 100000000)` ends with the signal SIGSEGV, status 139; with the
index 0, `vec_get` gives 7 and `map_value_at` gives 2).
`#[raw_memory(open)] fn f(p: i64) -> i64 { return __mind_load_i64(p); }`: Core v1 refuses; the code is `E2502` only, and
the call gets no `E2501`; reference gap (`mindc check` accepts it; the native backend refuses it with
`lane.source.function_contract`; the MLIR backend builds it and its image exits with the status 0). `assert(x == 2);`
with `x = 1`: Core v1; the program makes the [defined stop](../../spec/v1.0/memory.md#the-defined-stop); reference gap
(`mindc check` accepts it; the native backend refuses it with `lane.source.assert`; the MLIR backend builds it, and its
image writes "assertion failed at source span 38..53" and ends with the signal SIGABRT, status 134, not the status 77 of
the defined stop).

**Codes.** [`E2501`](../../spec/v1.0/errors.md#e2501-raw-memory-use-outside-a-raw-memory-function) (raw memory use
outside a raw memory function) and [`E2502`](../../spec/v1.0/errors.md#e2502-invalid-attribute) (invalid attribute) are
new; the published catalog defines neither. The trigger of `E2502` names every attribute: a name that the specification
does not define, a defined attribute at a position that its definition does not give, and an argument form that its
definition does not give. [`E6001`](../../spec/v1.0/errors.md#e6001-out-of-bounds-index) (out-of-bounds index) exists,
and its trigger now names an index function of the standard library too. The trigger of `E2501` excepts the body of a
function whose attribute `raw_memory` `E2502` refuses: that source gets the one code `E2502`.

## DN-15. One model for arrays, maps and strings

**Text before the decision.** [Types](../../spec/v1.0/types.md#record-identity-and-fixed-array-values) said that a value
of a struct type denotes a record with identity, and that a change of a field through one reference is visible through
other references to that record. For an owned `array<T>` the same chapter said that `push` returns the replacement owner
handle, and that a push whose handle cannot be bound again is refused with `E2300`.
[Standard Library](../../spec/v1.0/stdlib.md) said that `vec_push` is functional at the value level and returns the
replacement `Vec` owner, and that the map functions take the `Map` by value and return a fresh `Map` with no change in
place. No sentence said what an older handle shows after a push or an insert, or when the storage of a container is
released. No sentence gave the value of `map_get` for a key that the map does not hold, and no sentence said which
elements a `for` loop over a container visits when the loop changes the container.

**Reference.** `mindc check` accepts each source of this note except the two that are named below, and the MLIR backend
builds each source that it accepts: after `xs.push(5)`, an alias `view` of `xs` that was taken before the push gives
`view[4]` = 5, and after 99 pushes `view[99]` gives 99; `xs = xs.push(2)` gives `xs[1]` = 2. After
`map_insert(m, 1, 10)`, `map_len` of an alias that was taken before gives 0; two inserts through two aliases of a map
with one entry leave its length at 1. After `string_push_byte(s, 97)`, `string_len` of an alias that was taken before
gives 0. `string_slice_from(s, 1)` of `"abc"` keeps the length 2 after a push to `s`, and the record of
`let s: String = "ab";` in a loop has the length 2 after one push in each of two iterations. `mindc check` accepts
`xs.push(2);` where `xs` is bound by `let` without `mut` and where it is a parameter (the MLIR images exit with the
status 0). It refuses `let ys = xs.push(2);` with `E2300`, and it refuses `xs[2]` after a call that pushes to a
`let mut w = p;` copy of the parameter, on `let xs: array<i64> = [1, 2];`, with `E2621`, "index 2 out of bounds for
array of length 2". It accepts a region block in a function with and without `#[raw_memory]`; the native backend refuses
the first with `lane.source.function_contract` and the second with `lane.source.region`, and the MLIR images exit with
the status 0. The native backend refuses the array sources with `lane.type.array` or `lane.type.generic`, and the map
and string sources with `lane.call.unknown`. It accepts `fn f(s: &[i64], xs: array<i64>) -> i64` that pushes 9 through
`let mut w = xs;` and returns `s[2]`, called as `f(xs, xs)` on `let xs: array<i64> = [1, 2];`; the native backend
refuses it with `lane.type.slice`, and the MLIR image exits with the status 9. It accepts `xs.set(0, 5);` and
`return xs[0];` on `let mut xs: array<i64> = [1, 2];`, and the same source with `let` without `mut`; the native backend
refuses both with `lane.type.array`, and the MLIR images exit with the status 5. It accepts `return map_get(m, 7) + 5;`
on `let m = map_insert(map_new(), 1, 10);`; the native backend refuses it with `lane.call.unknown`, and the MLIR image
exits with the status 5, so `map_get` gives 0 for the key that the map does not hold. It accepts
`for v in xs { xs.push(v); n = n + 1; }` and `return n;` on `let mut xs: array<i64> = [1, 2];`; the native backend
refuses it with `lane.type.array`, and the MLIR image exits with the status 2.

**Options.** (A) Every container value is a handle to one record that changes in place, as a struct value is.
(B) A push or an insert consumes the handle, and a use of the old handle is refused at check time. (C) Arrays and
maps as in (A); a string value never changes, and a program builds the bytes of a string in an array.

**Decision.** Option A, decided by the specification owner on 2026-11-25
([Records and containers](../../spec/v1.0/memory.md#records-and-containers)). The container types are `array<T>`, which
is the type of the vector record of `std.vec` (its signatures write `Vec` for `array<i64>`), the type `Map` of `std.map`
and `String`. A value of a container type denotes a container record with identity, as a value of a struct type does. An
array literal where an `array<T>` is expected, a string literal, and a library function that makes a container
(`vec_new`, `map_new`, `string_new`) create a new record. Binding, assigning, passing and returning keep the record;
none of them copies the elements. `push`, the insert function of a map and the string push functions change the record
in place, and a change through one reference is visible through every other reference to that record. A library function
that changes a container and returns a container returns the handle that it received. Each evaluation of a string
literal creates a new string record; an implementation MAY share one read-only record when no change can reach it. A
function that gives a part of a string (`string_slice_from`) creates a new record with a copy of the bytes. On a value
`xs` of type `array<T>`, `xs[i]` is the element `i`, counted from 0, and `xs.push(v)` appends the value `v` of type `T`
to the record and has the value `xs`. `xs.set(i, v)` replaces the element `i` with the value `v` of type `T`. An index
outside the container is the case of [Index bounds](../../spec/v1.0/ir.md#index-bounds)
([DN-21](#dn-21-no-undefined-value-index-bounds-and-size-0-dimensions)): an index or a slice bound that is outside its
axis MUST be refused at check time with `E3011` exactly when it is an integer literal with its sign
([Literals](../../spec/v1.0/lexical.md#literals)), with or without parentheses around it (one pair or more), and the
type gives the extent of the axis; every other index or slice bound that is outside its axis makes the
[defined stop](../../spec/v1.0/memory.md#the-defined-stop) at run time with `E6001`, and an implementation refuses no
other index or slice bound at check time. `map_get(m, key)` gives 0 when `m` holds no pair with the key, and
`map_contains_key` tests whether `m` holds a key
([Four pure-MIND modules](../../spec/v1.0/stdlib.md#four-pure-mind-modules)).

- A slice parameter (`&[T]` or `&mut [T]`) is an extension: the Core v1 grammar does not derive it. Where an
  implementation provides it, a slice made from a container at a call refers to the container record: after a push
  through another reference it shows the grown container, and it never shows released storage.
- [Changing a container](../../spec/v1.0/memory.md#changing-a-container). A method call that changes a container
  (`xs.push(v)`, `xs.set(i, v)`) is a change of the place `xs`. The receiver must be a place whose root name is declared
  with `let mut`, as for an assignment; otherwise the call MUST be refused at check time with `E2402`. A parameter is
  not mutable: a function changes a container that it receives through a binding such as `let mut w = p;`. A `push`
  stands as a statement or in the update `xs = xs.push(v)` of the same place; any other use MUST be refused at check
  time with `E2300`. These rules follow the type of the receiver; a method of the same name on a value that is not a
  container is not affected.
- When a container needs more storage, the implementation moves the elements to new storage and releases the old storage
  if the implementation allocated it. After that, no container handle shows the old storage. A function that releases a
  container explicitly (`vec_free`) is a raw memory function ([DN-14](#dn-14-raw-memory-and-its-mark)), because other
  references to the record can still exist. A use of a container after its explicit release is an error of the program,
  as a read or a write through an address that is not valid
  ([Address validity](../../spec/v1.0/memory.md#address-validity)).
- [Region blocks](../../spec/v1.0/memory.md#region-blocks). A region block is a raw memory use: it stands only in the
  body of a function declared with `#[raw_memory]` or `#[raw_memory(sealed)]`, and a function of the standard library
  also needs the attribute for it. Where a statement can start, the name `region` directly followed by `{` is a region
  block; in the body of a function without that attribute it MUST be refused at check time with `E2501`, by every
  implementation, also one that does not provide region blocks, except in a function whose attribute `raw_memory`
  `E2502` refuses ([Raw memory](../../spec/v1.0/memory.md#raw-memory)).
- [Loops](../../spec/v1.0/language.md#loops). A `for` loop over a container reads the length of the container one time,
  at the start of the loop. For each index from 0 to that length minus 1, in order, one iteration binds the pattern to
  the element at that index. Elements that are added during the loop are not visited, and an element that is no longer
  there when its iteration starts makes the [defined stop](../../spec/v1.0/memory.md#the-defined-stop) of an index
  outside the container, with `E6001`.

These rules replace the sentences on a replacement owner handle and on a fresh `Map` in the types chapter and in
the standard library chapter. No warning period comes before the refusals of this note.

**Form status.** `let mut xs: array<i64> = [1, 2, 3, 4]; let view = xs; xs.push(5);` and a read of `view[4]`: Core v1;
reference gap (the native backend refuses it with `lane.type.array`; the MLIR backend builds it and its image exits with
the status 5, the value of this rule; with 99 pushes through `xs`, `view[99]` gives 99). A read of a map or a string
alias after an insert or a push (`let view = m; let r = map_insert(m, 1, 10);` and `map_len(view)`;
`let t = s; let r = string_push_byte(s, 97);` and `string_len(t)`): Core v1; reference gap (the native backend refuses
both with `lane.call.unknown`; the MLIR backend builds both and their images exit with the status 0 where this rule
gives 1; two inserts through two aliases of a map with one entry leave its length at 1 where this rule gives 3). A part
of a string and a string literal in a loop (`string_slice_from(s, 1)` before a push to `s`; `let s: String = "ab";` and
one push in each of two iterations): Core v1; reference gap (the native backend refuses both with `lane.call.unknown`;
the MLIR backend gives the length 2 of the part, the value of this rule, and the length 2 of the literal record after
the push, where this rule gives 3). `xs.push(2);` where `xs` is bound by `let` without `mut` or is a parameter: Core v1
refuses; the code is `E2402`; reference gap (`mindc check` accepts both; the MLIR backend builds both and their images
exit with the status 0). `let ys = xs.push(2);`: Core v1 refuses; the code is `E2300`; reference conforms (`mindc check`
refuses it with `E2300`). `let mut w = p; w.push(3);` in a function that receives the array `p`, and a read of `xs[2]`
in the caller after the call: Core v1; reference gap (`mindc check` refuses `xs[2]` on `let xs: array<i64> = [1, 2];`
with `E2621`, "index 2 out of bounds for array of length 2"; the native backend refuses it with `lane.type.generic`).
`region { let s: String = "a"; }` in a function without the attribute `raw_memory`, also in a function of the standard
library and also where an implementation does not provide region blocks: Core v1 refuses; the code is `E2501`; reference
gap (`mindc check` accepts it; the native backend refuses it with `lane.source.region`; the MLIR backend builds it and
its image exits with the status 0). `region { let s: String = "a"; }` in a function declared with `#[raw_memory]`:
Extension. `fn f(s: &[i64], xs: array<i64>) -> i64 { }`: Extension. `let mut xs: array<i64> = [1, 2]; xs.set(0, 5);` and
a read of `xs[0]`: Core v1; the value is 5; reference gap (`mindc check` accepts it; the native backend refuses it with
`lane.type.array`; the MLIR backend builds it and its image gives 5, the value of this rule). `xs.set(0, 5);` where `xs`
is bound by `let` without `mut`: Core v1 refuses; the code is `E2402`; reference gap (`mindc check` accepts it; the MLIR
backend builds it and its image gives 5 for a read of `xs[0]`). `map_get(m, 7)` where `m` holds no pair with the key 7:
Core v1; the value is 0; reference gap (`mindc check` accepts it; the native backend refuses it with
`lane.call.unknown`; the MLIR backend builds it and its image gives 0, the value of this rule).
`for v in xs { xs.push(v); n = n + 1; }` on `let mut xs: array<i64> = [1, 2];`: Core v1; the loop runs two iterations;
reference gap (`mindc check` accepts it; the native backend refuses it with `lane.type.array`; the MLIR backend builds
it and its image gives 2, the value of this rule).

**Codes.** No new code. [`E2402`](../../spec/v1.0/errors.md#e2402-invalid-target-of-a-change) (invalid target of a
change) now names a method call that changes a container (`xs.push(v)`, `xs.set(i, v)`); the published catalog does not
define `E2402`. [`E6001`](../../spec/v1.0/errors.md#e6001-out-of-bounds-index) (out-of-bounds index) exists; a `for`
loop that reaches an element that is no longer there makes the defined stop with it. `E3011` is the code of
[DN-21](#dn-21-no-undefined-value-index-bounds-and-size-0-dimensions).
[`E2300`](../../spec/v1.0/errors.md#e2300-collection-mutation-in-expression-position) (collection mutation in expression
position) exists, and its trigger now says which push it refuses: a `push` that stands neither as a statement nor in the
update of the same place. [`E2501`](../../spec/v1.0/errors.md#e2501-raw-memory-use-outside-a-raw-memory-function) names
a region block too, also in a function of the standard library and where an implementation does not provide region
blocks, and not in the body of a function whose attribute `raw_memory` `E2502` refuses, which gets the one code `E2502`.

**Open.**

- What a map keeps of a `String` key when the key is inserted. The normative text says nothing about it until it holds a
  function that inserts a `String` key.

## DN-16. The string type

**Text before the decision.** [Standard Library](../../spec/v1.0/stdlib.md) wrote the type of the message of `panic` as
`string` (`panic(message: string) -> !`) and the keys of a map as `map<string, _>`, and it named the type of the module
`std.string` `String`. [Tokenizer Format](../../spec/v1.0/tokenizer-format.md#encoding-api) wrote the text type of its
functions as `str` (`encode(text: str) -> [u32]`). No sentence of the type rules made one of these names usable in a
type position, and no sentence gave a string literal a type.

**Reference.** `mindc check` accepts `fn echo(s: String) -> String { return s; }` with `let t: String = echo("a");`,
it accepts `let n: i64 = "a";`, and it accepts `let s: string = "a";`. The native backend refuses the first source
with `lane.string.result`, the second with `lane.source.string` and the third with `lane.type.named`.

**Options.** (A) The name is `String`, the type of the module `std.string`, and a string literal has that type.
(B) The name is `string`, a primitive type. (C) No name: a string literal stands only where a function of the
standard library takes one.

**Decision.** Option A, decided by the specification owner on 2026-11-25. The string type is `String`, the type of the
module `std.string` of the standard library ([Type formation](../../spec/v1.0/types.md#type-formation)). Like every
entity of the standard library, `String` is available without an import. A string literal has the type `String`, so
`let s: String = "a";` is valid and `let n: i64 = "a";` MUST be refused at check time with `E2001`. The lower-case
spelling leaves the text: [Standard Library](../../spec/v1.0/stdlib.md) writes `panic(message: String) -> !` and "a map
whose keys are `String` values", and [Tokenizer Format](../../spec/v1.0/tokenizer-format.md#encoding-api) writes
`encode(text: String) -> [u32]` and the other functions of its encoding API with `String`.

**Form status.** `fn echo(s: String) -> String { }`, `let t: String = "a";`: Core v1; reference gap (`mindc check`
accepts it; the native backend refuses a `String` result with `lane.string.result`). `let n: i64 = "a";`: Core v1
refuses; reference gap (`mindc check` accepts it).

**Codes.** [`E2001`](../../spec/v1.0/errors.md#e2001-type-mismatch) (type mismatch) exists.

## DN-17. Elementwise operators

**Text before the decision.** The precedence table of
[Language](../../spec/v1.0/language.md#operator-precedence-and-associativity) listed `.*` and `./` with `*` and `/`,
and `.+` and `.-` with `+` and `-`, and the grammars had them as tokens and as productions at those levels. No
sentence gave them an operand rule, a result type or a value, for scalar or for tensor operands, and
[Core v1 forms](../../spec/v1.0/core-v1-forms.md) gave them the status Open.

**Reference.** `mindc check` accepts each of the four operators on two `i64` scalars, and it accepts `a .* b` with an
`f64` and an `i64` operand. The native backend refuses each of these sources with `lane.source.tensor`. `mindc check`
refuses `t .* s` with `t = tensor([1.0, 2.0])` and a scalar `s` with `E2003`, "unsupported call to `tensor`".

**Options.** (A) The operand rule of the arithmetic operators of
[Tensor operations](../../spec/v1.0/language.md#tensor-operations), and on two scalar operands the value of the
plain operator. (B) Tensor operands only: a scalar operand is refused. (C) Remove the four operators, because `*`,
`/`, `+` and `-` already broadcast.

**Decision.** Option A, decided by the specification owner on 2026-11-25
([Tensor operations](../../spec/v1.0/language.md#tensor-operations)). `.*`, `./`, `.+` and `.-` follow the operand
rule of the arithmetic operators: the operands share a dtype, the shapes follow the
[broadcasting rules](../../spec/v1.0/shapes.md#broadcasting), and a scalar extends to the shape of the other
operand. Operands of two different dtypes MUST be refused at check time with `E2004`. On two scalar operands of one
numeric type, the result is the value of the plain operator with that type: `a .* b` is `a * b`, `a ./ b` is
`a / b`, `a .+ b` is `a + b`, and `a .- b` is `a - b`.

**Form status.** `a .* b`, `a ./ b`, `a .+ b`, `a .- b`: Core v1; reference gap (`mindc check` accepts the four on
two `i64` scalars; the native backend refuses each with `lane.source.tensor`). `a .* b` with an `f64` and an `i64`
operand: Core v1 refuses; reference gap (`mindc check` accepts it).

**Codes.** [`E2004`](../../spec/v1.0/errors.md#e2004-dtype-mismatch-in-binary-operation) (dtype mismatch in binary
operation) exists.

## DN-18. The tensor constructor

**Text before the decision.** `tensor(e)` and `tensor(e, dtype: D)` (`TensorConstructor`) were productions of the
grammar, and [Core v1 forms](../../spec/v1.0/core-v1-forms.md) gave `tensor(e)` and `tensor(e, dtype: f64)` the
status Core v1. No sentence gave the dtype of `tensor(e)` without a dtype argument, its shape, or the meaning of a
dtype argument that differs from the type of `e`.

**Reference.** `mindc check` refuses `tensor([[1, 2], [3, 4]])` and `tensor(true)` with `E2003`, "unsupported call
to `tensor`", and it refuses `tensor(3, dtype: f32)` and `tensor(true, dtype: f32)` with `E1001`, "expected ')',
found Some(':')".

**Options.** (A) The dtype is the dtype argument when one is written, else the dtype of `e`; the shape is the shape
of `e`; a dtype argument that differs from the dtype of `e` converts as a cast where the cast table gives one, and
is refused where it gives none. (B) A fixed dtype, such as `f32`, when no dtype argument is written. (C) The dtype
argument MUST equal the dtype of `e`; no conversion.

**Decision.** Option A, decided by the specification owner on 2026-11-25
([Tensor operations](../../spec/v1.0/language.md#tensor-operations)). `tensor(e)` and `tensor(e, dtype: D)` make a
tensor from the value of `e`. Its shape is the shape of `e`: a scalar `e` gives rank 0, and an array literal gives
its dimensions (`tensor([[1, 2], [3, 4]])` has the shape `[2, 2]`), and a tensor `e` gives its shape. With a dtype
argument the dtype is `D`; without one it is the type of a scalar `e`, the element type of an array `e` at every
nesting level, or the dtype of a tensor `e`, which MUST be a dtype (`i32`, `i64`, `f32` or `f64`); another type, such
as `bool`, a tuple, a struct or `String`, MUST be refused at check time with `E2005`. The dtype argument is not an
expected type for `e`. When `D` differs from the element type of `e`, each element is converted as `as` converts
it where the cast table gives a cast from that type to `D` (`tensor(3, dtype: f32)` holds `3.0`); where the table
gives no such cast, the constructor MUST be refused at check time with `E2016`.

**Form status.** `tensor([[1, 2], [3, 4]])`, `tensor(3, dtype: f32)`: Core v1; reference gap (`mindc check` refuses
the first with `E2003`, "unsupported call to `tensor`", and the second with `E1001`, "expected ')', found Some(':')").
`tensor(true, dtype: f32)`, `tensor(true)`: Core v1 refuses; reference gap (`mindc check` refuses the first with
`E1001` and the second with `E2003`, not with `E2016` and `E2005`).

**Codes.** [`E2005`](../../spec/v1.0/errors.md#e2005-invalid-dtype-for-operation) (invalid dtype for operation) and
[`E2016`](../../spec/v1.0/errors.md#e2016-invalid-cast) (invalid cast) exist. The triggers of both now name the
tensor constructor: `E2005` an argument `e` whose type gives no dtype when no dtype argument is written, and `E2016` a
dtype argument `D` to which the cast table gives no cast from the element type of `e`.

## DN-19. Slice bounds and step

**Text before the decision.** `SliceExpression` derived `a[s:e]`, `a[:e]`, `a[s:]`, `a[:]` and `a[s:e:k]`.
[Language](../../spec/v1.0/language.md#tuple-index) gave a meaning only to `a[e1:e2]`
([DN-11](./decision-notes.md#dn-11-tuple-index-and-range-index)), and no sentence said what an omitted start, end or
step is. [Core v1 forms](../../spec/v1.0/core-v1-forms.md) gave the other forms the status Open.

**Reference.** On the array `[1, 2, 3, 4]`, `mindc check` refuses `a[:2]` and `a[:]` with `E1001`, "unexpected `:`,
expected an expression", and `a[1:]`, `a[0:4:2]` and `a[0:4:0]` with `E1001`, "expected `]` to close index
expression". It refuses `a[::2]` and `a[:::2]` with `E1001`, "unexpected `:`, expected an expression".

**Options.** (A) An omitted start is 0, an omitted end is the length of the axis, and an omitted step is 1.
(B) Only `a[s:e]` is in the language, and the grammar loses the other forms.

**Decision.** Option A, decided by the specification owner on 2026-11-25
([Tuple index](../../spec/v1.0/language.md#tuple-index)). `a[s:e:k]` is a slice: it takes the elements of the axis from
the index `s` up to, and not including, the index `e`, with the step `k`. An omitted `s` is 0, an omitted `e` is the
length of the axis, and an omitted `k` is 1, so for an axis of length `n`, `a[:e]` is `a[0:e:1]`, `a[s:]` is `a[s:n:1]`,
`a[:]` is `a[0:n:1]` and `a[s:e]` is `a[s:e:1]`. The form lowers to the `Slice` operation of
[Core IR](../../spec/v1.0/ir.md#indexing-and-slicing) with these bounds and this step, and the shape of the result
follows the shape rule of that operation: `a[0:4:2]` takes the elements 0 and 2. A step 0 has no slice: the `Slice`
operation needs steps that are not zero, and its catalog code is `E4008`. Inside the brackets of a slice the token `::`
is read as two `:` ([Tokens](../../spec/v1.0/lexical.md#tokens)), so `a[::2]` is `a[0:n:2]`. A bound outside the axis,
and a negative step that is known only at run time, are the case of
[DN-21](#dn-21-no-undefined-value-index-bounds-and-size-0-dimensions).

**Form status.** `a[:e2]`, `a[e1:]`, `a[:]`, `a[e1:e2:e3]`: Core v1; reference gap (`mindc check` refuses each of
`a[:2]`, `a[1:]`, `a[:]` and `a[0:4:2]` with `E1001`). `a[0:4:0]`: Core v1 refuses; reference gap (`mindc check`
refuses it with `E1001`, "expected `]` to close index expression", not with `E4008`). `a[::2]`: Core v1; reference gap
(`mindc check` refuses it with `E1001`, "unexpected `:`, expected an expression").

**Codes.** [`E4008`](../../spec/v1.0/errors.md#e4008-invalid-slice-step) (invalid slice step) exists.

## DN-20. The type of a literal

**Text before the decision.** [Types](../../spec/v1.0/types.md#type-inference) said that expressions without
annotations are checked by "propagating expected types from their context". No sentence gave the type of a literal
with no expected type, and no sentence said what happens to a literal whose value its type cannot hold, or to an
integer literal where a floating-point type is expected.

**Reference.** `mindc check` accepts `let a = 5; let b: i32 = 7; let c = 1.5; let d: f32 = 2.5;`, and it accepts
`let b: i32 = 3000000000;`, `let b: i32 = -2147483648;` and `let d: f32 = 1.0e39;`. It refuses `let y: f64 = 1;` and
`let z: i64 = 1.5;` with `E2015`, "no implicit int↔float conversion", a code that the catalog does not define. It
accepts `let m: i32 = -2147483649;`, and the MLIR image exits with the status 0; with `let a = 3;`, `let b = a-1;` gives
`b` the value 2 on the native and on the MLIR backend. It accepts `if x > 0 { }` followed by `-9223372036854775808;`,
and `while x < 0 { }` followed by `-1;`, and the native and the MLIR images exit with the status 0. It accepts
`let y = { 1 } -9223372036854775808;`; the native backend refuses it with `lane.source.set`, and the MLIR image exits
with the status 0.

**Options.** (A) A literal takes the type of its kind that its context expects, else `i64` or `f64`; a value that
its type cannot hold and a literal of the other kind are refused. (B) As (A), but a literal of the other kind is
converted to the expected type. (C) A literal always has the type `i64` or `f64`, and a program writes a cast for
every other type.

**Decision.** Option A, decided by the specification owner on 2026-11-25
([Type of a literal](../../spec/v1.0/types.md#type-of-a-literal)). A context expects a type in these places: the
annotation of a `let` or a `const`, a parameter (for the argument of a call), the result type of a function (for the
operand of `return` and the tail of the body), the other operand of a binary operator, and an element of an array or
a tensor whose type is given.

1. An integer literal takes the integer type that its context expects. With no expected type, it has the type
   `i64`: in `let a = 5;` the type of `a` is `i64`.
2. A floating-point literal takes the floating-point type that its context expects. With no expected type, it has
   the type `f64`: in `let c = 1.5;` the type of `c` is `f64`.
3. An integer literal whose value is outside the range of its type, and a floating-point literal whose value, rounded to
   its type to the nearest value with ties to even, is greater in magnitude than the largest finite value of that type,
   MUST be refused at check time with `E2408`: `let b: i32 = 3000000000;` is refused. The value of a literal is the
   value of its token. A `-` or `+` directly before the digits is part of the literal only where an operand can start
   ([Literals](../../spec/v1.0/lexical.md#literals)): at the start of an expression, after an operator, after `(`, `[`,
   `{`, `,`, `;`, `=` or `:`, after a keyword, or after the `}` that ends a block-like statement
   ([Block-like statements](../../spec/v1.0/language.md#block-like-statements)). After an identifier, a literal, `)`,
   `]` or any other `}` it is an operator. So `let m: i32 = -2147483648;` holds the one literal `-2147483648`, which
   `i32` can hold, `let m: i32 = -2147483649;` is refused, `a-1` is a subtraction, `if x > 0 { }` followed by `-1;`
   holds the literal `-1`, and `{ 1 } -1` as an operand is a subtraction.
4. An integer literal where a floating-point type is expected, and a floating-point literal where an integer type is
   expected, MUST be refused at check time with `E2001`: `let y: f64 = 1;` and `let z: i64 = 1.5;` are refused.

**Form status.** `let a = 5;`, `let c = 1.5;`, `let b: i32 = 7;`: Core v1; reference conforms (`mindc check` accepts
them). `let b: i32 = 3000000000;`: Core v1 refuses; reference gap (`mindc check` accepts it). `let y: f64 = 1;`,
`let z: i64 = 1.5;`: Core v1 refuses; reference gap (`mindc check` refuses both with `E2015`, "no implicit int↔float
conversion", a code that the catalog does not define, not with `E2001`). `let m: i32 = -2147483648;` and `let b = a-1;`:
Core v1; reference gap (`mindc check` accepts both; the native backend refuses the first with `lane.type.int_width` and
builds the second, whose image exits with the status 2 for `a = 3`; the MLIR backend builds the first and its image
exits with the status 0). `let m: i32 = -2147483649;`: Core v1 refuses; the code is `E2408`; reference gap
(`mindc check` accepts it; the MLIR backend builds it and its image exits with the status 0). `if x > 0 { }` followed by
`-9223372036854775808;`: Core v1; the sign is part of the literal, which `i64` can hold; reference conforms
(`mindc check` accepts it; the native and the MLIR backends build it, and the images exit with the status 0).
`let y = { 1 } -9223372036854775808;`: Core v1 refuses; the sign is an operator, and the literal `9223372036854775808`
is outside the range of `i64`; the code is `E2408`; reference gap (`mindc check` accepts it; the MLIR backend builds it
and its image exits with the status 0).

**Codes.** [`E2408`](../../spec/v1.0/errors.md#e2408-literal-out-of-range) (literal out of range) is new; the
published catalog defines no code for a literal outside the range of its type.
[`E2001`](../../spec/v1.0/errors.md#e2001-type-mismatch) (type mismatch) exists.

## DN-21. No undefined value, index bounds and size-0 dimensions

**Text before the decision.** [Core IR](../../spec/v1.0/ir.md#index-bounds) said for `Index` that out-of-bounds indices
"MAY produce an error, undefined value, or backend-specific handling", and for `Slice` that negative `starts` and `ends`
are clamped to 0 and that an empty slice produces size-0 dimensions.
[Security](../../spec/v1.0/security.md#tensor-safety) said that zero or negative dimensions MUST be rejected, that
indexing operations MUST verify bounds at runtime, and that an out-of-bounds access MUST NOT return undefined values.
[Tensor ranks and shapes](../../spec/v1.0/shapes.md#tensor-ranks-and-shapes) gave a shape as a sequence of positive
integers, and the catalog heading of `E3006` was "Zero or negative dimension". The reshape rule of Core IR computed the
dimension at `-1` from the element count, and no sentence gave the value of a reduction over an axis of extent 0. No
sentence said whether an index outside its axis is refused at check time, and the chapters did not agree on a dimension
of size 0. No sentence refused a negative length of a fixed array type.

**Reference.** On `let a: [i64; 4] = [1, 2, 3, 4];`, `mindc check` refuses `a[4]` with `E2621`, "index 4 out of bounds
for array of length 4", and `a[-1]` with `E2621`, "index -1 out of bounds for array of length 4". It refuses `a[(4)]`
and `a[((4))]` with the message of `a[4]`, and `a[(-1)]` with the message of `a[-1]`; the native backend builds these
three sources, and their images stop with the status 77 of the defined stop and write no diagnostic; the MLIR backend
refuses them with `E2621`. It refuses `a[1:5]`, `a[1:(5)]`, `a[1:4]`, `a[2:2]` and `a[-1:2]` with `E1001`, "expected `]`
to close index expression". It accepts `return a[3];`, and the native and the MLIR images exit with the status 4. It
accepts `return a[2 + 2];` on that array, and the native and the MLIR images stop with the status 77 of the defined stop
and write no diagnostic, also when the read value is not used; with `a[1 + 2]` and the read value not used, the images
of `return 5;` exit with the status 5. It accepts `let i = 4; return a[i];` on that array; the native backend builds it,
and its image stops with the status 77 of the defined stop and writes no diagnostic, also when the read value is not
used; the MLIR backend refuses it: "constant index 4 is out of bounds for a length-4 array". It refuses
`Tensor<f32, [-1, 3]>` in a parameter type with `E1001`, "expected dimension (integer or symbol)", and it accepts
`Tensor<f32, [0, 3]>` there; the native backend refuses that source with `lane.type.tensor`, and the MLIR image exits
with the status 0. It accepts `fn at(a: [i64; 4], i: i64) -> i64 { return a[i]; }` called with 5, and `xs[i]` with
`let i: i64 = 5;` on `let xs: array<i64> = [1, 2];`; the native backend refuses both with `lane.type.array`. The MLIR
image of `at` stops with the status 77 of the defined stop; with the read value not used, it stops in the same way and
writes no diagnostic, and with `at(a, 3)` the image of `return 5;` exits with the status 5. The MLIR image of `xs[i]`
does not stop: it exits with the status 33; with the read value not used, the image of `return 5;` exits with the status
5, and the index 100000000 ends it with the signal SIGSEGV, status 139. It refuses `fn f(a: [i64; -1]) -> i64 { }` with
`E1001`, "expected array length (positive integer)", and the native and the MLIR backends refuse it with `E1001`. It
accepts `let a: [i64; 0] = [];`; the native backend refuses that source with `lane.source.array_element`, and the MLIR
image exits with the status 0. On a parameter `t: Tensor<f32, [0, 3]>` it accepts `reshape(t, [0, -1])`, `mean(t)`,
`max(t)` and `sum(t)`, and it refuses `min(t)` and `prod(t)` with `E2003`, "unsupported call to `min`" and "unsupported
call to `prod`"; the native backend refuses each of the six sources with `lane.type.tensor`, and the MLIR backend
refuses the four sources that the check accepts, each with "non-i64 argument to call" and the name of the function. It
refuses `zeros([n, 3])` in `fn f(n: i64)` with `E2003`, "unsupported call to `zeros`", and `a[0:4:k]` in
`fn g(a: [i64; 4], k: i64)` with `E1001`, "expected `]` to close index expression".

**Options.** (A) No operation gives an undefined value: an index or a slice bound outside its axis is refused at
check time when the check can know it, and makes the defined stop at run time in every other case; no bound is
clamped; a dimension of size 0 is valid and a negative one is refused. (B) As (A), but a slice bound outside the axis
is clamped to the axis. (C) The text before: an index outside its axis gives a value that the implementation chooses.

**Decision.** Option A, decided by the specification owner on 2026-11-25
([Index bounds](../../spec/v1.0/ir.md#index-bounds)). No operation of the language gives an undefined value. An index or
a slice bound that is outside its axis MUST be refused at check time with `E3011` exactly when it is an integer literal
with its sign ([Literals](../../spec/v1.0/lexical.md#literals)), with or without parentheses around it (one pair or
more), and the type gives the extent of the axis; every other index or slice bound that is outside its axis makes the
[defined stop](../../spec/v1.0/memory.md#the-defined-stop) at run time with `E6001`, and an implementation refuses no
other index or slice bound at check time. On `a: [i64; 4]`, `a[4]`, `a[-1]` and `a[(4)]` are refused at check time, and
`a[2 + 2]` and `a[i]` with `i = 4` pass the check and make the defined stop. An index is outside its axis when it is
negative or not less than the extent of the axis, and a slice bound when it is negative or greater than the extent. No
bound is clamped, and no index counts from the end. A dimension of size 0 is valid (an empty slice gives one); a
negative dimension MUST be refused with `E3006`, and a negative dimension that is known only at run time makes the
defined stop, whose diagnostic names `E3006`. [Security](../../spec/v1.0/security.md#tensor-safety) says the same
sentences, and the sentence that out-of-bounds indices MAY produce an undefined value leaves the text.
[Types](../../spec/v1.0/types.md#fixed-array-literal-cardinality) says the same of the length `n` of a fixed array type
`[T; n]`, the extent of its one axis: a length of 0 is valid, and a negative length (`[i64; -1]`) MUST be refused at
check time with `E3006`.

- [Indexing and slicing](../../spec/v1.0/ir.md#indexing-and-slicing). Negative steps are NOT supported; steps MUST be
  positive. A negative step that is known only at run time makes the defined stop, whose diagnostic names `E4008`.
- [Shape manipulation](../../spec/v1.0/ir.md#shape-manipulation). Exactly one entry of the new shape of a reshape MAY be
  the marker `-1`, which is not a dimension. When another entry is 0, the dimension at the marker cannot be computed,
  and the reshape MUST be refused with `E3007`.
- [Empty axes](../../spec/v1.0/ir.md#empty-axes). An axis of extent 0 that a reduction reduces is an empty axis. Over an
  empty axis `Sum` and the library function `sum` give 0, and the library function `prod` gives 1, at each position of
  the result. `Mean` and the library functions `mean`, `max` and `min` have no value over an empty axis: such a
  reduction MUST be refused at check time when the type gives the shape of the input, and makes the defined stop at run
  time otherwise.

**Form status.** `let a: [i64; 4] = [1, 2, 3, 4];` and `a[4]`, `a[-1]`, `a[(4)]`, `a[((4))]` or `a[1:5]`: Core v1
refuses; the code is `E3011`; reference gap (`mindc check` refuses `a[4]`, `a[(4)]` and `a[((4))]` with `E2621`, "index
4 out of bounds for array of length 4", `a[-1]` with `E2621`, "index -1 out of bounds for array of length 4", and
`a[1:5]` and `a[1:(5)]` with `E1001`, "expected `]` to close index expression"). `a[1:4]` and `a[2:2]` on
`let a: [i64; 4]`, and `Tensor<f32, [0, 3]>`: Core v1; reference gap (`mindc check` refuses `a[1:4]` with `E1001`,
"expected `]` to close index expression"; it accepts `Tensor<f32, [0, 3]>` in a parameter type, the native backend
refuses that with `lane.type.tensor`, and the MLIR backend builds it and its image exits with the status 0).
`Tensor<f32, [-1, 3]>`: Core v1 refuses; the code is `E3006`; reference gap (`mindc check` refuses it with `E1001`,
"expected dimension (integer or symbol)"). `fn f(a: [i64; -1]) -> i64 { }`: Core v1 refuses; the code is `E3006`;
reference gap (`mindc check` refuses it with `E1001`, "expected array length (positive integer)", and the native and the
MLIR backends refuse it with `E1001`). `fn at(a: [i64; 4], i: i64) -> i64 { return a[i]; }` called with 5, `a[2 + 2]`
and `a[i]` after `let i = 4;` on `let a: [i64; 4]`, and `xs[i]` with `i = 5` on an `array<i64>` of two elements: Core
v1; the check accepts it, and the program makes the [defined stop](../../spec/v1.0/memory.md#the-defined-stop) with
`E6001`; reference gap (`mindc check` accepts all four; the native backend refuses `at` and `xs[i]` with
`lane.type.array`, and builds `a[2 + 2]` and `a[i]`, whose images stop with the status 77 of the defined stop, also when
the read value is not used, and write no diagnostic; the MLIR backend refuses `a[i]` after `let i = 4;` ("constant index
4 is out of bounds for a length-4 array"), builds `at` and `a[2 + 2]`, whose images stop in the same way, and builds
`xs[i]`, whose image does not stop: `return xs[i];` exits with the status 33, with the read value not used the image of
`return 5;` exits with the status 5, and the index 100000000 ends it with the signal SIGSEGV, status 139; with an index
inside the axis, `a[1 + 2]` and `at(a, 3)`, the images of `return 5;` exit with the status 5). `reshape(t, [0, -1])` on
`t: Tensor<f32, [0, 3]>`: Core v1 refuses; the code is `E3007`; reference gap (`mindc check` accepts it; the native
backend refuses it with `lane.type.tensor`; the MLIR backend refuses it: "non-i64 argument to call `reshape`").
`mean(t)`, `max(t)` and `min(t)` on `t: Tensor<f32, [0, 3]>`: Core v1 refuses; reference gap (`mindc check` accepts
`mean(t)` and `max(t)`, and refuses `min(t)` with `E2003`, "unsupported call to `min`"; the native backend refuses all
three with `lane.type.tensor`; the MLIR backend refuses `mean(t)` and `max(t)`: "non-i64 argument to call"). `sum(t)`
and `prod(t)` on `t: Tensor<f32, [0, 3]>`: Core v1; the sum is 0 and the product is 1; reference gap (`mindc check`
accepts `sum(t)` and refuses `prod(t)` with `E2003`, "unsupported call to `prod`"; the native backend refuses both with
`lane.type.tensor`; the MLIR backend refuses `sum(t)`: "non-i64 argument to call `sum`"). `zeros([n, 3])` in
`fn f(n: i64)` called with -1, and `a[0:4:k]` in `fn g(a: [i64; 4], k: i64)` called with -1: Core v1; the program makes
the defined stop, whose diagnostic names `E3006` and `E4008`; reference gap (`mindc check` refuses `zeros([n, 3])` with
`E2003`, "unsupported call to `zeros`", and `a[0:4:k]` with `E1001`, "expected `]` to close index expression").

**Codes.** [`E3011`](../../spec/v1.0/errors.md#e3011-index-outside-its-axis) (index outside its axis) is new; the
published catalog defines no code for it. Its trigger is an index, or a slice bound, outside its axis that is an integer
literal with its sign, with or without parentheses around it (one pair or more), where the type gives the extent of the
axis, and no other index or bound. [`E3006`](../../spec/v1.0/errors.md#e3006-negative-dimension) exists, and its heading
"Zero or negative dimension" is now "Negative dimension". Its trigger now names a negative length of a fixed array type
too, says that the marker `-1` of a reshape is not a dimension, and says that a negative dimension that is known only at
run time makes the defined stop, whose diagnostic names this code.
[`E3007`](../../spec/v1.0/errors.md#e3007-element-count-mismatch) (element count mismatch) exists, and its trigger now
names a reshape whose marker `-1` cannot be computed because another entry of the new shape is 0.
[`E4008`](../../spec/v1.0/errors.md#e4008-invalid-slice-step) (invalid slice step) exists, and its trigger now says that
a negative step that is known only at run time makes the defined stop, whose diagnostic names this code.
[`E6001`](../../spec/v1.0/errors.md#e6001-out-of-bounds-index) (out-of-bounds index) exists, and its trigger now names
an index or a slice bound outside its axis at run time.
