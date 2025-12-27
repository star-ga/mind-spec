<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# RFC-0002: Mind AI Protocol (MAP)

| Status | Accepted |
|--------|----------|
| Author | STARGA AI Engineering |
| Created | 2025-12-26 |
| Updated | 2025-12-26 |
| Target | mind-spec v1.1, mind v0.2 |
| Depends | RFC-0001 (MindIR Compact) |

## Summary

This RFC defines the **Mind AI Protocol (MAP)**, a request-response protocol enabling AI agents to
interact with the MIND compiler in a structured, safe, and verifiable manner. MAP provides a
compiler-in-the-loop experience where AI can propose changes, receive type-checked feedback, and
iterate until correctness is achieved.

## Motivation

AI-assisted code generation faces a fundamental challenge: LLMs generate code that may be
syntactically valid but semantically incorrect. Without compiler feedback, AI agents cannot:

1. Validate their generated code before presenting to users
2. Receive structured diagnostic information to guide corrections
3. Safely apply incremental patches to existing code
4. Operate within defined security boundaries

MAP solves this by providing a bidirectional protocol where the compiler acts as a verification
oracle, enabling AI agents to achieve higher correctness rates through iterative refinement.

## Design Goals

1. **Compiler-in-the-Loop**: Every AI-generated change is verified before acceptance.
2. **Incremental Patching**: Support fine-grained modifications, not just full rewrites.
3. **Structured Diagnostics**: Return machine-readable errors with fix suggestions.
4. **Sandboxed Execution**: Restrict AI capabilities to safe operations.
5. **Token Efficiency**: Minimize protocol overhead for AI context windows.
6. **Stateful Sessions**: Maintain compilation context across interactions.

## Protocol Overview

MAP operates over a bidirectional text stream (stdin/stdout, WebSocket, or TCP). Each message is
a single line terminated by newline.

### Message Format

**Requests** (AI → Compiler):
```
@<seq> <command> [args...]
```

**Responses** (Compiler → AI):
```
=<seq> <status> [data...]
```

**Events** (Compiler → AI, unsolicited):
```
!<event> [data...]
```

Where:
- `<seq>` is a monotonic sequence number for request/response correlation
- `<status>` is `ok`, `err`, or `partial`
- `<event>` is an event type (e.g., `diag`, `progress`)

## Session Lifecycle

### 1. Handshake

```
# AI initiates
@1 hello mic=1 map=1

# Compiler responds with capabilities
=1 ok version=0.2.0 mic=1 map=1 features=[patch,check,run,fix]
```

### 2. Load Module

```
# Load from file
@2 load path=/project/model.mind

# Or load inline MIC
@3 load.mic <<EOF
mic@1
S0 "x"
T0 f32
T1 [f32;3,4]
N1 input S0 T1
O N1
EOF

=3 ok nodes=1 types=2 symbols=1
```

### 3. Interact

See Commands section below.

### 4. Close

```
@99 bye
=99 ok
```

## Commands

### Core Commands

#### `hello` - Initialize Session

```
@1 hello mic=1 map=1 [mode=<mode>]
=1 ok version=<version> mic=<mic-version> map=<map-version> features=[...]
```

Modes:
- `default`: Full capabilities
- `no_io`: Disable file I/O operations
- `no_unsafe`: Disable unsafe operations
- `pure_only`: Only pure (side-effect-free) operations

#### `load` - Load Module

```
@2 load path=<filepath>
=2 ok nodes=<n> types=<n> symbols=<n>
=2 err msg="file not found"
```

#### `load.mic` - Load Inline MIC

```
@3 load.mic <<EOF
<mic content>
EOF
=3 ok nodes=<n> types=<n> symbols=<n>
=3 err line=<n> msg="parse error"
```

#### `dump` - Export Current Module

```
@4 dump [format=mic|ir|json]
=4 ok <<EOF
<module content>
EOF
```

#### `bye` - Close Session

```
@99 bye
=99 ok
```

### Verification Commands

#### `check` - Type Check Module

```
@5 check
=5 ok diags=0
=5 ok diags=2 <<EOF
W:N3:shape may be dynamic
E:N7:type mismatch in matmul
EOF
```

Diagnostic format: `<severity>:<node>:<message>`
- Severity: `E` (error), `W` (warning), `I` (info), `H` (hint)

#### `verify` - Run Full Verification

```
@6 verify [level=basic|strict|pedantic]
=6 ok
=6 err count=<n> <<EOF
<diagnostics>
EOF
```

#### `lint` - Style and Best Practice Checks

```
@7 lint [rules=all|perf|style|security]
=7 ok hints=0
=7 ok hints=3 <<EOF
H:N4:prefer fused add-relu
H:N12:unused intermediate
H:N15:potential precision loss
EOF
```

