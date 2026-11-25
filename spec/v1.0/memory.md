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

# Memory Model (Normative)

This chapter says what a value of a container type denotes, when the storage of a container is released, which functions
use raw memory, how long an address is valid, and how a failed check of the standard library stops a program. A value of
a struct type denotes a record with identity ([Record identity](./types.md#record-identity-and-fixed-array-values)); a
container follows the same rule.

## Records and containers

The container types are `array<T>`, the type `Vec` of `std.vec`, the type `Map` of `std.map` and `String`
([Four pure-MIND modules](./stdlib.md#four-pure-mind-modules)). A value of a container type denotes a container
record with identity, as a value of a struct type does. An array literal where an `array<T>` is expected, a string
literal, and a library function that makes a container (`vec_new`, `map_new`, `string_new`) create a new record.
Binding, assigning, passing and returning keep the record; none of them copies the elements.

`push`, the insert function of a map and the string push functions change the record in place, and a change
through one reference is visible through every other reference to that record. A library function that changes a
container and returns a container returns the handle that it received (`vec_push`, `map_insert`,
`string_push_byte`, `string_push_str`, `string_push_i64`). Each evaluation of a string literal creates a new string
record; an implementation MAY share one read-only record when no change can reach it. A function that gives a part
of a string (`string_slice`, `string_slice_from`) creates a new record with a copy of the bytes. A map keeps the
bytes that a string key had when it was inserted.

On a value `xs` of type `array<T>`, `xs[i]` is the element `i`, counted from 0, and `xs.push(v)` appends the value
`v` of type `T` to the record and has the value `xs`. An index outside the container is the case of
[Index bounds](./ir.md#index-bounds).

A slice made from a container at a call (a `&[T]` or `&mut [T]` parameter,
[Slice call implementation boundary](./types.md#slice-call-implementation-boundary)) refers to the container
record: after a push through another reference it shows the grown container, and it never shows released storage.

## Changing a container

A method call that changes a container (`xs.push(v)`) is a change of the place `xs`
([Bindings and assignment](./language.md#bindings-and-assignment)). The receiver must be a place whose root name is
declared with `let mut`, as for an assignment; otherwise the call MUST be refused at check time with
[`E2402`](./errors.md#e2402-invalid-assignment-target). A parameter is not mutable: a function changes a container
that it receives through a binding such as `let mut w = p;`. A `push` stands as a statement or in the update
`xs = xs.push(v)` of the same place; any other use MUST be refused at check time with
[`E2300`](./errors.md#e2300-collection-mutation-in-expression-position): after `let mut xs: array<i64> = [1];`, the
statement `let ys = xs.push(2);` is refused. These rules follow the type of the receiver; a method of the same name
on a value that is not a container is not affected.

When a container needs more storage, the implementation moves the elements to new storage and releases the old
storage if the implementation allocated it. After that, no container handle shows the old storage. A function that
releases a container explicitly (`vec_free`) is a [raw memory function](#raw-memory-functions), because other
references to the record can still exist.

## Raw memory

An address is an `i64` value that a raw memory function gives or takes. A **raw memory function** is a function that
the list of [raw memory functions](#raw-memory-functions) names, or a function declared with `#[raw_memory]`. An
implementation that adds an external function as an extension treats one with a pointer type in its signature, or
with the tag `unsafe fn`, as a raw memory function. A call of a raw memory function, and a
[region block](#region-blocks), is a **raw memory use**.

A call of a raw memory function is allowed only in the body of a function declared with `#[raw_memory]` or
`#[raw_memory(sealed)]`, or in a function of the standard library. A region block is allowed only in the body of a
function declared with `#[raw_memory]` or `#[raw_memory(sealed)]`; a function of the standard library also needs the
attribute for a region block ([Region blocks](#region-blocks)). Any other raw memory use MUST be refused at check time
with [`E2501`](./errors.md#e2501-raw-memory-use-outside-a-raw-memory-function).

`#[raw_memory(sealed)]` states that no parameter and no result of the function carries an address and that the
function keeps no address after it returns. A call of a sealed function is not a raw memory use. An implementation
does not check this statement.

The attribute `raw_memory` stands only directly before a function declaration and takes no argument or the one
argument `sealed` ([Attributes](./language.md#attributes)). Any other use of the attribute `raw_memory`, before
another item or with another argument, MUST be refused at check time with
[`E2502`](./errors.md#e2502-invalid-attribute).

In a raw memory function the program keeps the [address rules](#address-validity). An implementation does not have
to detect a read or a write through an address that is not valid, and this specification gives the value of such a
read no meaning.

## Address validity

An address that a function gives for the storage of a buffer (`vec_addr`, `string_addr`, `map_keys_addr`,
`map_vals_addr`, `vec_zeroed`) is valid until the next operation that can grow, shrink or release that buffer. An
address from `__mind_alloc` or `__mind_realloc` is valid until it is passed to `__mind_free` or `__mind_realloc`. A
read or a write through an address that is not valid, and a read of memory that the program did not write after the
allocation, is an error of the program. An implementation does not have to detect it, and this specification gives
the value of such a read no meaning.

Determinism rule: an implementation MAY return different concrete addresses across runs, but a program that keeps
the address rules above and the rules of [Records and containers](#records-and-containers) MUST observe the same
logical behaviour byte-for-byte given identical inputs. The rule makes no statement about a program that breaks an
address rule.

## Raw memory functions

These functions of the standard library and intrinsics of the lowering take or give an address, or release the
storage of a container. Each is a raw memory function: a call of one is allowed only in a function declared with
`#[raw_memory]` or `#[raw_memory(sealed)]`, or in a function of the standard library.

| Function | Takes or gives |
| --- | --- |
| `__mind_alloc`, `__mind_realloc` | give an address (`__mind_realloc` also takes one) |
| `__mind_free` | takes an address and frees its region |
| `__mind_load_i8`, `__mind_load_i16`, `__mind_load_i32`, `__mind_load_i64` | take an address |
| `__mind_store_i8`, `__mind_store_i16`, `__mind_store_i32`, `__mind_store_i64` | take an address |
| `__mind_read`, `__mind_write` | take the address of a buffer |
| `__mind_group_bank_i64`, `__mind_group_acc32_i64`, `__mind_group_accrows_i64` | take addresses and write memory ([MLIR lowering](./mlir-lowering.md)) |
| `vec_addr`, `string_addr`, `map_keys_addr`, `map_vals_addr`, `vec_zeroed` | give the address of a buffer |
| `vec_free` | releases the storage of a container, which other references to the record can still reach |
| `print_bytes`, `eprint_bytes`, `read_stdin_bytes`, `file_read`, `file_write` | take the address of a buffer |

An intrinsic that an implementation adds beyond this specification and that takes or gives an address is a raw
memory function too, for example `__mind_open`, which takes the address of a path, and `__mind_argv`, which gives an
address.

## Region blocks

A region block (`region { ... }`) releases, at its end, the storage that was allocated in it, while references to that
storage can still exist. The Core v1 grammar does not derive it; an implementation MAY provide it as an extension. A
region block is a raw memory use: it stands only in the body of a function declared with `#[raw_memory]` or
`#[raw_memory(sealed)]`, and a function of the standard library also needs the attribute for it. Where a statement can
start, the name `region` directly followed by `{` is a region block; in the body of a function without that attribute it
MUST be refused at check time with [`E2501`](./errors.md#e2501-raw-memory-use-outside-a-raw-memory-function), by every
implementation, also one that does not provide region blocks.

## Library functions that check

A function of the standard library that is not a raw memory function is safe for every argument: no argument makes
it read or write memory outside the storage that its containers own. An index function (`vec_get`, `vec_set`,
`string_get_byte`, `map_key_at`, `map_value_at`) MUST make the [defined stop](#the-defined-stop) when the index is
not less than the length of the container or is negative, with
[`E6001`](./errors.md#e6001-out-of-bounds-index). A form of an index function that does not check the index has its
own name and is declared with `#[raw_memory]`; this specification names no such form.

## The defined stop

The defined stop is how a program ends when a check of the language or of the standard library fails at run time:
an index function outside its container, an index or a slice bound outside its axis
([Index bounds](./ir.md#index-bounds)), and a false `assert`
([Control flow and assertions](./stdlib.md#control-flow-and-assertions)). At the defined stop the program ends at
the failed check: no later step of the program runs and `main` returns no value. The implementation writes a
diagnostic with the source location and, where the check has a code, that code; the process status is not 0. The stop is
at the same step of the program on every substrate.
