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

## Foreign Functions

MIND code may declare functions whose implementation is provided by the host
runtime via the `extern fn` keyword. Foreign function declarations name the
symbol and its full signature; they have no body in MIND source.

```rust
module crypto {
    extern fn sha256(data: [u8]) -> [u8; 32]
    extern fn random_bytes_32() -> [u8; 32]
}
```

The compiler emits each `extern fn` as an unresolved symbol reference at IR
emission time. The runtime backend is responsible for resolving the symbol
during link or load. A backend that cannot supply a required symbol MUST
refuse to lower the module rather than emitting a silent stub — the
attestation chain relies on every symbol being satisfied by a known
implementation.

### Determinism semantics
`extern fn` declarations are NOT statically known to be bit-identical across
runs or architectures. Programs that depend on cross-architecture
bit-identity for their outputs MUST keep extern call results out of any
hashed preimage (for example, attestation envelope `result_hash` fields).
Extern results MAY flow into envelope wrappers (timestamp slots, error
frames, session identifiers) and into side-effecting paths (stdout, stderr,
file I/O) without violating bit-identity, provided the hashed outputs of the
program do not depend on them.

### Surface restrictions
- Generic parameters on `extern fn` are RESERVED. Implementations MAY accept
  them in a future revision; for Core v1 the declaration must be
  monomorphic.
- Variadic foreign signatures (`...`) are NOT supported. Callers must
  fully enumerate parameters.
- `extern fn` declarations MAY appear at the top level of a `module`. They
  inherit the visibility of the surrounding scope; a top-level `extern fn`
  is module-private unless re-exported via `pub use`.

### Reference implementations
- `star-ga/512-mind/src/nexus_key.mind` declares HSM and AEAD primitives as
  `extern fn` and resolves them through the 512-mind HSM runtime adapter.
- `star-ga/mind-nerve/src/runtime_ffi.mind` declares I/O, time, and entropy
  primitives consumed by the inference path; mind-runtime resolves them on
  CPU and CUDA backends.

