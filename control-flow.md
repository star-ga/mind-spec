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

# Control Flow

## If Expressions
In MIND, `if` is an expression that returns a value.
```rust
let y = if x > 0 { 1 } else { -1 };
```

## Loops
- **loop**: Infinite loop.
- **while**: Condition-based loop.
- **for**: Iterator-based loop.

## Match
Pattern matching is exhaustive.
```rust
match value {
    0 => print!("Zero"),
    _ => print!("Non-zero"),
}
```
