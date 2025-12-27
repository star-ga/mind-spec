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

# Conformance Test Corpus

This directory contains sample conformance tests as specified in
[`conformance.md`](../spec/v1.0/conformance.md). The full golden test corpus
is distributed with the reference implementation at
[`cputer/mind`](https://github.com/cputer/mind).

## Directory Structure

```
tests/
├── README.md                    # This file
├── conformance/                 # Sample conformance tests (YAML format)
│   ├── lexical/                 # E1xxx error tests
│   ├── type_checker/            # E2xxx error tests
│   ├── shapes/                  # E3xxx shape inference tests
│   ├── ir_verification/         # E4xxx IR verification tests
│   ├── autodiff/                # E5xxx autodiff tests
│   └── runtime/                 # E6xxx runtime tests
└── golden/                      # Golden output files
```

## Test Format

Tests follow the YAML format specified in [`conformance.md`](../spec/v1.0/conformance.md):

```yaml
description: "Human-readable test description"
category: "lexical" | "type_checker" | "shapes" | "ir_verification" | "autodiff" | "runtime"
profile: "cpu" | "gpu"

input:
  source: |
    # MIND source or IR

expected:
  status: "success" | "error"
  output: ...     # For success
  error: ...      # For errors
```

## Sample Tests

This repository includes representative sample tests for each error category.
These samples demonstrate the test format and expected behaviors but are not
exhaustive.

For full conformance testing, use the complete corpus from the reference
implementation.

## Running Tests

```bash
# Using the reference test runner
mind-test tests/conformance/

# Check specific category
mind-test tests/conformance/shapes/

# Verbose output
mind-test --verbose tests/conformance/
```

## Adding New Tests

When contributing new tests:

1. Follow the YAML format from conformance.md
2. Place in the appropriate category directory
3. Include clear description and expected output
4. Reference relevant specification sections in comments
5. Test on the reference implementation before submitting

## Relationship to Specification

Each test corresponds to specific normative requirements:

| Category | Spec Reference | Error Codes |
|----------|----------------|-------------|
| lexical | `spec/v1.0/lexical.md`, `grammar-lexical.ebnf` | E1001-E1006 |
| type_checker | `spec/v1.0/language.md`, `types.md` | E2001-E2007 |
| shapes | `spec/v1.0/shapes.md` | E3001-E3008 |
| ir_verification | `spec/v1.0/ir.md` | E4001-E4006 |
| autodiff | `spec/v1.0/autodiff.md` | E5001-E5004 |
| runtime | `spec/v1.0/runtime.md` | E6001-E6008 |
