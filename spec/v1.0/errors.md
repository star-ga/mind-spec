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

# Error Catalog (Normative)

This chapter enumerates the error categories, error codes, and diagnostic requirements for Core v1
implementations. All errors MUST be deterministic and MUST include sufficient context for debugging.

## Error categories

Core v1 defines six primary error categories:

1. **Lexical errors (E1xxx)**: malformed source text, invalid tokens
2. **Type errors (E2xxx)**: type mismatches, unresolved types, trait violations
3. **Shape errors (E3xxx)**: broadcasting failures, dimension mismatches, invalid shapes
4. **Verification errors (E4xxx)**: IR verification failures, SSA violations
5. **Autodiff errors (E5xxx)**: differentiation failures, unsupported operations
6. **Runtime and artifact-production errors (E6xxx)**: execution failures, backend unavailability, resource errors, compiler materialization refusal

Each error code follows the pattern `E[category][number]` where category is 1-6 and number is a
three-digit identifier.

## E1xxx: Lexical errors

Lexical errors occur during tokenization before syntactic or semantic analysis.

### E1001: Invalid UTF-8 sequence
- **Trigger**: Source file contains ill-formed UTF-8 byte sequences
- **Required context**: byte offset, invalid sequence (first 4 bytes in hex)
- **Example**: `E1001: Invalid UTF-8 sequence at offset 42: [0xFF, 0xFE, 0x00, 0x01]`

### E1002: Invalid character in identifier
- **Trigger**: Identifier contains characters outside `[\p{XID_Start}_][\p{XID_Continue}_]*`
- **Required context**: source location, offending character
- **Example**: `E1002: Invalid character '$' in identifier at line 5, column 12`

### E1003: Unterminated string literal
- **Trigger**: String literal missing closing quote before EOF or newline
- **Required context**: start location of string literal
- **Example**: `E1003: Unterminated string literal starting at line 10, column 8`

### E1004: Invalid escape sequence
- **Trigger**: Unrecognized escape sequence in string literal (e.g., `\q`)
- **Required context**: source location, invalid escape
- **Example**: `E1004: Invalid escape sequence '\q' at line 10, column 15`

### E1005: Invalid numeric literal
- **Trigger**: Malformed integer or floating-point literal (e.g., `0b2`, `1.2.3`)
- **Required context**: source location, literal text
- **Example**: `E1005: Invalid binary literal '0b2' at line 3, column 10`

### E1006: Unterminated block comment
- **Trigger**: Block comment `/* ... */` not closed before EOF
- **Required context**: start location of block comment
- **Example**: `E1006: Unterminated block comment starting at line 20, column 1`

## E2xxx: Type errors

Type errors occur during type checking and type inference.

### E2001: Type mismatch
- **Trigger**: Expression has type that doesn't match expected type
- **Required context**: expression location, expected type, actual type
- **Example**: `E2001: Type mismatch at line 15, column 10: expected 'f32', found 'i32'`

### E2002: Unresolved name or qualified owner
- **Trigger**: reference to an undeclared variable, or to a qualified type or
  enum variant whose owner is unknown, unimported, ambiguous, or does not
  export that declaration. This covers a bare-headed `Enum::Variant` (or
  `Enum.Variant`) value or pattern whose head names an enum declared by another
  project module, when the current module declares no type of that name and
  (a) no import exports a type of that name, including when the module that
  declares the enum is imported but does not export it, (b) several imports
  export one, or (c) the single import exports an enum of that name that does
  not declare the variant. Recognising a qualified path during parsing does not
  establish semantic module ownership.
- **Implementation status**: bare-headed variant resolution is pending compiler
  integration (compiler commit `1def5dde`). It applies in compiler builds with
  the `cross-module-imports` feature, which is not a default feature, wherever
  several source modules are checked or built together (see Scope). The
  control `cross_module_enum_variant_lowering` is compiled only with the
  `mlir-build` and `cross-module-imports` features on a unix host. Checking
  reports a located E2002, and the project build refuses to embed the module
  as a runtime fallback.
- **Required context**: unresolved name or qualified path and source location
- **Examples**: `E2002: Undefined variable 'x' at line 8, column 5`;
  ``E2002: unknown module-qualified type `config.Mode` ``;
  ``E2002: enum `Table` in `Table::Other` is not visible in this module; import the module that declares it``;
  ``E2002: ambiguous enum `Table` in `Table::Other`: several imported modules export it; qualify it with its module``;
  ``E2002: unknown variant `X` of imported enum `Table` ``
