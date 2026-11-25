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
of [`conformance.md`](../../../spec/v1.0/conformance.md#test-format) with the category `syntax`: a row about a
form of that page, with the rule of the grammar or the normative chapter that decides its verdict.

A row exists only where a normative sentence decides the result.

- An **accept** row has a source that [`grammar-syntax.ebnf`](../../../spec/v1.0/grammar-syntax.ebnf) derives.
  Every implementation of Core v1 MUST accept it. A row that gives a returned value gives the value that the
  program has by the rules of the specification.
- A **reject** row has a source that a normative sentence forbids. Every implementation of Core v1 MUST refuse it.
  A row gives an error code where the [error catalog](../../../spec/v1.0/errors.md) has the code for the
  fault, also when the grammar does not derive the source (`loop { }` gives `E2405`). A reject row whose fault
  has no code in the catalog gives the status only. A reject row holds one fault.

No row's verdict depends on a form that is marked NOT IN CORE v1, an extension or an open form: an
implementation MAY accept or refuse those.

## Rows

| Row | Result | Normative sentence |
|-----|--------|--------------------|
| [`escape_single_quote_accept`](./escape_single_quote_accept.yaml) | accept | `EscapeSequence` in [`grammar-lexical.ebnf`](../../../spec/v1.0/grammar-lexical.ebnf) |
| [`escape_reject_unlisted_letter`](./escape_reject_unlisted_letter.yaml) | reject, `E1004` | [String escapes](../../../spec/v1.0/language.md#string-escapes): any other escape MUST be diagnosed |
| [`escape_reject_hex`](./escape_reject_hex.yaml) | reject, `E1004` | as above |
| [`loop_exit_accept_while`](./loop_exit_accept_while.yaml) | accept, returns 8 | `LoopExitStatement` and [Loop exits](../../../spec/v1.0/language.md#loop-exits) |
| [`loop_exit_accept_for_array`](./loop_exit_accept_for_array.yaml) | accept | as above |
| [`loop_exit_accept_statement_after_break`](./loop_exit_accept_statement_after_break.yaml) | accept, returns 1 | as above: the statement after `break;` is the next statement |
| [`loop_exit_accept_name_break_assigned`](./loop_exit_accept_name_break_assigned.yaml) | accept, returns 5 | as above: `break = 5;` has no derivation with the loop exit, so `break` is a name |
| [`loop_exit_reject_label`](./loop_exit_reject_label.yaml) | reject | as above: a label is an invalid token and MUST be diagnosed |
| [`loop_exit_reject_continue_label`](./loop_exit_reject_continue_label.yaml) | reject | as above |
| [`loop_exit_reject_label_in_for`](./loop_exit_reject_label_in_for.yaml) | reject | as above |
| [`loop_exit_reject_break_outside_loop`](./loop_exit_reject_break_outside_loop.yaml) | reject, `E2401` | [Loop exits](../../../spec/v1.0/language.md#loop-exits): a loop exit outside a loop MUST be refused |
| [`loop_exit_reject_continue_after_loop`](./loop_exit_reject_continue_after_loop.yaml) | reject, `E2401` | as above |
| [`loop_exit_reject_without_semicolon`](./loop_exit_reject_without_semicolon.yaml) | reject, `E2002` | as above: the loop exit needs its `;`, so in `break - 1;` the word is a name, and no name `break` is declared |
| [`loop_reject_loop_block`](./loop_reject_loop_block.yaml) | reject, `E2405` | as above: Core v1 has no `loop` statement |
| [`loop_accept_name_loop`](./loop_accept_name_loop.yaml) | accept, returns 1 | as above: `loop` is not a keyword |
| [`loop_value_accept_unit`](./loop_value_accept_unit.yaml) | accept, returns 7 | `WhileExpression`, `ForExpression` and [Loops](../../../spec/v1.0/language.md#loops): a loop has the type `unit` |
| [`loop_value_reject_other_type`](./loop_value_reject_other_type.yaml) | reject, `E2001` | as above: the value of a loop is not an `i64` |
| [`block_like_accept_without_semicolon`](./block_like_accept_without_semicolon.yaml) | accept, returns 8 | `BlockLikeStatement` and [Block-like statements](../../../spec/v1.0/language.md#block-like-statements) |
| [`block_like_accept_tail_value`](./block_like_accept_tail_value.yaml) | accept, returns 4 | as above: a form that only the closing brace follows is the tail |
| [`block_like_accept_operand_in_parentheses`](./block_like_accept_operand_in_parentheses.yaml) | accept, returns 3 | as above: parentheses make a form an operand; a `;` after a form discards its value |
| [`block_like_reject_value_statement`](./block_like_reject_value_statement.yaml) | reject, `E2001` | as above: a block-like statement that is not the tail MUST have the type `unit` |
| [`block_like_reject_operand_without_parentheses`](./block_like_reject_operand_without_parentheses.yaml) | reject, `E2001` | as above: the `if` ends at its closing brace, so it is a statement of the type `i64` |
| [`let_mut_accept_assignment`](./let_mut_accept_assignment.yaml) | accept, returns 3 | `LetStatement` and [Bindings and assignment](../../../spec/v1.0/language.md#bindings-and-assignment) |
| [`let_mut_accept_new_binding`](./let_mut_accept_new_binding.yaml) | accept, returns 2 | as above: a later `let` is a new binding |
| [`let_mut_accept_place`](./let_mut_accept_place.yaml) | accept, returns 9 | as above: an index and a tuple index on a `let mut` root are places |
| [`let_mut_reject_assign_without_mut`](./let_mut_reject_assign_without_mut.yaml) | reject, `E2402` | as above: an assignment to a place whose root is not mutable MUST be refused |
| [`let_mut_reject_compound_without_mut`](./let_mut_reject_compound_without_mut.yaml) | reject, `E2402` | as above |
| [`let_mut_reject_assign_parameter`](./let_mut_reject_assign_parameter.yaml) | reject, `E2402` | as above: a parameter is not mutable |
| [`let_mut_reject_assign_for_variable`](./let_mut_reject_assign_for_variable.yaml) | reject, `E2402` | as above: a `for` pattern binding is not mutable |
| [`let_mut_reject_assign_match_binding`](./let_mut_reject_assign_match_binding.yaml) | reject, `E2402` | as above: a `match` arm binding is not mutable |
| [`let_mut_reject_index_store_without_mut`](./let_mut_reject_index_store_without_mut.yaml) | reject, `E2402` | as above: the root of `a[0]` is not mutable |
| [`let_mut_reject_not_a_place`](./let_mut_reject_not_a_place.yaml) | reject, `E2402` | as above: the left operand MUST be a place |
| [`colon_assign_reject`](./colon_assign_reject.yaml) | reject | [Tokens](../../../spec/v1.0/lexical.md#tokens): MIND has no operator `:=`; the accept side is `let_mut_accept_assignment` |
| [`compound_assign_accept_six_operators`](./compound_assign_accept_six_operators.yaml) | accept, returns 59 | `AssignmentOperator` and [Bindings and assignment](../../../spec/v1.0/language.md#bindings-and-assignment): `x op= e` is `x = x op e` |
| [`compound_assign_accept_longest_match`](./compound_assign_accept_longest_match.yaml) | accept, returns 4 | [Tokens](../../../spec/v1.0/lexical.md#tokens): longest match makes `<<=` one token |
| [`compound_assign_reject_mixed_types`](./compound_assign_reject_mixed_types.yaml) | reject, `E2004` | as above: `x %= y` is `x = x % y`, and the operands of `%` share a type |
| [`separator_accept_strict_form`](./separator_accept_strict_form.yaml) | accept, returns 7 | [Statement separators](../../../spec/v1.0/language.md#statement-separators) |
| [`separator_reject_let_without_semicolon`](./separator_reject_let_without_semicolon.yaml) | reject | as above: a missing `;` MUST be refused |
| [`separator_reject_expression_statement_without_semicolon`](./separator_reject_expression_statement_without_semicolon.yaml) | reject | as above |
| [`separator_reject_match_arm_without_comma`](./separator_reject_match_arm_without_comma.yaml) | reject | as above: a missing `,` of an expression arm MUST be refused |
| [`defer_reject_semicolon`](./defer_reject_semicolon.yaml) | reject | [Block-like statements](../../../spec/v1.0/language.md#block-like-statements): a `defer` statement takes no `;`, so `defer { };` MUST be refused |
| [`tuple_index_accept`](./tuple_index_accept.yaml) | accept, returns 9 | `TupleIndexOperator` and [Tuple index](../../../spec/v1.0/language.md#tuple-index) |
| [`tuple_index_accept_nested`](./tuple_index_accept_nested.yaml) | accept, returns 2 | as above: the float literal `0.1` after `.` is read as two tuple indices |
| [`tuple_index_reject_float_with_exponent`](./tuple_index_reject_float_with_exponent.yaml) | reject | as above: a float literal with an exponent is not read as two tuple indices |
| [`tuple_index_reject_out_of_range`](./tuple_index_reject_out_of_range.yaml) | reject, `E2404` | [Tuple index](../../../spec/v1.0/language.md#tuple-index) |
| [`tuple_index_reject_not_a_tuple`](./tuple_index_reject_not_a_tuple.yaml) | reject, `E2404` | as above |
| [`tuple_index_reject_bracket`](./tuple_index_reject_bracket.yaml) | reject, `E2404` | as above: `t[0]` on a tuple has no meaning |
| [`range_index_reject`](./range_index_reject.yaml) | reject, `E2406` | as above: `a[1..3]` MUST be refused |
| [`unit_value_accept`](./unit_value_accept.yaml) | accept, returns 0 | `UnitExpression` and [The unit value](../../../spec/v1.0/types.md#the-unit-value) |
| [`unit_value_reject_other_type`](./unit_value_reject_other_type.yaml) | reject, `E2001` | as above: `()` where another type is expected MUST be refused |
| [`unit_value_reject_argument`](./unit_value_reject_argument.yaml) | reject, `E2001` | as above |
| [`float_remainder_accept_truncated`](./float_remainder_accept_truncated.yaml) | accept, returns 1 | [Floating-point remainder](../../../spec/v1.0/language.md#floating-point-remainder), rows 4 and 7 |
| [`float_remainder_reject_mixed_types`](./float_remainder_reject_mixed_types.yaml) | reject, `E2004` | as above: the operands have the same type |
| [`cast_precedence_accept_tighter_than_mul`](./cast_precedence_accept_tighter_than_mul.yaml) | accept, returns 3 | `CastExpression` and [Casts](../../../spec/v1.0/language.md#casts): `a * 2 as f64` is `a * (2 as f64)` |
| [`cast_precedence_reject_mixed_product`](./cast_precedence_reject_mixed_product.yaml) | reject, `E2004` | as above: with `a: i64` the product mixes `i64` and `f64` |
| [`cast_accept_integer_float_bool`](./cast_accept_integer_float_bool.yaml) | accept, returns 5 | [Casts](../../../spec/v1.0/language.md#casts), rows 1, 2, 3 and 6 |
| [`cast_accept_float_to_integer_bounds`](./cast_accept_float_to_integer_bounds.yaml) | accept, returns 47 | as above, row 3: the nearest bound, and NaN gives 0 |
| [`cast_reject_integer_to_bool`](./cast_reject_integer_to_bool.yaml) | reject, `E2016` | as above: a cast that the table does not list MUST be refused |
| [`cast_reject_bool_to_float`](./cast_reject_bool_to_float.yaml) | reject, `E2016` | as above |
| [`literal_accept_float_without_suffix`](./literal_accept_float_without_suffix.yaml) | accept, returns 0 | `FloatingPointLiteral` |
| [`literal_reject_caret_suffix`](./literal_reject_caret_suffix.yaml) | reject | [Literals](../../../spec/v1.0/lexical.md#literals): a literal has no suffix `^` |
| [`entry_accept_no_result_type`](./entry_accept_no_result_type.yaml) | accept | [Entry function](../../../spec/v1.0/language.md#entry-function) |
| [`entry_accept_unit_result`](./entry_accept_unit_result.yaml) | accept | as above: the result type `unit` may be written |
| [`entry_reject_f64_result`](./entry_reject_f64_result.yaml) | reject, `E2403` | as above: another result type MUST be refused |
| [`entry_reject_parameter`](./entry_reject_parameter.yaml) | reject, `E2403` | as above: `main` has no parameter |
