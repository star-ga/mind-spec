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

# RFC-0001: MindIR Compact (MIC) Format

| Status | Accepted |
|--------|----------|
| Author | STARGA AI Engineering |
| Created | 2025-12-26 |
| Updated | 2025-12-26 |
| Target | mind-spec v1.1, mind v0.2 |

## Summary

This RFC defines **MindIR Compact (MIC)**, a text-based, line-oriented, token-efficient serialization
format for MIND Core IR. MIC is designed specifically for AI agent consumption, enabling LLMs to read,
reason about, and generate valid IR patches with minimal token overhead.

## Motivation

Current IR serialization formats are designed for human readability or binary efficiency, neither of
which is optimal for AI-assisted development workflows. AI agents (LLMs) have unique requirements:

1. **Token efficiency**: LLMs pay per-token; verbose formats waste context window and budget.
2. **Line-oriented structure**: Git diffs, code reviews, and patch operations work line-by-line.
3. **Deterministic ordering**: AI agents need predictable output for reliable diffs.
4. **Stable identifiers**: Node IDs must be monotonic and never reused for safe patching.
5. **Text over binary**: LLMs cannot reason over binary data.

MIC addresses these requirements with a minimal, canonical format that preserves full IR semantics.

## Design Principles

1. **Token Minimal**: Every character earns its place. No redundant delimiters or whitespace.
2. **Line-Oriented**: One node per line. Git-friendly diffs. Streaming parseable.
3. **Stable IDs**: Monotonic numeric IDs. Never reused. Safe for concurrent patch operations.
4. **Canonical Order**: Deterministic serialization. Same IR always produces same MIC.
5. **Roundtrip Lossless**: `parse(emit(ir)) == ir` for all valid IR modules.
6. **Self-Describing**: Version header. No external schema required.

## Format Specification

### File Structure

```
mic@1                           # Version header (required, line 1)
# Comment lines start with #    # Comments (optional)
S<id> "<name>"                  # Symbol table entries
T<id> <type>                    # Type table entries
N<id> <kind> <args...>          # Node definitions
O <id>                          # Output markers
```

### Version Header

The first non-empty, non-comment line MUST be the version header:

```
mic@1
```

Future versions increment the version number. Parsers MUST reject unknown versions.

### Symbol Table

Symbols (function names, variable names) are interned into a symbol table:

```
S0 "main"
S1 "input_x"
S2 "weight"
```

Format: `S<id> "<name>"` where:
- `<id>` is a non-negative integer (0-indexed, monotonic)
- `<name>` is a quoted string with standard escapes (`\\`, `\"`, `\n`, `\t`)

### Type Table

Types are interned to avoid repetition:

```
T0 i32
T1 i64
T2 f32
T3 f64
T4 [f32;3,4]
T5 [f64;2,3,4]
T6 [f32;?]
```

Format: `T<id> <type-spec>` where `<type-spec>` is:
- Scalar: `i32`, `i64`, `f32`, `f64`, `bool`
- Tensor: `[<dtype>;<shape>]` where shape is comma-separated dimensions
- Dynamic: `[<dtype>;?]` for runtime-determined shape
- Named/Symbolic: `[<dtype>;N,M]` for symbolic dimensions

### Node Definitions

Each instruction maps to a single line:

```
N<id> <kind> <operands...> <attrs...> T<type-id>
```

#### Constants

```
N1 const.i64 42 T1
N2 const.f32 3.14 T2
N3 const.tensor [1.0,2.0,3.0,4.0] T4
```

#### Binary Operations

```
N4 add N1 N2 T2
N5 sub N3 N4 T2
N6 mul N4 N5 T2
N7 div N5 N6 T2
```

Format: `N<id> <op> <lhs> <rhs> T<type-id>`

#### Unary Operations

```
N8 relu N7 T2
N9 neg N8 T2
N10 exp N9 T2
N11 log N10 T2
```

Format: `N<id> <op> <src> T<type-id>`

#### Reductions

```
N12 sum N7 [1,2] kd=1 T5
N13 mean N7 [] kd=0 T2
```

Format: `N<id> <op> <src> [<axes>] kd=<keepdims:0|1> T<type-id>`

#### Shape Operations

```
N14 reshape N7 [2,6] T6
N15 transpose N7 [1,0] T6
N16 expand N7 [0,2] T7
N17 squeeze N7 [1] T8
```

Format varies by operation:
- `reshape`: `N<id> reshape <src> [<new-shape>] T<type-id>`
- `transpose`: `N<id> transpose <src> [<perm>] T<type-id>`
- `expand`: `N<id> expand <src> [<axes>] T<type-id>`
- `squeeze`: `N<id> squeeze <src> [<axes>] T<type-id>`

#### Linear Algebra

```
N18 dot N4 N5 T2
N19 matmul N6 N7 T5
N20 conv2d N8 N9 s=[1,1] p=same T6
```

Format:
- `dot`: `N<id> dot <a> <b> T<type-id>`
- `matmul`: `N<id> matmul <a> <b> T<type-id>`
- `conv2d`: `N<id> conv2d <input> <filter> s=[<stride_h>,<stride_w>] p=<padding> T<type-id>`

#### Indexing

```
N21 index N7 [0,1,2] T2
N22 slice N7 0:2:1,1:4:1 T6
N23 gather N7 N8 ax=0 T6
```

Format:
- `index`: `N<id> index <src> [<indices>] T<type-id>`
- `slice`: `N<id> slice <src> <start>:<end>:<step>,... T<type-id>`
- `gather`: `N<id> gather <src> <indices> ax=<axis> T<type-id>`

