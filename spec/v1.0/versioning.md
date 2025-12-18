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

# Versioning and Stability Policy (Normative)

This chapter defines the versioning scheme, stability guarantees, and evolution policy for the MIND
language specification and its implementations.

## Semantic versioning

The MIND specification uses **Semantic Versioning 2.0.0** with the format `MAJOR.MINOR.PATCH`:

- **MAJOR version**: Incompatible changes to language syntax, semantics, or IR format
- **MINOR version**: Backwards-compatible additions (new operations, error codes, stdlib functions)
- **PATCH version**: Clarifications, typo fixes, non-normative improvements (no semantic changes)

### Version scope

Version numbers apply to:

1. **The specification**: This document and all normative chapters
2. **Error codes**: E1xxx-E6xxx catalog from errors.md
3. **Standard library**: Functions and modules from stdlib.md
4. **IR format**: Core IR instruction set and semantics
5. **Test corpus**: Golden test corpus for conformance

Implementations (compilers, runtimes) have their own version numbers but MUST clearly state which
specification version they implement.

## Stability levels

Different parts of the specification have different stability guarantees:

### Stable

**Definition**: Changes require major version bump (breaking change)

**Includes**:
- Core IR instruction set (instruction names, operand count, semantics)
- Error code numbers (E1001, E2003, etc.)
- Standard library function signatures (names, parameter types, return types)
- Type system rules (dtype lattice, shape inference algorithm)
- Autodiff rules for existing operations
- Broadcasting algorithm

**Guarantees**:
- Code written for Core v1.0 MUST compile and execute correctly on v1.x implementations
- IR modules from v1.0 MUST verify and execute on v1.x runtimes
- Error codes MUST NOT be renumbered or removed

### Evolving

**Definition**: Changes permitted in minor versions with compatibility measures

**Includes**:
- New IR instructions (added to instruction set)
- New error codes (adding E1009, E2008, etc.)
- New standard library functions
- New traits or type system extensions
- MLIR lowering patterns

**Guarantees**:
- Existing functionality remains unchanged
- New features MAY be unsupported (implementations return "unsupported operation" error)
- Deprecation warnings for features planned for removal
- At least one minor version deprecation cycle before removal

### Unstable

**Definition**: May change at any time, even in patch versions

**Includes**:
- Error message text (only error codes are stable)
- Diagnostic formatting
- Performance characteristics
- Compiler warnings (not errors)
- Non-normative examples in specification
- Internal compiler/runtime implementation details

**Guarantees**: None. Implementations SHOULD document changes in release notes.

## Breaking changes

A change is **breaking** if it:

1. **Rejects previously valid code**: Syntax or semantics that compiled in v1.x no longer compile
2. **Changes semantics**: Same code produces different results (beyond numeric tolerance)
3. **Removes functionality**: Instruction, stdlib function, or feature no longer available
4. **Renumbers error codes**: E-codes change their numeric identifiers
5. **Changes IR format**: Module structure incompatible with previous version

Breaking changes REQUIRE a major version bump (v1.x → v2.0).

### Examples of breaking changes

- Removing an IR instruction (e.g., removing `Div` from Core IR)
- Changing broadcasting rules (different shape inference results)
- Renaming stdlib function (`matmul` → `mm`)
- Changing function signature (`sum(x, axes)` → `sum(x, dim)`)
- Modifying autodiff gradient formula (different gradients for same operation)

## Non-breaking changes

A change is **non-breaking** if it:

1. **Adds functionality**: New instruction, operation, stdlib function, or error code
2. **Clarifies specification**: Fixes ambiguity without changing semantics
3. **Improves diagnostics**: Better error messages, more context (error codes unchanged)
4. **Extends compatibility**: Relaxes restrictions (accepts more valid programs)
5. **Fixes bugs**: Corrects unintended behavior to match specification intent

Non-breaking changes MAY be included in minor versions (v1.0 → v1.1).

### Examples of non-breaking changes

- Adding new IR instruction (`Div`, `Mod`, `Pow`)
- Adding new stdlib function (`tensor.clip`, `math.clamp`)
- Adding new error code (E3011 for new shape error case)
- Clarifying that "rank-0 scalars" means "shape []" (was ambiguous)
- Adding optional parameter with default value (`sum(x, axes, keepdims=false)`)