- **Scope**: the reference reports the three bare-variant messages above only
  when its owner registry is built from several source modules: by a project
  build, by a single-file entry that imports modules of its enclosing manifest
  project, or by `mindc check` run on several files or on a directory that
  holds several, which builds the registry from the checked files and does not
  read a `Mind.toml`. A single source checked or built on its own gets none of
  them. It reports them only when the head names an enum that some project
  module declares; a head that names no project enum, and the `Option` and
  `Result` heads, are not inspected by this check. It inspects a unit-variant
  value path (`Enum::Variant`) and a `match` pattern, which is reported at its
  match arm. It does not inspect a payload-constructor call
  (`Enum::Variant(...)`) or a struct-variant literal (`Enum::Variant { ... }`).
  It rewrites `Enum.Variant` to the `::` form only for an enum that is visible
  to the module, so for the dot spelling it covers an unknown variant of an
  imported enum but not an unimported or ambiguous enum. A type that the
  current module declares keeps lexical precedence over an imported type of the
  same name.

### E2003: Cannot infer type
- **Trigger**: Type inference fails due to insufficient constraints
- **Required context**: expression location, inference context
- **Example**: `E2003: Cannot infer type for variable 'result' at line 12, column 8`

### E2004: Dtype mismatch in binary operation
- **Trigger**: Binary operation operands have different dtypes (mixing i32 with f32)
- **Required context**: operation location, left dtype, right dtype
- **Example**: `E2004: Dtype mismatch in Add at line 10, column 15: i32 + f64`

### E2005: Invalid dtype for operation
- **Trigger**: Operation applied to unsupported dtype (e.g., Log on integers)
- **Required context**: operation name, actual dtype, supported dtypes
- **Example**: `E2005: Log requires floating-point dtype, found i32 at line 20, column 10`

### E2006: Trait bound not satisfied
- **Trigger**: Type does not implement required trait
- **Required context**: type, required trait, source location
- **Example**: `E2006: Type 'MyStruct' does not implement 'Differentiable' at line 25, column 5`

### E2007: Arity mismatch
- **Trigger**: Function called with wrong number of arguments
- **Required context**: function name, expected arity, actual arity, call location
- **Example**: `E2007: Function 'matmul' expects 2 arguments, found 3 at line 18, column 12`

### E2026: Numeric scalar used as a known struct

