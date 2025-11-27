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

# Functions

Functions are the primary unit of code organization in MIND.

## Syntax
Functions are declared using the `fn` keyword.
```rust
fn add(a: i32, b: i32) -> i32 {
    return a + b;
}
```

## Implicit Returns
If the last expression in a block has no semicolon, it is returned.
```rust
fn square(x: i32) -> i32 {
    x * x
}
```