## Deprecation policy

Features marked for removal MUST follow a deprecation cycle:

### Phase 1: Deprecation warning (minor version N)

- Feature is marked **deprecated** in specification
- Implementations SHOULD emit deprecation warnings when feature is used
- Feature continues to work exactly as before
- Documentation updated with migration guide

### Phase 2: Removal (major version N+1)

- Feature is removed from specification
- Implementations MUST reject programs using deprecated feature
- Error message SHOULD reference migration guide

### Minimum deprecation period

- **Standard library functions**: At least 2 minor versions (v1.0 → v1.2 → v2.0)
- **IR instructions**: At least 2 minor versions
- **Language syntax**: At least 1 minor version
- **Error codes**: Cannot be deprecated (renumbering is breaking change)

### Example deprecation timeline

```
v1.0 (Jan 2025):  Function `old_api()` stable
v1.1 (Apr 2025):  `old_api()` marked deprecated, `new_api()` added
v1.2 (Jul 2025):  `old_api()` still works with warning
v2.0 (Oct 2025):  `old_api()` removed, only `new_api()` available
```

## Compatibility

### Forward compatibility

**Definition**: Newer implementations can run older code

**Guarantee**: Core v1.x implementation MUST accept any valid Core v1.0 program

- Implementations MUST support all v1.0 IR instructions
- Implementations MUST provide all v1.0 stdlib functions
- Implementations MUST accept v1.0 IR modules

### Backward compatibility

**Definition**: Older implementations can run newer code

**NOT guaranteed**: Core v1.0 implementation MAY reject v1.2 programs

- v1.2 programs MAY use features not in v1.0 (new instructions, functions)
- v1.0 implementations MUST reject with clear "unsupported operation" error
- Code using only v1.0 features MUST work on v1.0 implementations

### Recommendations for portable code

To maximize compatibility across v1.x implementations:

- Use only features from the minimum required specification version
- Declare required version in module metadata
- Avoid relying on error message text (use error codes)
- Test on multiple implementation versions

## Version declaration

### In source code

Programs MAY declare their required specification version:

```mind
#[requires(mind_spec = "1.2")]
module my_program;
```

Implementations MUST reject programs requiring newer specification versions than supported.

### In IR modules

IR modules SHOULD include version metadata:

```
# MIND IR v1.2
# Generated by: mind-compiler v0.4.2
# Specification: Core v1.2.0

inputs: ...
outputs: ...
```

### Implementation version reporting

Implementations MUST provide version information:

- **Specification version**: Which Core vX.Y the implementation conforms to
- **Implementation version**: Compiler/runtime own version number
- **Supported features**: List of optional features (GPU profile, etc.)

Example:

```
$ mind --version
mind-compiler 0.4.2
Core v1.2.0 (CPU baseline + GPU profile)
Features: autodiff, mlir-lowering, gpu-cuda
```

## Evolution examples

### Adding new operation (minor version)

**v1.0**: IR has Add, Sub, Mul
**v1.1**: IR adds Div instruction

- v1.1 specification documents Div with semantics, shape rules, autodiff gradient
- v1.0 implementations reject Div with E6003 "unsupported operation"
- v1.1 implementations support Div
- Programs using only Add/Sub/Mul work on both v1.0 and v1.1

### Changing semantics (major version)

**v1.x**: Broadcasting aligns from right, prepends 1s to shorter shape
**v2.0**: Broadcasting changes to different algorithm

- Breaking change: same shapes produce different results
- Requires major version bump
- v1.x code may behave differently on v2.0 (semantic change)
- Migration guide explains differences and update process

### Clarifying ambiguity (patch version)

**v1.0.0**: "Scalars have empty shape" (ambiguous: `[]` or`[1]`?)
**v1.0.1**: "Scalars have shape `[]` (rank-0)" (clarification)

- No semantic change: behavior was already `[]` in reference implementation
- Patch version: fixes ambiguity in documentation
- Code behavior unchanged

## Specification versioning

