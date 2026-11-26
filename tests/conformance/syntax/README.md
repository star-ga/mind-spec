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
  fault, also when the grammar does not derive the source (`a[1..3]` gives `E1101`). A reject row whose fault
  has no code in the catalog gives the status only. A reject row holds one fault; a row of the rule "one diagnostic
  for each top-level item" holds one fault in each of several items, and gives the first diagnostic and the count.

No row's verdict depends on a form that is marked NOT IN CORE v1, an extension or an open form: an
implementation MAY accept or refuse those.

**Position and count.** A reject row whose code is a lexical or a syntax code (E1xxx) carries the position of its
diagnostic (`location`, line and column): the first token that cannot continue, or the point that the entry of the
code fixes (the insertion point of a missing separator, the opening quote of a string, the first character that no
form of a literal allows). It also carries the count of diagnostics (`count`)
([Diagnostics](../../../spec/v1.0/lexical.md#diagnostics)). A reject row whose code is given at check time carries the
position where a rule of the specification fixes the point; where no rule fixes it, the field says so:
`location: "not fixed by the text"`. A lint of these two fields is later work, and older rows may lack `count`. A
reject row whose code has the fix class EXACT or TYPED carries the text after the fix (`fix`); a check of the
specification repository asserts it ([Code table](../../../spec/v1.0/errors.md#code-table)).

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
| [`loop_accept_loop_block`](./loop_accept_loop_block.yaml) | accept, returns 3 | [Loops](../../../spec/v1.0/language.md#loops): `loop B` runs until a `break` ends it (DN-54) |
| [`loop_reject_name_loop`](./loop_reject_name_loop.yaml) | reject, `E1007` at 2:9 | [Keywords](../../../spec/v1.0/lexical.md#keywords): `loop` is a keyword (DN-54) |
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
| [`compound_assign_accept_longest_match`](./compound_assign_accept_longest_match.yaml) | accept, returns 4 | [Tokens](../../../spec/v1.0/lexical.md#tokens): the joined tokens `<`, `<` and `=` are the operator `<<=` |
| [`compound_assign_reject_mixed_types`](./compound_assign_reject_mixed_types.yaml) | reject, `E2004` | as above: `x %= y` is `x = x % y`, and the operands of `%` share a type |
| [`bitwise_accept_and_or_xor`](./bitwise_accept_and_or_xor.yaml) | accept, returns 28 | `BitwiseExpression` and [Bitwise and shift operators](../../../spec/v1.0/language.md#bitwise-and-shift-operators), row 1 |
| [`bitwise_accept_parentheses`](./bitwise_accept_parentheses.yaml) | accept, returns 23 | [Precedence rules](../../../spec/v1.0/language.md#precedence-rules): a bit operator beside `+` or `-` is written with parentheses (DN-50) |
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
| [`range_index_reject`](./range_index_reject.yaml) | reject, `E1101` at 3:16 | [Loops](../../../spec/v1.0/language.md#loops): `..` stands only in a `for` header, so `a[1..3]` has no derivation (DN-47) |
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
| [`loop_reject_name_in_while_condition`](./loop_reject_name_in_while_condition.yaml) | reject, `E1007` at 2:9 | [Keywords](../../../spec/v1.0/lexical.md#keywords): `loop` is a keyword in every place (DN-54) |
| [`cast_accept_primitive_type_then_less`](./cast_accept_primitive_type_then_less.yaml) | accept, returns 1 | [Casts](../../../spec/v1.0/language.md#casts): reading rule for the type of a cast, a primitive type name ends the type |
| [`cast_reject_named_type_then_less`](./cast_reject_named_type_then_less.yaml) | reject | as above: the type of a cast has no type-argument list, so `<` compares, and `x as Option` is a cast that the table does not list (DN-53) |
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
| [`rawmem_reject_attr_argument_with_use`](./rawmem_reject_attr_argument_with_use.yaml) | reject, `E2502` | [Raw memory](../../../spec/v1.0/memory.md#raw-memory): a function whose attribute `raw_memory` `E2502` refuses gets no `E2501` |
| [`attribute_reject_unknown_name`](./attribute_reject_unknown_name.yaml) | reject, `E2502` | [Attributes](../../../spec/v1.0/language.md#attributes): an attribute name that the specification does not define MUST be refused |
| [`attribute_reject_unknown_name_before_struct`](./attribute_reject_unknown_name_before_struct.yaml) | reject, `E2502` | as above, before another item |
| [`string_type_accept_named`](./string_type_accept_named.yaml) | accept | [Type formation](../../../spec/v1.0/types.md#type-formation): the string type `String` |
| [`string_type_reject_literal_as_integer`](./string_type_reject_literal_as_integer.yaml) | reject, `E2001` | as above: a string literal has the type `String` |
| [`elementwise_reject_scalar_values`](./elementwise_reject_scalar_values.yaml) | reject | [Tensor operators and broadcasting](../../../spec/v1.0/language.md#tensor-operators-and-broadcasting): a dotted operator that expands no operand MUST be refused with `E3016` (DN-81) |
| [`elementwise_accept_tensor_scalar`](./elementwise_accept_tensor_scalar.yaml) | accept | as above |
| [`elementwise_reject_mixed_dtypes`](./elementwise_reject_mixed_dtypes.yaml) | reject, `E2004` | [Tensor operations](../../../spec/v1.0/language.md#tensor-operations): tensor operands of two different dtypes MUST be refused |
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
| [`bounds_reject_index_literal_outside`](./bounds_reject_index_literal_outside.yaml) | reject, `E3011` | [Index bounds](../../../spec/v1.0/ir.md#index-bounds): an integer literal index outside its axis, where the type gives the extent, MUST be refused at check time |
| [`bounds_reject_index_parenthesized_literal`](./bounds_reject_index_parenthesized_literal.yaml) | reject, `E3011` | as above: with or without parentheses around the literal |
| [`bounds_accept_index_expression_unchecked`](./bounds_accept_index_expression_unchecked.yaml) | accept, returns 0 | as above: an implementation refuses no other index at check time (`a[2 + 2]`) |
| [`bounds_accept_index_variable_unchecked`](./bounds_accept_index_variable_unchecked.yaml) | accept, returns 0 | as above (`a[i]` with `i = 4`) |
| [`bounds_reject_negative_index`](./bounds_reject_negative_index.yaml) | reject, `E3011` | as above: a negative index is outside its axis |
| [`bounds_reject_slice_bound_outside`](./bounds_reject_slice_bound_outside.yaml) | reject, `E3011` | as above: a slice bound outside its axis |
| [`bounds_accept_slice_bounds_in_axis`](./bounds_accept_slice_bounds_in_axis.yaml) | accept | as above: a bound equal to the extent is in the axis, and a dimension of size 0 is valid |
| [`bounds_accept_last_index`](./bounds_accept_last_index.yaml) | accept, returns 4 | as above |
| [`dimension_reject_negative`](./dimension_reject_negative.yaml) | reject, `E3006` | as above: a negative dimension MUST be refused |
| [`dimension_accept_zero`](./dimension_accept_zero.yaml) | accept | as above: a dimension of size 0 is valid |
| [`reshape_reject_marker_with_zero`](./reshape_reject_marker_with_zero.yaml) | reject, `E3007` | [Shape manipulation](../../../spec/v1.0/ir.md#shape-manipulation): a marker `-1` that another entry 0 leaves without a value MUST be refused |
| [`reduction_reject_mean_empty_axis`](./reduction_reject_mean_empty_axis.yaml) | reject | [Empty axes](../../../spec/v1.0/ir.md#empty-axes): `mean` over an axis of extent 0 has no value and MUST be refused at check time when the type gives the shape |
| [`reduction_accept_sum_prod_empty_axis`](./reduction_accept_sum_prod_empty_axis.yaml) | accept, returns 0 | as above: a sum and a product over an axis of extent 0 have a value (0 and 1), so the check accepts them; the row does not read the values |
| [`dimension_reject_negative_array_length`](./dimension_reject_negative_array_length.yaml) | reject, `E3006` | [Fixed-array literal cardinality](../../../spec/v1.0/types.md#fixed-array-literal-cardinality): a negative length of a fixed array type MUST be refused |
| [`literal_sign_accept_i32_min`](./literal_sign_accept_i32_min.yaml) | accept | [Literals](../../../spec/v1.0/lexical.md#literals): a unary `-` applied to a literal is one negative value, which `i32` holds (DN-48) |
| [`literal_sign_accept_minus_after_name`](./literal_sign_accept_minus_after_name.yaml) | accept, returns 2 | as above: `-` is always an operator, so `a-1` is a subtraction |
| [`literal_sign_reject_below_i32_min`](./literal_sign_reject_below_i32_min.yaml) | reject, `E2408` | as above: the negative value is outside the range of `i32` |
| [`literal_sign_accept_after_block_statement`](./literal_sign_accept_after_block_statement.yaml) | accept, returns 0 | [Literals](../../../spec/v1.0/lexical.md#literals): after the `}` that ends a block-like statement a new statement starts, and `-` applied to the literal is one negative value that `i64` holds |
| [`literal_sign_reject_after_block_operand`](./literal_sign_reject_after_block_operand.yaml) | reject, `E2408` | as above: after the `}` of a block that is an operand, `-` is a binary operator, and the literal is outside the range of `i64` |
| [`map_get_accept_missing_key`](./map_get_accept_missing_key.yaml) | accept, returns 5 | [Four pure-MIND modules](../../../spec/v1.0/stdlib.md#four-pure-mind-modules): `map_get` of a key that the map does not hold gives 0 |
| [`for_accept_length_read_once`](./for_accept_length_read_once.yaml) | accept, returns 2 | [Loops](../../../spec/v1.0/language.md#loops): a `for` loop over a container reads the length one time, at its start |
| [`set_accept_with_mut_root`](./set_accept_with_mut_root.yaml) | accept, returns 5 | [Records and containers](../../../spec/v1.0/memory.md#records-and-containers): `xs.set(i, v)` replaces the element `i` |
| [`set_reject_root_not_mut`](./set_reject_root_not_mut.yaml) | reject, `E2402` | [Changing a container](../../../spec/v1.0/memory.md#changing-a-container): `xs.set(i, v)` needs a `let mut` root |
| [`slice_accept_double_colon_step`](./slice_accept_double_colon_step.yaml) | accept | [Tuple index](../../../spec/v1.0/language.md#tuple-index): inside an index bracket the token `::` is read as two `:` |
| [`slice_reject_three_colons`](./slice_reject_three_colons.yaml) | reject | as above: `a[:::2]` is not derived |

## Rows of the grammar decisions

Each decision DN-22 to DN-85 and DN-89 of [Decision Notes, Part 3](../../../design/rfcs/decision-notes-3.md) has rows here,
in the folder of its category: the tensor forms in [`shapes`](../shapes), the gradient attribute in
[`autodiff`](../autodiff), the lexical forms in [`lexical`](../lexical), the type and pattern rules in
[`type_checker`](../type_checker), and the rest in this folder. The rows `dn63_fault_*`, `dn64_fault_*` and
`dn76_fault_*` are a set of 40 syntax faults; each has one fault, and its row gives the code and the position of the one
diagnostic. DN-74 changes only names of the IR grammar and has no row; DN-25 has no refused form; DN-69 has no reject
row, because the nesting limit of an implementation has no upper bound. The accept row of DN-84 names the tools that
its project file lists (`input.project_tools`); the byte rule of DN-84 is a gate of the reference compiler repository,
not a row.

| Decision | Row | Result | Rule |
|----------|-----|--------|------|
| DN-22 | [`dn22_binding_last_arm_accept`](../type_checker/dn22_binding_last_arm_accept.yaml) | accept, returns 5 | [Patterns and match](../../../spec/v1.0/language.md#patterns-and-match): a bare name always binds |
| DN-22 | [`dn22_const_name_arm_not_last_reject`](../type_checker/dn22_const_name_arm_not_last_reject.yaml) | reject, `E2301` at 6:9 | as above: the fix is `n if n == K` |
| DN-22 | [`dn22_const_name_arm_last_reject`](../type_checker/dn22_const_name_arm_last_reject.yaml) | reject, `E2314` at 7:9 | as above |
| DN-22 | [`dn22_binding_not_last_reject`](../type_checker/dn22_binding_not_last_reject.yaml) | reject, `E2312` | as above: no later arm can run |
| DN-23 | [`dn23_tuple_equality_accept`](../type_checker/dn23_tuple_equality_accept.yaml) | accept, returns 1 | [Operand and condition types](../../../spec/v1.0/language.md#operand-and-condition-types) |
| DN-23 | [`dn23_integer_condition_reject`](../type_checker/dn23_integer_condition_reject.yaml) | reject, `E2001` | as above: a condition MUST be a `bool` |
| DN-23 | [`dn23_not_on_integer_reject`](../type_checker/dn23_not_on_integer_reject.yaml) | reject, `E2005` | as above |
| DN-23 | [`dn23_bool_plus_reject`](../type_checker/dn23_bool_plus_reject.yaml) | reject, `E2005` | as above |
| DN-23 | [`dn23_minus_on_unsigned_reject`](../type_checker/dn23_minus_on_unsigned_reject.yaml) | reject | as above: `0 - x` writes the wrapping subtraction |
| DN-24 | [`dn24_loop_tail_accept`](../type_checker/dn24_loop_tail_accept.yaml) | accept, returns 4 | [Loops](../../../spec/v1.0/language.md#loops): divergence is a property of the text |
| DN-24 | [`dn24_assign_other_type_reject`](../type_checker/dn24_assign_other_type_reject.yaml) | reject, `E2001` | [Bindings and assignment](../../../spec/v1.0/language.md#bindings-and-assignment) |
| DN-24 | [`dn24_tail_with_semicolon_reject`](../type_checker/dn24_tail_with_semicolon_reject.yaml) | reject | as above: only the tail gives the block its value |
| DN-24 | [`dn24_assign_const_reject`](../type_checker/dn24_assign_const_reject.yaml) | reject, `E2402` | as above |
| DN-25 | [`dn25_short_circuit_accept`](dn25_short_circuit_accept.yaml) | accept, returns 7 | [Evaluation order](../../../spec/v1.0/language.md#evaluation-order) |
| DN-25 | [`dn25_left_to_right_accept`](dn25_left_to_right_accept.yaml) | accept, returns 3 | as above |
| DN-26 | [`dn26_block_like_without_semicolon_accept`](dn26_block_like_without_semicolon_accept.yaml) | accept, returns 1 | [Statement separators](../../../spec/v1.0/language.md#statement-separators) |
| DN-26 | [`dn26_let_without_semicolon_reject`](dn26_let_without_semicolon_reject.yaml) | reject, `E1103` at 2:14 | as above |
| DN-27 | [`dn27_wildcard_let_twice_accept`](dn27_wildcard_let_twice_accept.yaml) | accept, returns 0 | [Identifiers](../../../spec/v1.0/lexical.md#identifiers): a lone `_` binds nothing |
| DN-27 | [`dn27_wildcard_parameters_accept`](dn27_wildcard_parameters_accept.yaml) | accept, returns 3 | as above |
| DN-27 | [`dn27_wildcard_read_reject`](dn27_wildcard_read_reject.yaml) | reject, `E1101` at 3:12 | as above |
| DN-28 | [`dn28_record_literal_accept`](dn28_record_literal_accept.yaml) | accept, returns 2 | [Record literals](../../../spec/v1.0/language.md#record-literals) |
| DN-28 | [`dn28_record_in_head_with_parentheses_accept`](dn28_record_in_head_with_parentheses_accept.yaml) | accept, returns 1 | as above |
| DN-28 | [`dn28_identifier_then_block_in_head_accept`](dn28_identifier_then_block_in_head_accept.yaml) | accept, returns 4 | as above |
| DN-28 | [`dn28_record_in_head_bare_reject`](dn28_record_in_head_bare_reject.yaml) | reject, `E1101` | as above |
| DN-29 | [`dn29_call_of_function_name_accept`](dn29_call_of_function_name_accept.yaml) | accept, returns 3 | [Field access and method calls](../../../spec/v1.0/language.md#field-access-and-method-calls) |
| DN-29 | [`dn29_call_on_literal_reject`](dn29_call_on_literal_reject.yaml) | reject, `E1101` | as above: a value is not a function in this edition |
| DN-29 | [`dn29_call_of_call_reject`](dn29_call_of_call_reject.yaml) | reject, `E1101` | as above |
| DN-29 | [`dn29_call_of_value_reject`](../type_checker/dn29_call_of_value_reject.yaml) | reject, `E2409` | [`E2409`](../../../spec/v1.0/errors.md#e2409-callee-is-not-a-function) |
| DN-30 | [`dn30_same_parameter_name_in_two_functions_accept`](../type_checker/dn30_same_parameter_name_in_two_functions_accept.yaml) | accept, returns 3 | [Module level](../../../spec/v1.0/language.md#module-level) |
| DN-30 | [`dn30_duplicate_function_reject`](../type_checker/dn30_duplicate_function_reject.yaml) | reject, `E2720` | as above |
| DN-30 | [`dn30_unknown_type_reject`](../type_checker/dn30_unknown_type_reject.yaml) | reject, `E2002` | as above |
| DN-30 | [`dn30_no_such_method_reject`](../type_checker/dn30_no_such_method_reject.yaml) | reject, `E2410` | [Field access and method calls](../../../spec/v1.0/language.md#field-access-and-method-calls) |
| DN-31 | [`dn31_test_attribute_accept`](dn31_test_attribute_accept.yaml) | accept, returns 0 | [Attributes](../../../spec/v1.0/language.md#attributes): the row `test` of the table |
| DN-31 | [`dn31_repr_packed_reject`](dn31_repr_packed_reject.yaml) | reject, `E2502` | as above |
| DN-31 | [`dn31_test_with_parameter_reject`](dn31_test_with_parameter_reject.yaml) | reject, `E2502` | as above |
| DN-31 | [`dn31_test_with_result_reject`](dn31_test_with_result_reject.yaml) | reject, `E2502` | as above |
| DN-32 | [`dn32_comparison_in_parentheses_accept`](dn32_comparison_in_parentheses_accept.yaml) | accept, returns 1 | [Precedence rules](../../../spec/v1.0/language.md#precedence-rules), rule 6 |
| DN-32 | [`dn32_comparison_chain_reject`](dn32_comparison_chain_reject.yaml) | reject, `E1101` at 2:14 | as above: the message gives `a < b && b < c` |
| DN-32 | [`dn32_equality_chain_reject`](dn32_equality_chain_reject.yaml) | reject, `E1101` at 3:15 | as above |
| DN-33 | [`dn33_true_value_accept`](../lexical/dn33_true_value_accept.yaml) | accept, returns 3 | [Keywords](../../../spec/v1.0/lexical.md#keywords) |
| DN-33 | [`dn33_true_as_name_reject`](../lexical/dn33_true_as_name_reject.yaml) | reject, `E1007` at 1:24 | as above |
| DN-33 | [`dn33_false_as_parameter_reject`](../lexical/dn33_false_as_parameter_reject.yaml) | reject, `E1007` at 1:6 | as above |
| DN-34 | [`dn34_complement_i64_accept`](dn34_complement_i64_accept.yaml) | accept, returns 4 | [Operand and condition types](../../../spec/v1.0/language.md#operand-and-condition-types): `~e` is the bitwise complement |
| DN-34 | [`dn34_complement_u8_accept`](dn34_complement_u8_accept.yaml) | accept, returns 255 | as above |
| DN-34 | [`dn34_complement_bool_reject`](dn34_complement_bool_reject.yaml) | reject, `E2005` | as above: `!` takes a `bool`, `~` an integer |
| DN-35 | [`dn35_digit_separator_accept`](../lexical/dn35_digit_separator_accept.yaml) | accept, returns 1 | [Literals](../../../spec/v1.0/lexical.md#literals) |
| DN-35 | [`dn35_literal_typed_by_cast_accept`](../lexical/dn35_literal_typed_by_cast_accept.yaml) | accept, returns 0 | as above |
| DN-35 | [`dn35_type_suffix_reject`](../lexical/dn35_type_suffix_reject.yaml) | reject, `E1005` at 2:16 | as above: a literal has no type suffix |
| DN-35 | [`dn35_underscore_after_prefix_reject`](../lexical/dn35_underscore_after_prefix_reject.yaml) | reject, `E1005` | as above |
| DN-35 | [`dn35_leading_zero_reject`](../lexical/dn35_leading_zero_reject.yaml) | reject, `E1005` | as above |
| DN-36 | [`dn36_exhaustive_bool_accept`](../type_checker/dn36_exhaustive_bool_accept.yaml) | accept, returns 1 | [Patterns and match](../../../spec/v1.0/language.md#patterns-and-match) |
| DN-36 | [`dn36_not_exhaustive_bool_reject`](../type_checker/dn36_not_exhaustive_bool_reject.yaml) | reject, `E2311` | as above: one missing case by a fixed order |
| DN-36 | [`dn36_dead_arm_reject`](../type_checker/dn36_dead_arm_reject.yaml) | reject, `E2312` | as above |
| DN-36 | [`dn36_pattern_does_not_fit_reject`](../type_checker/dn36_pattern_does_not_fit_reject.yaml) | reject, `E2001` | as above: a pattern that does not fit is `E2001` at every site |
| DN-37 | [`dn37_tensor_dtypes_accept`](../shapes/dn37_tensor_dtypes_accept.yaml) | accept, returns 0 | [The tensor type](../../../spec/v1.0/shapes.md#the-tensor-type) |
| DN-37 | [`dn37_tensor_bool_dtype_reject`](../shapes/dn37_tensor_bool_dtype_reject.yaml) | reject, `E2005` | as above |
| DN-37 | [`dn37_tensor_without_shape_reject`](../shapes/dn37_tensor_without_shape_reject.yaml) | reject | as above: both arguments are required |
| DN-37 | [`dn37_old_tensor_spelling_reject`](../shapes/dn37_old_tensor_spelling_reject.yaml) | reject, `E1105` at 1:9 | as above |
| DN-38 | [`dn38_tensor_as_value_name_accept`](../lexical/dn38_tensor_as_value_name_accept.yaml) | accept, returns 3 | [Keywords](../../../spec/v1.0/lexical.md#keywords): the word `tensor` |
| DN-38 | [`dn38_function_named_tensor_reject`](../lexical/dn38_function_named_tensor_reject.yaml) | reject, `E1007` at 1:4 | as above: `tensor(` is always the constructor |
| DN-39 | [`dn39_matmul_call_accept`](../shapes/dn39_matmul_call_accept.yaml) | accept, returns 0 | [Matrix multiplication](../../../spec/v1.0/shapes.md#matrix-multiplication) |
| DN-39 | [`dn39_at_sign_reject`](../shapes/dn39_at_sign_reject.yaml) | reject, `E1105` at 1:40 | as above: `@` has no production |
| DN-40 | [`dn40_tensor_literal_accept`](../shapes/dn40_tensor_literal_accept.yaml) | accept, returns 0 | [Tensor literals](../../../spec/v1.0/shapes.md#tensor-literals) |
| DN-40 | [`dn40_tensor_literal_length_reject`](../shapes/dn40_tensor_literal_length_reject.yaml) | reject, `E3010` | as above |
| DN-40 | [`dn40_tensor_literal_ragged_reject`](../shapes/dn40_tensor_literal_ragged_reject.yaml) | reject, `E3010` | as above |
| DN-40 | [`dn40_cast_to_tensor_type_reject`](../shapes/dn40_cast_to_tensor_type_reject.yaml) | reject, `E2016` | as above |
| DN-41 | [`dn41_unit_if_then_minus_accept`](dn41_unit_if_then_minus_accept.yaml) | accept, returns -1 | [Block-like statements](../../../spec/v1.0/language.md#block-like-statements) |
| DN-41 | [`dn41_tail_if_then_minus_reject`](dn41_tail_if_then_minus_reject.yaml) | reject, `E2001` | as above: the message gives `(if c { 1 } else { 2 }) - 3` |
| DN-42 | [`dn42_two_slice_colons_accept`](dn42_two_slice_colons_accept.yaml) | accept, returns 6 | [Tuple index](../../../spec/v1.0/language.md#tuple-index) |
| DN-42 | [`dn42_slice_bounds_named_by_constants_accept`](dn42_slice_bounds_named_by_constants_accept.yaml) | accept, returns 6 | as above: `a[E::B]` with two constants is a slice |
| DN-43 | [`dn43_line_comment_accept`](../lexical/dn43_line_comment_accept.yaml) | accept, returns 0 | [Comments and whitespace](../../../spec/v1.0/lexical.md#comments-and-whitespace) |
| DN-43 | [`dn43_block_comment_reject`](../lexical/dn43_block_comment_reject.yaml) | reject, `E1010` at 2:5 | as above: there is no block comment |
| DN-44 | [`dn44_unicode_escape_accept`](../lexical/dn44_unicode_escape_accept.yaml) | accept, returns 0 | [Literals](../../../spec/v1.0/lexical.md#literals): `\u{...}` holds one to six hexadecimal digits |
| DN-44 | [`dn44_unicode_escape_too_big_reject`](../lexical/dn44_unicode_escape_too_big_reject.yaml) | reject, `E1004` | as above |
| DN-44 | [`dn44_unicode_escape_surrogate_reject`](../lexical/dn44_unicode_escape_surrogate_reject.yaml) | reject, `E1004` | as above |
| DN-45 | [`dn45_assert_statement_accept`](dn45_assert_statement_accept.yaml) | accept, returns 2 | [Statement separators](../../../spec/v1.0/language.md#statement-separators) |
| DN-45 | [`dn45_const_without_semicolon_reject`](dn45_const_without_semicolon_reject.yaml) | reject, `E1103` at 1:17 | as above: an item without a block ends with `;` |
| DN-45 | [`dn45_semicolon_after_item_reject`](dn45_semicolon_after_item_reject.yaml) | reject | as above: an item that ends with `}` takes no `;` |
| DN-46 | [`dn46_block_arm_with_comma_accept`](dn46_block_arm_with_comma_accept.yaml) | accept, returns 3 | [Patterns and match](../../../spec/v1.0/language.md#patterns-and-match) |
| DN-46 | [`dn46_block_arm_minus_accept`](dn46_block_arm_minus_accept.yaml) | accept, returns 0 | as above |
| DN-46 | [`dn46_arm_return_accept`](dn46_arm_return_accept.yaml) | accept, returns 9 | as above |
| DN-46 | [`dn46_block_arm_without_comma_reject`](dn46_block_arm_without_comma_reject.yaml) | reject, `E1103` at 3:19 | as above |
| DN-47 | [`dn47_for_range_sum_accept`](dn47_for_range_sum_accept.yaml) | accept, returns 3 | [Loops](../../../spec/v1.0/language.md#loops): counting loops |
| DN-47 | [`dn47_for_range_empty_accept`](dn47_for_range_empty_accept.yaml) | accept, returns 0 | as above |
| DN-47 | [`dn47_range_value_reject`](dn47_range_value_reject.yaml) | reject, `E1101` at 2:14 | as above: a range is not a value |
| DN-48 | [`dn48_negative_minimum_accept`](../lexical/dn48_negative_minimum_accept.yaml) | accept, returns 0 | [Literals](../../../spec/v1.0/lexical.md#literals): no sign in a literal |
| DN-48 | [`dn48_negative_out_of_range_reject`](../lexical/dn48_negative_out_of_range_reject.yaml) | reject, `E2408` | as above |
| DN-48 | [`dn48_unary_plus_reject`](../lexical/dn48_unary_plus_reject.yaml) | reject, `E1101` at 2:13 | as above |
| DN-49 | [`dn49_assignment_statement_accept`](dn49_assignment_statement_accept.yaml) | accept, returns 5 | [Bindings and assignment](../../../spec/v1.0/language.md#bindings-and-assignment) |
| DN-49 | [`dn49_assignment_chain_reject`](dn49_assignment_chain_reject.yaml) | reject, `E1107` at 4:11 | as above |
| DN-49 | [`dn49_assignment_in_condition_reject`](dn49_assignment_in_condition_reject.yaml) | reject, `E1107` at 3:10 | as above |
| DN-50 | [`dn50_same_bit_operator_chain_accept`](dn50_same_bit_operator_chain_accept.yaml) | accept, returns 7 | [Precedence rules](../../../spec/v1.0/language.md#precedence-rules), rule 5 |
| DN-50 | [`dn50_bit_operator_and_comparison_accept`](dn50_bit_operator_and_comparison_accept.yaml) | accept, returns 1 | as above: a bit expression is a comparison operand |
| DN-50 | [`dn50_parentheses_accept`](dn50_parentheses_accept.yaml) | accept, returns 6 | as above |
| DN-50 | [`dn50_or_beside_shift_reject`](dn50_or_beside_shift_reject.yaml) | reject, `E1106` | as above: the message gives both parenthesised forms |
| DN-50 | [`dn50_minus_beside_shift_reject`](dn50_minus_beside_shift_reject.yaml) | reject, `E1106` | as above |
| DN-50 | [`dn50_shift_chain_reject`](dn50_shift_chain_reject.yaml) | reject, `E1106` | as above: shifts do not chain |
| DN-51 | [`dn51_tuple_element_minus_accept`](dn51_tuple_element_minus_accept.yaml) | accept, returns 0 | [Tensor operators and broadcasting](../../../spec/v1.0/language.md#tensor-operators-and-broadcasting) (DN-81 replaces DN-51) |
| DN-51 | [`dn51_dotted_minus_on_tuple_reject`](dn51_dotted_minus_on_tuple_reject.yaml) | reject | as above |
| DN-52 | [`dn52_tuple_index_pair_accept`](../lexical/dn52_tuple_index_pair_accept.yaml) | accept, returns 2 | [Tokens](../../../spec/v1.0/lexical.md#tokens) |
| DN-52 | [`dn52_tuple_index_float_reject`](../lexical/dn52_tuple_index_float_reject.yaml) | reject, `E1005` | as above: after the token `.` a digit run is an integer token |
| DN-52 | [`dn52_spaced_operator_reject`](../lexical/dn52_spaced_operator_reject.yaml) | reject, `E1101` at 3:12 | as above |
| DN-53 | [`dn53_cast_to_alias_then_less_accept`](dn53_cast_to_alias_then_less_accept.yaml) | accept, returns 1 | [Casts](../../../spec/v1.0/language.md#casts) |
| DN-53 | [`dn53_cast_with_type_arguments_reject`](dn53_cast_with_type_arguments_reject.yaml) | reject, `E1101` | as above |
| DN-54 | [`dn54_loop_break_accept`](dn54_loop_break_accept.yaml) | accept, returns 7 | [Loops](../../../spec/v1.0/language.md#loops) |
| DN-54 | [`dn54_loop_as_name_reject`](dn54_loop_as_name_reject.yaml) | reject, `E1007` at 2:9 | as above |
| DN-55 | [`dn55_u8_accept`](../type_checker/dn55_u8_accept.yaml) | accept, returns 255 | [Type formation](../../../spec/v1.0/types.md#type-formation) |
| DN-55 | [`dn55_usize_reject`](../type_checker/dn55_usize_reject.yaml) | reject, `E2002` | as above: a platform width gives one program two sizes |
| DN-55 | [`dn55_u8_range_reject`](../type_checker/dn55_u8_range_reject.yaml) | reject, `E2408` | as above |
| DN-56 | [`dn56_attribute_before_pub_accept`](dn56_attribute_before_pub_accept.yaml) | accept, returns 0 | [Attributes](../../../spec/v1.0/language.md#attributes): one order for every item kind |
| DN-56 | [`dn56_attribute_after_pub_reject`](dn56_attribute_after_pub_reject.yaml) | reject, `E1101` at 1:5 | as above |
| DN-57 | [`dn57_two_axis_index_accept`](../shapes/dn57_two_axis_index_accept.yaml) | accept, returns 0 | [Indexing a tensor](../../../spec/v1.0/shapes.md#indexing-a-tensor) |
| DN-57 | [`dn57_array_repeat_accept`](dn57_array_repeat_accept.yaml) | accept, returns 7 | [`grammar-syntax.ebnf`](../../../spec/v1.0/grammar-syntax.ebnf) `ArrayExpression` |
| DN-57 | [`dn57_const_array_length_accept`](dn57_const_array_length_accept.yaml) | accept, returns 3 | as above: `ArrayLength` |
| DN-57 | [`dn57_too_many_index_items_reject`](../shapes/dn57_too_many_index_items_reject.yaml) | reject, `E3014` | as above |
| DN-57 | [`dn57_repeat_of_handle_reject`](dn57_repeat_of_handle_reject.yaml) | reject, `E2001` | as above: `v` has a value type |
| DN-58 | [`dn58_one_tuple_type_accept`](../type_checker/dn58_one_tuple_type_accept.yaml) | accept, returns 5 | [Type formation](../../../spec/v1.0/types.md#type-formation) |
| DN-58 | [`dn58_parenthesised_type_reject`](../type_checker/dn58_parenthesised_type_reject.yaml) | reject, `E1101` | as above: the message names `T` and `(T,)` |
| DN-58 | [`dn58_unit_written_as_parentheses_reject`](../type_checker/dn58_unit_written_as_parentheses_reject.yaml) | reject | as above |
| DN-59 | [`dn59_parenthesised_tuple_type_accept`](../type_checker/dn59_parenthesised_tuple_type_accept.yaml) | accept, returns 1 | [Type formation](../../../spec/v1.0/types.md#type-formation) |
| DN-59 | [`dn59_function_type_reject`](../type_checker/dn59_function_type_reject.yaml) | reject, `E2037` | as above |
| DN-60 | [`dn60_contextual_word_as_name_accept`](../lexical/dn60_contextual_word_as_name_accept.yaml) | accept, returns 1 | [Keywords](../../../spec/v1.0/lexical.md#keywords) |
| DN-60 | [`dn60_mut_as_name_reject`](../lexical/dn60_mut_as_name_reject.yaml) | reject, `E1007` at 2:13 | as above |
| DN-60 | [`dn60_assert_as_function_name_reject`](../lexical/dn60_assert_as_function_name_reject.yaml) | reject, `E1007` at 1:4 | as above |
| DN-61 | [`dn61_ascii_comment_accept`](../lexical/dn61_ascii_comment_accept.yaml) | accept, returns 0 | [Source text](../../../spec/v1.0/lexical.md#source-text) |
| DN-61 | [`dn61_bidi_override_in_comment_reject`](../lexical/dn61_bidi_override_in_comment_reject.yaml) | reject, `E1008` at 2:10 | as above: forbidden code points |
| DN-61 | [`dn61_nul_in_comment_reject`](../lexical/dn61_nul_in_comment_reject.yaml) | reject, `E1008` at 2:10 | as above |
| DN-61 | [`dn61_non_ascii_identifier_reject`](../lexical/dn61_non_ascii_identifier_reject.yaml) | reject, `E1002` at 2:9 | [Identifiers](../../../spec/v1.0/lexical.md#identifiers) |
| DN-61 | [`dn61_lone_carriage_return_reject`](../lexical/dn61_lone_carriage_return_reject.yaml) | reject | [Source text](../../../spec/v1.0/lexical.md#source-text) |
| DN-62 | [`dn62_line_strings_accept`](../lexical/dn62_line_strings_accept.yaml) | accept, returns 0 | [Literals](../../../spec/v1.0/lexical.md#literals): line strings |
| DN-62 | [`dn62_line_end_in_string_reject`](../lexical/dn62_line_end_in_string_reject.yaml) | reject, `E1003` at 2:13 | as above |
| DN-62 | [`dn62_raw_tab_in_string_reject`](../lexical/dn62_raw_tab_in_string_reject.yaml) | reject, `E1008` at 2:15 | as above: the escape `\t` writes a tab |
| DN-76 | [`dn76_fault_d01_missing_close_brace_eof_reject`](dn76_fault_d01_missing_close_brace_eof_reject.yaml) | reject, `E1102` at 4:1 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d02_missing_close_brace_if_reject`](dn63_fault_d02_missing_close_brace_if_reject.yaml) | reject | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d03_missing_open_brace_fn_reject`](dn63_fault_d03_missing_open_brace_fn_reject.yaml) | reject, `E1101` at 1:17 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d04_extra_close_brace_reject`](dn63_fault_d04_extra_close_brace_reject.yaml) | reject, `E1101` at 4:1 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d05_missing_close_paren_call_reject`](dn63_fault_d05_missing_close_paren_call_reject.yaml) | reject, `E1102` at 7:20 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d06_missing_open_paren_fn_reject`](dn63_fault_d06_missing_open_paren_fn_reject.yaml) | reject, `E1101` at 1:8 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d07_missing_close_bracket_reject`](dn63_fault_d07_missing_close_bracket_reject.yaml) | reject, `E1102` at 3:15 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d08_missing_close_brace_match_reject`](dn63_fault_d08_missing_close_brace_match_reject.yaml) | reject, `E1102` at 6:5 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d09_missing_semi_let_reject`](dn63_fault_d09_missing_semi_let_reject.yaml) | reject, `E1103` at 2:14 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d10_missing_semi_return_brace_reject`](dn63_fault_d10_missing_semi_return_brace_reject.yaml) | reject, `E1103` at 2:13 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d11_missing_semi_expr_stmt_reject`](dn63_fault_d11_missing_semi_expr_stmt_reject.yaml) | reject, `E1103` at 7:14 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d12_missing_semi_break_reject`](dn63_fault_d12_missing_semi_break_reject.yaml) | reject, `E1103` at 3:14 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d13_missing_semi_type_alias_reject`](dn63_fault_d13_missing_semi_type_alias_reject.yaml) | reject, `E1103` at 1:13 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d14_missing_semi_import_reject`](dn63_fault_d14_missing_semi_import_reject.yaml) | reject, `E1103` at 1:14 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d15_missing_comma_fields_reject`](dn63_fault_d15_missing_comma_fields_reject.yaml) | reject, `E1103` at 2:11 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d16_missing_comma_args_reject`](dn63_fault_d16_missing_comma_args_reject.yaml) | reject, `E1103` at 7:17 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d17_missing_comma_match_arm_reject`](dn63_fault_d17_missing_comma_match_arm_reject.yaml) | reject, `E1103` at 4:15 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d18_wrong_eqeq_in_let_reject`](dn63_fault_d18_wrong_eqeq_in_let_reject.yaml) | reject, `E1101` at 2:11 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d19_wrong_fat_arrow_ret_reject`](dn63_fault_d19_wrong_fat_arrow_ret_reject.yaml) | reject, `E1101` at 1:14 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d20_wrong_missing_type_after_colon_reject`](dn63_fault_d20_wrong_missing_type_after_colon_reject.yaml) | reject, `E1101` at 2:12 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d21_wrong_do_keyword_reject`](dn64_fault_d21_wrong_do_keyword_reject.yaml) | reject, `E1105` at 3:17 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d22_wrong_param_no_colon_reject`](dn63_fault_d22_wrong_param_no_colon_reject.yaml) | reject, `E1101` at 1:7 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d24_wrong_double_operator_reject`](dn63_fault_d24_wrong_double_operator_reject.yaml) | reject, `E1101` at 2:16 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d25_wrong_elif_reject`](dn64_fault_d25_wrong_elif_reject.yaml) | reject, `E1105` at 5:7 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d26_unclosed_string_reject`](dn63_fault_d26_unclosed_string_reject.yaml) | reject, `E1003` at 2:13 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d27_unclosed_block_comment_reject`](dn63_fault_d27_unclosed_block_comment_reject.yaml) | reject, `E1010` at 2:5 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d28_bad_escape_reject`](dn63_fault_d28_bad_escape_reject.yaml) | reject, `E1004` at 2:15 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d29_newline_in_string_reject`](dn63_fault_d29_newline_in_string_reject.yaml) | reject, `E1003` at 2:13 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d30_misspelled_fn_reject`](dn64_fault_d30_misspelled_fn_reject.yaml) | reject, `E1104` at 1:1 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d31_misspelled_return_reject`](dn64_fault_d31_misspelled_return_reject.yaml) | reject, `E1104` at 2:5 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d32_misspelled_let_reject`](dn64_fault_d32_misspelled_let_reject.yaml) | reject, `E1104` at 2:5 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d33_misspelled_while_reject`](dn64_fault_d33_misspelled_while_reject.yaml) | reject, `E1104` at 2:5 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d34_misspelled_else_reject`](dn64_fault_d34_misspelled_else_reject.yaml) | reject, `E1104` at 5:7 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-64 | [`dn64_fault_d35_misspelled_struct_reject`](dn64_fault_d35_misspelled_struct_reject.yaml) | reject, `E1104` at 1:1 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d36_stray_dollar_reject`](dn63_fault_d36_stray_dollar_reject.yaml) | reject, `E1002` at 2:15 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d37_stray_backtick_reject`](dn63_fault_d37_stray_backtick_reject.yaml) | reject, `E1002` at 2:13 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d38_stray_unicode_quote_reject`](dn63_fault_d38_stray_unicode_quote_reject.yaml) | reject, `E1002` at 2:13 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d39_stray_question_reject`](dn63_fault_d39_stray_question_reject.yaml) | reject, `E1105` at 2:14 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-63 | [`dn63_fault_d40_tensor_missing_comma_reject`](dn63_fault_d40_tensor_missing_comma_reject.yaml) | reject, `E1103` at 1:19 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors): one diagnostic at the first fault |
| DN-47 | [`dn47_fault_d23_range_for_accept`](dn47_fault_d23_range_for_accept.yaml) | accept, returns 1 | [Loops](../../../spec/v1.0/language.md#loops): counting loops |
| DN-64 | [`dn64_habit_macro_call_reject`](dn64_habit_macro_call_reject.yaml) | reject, `E1105` at 2:13 | [E1105](../../../spec/v1.0/errors.md#e1105-form-that-mind-writes-another-way): the table of habit forms |
| DN-64 | [`dn64_habit_reference_type_reject`](dn64_habit_reference_type_reject.yaml) | reject, `E1105` at 1:9 | as above |
| DN-64 | [`dn64_habit_closure_bar_reject`](dn64_habit_closure_bar_reject.yaml) | reject, `E1105` at 2:13 | as above |
| DN-64 | [`dn64_habit_if_let_reject`](dn64_habit_if_let_reject.yaml) | reject, `E1105` at 3:5 | as above |
| DN-64 | [`dn64_habit_postfix_question_reject`](dn64_habit_postfix_question_reject.yaml) | reject, `E1105` at 6:16 | as above |
| DN-64 | [`dn64_habit_use_reject`](dn64_habit_use_reject.yaml) | reject, `E1105` at 1:1 | as above: `use` is a repair row to `import` |
| DN-64 | [`dn64_name_near_keyword_accept`](dn64_name_near_keyword_accept.yaml) | accept, returns 1 | [`E1104`](../../../spec/v1.0/errors.md#e1104-misspelled-keyword) |
| DN-63 | [`dn63_one_diagnostic_for_each_item_reject`](dn63_one_diagnostic_for_each_item_reject.yaml) | reject, `E1101` at 2:18, count 3 | [Diagnostics](../../../spec/v1.0/lexical.md#diagnostics): one diagnostic for each top-level item |
| DN-63 | [`dn63_valid_program_accept`](dn63_valid_program_accept.yaml) | accept, returns 2 | [E1xxx](../../../spec/v1.0/errors.md#e1xxx-lexical-and-syntax-errors) |
| DN-76 | [`dn76_head_identifier_then_parentheses_accept`](dn76_head_identifier_then_parentheses_accept.yaml) | accept, returns 4 | [Diagnostic requirements](../../../spec/v1.0/errors.md#diagnostic-requirements) |
| DN-65 | [`dn65_const_expression_accept`](dn65_const_expression_accept.yaml) | accept, returns 5 | [Module level](../../../spec/v1.0/language.md#module-level) |
| DN-65 | [`dn65_let_at_module_level_reject`](dn65_let_at_module_level_reject.yaml) | reject, `E1101` at 1:1 | as above |
| DN-65 | [`dn65_const_with_call_reject`](dn65_const_with_call_reject.yaml) | reject, `E2001` | as above |
| DN-65 | [`dn65_build_without_main_reject`](dn65_build_without_main_reject.yaml) | reject, `E2403` | as above |
| DN-65 | [`dn65_binding_hides_import_reject`](dn65_binding_hides_import_reject.yaml) | reject, `E2730` | as above |
| DN-65 | [`dn65_module_path_colon_reject`](../type_checker/dn65_module_path_colon_reject.yaml) | reject, `E2731` at 8:12 | as above: `.` follows a module |
| DN-66 | [`dn66_or_pattern_accept`](../type_checker/dn66_or_pattern_accept.yaml) | accept, returns 10 | [Patterns and match](../../../spec/v1.0/language.md#patterns-and-match) |
| DN-66 | [`dn66_nested_let_pattern_accept`](../type_checker/dn66_nested_let_pattern_accept.yaml) | accept, returns 6 | as above |
| DN-66 | [`dn66_alternatives_bind_differently_reject`](../type_checker/dn66_alternatives_bind_differently_reject.yaml) | reject, `E2313` | as above |
| DN-66 | [`dn66_refutable_let_pattern_reject`](../type_checker/dn66_refutable_let_pattern_reject.yaml) | reject, `E2310` at 3:9 | as above: the pattern of a `let` is irrefutable |
| DN-66 | [`dn66_refutable_for_pattern_reject`](../type_checker/dn66_refutable_for_pattern_reject.yaml) | reject, `E2310` at 3:9 | as above: the pattern of a `for` is irrefutable |
| DN-66 | [`dn66_pattern_parameter_reject`](dn66_pattern_parameter_reject.yaml) | reject, `E1101` at 1:6 | as above: a parameter is a name or `_` |
| DN-66 | [`dn66_leading_bar_reject`](dn66_leading_bar_reject.yaml) | reject, `E1101` at 4:9 | as above: a pattern has no leading `\|` |
| DN-67 | [`dn67_predeclared_variants_accept`](../type_checker/dn67_predeclared_variants_accept.yaml) | accept, returns 1 | [Patterns and match](../../../spec/v1.0/language.md#patterns-and-match) |
| DN-67 | [`dn67_binding_named_none_reject`](../type_checker/dn67_binding_named_none_reject.yaml) | reject, `E2042` | as above |
| DN-67 | [`dn67_qualified_variant_reject`](../type_checker/dn67_qualified_variant_reject.yaml) | reject, `E2002` | as above |
| DN-68 | [`dn68_name_that_starts_with_where_accept`](../lexical/dn68_name_that_starts_with_where_accept.yaml) | accept, returns 2 | [Keywords](../../../spec/v1.0/lexical.md#keywords): `where` is reserved |
| DN-68 | [`dn68_where_as_name_reject`](../lexical/dn68_where_as_name_reject.yaml) | reject, `E1007` at 2:9 | as above |
| DN-69 | [`dn69_parentheses_254_accept`](dn69_parentheses_254_accept.yaml) | accept, returns 1 | [Nesting depth](../../../spec/v1.0/language.md#nesting-depth): at least 256 |
| DN-69 | [`dn69_long_chain_accept`](dn69_long_chain_accept.yaml) | accept, returns 1000 | as above |
| DN-70 | [`dn70_index_with_cast_accept`](../type_checker/dn70_index_with_cast_accept.yaml) | accept, returns 2 | [Tuple index](../../../spec/v1.0/language.md#tuple-index) |
| DN-70 | [`dn70_float_index_reject`](../type_checker/dn70_float_index_reject.yaml) | reject, `E2005` | as above |
| DN-71 | [`dn71_const_dimension_accept`](../shapes/dn71_const_dimension_accept.yaml) | accept, returns 0 | [The tensor type](../../../spec/v1.0/shapes.md#the-tensor-type) |
| DN-71 | [`dn71_rank_zero_is_scalar_accept`](../shapes/dn71_rank_zero_is_scalar_accept.yaml) | accept, returns 0 | as above |
| DN-71 | [`dn71_tensor_equality_accept`](../shapes/dn71_tensor_equality_accept.yaml) | accept, returns 0 | [Comparison of tensors](../../../spec/v1.0/shapes.md#comparison-of-tensors) |
| DN-71 | [`dn71_unknown_dimension_reject`](../shapes/dn71_unknown_dimension_reject.yaml) | reject, `E3013` | [The tensor type](../../../spec/v1.0/shapes.md#the-tensor-type) |
| DN-71 | [`dn71_dimension_too_large_reject`](../shapes/dn71_dimension_too_large_reject.yaml) | reject, `E3012` | as above |
| DN-71 | [`dn71_question_dimension_reject`](../shapes/dn71_question_dimension_reject.yaml) | reject, `E1105` at 1:22 | as above |
| DN-71 | [`dn71_tensor_less_reject`](../shapes/dn71_tensor_less_reject.yaml) | reject, `E2008` | [Comparison of tensors](../../../spec/v1.0/shapes.md#comparison-of-tensors) |
| DN-72 | [`dn72_named_argument_colon_accept`](dn72_named_argument_colon_accept.yaml) | accept, returns 0 | [Tensor operations](../../../spec/v1.0/language.md#tensor-operations) |
| DN-72 | [`dn72_named_argument_equals_reject`](dn72_named_argument_equals_reject.yaml) | reject, `E1105` at 2:29 | as above |
| DN-73 | [`dn73_cast_to_primitive_accept`](dn73_cast_to_primitive_accept.yaml) | accept, returns 3 | [Casts](../../../spec/v1.0/language.md#casts) |
| DN-73 | [`dn73_reference_reject`](dn73_reference_reject.yaml) | reject, `E1101` at 3:13 | [Operand and condition types](../../../spec/v1.0/language.md#operand-and-condition-types) |
| DN-73 | [`dn73_cast_to_parenthesised_type_reject`](dn73_cast_to_parenthesised_type_reject.yaml) | reject, `E1101` at 2:18 | [Casts](../../../spec/v1.0/language.md#casts) |
| DN-75 | [`dn75_tuple_not_comma_operator_accept`](dn75_tuple_not_comma_operator_accept.yaml) | accept, returns 2 | [Operator precedence and associativity](../../../spec/v1.0/language.md#operator-precedence-and-associativity) |
| DN-75 | [`dn75_comma_operator_reject`](dn75_comma_operator_reject.yaml) | reject, `E1101` at 2:13 | as above |
| DN-77 | [`dn77_doc_comment_accept`](../lexical/dn77_doc_comment_accept.yaml) | accept, returns 2 | [Comments and whitespace](../../../spec/v1.0/lexical.md#comments-and-whitespace) |
| DN-77 | [`dn77_shebang_accept`](../lexical/dn77_shebang_accept.yaml) | accept, returns 0 | [Source text](../../../spec/v1.0/lexical.md#source-text): shebang |
| DN-77 | [`dn77_doc_comment_before_statement_reject`](../lexical/dn77_doc_comment_before_statement_reject.yaml) | reject | [Comments and whitespace](../../../spec/v1.0/lexical.md#comments-and-whitespace) |
| DN-78 | [`dn78_tuple_index_accept`](dn78_tuple_index_accept.yaml) | accept, returns 5 | [Tuple index](../../../spec/v1.0/language.md#tuple-index) |
| DN-78 | [`dn78_tuple_index_leading_zero_reject`](dn78_tuple_index_leading_zero_reject.yaml) | reject, `E2404` | as above |
| DN-79 | [`dn79_compound_shift_accept`](dn79_compound_shift_accept.yaml) | accept, returns 4 | [Bindings and assignment](../../../spec/v1.0/language.md#bindings-and-assignment) |
| DN-79 | [`dn79_lone_semicolon_reject`](dn79_lone_semicolon_reject.yaml) | reject | [Statement separators](../../../spec/v1.0/language.md#statement-separators) |
| DN-79 | [`dn79_split_compound_operator_reject`](dn79_split_compound_operator_reject.yaml) | reject, `E1101` at 3:9 | [Bindings and assignment](../../../spec/v1.0/language.md#bindings-and-assignment) |
| DN-80 | [`dn80_closed_range_accept`](dn80_closed_range_accept.yaml) | accept, returns 6 | [Loops](../../../spec/v1.0/language.md#loops) |
| DN-80 | [`dn80_closed_range_to_top_accept`](dn80_closed_range_to_top_accept.yaml) | accept, returns 6 | as above |
| DN-80 | [`dn80_range_pattern_accept`](dn80_range_pattern_accept.yaml) | accept, returns 1 | [Patterns and match](../../../spec/v1.0/language.md#patterns-and-match) |
| DN-80 | [`dn80_half_open_range_pattern_reject`](dn80_half_open_range_pattern_reject.yaml) | reject, `E1101` at 3:10 | as above |
| DN-80 | [`dn80_closed_range_value_reject`](dn80_closed_range_value_reject.yaml) | reject, `E1101` at 2:14 | [Loops](../../../spec/v1.0/language.md#loops) |
| DN-81 | [`dn81_dotted_broadcast_accept`](../shapes/dn81_dotted_broadcast_accept.yaml) | accept, returns 0 | [Elementwise binary](../../../spec/v1.0/shapes.md#elementwise-binary) |
| DN-81 | [`dn81_plain_same_shape_accept`](../shapes/dn81_plain_same_shape_accept.yaml) | accept, returns 0 | as above |
| DN-81 | [`dn81_plain_different_shapes_reject`](../shapes/dn81_plain_different_shapes_reject.yaml) | reject, `E3015` at 2:16 | as above |
| DN-81 | [`dn81_dotted_on_scalars_reject`](../shapes/dn81_dotted_on_scalars_reject.yaml) | reject, `E3016` at 4:14 | as above |
| DN-81 | [`dn81_dotted_same_shape_reject`](../shapes/dn81_dotted_same_shape_reject.yaml) | reject, `E3016` at 2:14 | as above: a dotted operator expands an operand |
| DN-81 | [`dn81_dotted_scalar_operand_reject`](../shapes/dn81_dotted_scalar_operand_reject.yaml) | reject, `E3016` at 2:14 | as above: a scalar extends with the plain operator |
| DN-82 | [`dn82_gradient_attribute_accept`](../autodiff/dn82_gradient_attribute_accept.yaml) | accept, returns 0 | [Source form: the gradient attribute](../../../spec/v1.0/autodiff.md#source-form-the-gradient-attribute) |
| DN-82 | [`dn82_diff_type_reject`](../autodiff/dn82_diff_type_reject.yaml) | reject, `E1105` at 1:9 | as above: `diff T` is not in Core v1 |
| DN-82 | [`dn82_gradient_of_unknown_parameter_reject`](../autodiff/dn82_gradient_of_unknown_parameter_reject.yaml) | reject | as above |
| DN-82 | [`dn82_gradient_of_integer_result_reject`](../autodiff/dn82_gradient_of_integer_result_reject.yaml) | reject | as above: the result of `f` is a floating-point scalar |
| DN-83 | [`dn83_pub_item_accept`](dn83_pub_item_accept.yaml) | accept, returns 5 | [Visibility](../../../spec/v1.0/language.md#visibility) |
| DN-83 | [`dn83_export_list_reject`](dn83_export_list_reject.yaml) | reject | as above: `export` is reserved with no production |
| DN-83 | [`dn83_pub_as_name_reject`](dn83_pub_as_name_reject.yaml) | reject, `E1007` at 2:9 | as above |
| DN-89 | [`dn89_glob_import_reject`](dn89_glob_import_reject.yaml) | reject, `E1101` at 1:12 | [Module level](../../../spec/v1.0/language.md#module-level): no glob import |
| DN-84 | [`dn84_tool_attribute_listed_accept`](dn84_tool_attribute_listed_accept.yaml) | accept, returns 1 | [Attributes](../../../spec/v1.0/language.md#attributes): tool attributes; a gap of the reference |
| DN-84 | [`dn84_three_segment_name_reject`](dn84_three_segment_name_reject.yaml) | reject, `E1101` at 1:6 | [Attributes](../../../spec/v1.0/language.md#attributes): tool attributes |
| DN-84 | [`dn84_tool_attribute_not_listed_reject`](dn84_tool_attribute_not_listed_reject.yaml) | reject | as above |
| DN-84 | [`dn84_unknown_one_segment_name_reject`](dn84_unknown_one_segment_name_reject.yaml) | reject, `E2502` | as above |
| DN-85 | [`dn85_vec_accept`](../type_checker/dn85_vec_accept.yaml) | accept, returns 2 | [Type formation](../../../spec/v1.0/types.md#type-formation): type names |
| DN-85 | [`dn85_bare_vec_reject`](../type_checker/dn85_bare_vec_reject.yaml) | reject | as above |
| DN-85 | [`dn85_array_generic_reject`](../type_checker/dn85_array_generic_reject.yaml) | reject | as above |
| DN-85 | [`dn85_lower_case_string_reject`](../type_checker/dn85_lower_case_string_reject.yaml) | reject | as above |