### Output Markers

Module outputs are marked with:

```
O N19
O N20
```

### Comments

Lines starting with `#` are comments:

```
# This is a comment
N1 const.i64 42 T1  # Inline comments not supported
```

## Complete Example

```
mic@1
# Simple MLP forward pass
S0 "input"
S1 "weight1"
S2 "bias1"
S3 "output"
T0 f32
T1 [f32;784]
T2 [f32;784,256]
T3 [f32;256]
T4 [f32;256]
N1 input S0 T1
N2 input S1 T2
N3 input S2 T3
N4 matmul N1 N2 T4
N5 add N4 N3 T4
N6 relu N5 T4
O N6
```

## Canonicalization Rules

To ensure deterministic output:

1. **ID Assignment**: Node IDs are assigned in definition order, starting from 1.
2. **Symbol Order**: Symbols are ordered by first use.
3. **Type Order**: Types are ordered by first use.
4. **Operand Order**: Commutative operations (add, mul) order operands by ascending ID.
5. **Attribute Order**: Attributes within a node are alphabetically ordered.
6. **No Trailing Whitespace**: Lines have no trailing spaces or tabs.
7. **Unix Line Endings**: Use `\n` not `\r\n`.

## Parsing Algorithm

```
1. Read version header, verify "mic@1"
2. For each line:
   a. Skip empty lines and comments
   b. Parse first token to determine entry type (S, T, N, O)
   c. Parse remaining tokens according to entry type
   d. Validate references exist
3. Build IR module from parsed entries
4. Return module or error with line number
```

## Token Efficiency Analysis

Comparison for a 6-node neural network layer (param, matmul, add, relu):

| Format | Size (bytes) | Tokens | vs JSON | Parse Speed |
|--------|--------------|--------|---------|-------------|
| JSON | 1,115 | 278 | baseline | 5.31 us |
| TOML | 606 | 151 | 1.8x | 137.06 us |
| TOON | 269 | 67 | 4.1x | 2.67 us |
| **MIC** | **209** | **52** | **5.3x** | **2.26 us** |

### Cost Impact (GPT-4 Pricing at $0.03/1K tokens)

| Format | Cost/1K IRs | Annual Cost (1M IRs) | Savings vs JSON |
|--------|-------------|----------------------|-----------------|
| JSON | $8.34 | $8,340 | - |
| TOML | $4.53 | $4,530 | $3,810 (46%) |
| TOON | $2.01 | $2,010 | $6,330 (76%) |
| **MIC** | **$1.56** | **$1,560** | **$6,780 (81%)** |

**MIC achieves 5.3x token reduction and 2.4x faster parsing compared to JSON.**

## Error Handling

Parsers MUST report errors with line numbers:

```
mic:12: error: undefined reference N99
mic:15: error: type mismatch in matmul: [f32;3,4] @ [f32;5,6]
mic:1: error: unsupported version mic@2
```

## Backwards Compatibility

- Version 1 parsers MUST reject unknown versions.
- New node kinds MAY be added in minor versions.
- Existing node formats MUST NOT change within a major version.
- Deprecated features SHOULD emit warnings for one major version before removal.

## Implementation Requirements

Conforming implementations MUST:

1. Parse and emit MIC v1 format
2. Preserve semantic equivalence on roundtrip
3. Report errors with line numbers
4. Validate all references before building IR
5. Emit canonical output (deterministic for equal inputs)

## Security Considerations

- Parsers MUST limit recursion depth to prevent stack overflow.
- Parsers MUST limit input size to prevent memory exhaustion.
- String parsing MUST handle escape sequences safely.
- Numeric parsing MUST handle overflow gracefully.

## Related Work

- MLIR's textual format: More verbose, designed for humans
- ONNX: Binary format, not AI-friendly
- TorchScript: Python-like, high token overhead
- JAX's jaxpr: Functional, not line-oriented

## References

- [Core IR Specification](../../spec/v1.0/ir.md)
- [Type System](../../spec/v1.0/types.md)
- [Shape Semantics](../../spec/v1.0/shapes.md)

## Appendix A: Grammar (EBNF)

```ebnf
module      = version { entry } ;
version     = "mic@" digit+ newline ;
entry       = symbol | type | node | output | comment | empty ;
symbol      = "S" id space quoted newline ;
type        = "T" id space typespec newline ;
node        = "N" id space kind space args newline ;
output      = "O" space noderef newline ;
comment     = "#" { any } newline ;
empty       = newline ;

id          = digit+ ;
kind        = ident ;
args        = { arg } ;
arg         = noderef | symref | typeref | literal | attr ;
noderef     = "N" id ;
symref      = "S" id ;
typeref     = "T" id ;
literal     = number | string | array ;
attr        = ident "=" value ;

typespec    = scalar | tensor ;
scalar      = "i32" | "i64" | "f32" | "f64" | "bool" ;
tensor      = "[" scalar ";" shape "]" ;
shape       = dim { "," dim } | "?" ;
dim         = digit+ | ident ;

quoted      = '"' { char } '"' ;
number      = [ "-" ] digit+ [ "." digit+ ] [ exp ] ;
exp         = ( "e" | "E" ) [ "+" | "-" ] digit+ ;
array       = "[" [ number { "," number } ] "]" ;
```

## Appendix B: Reference Implementation

See `mind/src/ir/compact/` for the reference Rust implementation:
- `emit.rs`: MIC serialization
- `parse.rs`: MIC deserialization
- `canon.rs`: Canonicalization pass