### Version history

- **Core v1.0.0** (2025-01): Initial release
  - Complete IR instruction set
  - Broadcasting, reductions, matmul, conv2d
  - Autodiff for all operations
  - Error catalog E1xxx-E6xxx
  - Standard library (core, math, tensor, diff, io)

- **Core v1.1.0** (planned): Minor additions
  - New IR instructions (Div, Mod)
  - Additional stdlib functions
  - Extended error codes
  - Performance improvements (non-breaking)

- **Core v2.0.0** (future): Major revision
  - Control flow in IR (loops, branches)
  - Dynamic shapes
  - Additional dtypes (f16, bf16, complex)
  - Breaking changes to IR format

### Changelog requirements

Each specification release MUST include:

1. **Version number**: Full MAJOR.MINOR.PATCH
2. **Release date**: ISO 8601 format (YYYY-MM-DD)
3. **Breaking changes**: List with migration guide
4. **New features**: Added operations, functions, error codes
5. **Deprecations**: Features marked for future removal
6. **Bug fixes**: Specification clarifications, typo corrections

### Reference implementation versioning

The reference implementation (`cputer/mind`) has its own version numbers:

- **Implementation version**: mind-compiler v0.4.2
- **Implements specification**: Core v1.2.0
- **Relationship**: Implementation versions can increment independently

One implementation version MAY support multiple specification versions (v1.0, v1.1, v1.2).

## Stability guarantees summary

| Component | Stable at | Changes allowed | Version bump |
|-----------|-----------|-----------------|--------------|
| IR instruction names | MAJOR | Add new, deprecate old | Minor (add), Major (remove) |
| IR instruction semantics | MAJOR | Clarify only | Patch (clarify), Major (change) |
| Error code numbers | MAJOR | Add new, never renumber | Minor (add), Never remove |
| Stdlib function signatures | MAJOR | Add new, deprecate old | Minor (add), Major (remove) |
| Broadcasting algorithm | MAJOR | Clarify only | Patch (clarify), Major (change) |
| Type system rules | MAJOR | Extend, clarify | Minor (extend), Major (change) |
| Error message text | UNSTABLE | Change anytime | Any |
| Diagnostic format | UNSTABLE | Change anytime | Any |
| Test corpus | EVOLVING | Add tests, change minor | Minor (add), Major (change) |

## Implementation compatibility matrix

| Implementation | Core v1.0 | Core v1.1 | Core v1.2 | Core v2.0 |
|----------------|-----------|-----------|-----------|-----------|
| mind v0.3.x    | ✅ Full   | ❌ No     | ❌ No     | ❌ No     |
| mind v0.4.x    | ✅ Full   | ✅ Full   | ✅ Full   | ❌ No     |
| mind v0.5.x    | ✅ Full   | ✅ Full   | ✅ Full   | ⚠️  Beta  |
| mind v1.0.x    | ✅ Full   | ✅ Full   | ✅ Full   | ✅ Full   |

**Legend:**
- ✅ Full: Complete conformance, all tests pass
- ⚠️  Beta: Experimental support, may have issues
- ❌ No: Not supported, programs will be rejected

## Questions and answers

**Q: Can I use v1.2 features and still claim v1.0 compatibility?**
A: No. If you use v1.2 features, declare `#[requires(mind_spec = "1.2")]`. Programs using only v1.0 features can claim v1.0 compatibility.

**Q: What if two minor versions conflict (v1.1 deprecates X, v1.2 adds new X)?**
A: The v1.2 "X" is a different entity with different semantics. Use namespacing or different names to avoid confusion.

**Q: Can implementations support only a subset of the specification?**
A: Implementations may omit optional features (GPU profile, MLIR lowering) but MUST support all required features for the profile they claim (CPU baseline). Partial support MUST NOT claim conformance.

**Q: How long will v1.x be supported?**
A: Core v1.x receives updates until Core v2.0 is released. After v2.0 release, v1.x enters maintenance mode (critical bugs only) for at least 12 months.

**Q: Can error messages change in patch versions?**
A: Yes. Error message text is UNSTABLE. Only error codes (E1xxx-E6xxx) are stable.
