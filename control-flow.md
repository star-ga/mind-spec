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
```mind
let y = if x > 0 { 1 } else { -1 };
```

## Loops
- **while**: Condition-based loop.
- **for**: Iterator-based loop.

Core v1 has no `loop` statement: write `while true { ... }`. Where a statement can start, the name `loop` directly
followed by `{` is refused with `E2405` ([Loop exits](spec/v1.0/language.md#loop-exits)). In every other place `loop`
is a valid name: in `while loop { }` it is the condition of the `while`.

## Match
Pattern matching is exhaustive.
```mind
let first = match pair {
    (a, _) => a,
};
```
