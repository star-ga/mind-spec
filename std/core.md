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

# Core Library

Essential utilities included in every MIND program.

> **Status: design sketch (informative).** The macro forms below (`print!`/`panic!` with `&[u8]`
> slice parameters and variadic arguments) are a target design — macros, slices, and variadics are
> not in the shipped executable subset (v0.10.x). The shipped I/O and abort surface is the
> function-based one in [`spec/v1.0/stdlib.md`](../spec/v1.0/stdlib.md) (`io` module + `std.io`).

## IO
```
macro print!(fmt: &[u8], args...)
```
Prints to stdout.

## Panic
```
macro panic!(msg: &[u8]) -> !
```
Terminates the program immediately.