### Patch Commands

#### `patch.insert` - Insert New Node

```
@8 patch.insert after=N5 <<EOF
N6 relu N5 T2
EOF
=8 ok id=N6
=8 err msg="invalid reference N99"
```

#### `patch.delete` - Delete Node

```
@9 patch.delete N6
=9 ok
=9 err msg="N6 has dependents: N7, N8"
```

#### `patch.replace` - Replace Node

```
@10 patch.replace N6 <<EOF
N6 gelu N5 T2
EOF
=10 ok
=10 err msg="type mismatch"
```

#### `patch.attr` - Modify Attribute

```
@11 patch.attr N12 axes=[0,1]
=11 ok
```

#### `patch.rename` - Rename Symbol

```
@12 patch.rename S3 "output_logits"
=12 ok refs=5
```

#### `patch.batch` - Atomic Batch Patch

```
@13 patch.batch <<EOF
delete N8
insert after=N5 { N8 gelu N5 T2 }
replace N12 { N12 sum N8 [0] kd=1 T3 }
EOF
=13 ok applied=3
=13 partial applied=2 failed=1 <<EOF
E:replace N12:type mismatch
EOF
```

### Query Commands

#### `query.node` - Get Node Details

```
@14 query.node N5
=14 ok kind=matmul inputs=[N3,N4] type=T2 shape=[256,128]
```

#### `query.type` - Get Type Details

```
@15 query.type T2
=15 ok dtype=f32 shape=[256,128] rank=2
```

#### `query.deps` - Get Dependencies

```
@16 query.deps N10 [direction=up|down|both]
=16 ok up=[N8,N5,N3,N4,N1,N2] down=[N12,N15]
```

#### `query.stats` - Get Module Statistics

```
@17 query.stats
=17 ok nodes=42 params=1.2M flops=2.4G mem=4.8MB
```

### Execution Commands

#### `run` - Execute Module

```
@18 run inputs={x:[1.0,2.0,3.0]} [device=cpu|cuda]
=18 ok outputs={y:[2.5,3.5,4.5]} time=1.2ms
=18 err msg="shape mismatch"
```

#### `profile` - Profile Execution

```
@19 profile inputs={...} [iterations=100]
=19 ok <<EOF
total=125ms mean=1.25ms std=0.05ms
N5:matmul 45% 56ms
N12:conv2d 30% 38ms
N8:relu 5% 6ms
other 20% 25ms
EOF
```

### Fix Commands

#### `fix` - Apply Suggested Fix

```
@20 fix diag=1
=20 ok applied=1 <<EOF
N7 matmul N5 N6 T3  # was: T2
EOF
```

#### `fix.all` - Apply All Auto-Fixes

```
@21 fix.all [scope=errors|warnings|all]
=21 ok applied=5 remaining=2
```

### Transform Commands

#### `opt` - Optimize Module

```
@22 opt [level=0|1|2|3] [passes=fold,fuse,tile]
=22 ok before=42 after=38 removed=4
```

#### `autodiff` - Generate Gradients

```
@23 autodiff wrt=[N2,N3] output=N15
=23 ok grad_nodes=12 <<EOF
N16 grad.matmul.lhs ...
N17 grad.matmul.rhs ...
...
EOF
```

## Events (Unsolicited)

The compiler may emit events without a request:

```
!diag E:N7:type mismatch detected
!progress check 50%
!warn memory approaching limit
```

Events do not require responses.

## Error Codes

| Code | Meaning |
|------|---------|
| E001 | Parse error |
| E002 | Invalid reference |
| E003 | Type mismatch |
| E004 | Shape mismatch |
| E005 | Unsupported operation |
| E006 | Permission denied |
| E007 | Resource limit exceeded |
| E008 | Session error |
| E009 | Internal error |

## Security Model

MAP supports restricted execution modes to sandbox AI operations:

### Mode: `no_io`
- Disables: `load path=`, file writes, network access
- Allows: `load.mic`, `dump`, all verification and patch commands

### Mode: `no_unsafe`
- Disables: Raw pointer operations, unchecked indexing
- Allows: Safe tensor operations only

### Mode: `pure_only`
- Disables: Any operation with side effects
- Allows: Pure functional transformations only

Modes can be combined:
```
@1 hello mic=1 map=1 mode=no_io,no_unsafe
```

## Session State

The protocol is stateful. Each session maintains:

1. Current module (loaded via `load` or `load.mic`)
2. Modification history (for undo support)
3. Cached diagnostics
4. Execution context (device, memory)

State is lost on session close or crash.

## Wire Format

