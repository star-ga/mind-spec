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
| [`loop_exit_reject_break_as_name`](./loop_exit_reject_break_as_name.yaml) | reject | as above: `break` is a keyword, so `let break = 4;` has no derivation and MUST be refused |
| [`loop_exit_reject_continue_as_name`](./loop_exit_reject_continue_as_name.yaml) | reject | as above: `continue` is a keyword |
| [`loop_exit_reject_break_as_operand`](./loop_exit_reject_break_as_operand.yaml) | reject | as above: `break - 1;` uses the keyword as an operand |
| [`loop_exit_reject_label`](./loop_exit_reject_label.yaml) | reject | as above: a label is an invalid token and MUST be diagnosed |
| [`loop_exit_reject_continue_label`](./loop_exit_reject_continue_label.yaml) | reject | as above |
| [`loop_exit_reject_label_in_for`](./loop_exit_reject_label_in_for.yaml) | reject | as above |
| [`loop_exit_reject_break_outside_loop`](./loop_exit_reject_break_outside_loop.yaml) | reject, `E2401` | [Loop exits](../../../spec/v1.0/language.md#loop-exits): a loop exit outside a loop MUST be refused |
| [`loop_exit_reject_continue_after_loop`](./loop_exit_reject_continue_after_loop.yaml) | reject, `E2401` | as above |
| [`loop_exit_reject_without_semicolon`](./loop_exit_reject_without_semicolon.yaml) | reject | [Statement separators](../../../spec/v1.0/language.md#statement-separators): the `;` of a loop exit is required, so `while c { break }` MUST be refused |
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
| [`bitwise_accept_and_or_xor`](./bitwise_accept_and_or_xor.yaml) | accept, returns 28 | `BitwiseExpression` and [Bitwise and shift operators](../../../spec/v1.0/language.md#bitwise-and-shift-operators), row 1 |
| [`bitwise_accept_precedence`](./bitwise_accept_precedence.yaml) | accept, returns 23 | `AdditiveExpression` over `BitwiseExpression` and [Operator precedence](../../../spec/v1.0/language.md#operator-precedence-and-associativity): shifts and bitwise operators bind tighter than `+` and `-` |
| [`shift_accept_count_modulo_width`](./shift_accept_count_modulo_width.yaml) | accept, returns 13 | [Bitwise and shift operators](../../../spec/v1.0/language.md#bitwise-and-shift-operators), rows 2 and 3: the count is the right operand modulo the width |
| [`shift_accept_count_modulo_width_i32`](./shift_accept_count_modulo_width_i32.yaml) | accept, returns 3 | as above, for `i32`; the cast is row 1 of [Casts](../../../spec/v1.0/language.md#casts) |
| [`shift_accept_negative_count`](./shift_accept_negative_count.yaml) | accept, returns 10 | as above: a negative count uses its two's complement value modulo the width |
| [`shift_accept_arithmetic_right`](./shift_accept_arithmetic_right.yaml) | accept, returns 5 | as above, row 3: `>>` on a signed type is the arithmetic shift |
| [`bitwise_reject_mixed_types`](./bitwise_reject_mixed_types.yaml) | reject, `E2004` | as above: the operands of `&` have the same integer type |
| [`bitwise_reject_bool_operand`](./bitwise_reject_bool_operand.yaml) | reject, `E2005` | as above: an operand that is not of an integer type MUST be refused |
| [`shift_reject_float_operand`](./shift_reject_float_operand.yaml) | reject, `E2005` | as above |
| [`closing_angle_accept_nested_type_arguments`](./closing_angle_accept_nested_type_arguments.yaml) | accept, returns 0 | `CloseAngle` and [Tokens](../../../spec/v1.0/lexical.md#tokens): the first `>` of `>>=` closes a type argument list |
| [`closing_angle_reject_extra_angle`](./closing_angle_reject_extra_angle.yaml) | reject | as above: after the list closes, `>=` is left where the `let` needs `=` |
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
| [`slice_accept_array`](./slice_accept_array.yaml) | accept, returns 0 | `SliceExpression` and [Tuple index](../../../spec/v1.0/language.md#tuple-index): `a[1:3]` is the slice form |
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
| [`loop_accept_name_in_while_condition`](./loop_accept_name_in_while_condition.yaml) | accept, returns 3 | [Loop exits](../../../spec/v1.0/language.md#loop-exits): only the name `loop` directly followed by `{` where a statement can start is refused |
| [`cast_accept_primitive_type_then_less`](./cast_accept_primitive_type_then_less.yaml) | accept, returns 1 | [Casts](../../../spec/v1.0/language.md#casts): reading rule for the type of a cast, a primitive type name ends the type |
| [`cast_reject_named_type_then_less`](./cast_reject_named_type_then_less.yaml) | reject | as above: after any other type name the type reading wins |
| [`method_call_accept_option_unwrap_or`](./method_call_accept_option_unwrap_or.yaml) | accept | [Field access and method calls](../../../spec/v1.0/language.md#field-access-and-method-calls): `x.m(a)` has one derivation, the method call |
| [`method_call_reject_field_then_call`](./method_call_reject_field_then_call.yaml) | reject | as above: a field access whose name is not a field of the type MUST be refused |
| [`struct_accept_field_of_other_struct`](./struct_accept_field_of_other_struct.yaml) | accept | [Type formation](../../../spec/v1.0/types.md#type-formation): only a struct that holds itself is refused |
| [`struct_reject_holds_itself`](./struct_reject_holds_itself.yaml) | reject, `E2407` | as above: a struct that holds itself MUST be refused |
| [`struct_reject_holds_itself_through_other`](./struct_reject_holds_itself_through_other.yaml) | reject, `E2407` | as above |
| [`rawmem_accept_marked_load`](./rawmem_accept_marked_load.yaml) | accept, returns 9 | [Raw memory](../../../spec/v1.0/memory.md#raw-memory): a raw memory use is allowed in a function declared with `#[raw_memory]` |
| [`rawmem_accept_sealed_called`](./rawmem_accept_sealed_called.yaml) | accept, returns 5 | as above: a call of a `#[raw_memory(sealed)]` function is not a raw memory use |
| [`rawmem_accept_std_safe_call`](./rawmem_accept_std_safe_call.yaml) | accept | [Raw memory functions](../../../spec/v1.0/memory.md#raw-memory-functions): a function of the list needs the mark, another library function does not |
| [`rawmem_reject_unmarked_load`](./rawmem_reject_unmarked_load.yaml) | reject, `E2501` | [Raw memory](../../../spec/v1.0/memory.md#raw-memory): any other raw memory use MUST be refused |
| [`rawmem_reject_unmarked_vec_addr`](./rawmem_reject_unmarked_vec_addr.yaml) | reject, `E2501` | as above: `vec_addr` gives an address |
| [`rawmem_reject_unmarked_calls_marked`](./rawmem_reject_unmarked_calls_marked.yaml) | reject, `E2501` | as above: a call of a `#[raw_memory]` function is a raw memory use |
| [`rawmem_reject_attr_on_struct`](./rawmem_reject_attr_on_struct.yaml) | reject, `E2502` | as above: another use of the attribute MUST be refused |
| [`rawmem_reject_attr_argument`](./rawmem_reject_attr_argument.yaml) | reject, `E2502` | as above |
| [`attribute_reject_unknown_name`](./attribute_reject_unknown_name.yaml) | reject, `E2502` | [Attributes](../../../spec/v1.0/language.md#attributes): an attribute name that the specification does not define MUST be refused |
| [`attribute_reject_unknown_name_before_struct`](./attribute_reject_unknown_name_before_struct.yaml) | reject, `E2502` | as above, before another item |
| [`string_type_accept_named`](./string_type_accept_named.yaml) | accept | [Type formation](../../../spec/v1.0/types.md#type-formation): the string type `String` |
| [`string_type_reject_literal_as_integer`](./string_type_reject_literal_as_integer.yaml) | reject, `E2001` | as above: a string literal has the type `String` |
| [`elementwise_accept_scalar_values`](./elementwise_accept_scalar_values.yaml) | accept, returns 24 | [Tensor operations](../../../spec/v1.0/language.md#tensor-operations): elementwise operators |
| [`elementwise_accept_tensor_scalar`](./elementwise_accept_tensor_scalar.yaml) | accept | as above |
| [`elementwise_reject_mixed_dtypes`](./elementwise_reject_mixed_dtypes.yaml) | reject, `E2004` | as above: operands of two different dtypes MUST be refused |
| [`tensor_ctor_accept_shape_and_dtype`](./tensor_ctor_accept_shape_and_dtype.yaml) | accept | [Tensor operations](../../../spec/v1.0/language.md#tensor-operations): tensor constructor |
| [`tensor_ctor_reject_no_cast`](./tensor_ctor_reject_no_cast.yaml) | reject, `E2016` | as above: no cast from the element type to the dtype |
| [`tensor_ctor_reject_bool_without_dtype`](./tensor_ctor_reject_bool_without_dtype.yaml) | reject, `E2005` | as above: another element type MUST be refused |
| [`slice_accept_omitted_parts`](./slice_accept_omitted_parts.yaml) | accept | [Tuple index](../../../spec/v1.0/language.md#tuple-index): an omitted start is 0, an omitted end the length, an omitted step 1 |
| [`slice_reject_zero_step`](./slice_reject_zero_step.yaml) | reject, `E4008` | [Indexing and slicing](../../../spec/v1.0/ir.md#indexing-and-slicing): every step of `Slice` MUST be non-zero |
| [`literal_type_accept_defaults`](./literal_type_accept_defaults.yaml) | accept, returns 12 | [Type of a literal](../../../spec/v1.0/types.md#type-of-a-literal), rules 1 and 2 |
| [`literal_type_reject_out_of_range`](./literal_type_reject_out_of_range.yaml) | reject, `E2408` | as above, rule 3 |
| [`literal_type_reject_integer_for_float`](./literal_type_reject_integer_for_float.yaml) | reject, `E2001` | as above, rule 4 |
| [`literal_type_reject_float_for_integer`](./literal_type_reject_float_for_integer.yaml) | reject, `E2001` | as above, rule 4 |
| [`cont_array_alias_sees_push`](./cont_array_alias_sees_push.yaml) | accept, returns 5 | [Records and containers](../../../spec/v1.0/memory.md#records-and-containers): a change through one reference is visible through every other reference |
| [`cont_array_alias_sees_growth`](./cont_array_alias_sees_growth.yaml) | accept, returns 99 | as above, and no container handle shows released storage |
| [`cont_array_param_change_seen`](./cont_array_param_change_seen.yaml) | accept, returns 3 | [Changing a container](../../../spec/v1.0/memory.md#changing-a-container): a parameter is changed through `let mut w = p;` |
| [`cont_array_same_name_update`](./cont_array_same_name_update.yaml) | accept, returns 2 | as above: a push stands as a statement or in the update of the same place |
| [`cont_push_root_not_mut`](./cont_push_root_not_mut.yaml) | reject, `E2402` | as above: a method call that changes a container whose root is not mutable MUST be refused |
| [`cont_push_on_parameter`](./cont_push_on_parameter.yaml) | reject, `E2402` | as above |
| [`cont_push_in_expression`](./cont_push_in_expression.yaml) | reject, `E2300` | as above: any other use of a push MUST be refused |
| [`cont_map_alias_sees_insert`](./cont_map_alias_sees_insert.yaml) | accept, returns 1 | [Records and containers](../../../spec/v1.0/memory.md#records-and-containers): the insert function of a map changes the record in place |
| [`cont_map_two_inserts_one_record`](./cont_map_two_inserts_one_record.yaml) | accept, returns 3 | as above |
| [`cont_string_alias_sees_push`](./cont_string_alias_sees_push.yaml) | accept, returns 1 | as above: the string push functions change the record in place |
| [`cont_string_part_is_copy`](./cont_string_part_is_copy.yaml) | accept, returns 2 | as above: a function that gives a part of a string creates a new record with a copy of the bytes |
| [`cont_string_literal_new_record`](./cont_string_literal_new_record.yaml) | accept, returns 3 | as above: each evaluation of a string literal creates a new string record |
| [`bounds_reject_index_literal_outside`](./bounds_reject_index_literal_outside.yaml) | reject, `E3011` | [Index bounds](../../../spec/v1.0/ir.md#index-bounds): an index outside its axis that is known at check time MUST be refused |
| [`bounds_reject_negative_index`](./bounds_reject_negative_index.yaml) | reject, `E3011` | as above: a negative index is outside its axis |
| [`bounds_reject_slice_bound_outside`](./bounds_reject_slice_bound_outside.yaml) | reject, `E3011` | as above: a slice bound outside its axis |
| [`bounds_accept_slice_bounds_in_axis`](./bounds_accept_slice_bounds_in_axis.yaml) | accept | as above: a bound equal to the extent is in the axis, and a dimension of size 0 is valid |
| [`bounds_accept_last_index`](./bounds_accept_last_index.yaml) | accept, returns 4 | as above |
| [`dimension_reject_negative`](./dimension_reject_negative.yaml) | reject, `E3006` | as above: a negative dimension MUST be refused |
| [`dimension_accept_zero`](./dimension_accept_zero.yaml) | accept | as above: a dimension of size 0 is valid |
| [`dimension_reject_negative_array_length`](./dimension_reject_negative_array_length.yaml) | reject, `E3006` | [Fixed-array literal cardinality](../../../spec/v1.0/types.md#fixed-array-literal-cardinality): a negative length of a fixed array type MUST be refused |
| [`literal_sign_accept_i32_min`](./literal_sign_accept_i32_min.yaml) | accept | [Literals](../../../spec/v1.0/lexical.md#literals): a sign directly before the digits is part of the literal where an operand can start |
| [`literal_sign_accept_minus_after_name`](./literal_sign_accept_minus_after_name.yaml) | accept, returns 2 | as above: after an identifier the sign is an operator |
| [`literal_sign_reject_below_i32_min`](./literal_sign_reject_below_i32_min.yaml) | reject, `E2408` | as above: the sign is part of the literal, and the literal is outside the range of `i32` |
| [`slice_accept_double_colon_step`](./slice_accept_double_colon_step.yaml) | accept | [Tuple index](../../../spec/v1.0/language.md#tuple-index): inside an index bracket the token `::` is read as two `:` |
| [`slice_reject_three_colons`](./slice_reject_three_colons.yaml) | reject | as above: `a[:::2]` is not derived |
