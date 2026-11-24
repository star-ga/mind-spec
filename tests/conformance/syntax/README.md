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

# Syntax Conformance Rows

Sample rows for the surface forms of [Core v1 forms](../../../spec/v1.0/core-v1-forms.md). They use the format
of [`conformance.md`](../../../spec/v1.0/conformance.md#test-format) with the category `syntax`: a row about the
grammar, not about a lexical, type or shape rule.

A row exists only where a normative sentence decides the result.

- An **accept** row has a source that [`grammar-syntax.ebnf`](../../../spec/v1.0/grammar-syntax.ebnf) derives.
  Every implementation of Core v1 MUST accept it. A row that gives a returned value gives the value that the
  program has by the rules of the specification.
- A **reject** row has a source that a normative sentence forbids. Every implementation of Core v1 MUST refuse it.
  A row gives an error code only where the [error catalog](../../../spec/v1.0/errors.md) has the code for the
  fault; the escape rows use `E1004`. The other reject rows give the status only.

No row covers a form that is marked NOT IN CORE v1, an extension or an open form: an implementation MAY accept or
refuse those.

## Rows

| Row | Result | Normative sentence |
|-----|--------|--------------------|
| [`escape_single_quote_accept`](./escape_single_quote_accept.yaml) | accept | `EscapeSequence` in [`grammar-lexical.ebnf`](../../../spec/v1.0/grammar-lexical.ebnf) |
| [`escape_reject_unlisted_letter`](./escape_reject_unlisted_letter.yaml) | reject, `E1004` | [String escapes](../../../spec/v1.0/language.md#string-escapes): any other escape MUST be diagnosed |
| [`escape_reject_hex`](./escape_reject_hex.yaml) | reject, `E1004` | as above |
| [`loop_exit_accept_while`](./loop_exit_accept_while.yaml) | accept, returns 8 | `LoopExitStatement` and [Loop exits](../../../spec/v1.0/language.md#loop-exits) |
| [`loop_exit_accept_for_array`](./loop_exit_accept_for_array.yaml) | accept | as above |
| [`loop_exit_accept_statement_after_break`](./loop_exit_accept_statement_after_break.yaml) | accept, returns 1 | as above: a statement that follows `break` is the next statement |
| [`loop_exit_accept_name_break_assigned`](./loop_exit_accept_name_break_assigned.yaml) | accept, returns 5 | as above: `break = 5;` has no derivation with the loop exit, so `break` is a name |
| [`loop_exit_reject_label`](./loop_exit_reject_label.yaml) | reject | as above: a label is an invalid token and MUST be diagnosed |
| [`loop_exit_reject_continue_label`](./loop_exit_reject_continue_label.yaml) | reject | as above |
| [`loop_exit_reject_label_in_for`](./loop_exit_reject_label_in_for.yaml) | reject | as above |