### Text Mode (Default)
- UTF-8 encoding
- LF line terminator
- Heredocs use `<<EOF ... EOF` syntax
- Suitable for stdio, debugging

### Binary Mode (Optional)
- MessagePack encoding
- Length-prefixed frames
- Higher throughput for production

Mode selection:
```
@1 hello mic=1 map=1 wire=binary
=1 ok wire=binary
<subsequent messages in MessagePack>
```

## Example Session

```
# AI initiates session
@1 hello mic=1 map=1 mode=no_io
=1 ok version=0.2.0 mic=1 map=1 features=[patch,check,run,fix]

# AI loads a module inline
@2 load.mic <<EOF
mic@1
S0 "x"
S1 "w"
T0 f32
T1 [f32;784]
T2 [f32;784,256]
T3 [f32;256]
N1 input S0 T1
N2 input S1 T2
N3 matmul N1 N2 T3
O N3
EOF
=2 ok nodes=3 types=4 symbols=2

# AI checks for errors
@3 check
=3 ok diags=0

# AI adds relu activation
@4 patch.insert after=N3 <<EOF
N4 relu N3 T3
EOF
=4 ok id=N4

# AI updates output
@5 patch.replace O <<EOF
O N4
EOF
=5 ok

# AI verifies final module
@6 check
=6 ok diags=0

# AI exports result
@7 dump format=mic
=7 ok <<EOF
mic@1
S0 "x"
S1 "w"
T0 f32
T1 [f32;784]
T2 [f32;784,256]
T3 [f32;256]
N1 input S0 T1
N2 input S1 T2
N3 matmul N1 N2 T3
N4 relu N3 T3
O N4
EOF

# AI closes session
@8 bye
=8 ok
```

## Implementation Notes

### Concurrency
- Single session per connection
- Commands within a session are processed sequentially
- Multiple concurrent sessions are supported

### Buffering
- Responses are line-buffered
- Large outputs (dumps, profiles) use heredoc syntax
- Progress events may be sent during long operations

### Timeouts
- Default command timeout: 30 seconds
- Configurable via `@n timeout <ms>` before command
- Long-running commands (`run`, `profile`) have extended timeouts

## Backwards Compatibility

- Protocol version is negotiated at handshake
- Unknown commands return `E005`
- Unknown arguments are ignored with warning
- Features are capability-gated

## Security Considerations

1. **Input Validation**: All inputs are validated before processing
2. **Resource Limits**: Memory, CPU, and output size are bounded
3. **Sandboxing**: Restricted modes prevent dangerous operations
4. **Audit Logging**: All commands may be logged for review
5. **Rate Limiting**: Excessive requests may be throttled

## Related Work

- Language Server Protocol (LSP): Similar structure, but heavier and not AI-optimized
- Debug Adapter Protocol (DAP): Execution-focused, not compilation-focused
- Jupyter Protocol: REPL-focused, not compiler-focused

## References

- [RFC-0001: MindIR Compact](./0001-mindir-compact.md)
- [Core IR Specification](../../spec/v1.0/ir.md)
- [Error Codes](../../spec/v1.0/errors.md)

## Appendix A: Command Summary

| Command | Args | Description |
|---------|------|-------------|
| `hello` | `mic=`, `map=`, `mode=` | Initialize session |
| `bye` | | Close session |
| `load` | `path=` | Load from file |
| `load.mic` | heredoc | Load inline MIC |
| `dump` | `format=` | Export module |
| `check` | | Type check |
| `verify` | `level=` | Full verification |
| `lint` | `rules=` | Style checks |
| `patch.insert` | `after=`, heredoc | Insert node |
| `patch.delete` | node-id | Delete node |
| `patch.replace` | node-id, heredoc | Replace node |
| `patch.attr` | node-id, attrs | Modify attribute |
| `patch.rename` | symbol-id, name | Rename symbol |
| `patch.batch` | heredoc | Batch operations |
| `query.node` | node-id | Node details |
| `query.type` | type-id | Type details |
| `query.deps` | node-id, `direction=` | Dependencies |
| `query.stats` | | Module statistics |
| `run` | `inputs=`, `device=` | Execute |
| `profile` | `inputs=`, `iterations=` | Profile |
| `fix` | `diag=` | Apply fix |
| `fix.all` | `scope=` | Apply all fixes |
| `opt` | `level=`, `passes=` | Optimize |
| `autodiff` | `wrt=`, `output=` | Generate gradients |

## Appendix B: Reference Implementation

See `mind/src/tools/mind-ai/` for the reference Rust implementation:
- `protocol.rs`: Message parsing and serialization
- `session.rs`: Session state management
- `commands.rs`: Command handlers
- `server.rs`: Transport layer (stdio, TCP, WebSocket)