- **Implementation status**: pending compiler integration for inferred
  bindings and reassignment; see [struct literal bindings](./types.md#struct-literal-bindings).
- **Trigger**: a provably numeric scalar is used where a locally declared
  struct is required, including replacement of a known struct binding.
- **Required context**: the binding, declared struct name and offending value
  span. Construct a struct value instead. A same-struct replacement must not
  be diagnosed as scalar narrowing.
- Unknown types do not establish known struct identity. General structural
  compatibility checking remains outside this diagnostic's implemented scope.

### E2032: Unsupported slice call ABI

- **Implementation status**: pending compiler integration; see the
  [slice call boundary](./types.md#slice-call-implementation-boundary).
- **Trigger**: unsupported slice layout, a call argument without proven
  compatible dynamic-array provenance, or a slice/array result that is not
  proven on every required path. Explicit slice-typed local bindings are also
  outside the current lowering boundary.
- **Required context**: the affected declaration, argument, or result; the
  unsupported layout or missing provenance; and a source span. The compiler
  refuses before artifact emission.

### E2033: Borrowed slice capability violation

- **Implementation status**: pending compiler integration.
- **Trigger**: read-only mutation, ownership operations, capability erasure,
  escape through a non-slice parameter or return, or a slice-containing
  aggregate or struct field.
- **Required context**: the binding or operation, the capability being lost or
  operation being attempted, and its source span. A declared slice return may
  preserve a compatible slice capability. The compiler preserves borrowed
  capabilities through branch and loop joins.

The pending checker does not provide general lifetime inference or mutable-alias
exclusivity analysis; those guarantees remain future work.

### E2036: Non-integer value stored into a narrow integer element

- **Implementation status**: pending compiler integration; additive Core v1
  catalog entry targeted for specification 1.7.0. It does not declare that
  release or promote an unreleased compiler artifact. Reference compiler
  commit `0a8b34a5`, merged with
  [compiler PR #263](https://github.com/star-ga/mind/pull/263) at `1833f095`;
  see [record identity implementation coverage](./types.md#implementation-coverage).
- **Trigger**: an indexed assignment whose destination element type, after
  resolving type aliases, is `i8`, `u8`, `i16` or `u16`, and whose right-hand
  side is proven not to be an integer value. That is either a known
  non-integer scalar class (for example a float literal, a float-typed
  binding, a float-returning call, or a cast to a float type) or an opaque
  handle: a string, a declared struct value, a value of an array, tuple,
  generic, slice, reference, tensor, raw-pointer or function-pointer type, or
  an array, tuple, struct, map or set literal, or a reference expression.
  `bool` counts as an integer class.
- **Required context**: the assigned value's span and guidance to use an
  explicit numeric conversion.
- **Scope**: best effort. A right-hand side whose type the checker cannot
  establish is admitted, and integer right-hand sides, including integer
  aliases and integer values outside the element's range, are not diagnosed by
  this rule. The reference resolves module-local `type` aliases when it builds
  the element types of struct fields; a destination whose element type is
  written as an alias elsewhere, such as in a parameter annotation, is
  classified by its written spelling and is admitted. The reference runs the
  check only in builds with the `std-surface` feature, which is a default
  feature. An indexed destination whose array, fixed-array or slice type the
  checker cannot establish is not checked, and the check runs only inside
  function bodies. Struct-field arrays and parameters typed as a fixed array,
  `array<T>` or a slice are checked; a local `let` fixed-array binding
  initialised from an array literal (for example
  `let xs: [u8; 4] = [0, 0, 0, 0]`) is not recorded, so a store into it is not
  checked. The compiler controls `fixed_array_narrow_assignment_types` and
  `fixed_array_struct_field_run` cover struct-field arrays only.
- The rule refuses a proven opaque handle instead of truncating it to the cell
  width; a handle the checker cannot prove is not covered.
- **Example**: `E2036: a narrow integer array element cannot store a proven non-integer or opaque-handle value; use an explicit numeric conversion`

### E2037: Function name used as a value

- **Implementation status**: pending compiler integration; additive Core v1
  catalog entry targeted for specification 1.7.0. It does not declare that
  release or promote an unreleased compiler artifact. Reference compiler
  commit `1def5dde`; the rule does not depend on the `cross-module-imports`
  feature, and without the default `std-surface` feature
  (`--no-default-features`) the function-only standard-surface names are not
  collected, so only the module's own functions are classified. Its only
  controls, in `cross_module_enum_variant_lowering`, are compiled with the
  `mlir-build` and `cross-module-imports` features on a unix host.
- **Trigger**: a bare identifier in value position whose only meaning is a
  function of the current module or a function-only standard-surface export.
  Function values are not part of the executable subset. Member-access
  receivers such as `sha256.hash(...)` are not affected.
- **Required context**: the function name and the source location of the
  reference.
- **Limit**: the reference classifies identifiers only inside function bodies;
  a module-level `const` or `let` initializer is not checked by this rule. A
  function name that resolves only through another project module's exports is
  not classified by the reference, which does not report `E2037` for it.
- **Check/build**: the reference refuses the build rather than lowering the
  module.
- **Example**: ``E2037: `null` is a function, not a value: first-class functions are not yet supported``

### E2300: Collection mutation in expression position

- **Implementation status**: pending compiler integration.
- **Trigger**: a mutating method on a tracked collection appears in an
  expression position rather than as a supported top-level owner update. This
  includes nested expressions, call arguments, conditions, match values or
  guards, and assignment of an owner-returning mutation to a different
  binding. The same-binding form `xs = xs.push(value)` and its bare-statement
  rewrite are allowed by this rule; their arguments are still checked for
  nested violations. Separate result-type rules still apply, so assigning the
  scalar result of `set` back to an array is `E2032`.
- **Required context**: the mutating call, its collection receiver, a source
  span, and guidance to use an owner-preserving statement or same-binding
  update. The decision is type-aware, so an equally named user-defined method
  on a non-collection receiver is not refused.
- **Check/build contract**: checking and artifact-producing builds MUST refuse
  the same source with `E2300`; a refused build MUST terminate as a user error
  and leave no artifact.

### E2301: Non-final enum-variant binding collision

- **Implementation status**: pending compiler integration.
- **Trigger**: an unguarded bare-identifier match arm occurs before the final
  arm and its identifier collides with a registered enum variant. Such an arm
  is neither a qualified discriminant test nor a valid final catch-all.
- **Required context**: the colliding identifier and source span, with guidance
  to qualify the variant, rename the binding, or move a catch-all binding to
  the final arm. A wildcard arm remains valid under first-match semantics.
- **Check/build contract**: checking and artifact-producing builds MUST refuse
  the same source with `E2301`; a refused build MUST terminate as a user error
  and leave no artifact.

## E3xxx: Shape errors

Shape errors occur during shape inference, broadcasting, or shape validation.

### E3001: Broadcasting failure
- **Trigger**: Shapes incompatible for broadcasting
- **Required context**: operand shapes, failing dimension index, extents at failing dimension
- **Example**: `E3001: Broadcasting failed at dimension 1: shape [3, 4] incompatible with [3, 5]`

### E3002: Rank mismatch
- **Trigger**: Operation requires specific rank(s)
- **Required context**: operation name, expected rank(s), actual rank, source location
- **Example**: `E3002: MatMul requires rank ≥ 2, found rank 1 at line 30, column 8`

### E3003: Dimension mismatch
- **Trigger**: Specific dimensions don't match when required (e.g., MatMul K dimension)
- **Required context**: operation, dimension name, expected extent, actual extent
- **Example**: `E3003: MatMul contracting dimension mismatch: lhs[-1]=5, rhs[-2]=6 at line 22, column 10`

### E3004: Invalid axis
- **Trigger**: Axis index out of range for tensor rank
- **Required context**: operation, axis value, tensor rank, source location
- **Example**: `E3004: Sum axis 3 out of range for rank-3 tensor at line 15, column 20`

### E3005: Duplicate axis
- **Trigger**: Reduction or reshape specifies same axis multiple times
- **Required context**: operation, axis list, duplicate axis
- **Example**: `E3005: Sum has duplicate axis 1 in axes [0, 1, 1] at line 12, column 15`

### E3006: Zero or negative dimension
- **Trigger**: Shape contains dimension ≤ 0 (except for scalars with shape [])
- **Required context**: shape, invalid dimension index, value
- **Example**: `E3006: Invalid dimension 0 in shape [3, 0, 5] at line 18, column 10`

### E3007: Element count mismatch
- **Trigger**: Reshape preserves element count but new shape has different product
- **Required context**: original shape, new shape, original count, new count
- **Example**: `E3007: Reshape element count mismatch: [2, 3] (6 elements) to [2, 4] (8 elements) at line 10, column 5`

### E3008: Invalid permutation
- **Trigger**: Transpose permutation invalid (wrong length, duplicate indices, out of range)
- **Required context**: permutation, tensor rank, specific violation
- **Example**: `E3008: Transpose permutation [0, 2, 2] has duplicate axis 2 for rank-3 tensor at line 20, column 8`

### E3009: Squeeze dimension not 1
- **Trigger**: Squeeze attempted on dimension with extent ≠ 1
- **Required context**: axis, actual extent, tensor shape
- **Example**: `E3009: Squeeze axis 1 has extent 3, must be 1 in shape [2, 3, 1] at line 14, column 12`

### E3010: Invalid shape in literal
- **Trigger**: Tensor literal shape doesn't match declared shape
- **Required context**: declared shape, inferred shape from data
- **Example**: `E3010: Tensor literal shape mismatch: declared [2, 3], inferred [2, 2] at line 8, column 10`

## E4xxx: Verification errors

Verification errors occur during IR verification before execution or optimization.

### E4001: SSA violation (use before definition)
- **Trigger**: Operand ValueId references undefined or future value
- **Required context**: instruction index, operand ValueId, definition ValueId (if exists)
- **Example**: `E4001: Instruction 10 uses %15 before definition (defined at instruction 20)`

### E4002: SSA violation (multiple definitions)
- **Trigger**: Same ValueId defined more than once
- **Required context**: ValueId, first definition location, second definition location
- **Example**: `E4002: ValueId %12 defined multiple times: instruction 8 and instruction 15`

### E4003: Undefined output
- **Trigger**: Module output references ValueId that doesn't exist
- **Required context**: output index, ValueId
- **Example**: `E4003: Output 2 references undefined ValueId %42`

### E4004: Invalid input declaration
- **Trigger**: Input instruction has invalid metadata (missing name, invalid dtype/shape)
- **Required context**: input index, specific issue
- **Example**: `E4004: Input 0 missing required 'name' attribute`

### E4005: Constant verification failure
- **Trigger**: ConstTensor data doesn't match declared dtype/shape
- **Required context**: ValueId, declared dtype/shape, data issue
- **Example**: `E4005: ConstTensor %5 element count mismatch: shape [2, 3] requires 6 elements, found 5`

### E4006: Index list length mismatch
- **Trigger**: Index operation index list length doesn't match tensor rank
- **Required context**: ValueId, tensor rank, index list length
- **Example**: `E4006: Index %10 has 2 indices for rank-3 tensor`

### E4007: Slice parameters length mismatch
- **Trigger**: Slice starts/ends/steps have different lengths or don't match rank
- **Required context**: ValueId, tensor rank, starts/ends/steps lengths
- **Example**: `E4007: Slice %8 starts/ends/steps length mismatch: 3/3/2 for rank-3 tensor`

### E4008: Invalid slice step
- **Trigger**: Slice step is zero
- **Required context**: ValueId, dimension, step value
- **Example**: `E4008: Slice %10 has zero step at dimension 1`

### E4009: Conv2d channel mismatch
- **Trigger**: Conv2d input channels don't match filter channels
- **Required context**: ValueId, input channels, filter channels
- **Example**: `E4009: Conv2d %15 channel mismatch: input.shape[3]=16, filter.shape[2]=32`

### E4010: Conv2d invalid strides
- **Trigger**: Conv2d strides not length 2 or contain non-positive values
- **Required context**: ValueId, strides value
- **Example**: `E4010: Conv2d %20 invalid strides [1, 0]: must be length 2 with positive values`

### E4011: Gather invalid indices dtype
- **Trigger**: Gather indices tensor has non-integer dtype
- **Required context**: ValueId, indices dtype
- **Example**: `E4011: Gather %12 indices have dtype f32, must be i32 or i64`

## E5xxx: Autodiff errors

Autodiff errors occur during gradient computation.

### E5001: Unsupported operation
- **Trigger**: Operation lacks derivative rule
- **Required context**: operation name, ValueId
- **Example**: `E5001: Autodiff unsupported operation 'CustomOp' at %25`

### E5002: Gradient verification failure
- **Trigger**: Generated gradient module fails IR verification
- **Required context**: specific verification error from E4xxx
- **Example**: `E5002: Gradient module verification failed: E4001 at instruction 15`

### E5003: Invalid axis in gradient
- **Trigger**: Reduction gradient has axis out of range
- **Required context**: operation, axis value, shape
- **Example**: `E5003: Sum gradient invalid axis 4 for shape [2, 3, 4]`

### E5004: Unsupported shape in gradient
- **Trigger**: Broadcasting or reduction shape not supported by autodiff engine
- **Required context**: operation, shapes involved
- **Example**: `E5004: Autodiff cannot compute gradient for broadcast [1, 5] → [3, 4, 5]`

### E5005: Non-differentiable input
- **Trigger**: Attempted to differentiate with respect to non-differentiable type
- **Required context**: ValueId, type
- **Example**: `E5005: Cannot differentiate with respect to i32 tensor at %10`

## E6xxx: Runtime and artifact-production errors

E6xxx errors occur during backend execution or while producing a runnable artifact.

### E6001: Out-of-bounds index
- **Trigger**: Index or Gather operation accesses invalid position
- **Required context**: operation, indices, tensor shape
- **Example**: `E6001: Index out of bounds: [2, 5] for shape [3, 4]`

### E6002: Backend unavailable
- **Trigger**: Requested backend not available (e.g., GPU in CPU-only build)
- **Required context**: requested backend, available backends
- **Example**: `E6002: Backend 'Gpu' unavailable, available: [Cpu]`

### E6003: Unsupported operation on backend
- **Trigger**: Backend doesn't implement operation
- **Required context**: operation name, backend
- **Example**: `E6003: Operation 'Conv2d' not supported on backend 'Cpu'`

### E6004: Allocation failure
- **Trigger**: Failed to allocate tensor (out of memory, size too large)
- **Required context**: requested shape/dtype, backend, available memory (if applicable)
- **Example**: `E6004: Failed to allocate tensor [10000, 10000, f32] on Gpu: out of memory`

### E6005: Numeric overflow
- **Trigger**: Operation produces overflow (integer sum, exp on large value)
- **Required context**: operation, operands (summary), result
- **Example**: `E6005: Integer overflow in Sum: i32 accumulator exceeded bounds`

### E6006: Invalid numeric value
- **Trigger**: Operation produces NaN or Inf when not expected
- **Required context**: operation, operands (summary)
- **Example**: `E6006: Log produced NaN for input value -1.0`

### E6007: Execution timeout
- **Trigger**: Operation exceeded allowed execution time
- **Required context**: operation, timeout limit
- **Example**: `E6007: Operation 'MatMul' exceeded timeout of 30s`

### E6008: Device error
- **Trigger**: Device-specific error (GPU kernel failure, driver error)
- **Required context**: device, operation, device-specific error code
- **Example**: `E6008: GPU kernel failed for Conv2d: CUDA error 77 (illegal memory access)`

### E6009: Compiler materialization refusal
- **Trigger**: Compiler-side aggregate expansion exceeds a deterministic
  materialization limit, its accounting overflows, or an accepted aggregate
  operation has no valid representation in the runnable lowering ABI (including
  a nested `[Struct; N]` element-field receiver)
- **Required context**: the exceeded resource and attempted/limit values, or
  the unsupported/invalid lowering operation and source location
- **Artifact contract**: Compilation MUST terminate with a non-zero status and
  MUST NOT publish a partial runnable artifact
- **Example**: `E6009: Compiler materialization payload 2097160 bytes exceeds limit 2097152`

### E6010: Invalid manifest export
- **Trigger**: A `Mind.toml [exports] c_abi` entry is empty, exceeds the
  manifest export bound, or is not a C-style identifier
- **Required context**: the invalid entry and the validation reason
- **Artifact contract**: Compilation MUST terminate with a non-zero status;
  this user configuration error MUST NOT be classified as backend capability
- **Example**: ``E6010: invalid Mind.toml [exports] c_abi entry `bad name`: export name must be ASCII alphanumeric or underscore``

## Diagnostic requirements

All error messages MUST include:

1. **Error code**: The E-code from this catalog
2. **Message**: Human-readable description
3. **Source location**: File, line, column (when applicable)
4. **Context**: Specific values mentioned in "Required context" above

Implementations SHOULD provide:

- **Suggestion**: How to fix the error (when applicable)
- **Note**: Additional explanatory information
- **Related locations**: Secondary locations involved in the error

### Error message format

Recommended format for CLI output:

```text
error[E3001]: Broadcasting failed at dimension 1
  --> src/model.mind:42:15
   |
42 |     let z = x + y;
   |               ^ shape [3, 4] incompatible with [3, 5]
   |
   = note: operand shapes: x=[3, 4], y=[3, 5]
   = help: ensure dimension 1 has extent 4 or 1 in both operands
```

### Programmatic error representation

Implementations SHOULD provide structured error data suitable for tooling:

```rust
struct CompilerError {
    code: ErrorCode,        // E.g., E3001
    message: String,
    span: SourceSpan,       // File, line, column range
    severity: Severity,     // Error, Warning, Note
    context: HashMap<String, Value>,
    related: Vec<RelatedInfo>,
}
```

## Error recovery

Implementations MAY attempt error recovery to report multiple errors, but MUST NOT:

- Execute IR after verification failure
- Continue execution after runtime error
- Silently ignore errors

Recovery is ONLY permitted for lexical and type errors during compilation to improve diagnostics.

## Stability guarantees

Error codes in this catalog are **stable across Core v1 versions**:

- Adding new error codes is permitted
- Changing error messages is permitted (messages are not part of stability guarantee)
- Renumbering or removing error codes is NOT permitted without major version change
- Context requirements MAY be expanded but MUST NOT be reduced

## Reference implementation (`star-ga/mind`)

The reference compiler implements the following error codes:

| Code  | Phase       | Description                              |
|-------|-------------|------------------------------------------|
| E1001 | Parse       | Unexpected token / parsing error         |
| E2001 | Type-check  | General type error                       |
| E2036 | Type-check  | Non-integer value stored into a narrow integer element (pending, `0a8b34a5`) |
| E2037 | Type-check  | Function name used as a value (pending, `1def5dde`) |
| E2101 | Type-check  | Broadcast compatibility failure          |
| E2102 | Type-check  | Rank/shape mismatch, invalid reductions  |
| E2103 | Type-check  | MatMul inner-dimension mismatch          |
| E3001 | IR Verify   | IR verification error                    |
| E4001 | Autodiff    | Autodiff operation failure               |
| E4002 | Autodiff    | Autodiff requires --func argument        |
| E4003 | Autodiff    | Autodiff feature not enabled             |
| E5001 | Autodiff    | Unsupported operation for autodiff       |
| E6002 | Backend     | Requested backend unavailable             |
| E6009 | Materialize | Compiler materialization refusal          |
| E6010 | Manifest    | Invalid Mind.toml export                  |

**Note**: The reference implementation uses E2xxx for both type AND shape errors (combining
the spec's E2xxx and E3xxx categories). Most error codes in the spec are reserved for future
expansion.
