// pythonGrammar.ts
//
// Railroad diagram factories for Python 3.14 PEG grammar.
// Uses @prantlf/railroad-diagrams library for SVG generation.

import rr from "@prantlf/railroad-diagrams";

const {
  Diagram,
  Sequence,
  Choice,
  Optional,
  ZeroOrMore,
  OneOrMore,
  Terminal,
  NonTerminal,
  Comment,
  Skip,
  Group,
} = rr;

// Helper functions for readability
const T = (text: string) => Terminal(text);
const NT = (name: string) => NonTerminal(name);
const Opt = Optional;
const Star = ZeroOrMore;
const Plus = OneOrMore;
const Seq = Sequence;
const Or = Choice;

// Rule name type
export type RuleName = string;

// Map of all diagram factories
const rules = new Map<RuleName, () => ReturnType<typeof Diagram>>();

// ============================================================================
// STARTING RULES
// ============================================================================

rules.set("file", () =>
  Diagram(
    Sequence(
      Optional(NT("statements")),
      T("ENDMARKER")
    )
  )
);

rules.set("interactive", () =>
  Diagram(
    NT("statement_newline")
  )
);

rules.set("eval", () =>
  Diagram(
    Sequence(
      NT("expressions"),
      ZeroOrMore(T("NEWLINE")),
      T("ENDMARKER")
    )
  )
);

rules.set("func_type", () =>
  Diagram(
    Sequence(
      T("("),
      Optional(NT("type_expressions")),
      T(")"),
      T("->"),
      NT("expression"),
      ZeroOrMore(T("NEWLINE")),
      T("ENDMARKER")
    )
  )
);

// ============================================================================
// GENERAL STATEMENTS
// ============================================================================

rules.set("statements", () =>
  Diagram(
    OneOrMore(NT("statement"))
  )
);

rules.set("statement", () =>
  Diagram(
    Choice(0,
      NT("compound_stmt"),
      NT("simple_stmts")
    )
  )
);

rules.set("single_compound_stmt", () =>
  Diagram(
    NT("compound_stmt")
  )
);

rules.set("statement_newline", () =>
  Diagram(
    Choice(0,
      Sequence(NT("single_compound_stmt"), T("NEWLINE")),
      NT("simple_stmts"),
      T("NEWLINE"),
      T("ENDMARKER")
    )
  )
);

rules.set("simple_stmts", () =>
  Diagram(
    Choice(0,
      Sequence(NT("simple_stmt"), T("NEWLINE")),
      Sequence(
        OneOrMore(NT("simple_stmt"), T(";")),
        Optional(T(";")),
        T("NEWLINE")
      )
    )
  )
);

rules.set("simple_stmt", () =>
  Diagram(
    Choice(0,
      NT("assignment"),
      NT("type_alias"),
      NT("star_expressions"),
      NT("return_stmt"),
      NT("import_stmt"),
      NT("raise_stmt"),
      NT("pass_stmt"),
      NT("del_stmt"),
      NT("yield_stmt"),
      NT("assert_stmt"),
      NT("break_stmt"),
      NT("continue_stmt"),
      NT("global_stmt"),
      NT("nonlocal_stmt")
    )
  )
);

rules.set("compound_stmt", () =>
  Diagram(
    Choice(0,
      NT("function_def"),
      NT("if_stmt"),
      NT("class_def"),
      NT("with_stmt"),
      NT("for_stmt"),
      NT("try_stmt"),
      NT("while_stmt"),
      NT("match_stmt")
    )
  )
);

// ============================================================================
// SIMPLE STATEMENTS
// ============================================================================

rules.set("assignment", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("NAME"),
        T(":"),
        NT("expression"),
        Optional(Sequence(T("="), NT("annotated_rhs")))
      ),
      Sequence(
        Choice(0,
          Sequence(T("("), NT("single_target"), T(")")),
          NT("single_subscript_attribute_target")
        ),
        T(":"),
        NT("expression"),
        Optional(Sequence(T("="), NT("annotated_rhs")))
      ),
      Sequence(
        OneOrMore(Sequence(NT("star_targets"), T("="))),
        NT("annotated_rhs"),
        Optional(T("TYPE_COMMENT"))
      ),
      Sequence(
        NT("single_target"),
        NT("augassign"),
        NT("annotated_rhs")
      )
    )
  )
);

rules.set("annotated_rhs", () =>
  Diagram(
    Choice(0,
      NT("yield_expr"),
      NT("star_expressions")
    )
  )
);

rules.set("augassign", () =>
  Diagram(
    Choice(0,
      T("+="),
      T("-="),
      T("*="),
      T("@="),
      T("/="),
      T("%="),
      T("&="),
      T("|="),
      T("^="),
      T("<<="),
      T(">>="),
      T("**="),
      T("//=")
    )
  )
);

rules.set("return_stmt", () =>
  Diagram(
    Sequence(
      T("return"),
      Optional(NT("star_expressions"))
    )
  )
);

rules.set("raise_stmt", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("raise"),
        NT("expression"),
        Optional(Sequence(T("from"), NT("expression")))
      ),
      T("raise")
    )
  )
);

rules.set("pass_stmt", () =>
  Diagram(T("pass"))
);

rules.set("break_stmt", () =>
  Diagram(T("break"))
);

rules.set("continue_stmt", () =>
  Diagram(T("continue"))
);

rules.set("global_stmt", () =>
  Diagram(
    Sequence(
      T("global"),
      OneOrMore(T("NAME"), T(","))
    )
  )
);

rules.set("nonlocal_stmt", () =>
  Diagram(
    Sequence(
      T("nonlocal"),
      OneOrMore(T("NAME"), T(","))
    )
  )
);

rules.set("del_stmt", () =>
  Diagram(
    Sequence(
      T("del"),
      NT("del_targets")
    )
  )
);

rules.set("yield_stmt", () =>
  Diagram(NT("yield_expr"))
);

rules.set("assert_stmt", () =>
  Diagram(
    Sequence(
      T("assert"),
      NT("expression"),
      Optional(Sequence(T(","), NT("expression")))
    )
  )
);

// ============================================================================
// IMPORT STATEMENTS
// ============================================================================

rules.set("import_stmt", () =>
  Diagram(
    Choice(0,
      NT("import_name"),
      NT("import_from")
    )
  )
);

rules.set("import_name", () =>
  Diagram(
    Sequence(
      T("import"),
      NT("dotted_as_names")
    )
  )
);

rules.set("import_from", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("from"),
        ZeroOrMore(Choice(0, T("."), T("..."))),
        NT("dotted_name"),
        T("import"),
        NT("import_from_targets")
      ),
      Sequence(
        T("from"),
        OneOrMore(Choice(0, T("."), T("..."))),
        T("import"),
        NT("import_from_targets")
      )
    )
  )
);

rules.set("import_from_targets", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("("),
        NT("import_from_as_names"),
        Optional(T(",")),
        T(")")
      ),
      NT("import_from_as_names"),
      T("*")
    )
  )
);

rules.set("import_from_as_names", () =>
  Diagram(
    OneOrMore(NT("import_from_as_name"), T(","))
  )
);

rules.set("import_from_as_name", () =>
  Diagram(
    Sequence(
      T("NAME"),
      Optional(Sequence(T("as"), T("NAME")))
    )
  )
);

rules.set("dotted_as_names", () =>
  Diagram(
    OneOrMore(NT("dotted_as_name"), T(","))
  )
);

rules.set("dotted_as_name", () =>
  Diagram(
    Sequence(
      NT("dotted_name"),
      Optional(Sequence(T("as"), T("NAME")))
    )
  )
);

rules.set("dotted_name", () =>
  Diagram(
    Choice(0,
      Sequence(NT("dotted_name"), T("."), T("NAME")),
      T("NAME")
    )
  )
);

// ============================================================================
// COMPOUND STATEMENTS - Common Elements
// ============================================================================

rules.set("block", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("NEWLINE"),
        T("INDENT"),
        NT("statements"),
        T("DEDENT")
      ),
      NT("simple_stmts")
    )
  )
);

rules.set("decorators", () =>
  Diagram(
    OneOrMore(
      Sequence(T("@"), NT("named_expression"), T("NEWLINE"))
    )
  )
);

// ============================================================================
// CLASS DEFINITIONS
// ============================================================================

rules.set("class_def", () =>
  Diagram(
    Choice(0,
      Sequence(NT("decorators"), NT("class_def_raw")),
      NT("class_def_raw")
    )
  )
);

rules.set("class_def_raw", () =>
  Diagram(
    Sequence(
      T("class"),
      T("NAME"),
      Optional(NT("type_params")),
      Optional(Sequence(T("("), Optional(NT("arguments")), T(")"))),
      T(":"),
      NT("block")
    )
  )
);

// ============================================================================
// FUNCTION DEFINITIONS
// ============================================================================

rules.set("function_def", () =>
  Diagram(
    Choice(0,
      Sequence(NT("decorators"), NT("function_def_raw")),
      NT("function_def_raw")
    )
  )
);

rules.set("function_def_raw", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("def"),
        T("NAME"),
        Optional(NT("type_params")),
        T("("),
        Optional(NT("params")),
        T(")"),
        Optional(Sequence(T("->"), NT("expression"))),
        T(":"),
        Optional(NT("func_type_comment")),
        NT("block")
      ),
      Sequence(
        T("async"),
        T("def"),
        T("NAME"),
        Optional(NT("type_params")),
        T("("),
        Optional(NT("params")),
        T(")"),
        Optional(Sequence(T("->"), NT("expression"))),
        T(":"),
        Optional(NT("func_type_comment")),
        NT("block")
      )
    )
  )
);

rules.set("func_type_comment", () =>
  Diagram(
    Choice(0,
      Sequence(T("NEWLINE"), T("TYPE_COMMENT")),
      T("TYPE_COMMENT")
    )
  )
);

// ============================================================================
// FUNCTION PARAMETERS
// ============================================================================

rules.set("params", () =>
  Diagram(NT("parameters"))
);

rules.set("parameters", () =>
  Diagram(
    Choice(0,
      Sequence(
        NT("slash_no_default"),
        ZeroOrMore(NT("param_no_default")),
        ZeroOrMore(NT("param_with_default")),
        Optional(NT("star_etc"))
      ),
      Sequence(
        NT("slash_with_default"),
        ZeroOrMore(NT("param_with_default")),
        Optional(NT("star_etc"))
      ),
      Sequence(
        OneOrMore(NT("param_no_default")),
        ZeroOrMore(NT("param_with_default")),
        Optional(NT("star_etc"))
      ),
      Sequence(
        OneOrMore(NT("param_with_default")),
        Optional(NT("star_etc"))
      ),
      NT("star_etc")
    )
  )
);

rules.set("slash_no_default", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("param_no_default")),
      T("/"),
      Choice(0, T(","), Comment("&')'"))
    )
  )
);

rules.set("slash_with_default", () =>
  Diagram(
    Sequence(
      ZeroOrMore(NT("param_no_default")),
      OneOrMore(NT("param_with_default")),
      T("/"),
      Choice(0, T(","), Comment("&')'"))
    )
  )
);

rules.set("star_etc", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("*"),
        NT("param_no_default"),
        ZeroOrMore(NT("param_maybe_default")),
        Optional(NT("kwds"))
      ),
      Sequence(
        T("*"),
        NT("param_no_default_star_annotation"),
        ZeroOrMore(NT("param_maybe_default")),
        Optional(NT("kwds"))
      ),
      Sequence(
        T("*"),
        T(","),
        OneOrMore(NT("param_maybe_default")),
        Optional(NT("kwds"))
      ),
      NT("kwds")
    )
  )
);

rules.set("kwds", () =>
  Diagram(
    Sequence(T("**"), NT("param_no_default"))
  )
);

rules.set("param_no_default", () =>
  Diagram(
    Choice(0,
      Sequence(NT("param"), T(","), Optional(T("TYPE_COMMENT"))),
      Sequence(NT("param"), Optional(T("TYPE_COMMENT")), Comment("&')'"))
    )
  )
);

rules.set("param_no_default_star_annotation", () =>
  Diagram(
    Choice(0,
      Sequence(NT("param_star_annotation"), T(","), Optional(T("TYPE_COMMENT"))),
      Sequence(NT("param_star_annotation"), Optional(T("TYPE_COMMENT")), Comment("&')'"))
    )
  )
);

rules.set("param_with_default", () =>
  Diagram(
    Choice(0,
      Sequence(NT("param"), NT("default"), T(","), Optional(T("TYPE_COMMENT"))),
      Sequence(NT("param"), NT("default"), Optional(T("TYPE_COMMENT")), Comment("&')'"))
    )
  )
);

rules.set("param_maybe_default", () =>
  Diagram(
    Choice(0,
      Sequence(NT("param"), Optional(NT("default")), T(","), Optional(T("TYPE_COMMENT"))),
      Sequence(NT("param"), Optional(NT("default")), Optional(T("TYPE_COMMENT")), Comment("&')'"))
    )
  )
);

rules.set("param", () =>
  Diagram(
    Sequence(T("NAME"), Optional(NT("annotation")))
  )
);

rules.set("param_star_annotation", () =>
  Diagram(
    Sequence(T("NAME"), NT("star_annotation"))
  )
);

rules.set("annotation", () =>
  Diagram(
    Sequence(T(":"), NT("expression"))
  )
);

rules.set("star_annotation", () =>
  Diagram(
    Sequence(T(":"), NT("star_expression"))
  )
);

rules.set("default", () =>
  Diagram(
    Sequence(T("="), NT("expression"))
  )
);

// ============================================================================
// CONTROL FLOW - If Statement
// ============================================================================

rules.set("if_stmt", () =>
  Diagram(
    Sequence(
      T("if"),
      NT("named_expression"),
      T(":"),
      NT("block"),
      Optional(NT("elif_stmt")),
      Optional(NT("else_block"))
    )
  )
);

rules.set("elif_stmt", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("elif"),
        NT("named_expression"),
        T(":"),
        NT("block"),
        NT("elif_stmt")
      ),
      Sequence(
        T("elif"),
        NT("named_expression"),
        T(":"),
        NT("block"),
        Optional(NT("else_block"))
      )
    )
  )
);

rules.set("else_block", () =>
  Diagram(
    Sequence(T("else"), T(":"), NT("block"))
  )
);

// ============================================================================
// CONTROL FLOW - While Statement
// ============================================================================

rules.set("while_stmt", () =>
  Diagram(
    Sequence(
      T("while"),
      NT("named_expression"),
      T(":"),
      NT("block"),
      Optional(NT("else_block"))
    )
  )
);

// ============================================================================
// CONTROL FLOW - For Statement
// ============================================================================

rules.set("for_stmt", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("for"),
        NT("star_targets"),
        T("in"),
        NT("star_expressions"),
        T(":"),
        Optional(T("TYPE_COMMENT")),
        NT("block"),
        Optional(NT("else_block"))
      ),
      Sequence(
        T("async"),
        T("for"),
        NT("star_targets"),
        T("in"),
        NT("star_expressions"),
        T(":"),
        Optional(T("TYPE_COMMENT")),
        NT("block"),
        Optional(NT("else_block"))
      )
    )
  )
);

// ============================================================================
// CONTROL FLOW - With Statement
// ============================================================================

rules.set("with_stmt", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("with"),
        T("("),
        OneOrMore(NT("with_item"), T(",")),
        Optional(T(",")),
        T(")"),
        T(":"),
        Optional(T("TYPE_COMMENT")),
        NT("block")
      ),
      Sequence(
        T("with"),
        OneOrMore(NT("with_item"), T(",")),
        T(":"),
        Optional(T("TYPE_COMMENT")),
        NT("block")
      ),
      Sequence(
        T("async"),
        T("with"),
        T("("),
        OneOrMore(NT("with_item"), T(",")),
        Optional(T(",")),
        T(")"),
        T(":"),
        NT("block")
      ),
      Sequence(
        T("async"),
        T("with"),
        OneOrMore(NT("with_item"), T(",")),
        T(":"),
        NT("block")
      )
    )
  )
);

rules.set("with_item", () =>
  Diagram(
    Sequence(
      NT("expression"),
      Optional(Sequence(T("as"), NT("star_target")))
    )
  )
);

// ============================================================================
// CONTROL FLOW - Try Statement
// ============================================================================

rules.set("try_stmt", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("try"),
        T(":"),
        NT("block"),
        NT("finally_block")
      ),
      Sequence(
        T("try"),
        T(":"),
        NT("block"),
        OneOrMore(NT("except_block")),
        Optional(NT("else_block")),
        Optional(NT("finally_block"))
      ),
      Sequence(
        T("try"),
        T(":"),
        NT("block"),
        OneOrMore(NT("except_star_block")),
        Optional(NT("else_block")),
        Optional(NT("finally_block"))
      )
    )
  )
);

rules.set("except_block", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("except"),
        NT("expression"),
        Optional(Sequence(T("as"), T("NAME"))),
        T(":"),
        NT("block")
      ),
      Sequence(T("except"), T(":"), NT("block"))
    )
  )
);

rules.set("except_star_block", () =>
  Diagram(
    Sequence(
      T("except"),
      T("*"),
      NT("expression"),
      Optional(Sequence(T("as"), T("NAME"))),
      T(":"),
      NT("block")
    )
  )
);

rules.set("finally_block", () =>
  Diagram(
    Sequence(T("finally"), T(":"), NT("block"))
  )
);

// ============================================================================
// MATCH STATEMENT (PEP 634)
// ============================================================================

rules.set("match_stmt", () =>
  Diagram(
    Sequence(
      T('"match"'),
      NT("subject_expr"),
      T(":"),
      T("NEWLINE"),
      T("INDENT"),
      OneOrMore(NT("case_block")),
      T("DEDENT")
    )
  )
);

rules.set("subject_expr", () =>
  Diagram(
    Choice(0,
      Sequence(NT("star_named_expression"), T(","), Optional(NT("star_named_expressions"))),
      NT("named_expression")
    )
  )
);

rules.set("case_block", () =>
  Diagram(
    Sequence(
      T('"case"'),
      NT("patterns"),
      Optional(NT("guard")),
      T(":"),
      NT("block")
    )
  )
);

rules.set("guard", () =>
  Diagram(
    Sequence(T("if"), NT("named_expression"))
  )
);

rules.set("patterns", () =>
  Diagram(
    Choice(0,
      NT("open_sequence_pattern"),
      NT("pattern")
    )
  )
);

rules.set("pattern", () =>
  Diagram(
    Choice(0,
      NT("as_pattern"),
      NT("or_pattern")
    )
  )
);

rules.set("as_pattern", () =>
  Diagram(
    Sequence(NT("or_pattern"), T("as"), NT("pattern_capture_target"))
  )
);

rules.set("or_pattern", () =>
  Diagram(
    OneOrMore(NT("closed_pattern"), T("|"))
  )
);

rules.set("closed_pattern", () =>
  Diagram(
    Choice(0,
      NT("literal_pattern"),
      NT("capture_pattern"),
      NT("wildcard_pattern"),
      NT("value_pattern"),
      NT("group_pattern"),
      NT("sequence_pattern"),
      NT("mapping_pattern"),
      NT("class_pattern")
    )
  )
);

rules.set("literal_pattern", () =>
  Diagram(
    Choice(0,
      NT("signed_number"),
      NT("complex_number"),
      NT("strings"),
      T("None"),
      T("True"),
      T("False")
    )
  )
);

rules.set("literal_expr", () =>
  Diagram(
    Choice(0,
      NT("signed_number"),
      NT("complex_number"),
      NT("strings"),
      T("None"),
      T("True"),
      T("False")
    )
  )
);

rules.set("complex_number", () =>
  Diagram(
    Choice(0,
      Sequence(NT("signed_real_number"), T("+"), NT("imaginary_number")),
      Sequence(NT("signed_real_number"), T("-"), NT("imaginary_number"))
    )
  )
);

rules.set("signed_number", () =>
  Diagram(
    Choice(0,
      T("NUMBER"),
      Sequence(T("-"), T("NUMBER"))
    )
  )
);

rules.set("signed_real_number", () =>
  Diagram(
    Choice(0,
      NT("real_number"),
      Sequence(T("-"), NT("real_number"))
    )
  )
);

rules.set("real_number", () =>
  Diagram(T("NUMBER"))
);

rules.set("imaginary_number", () =>
  Diagram(T("NUMBER"))
);

rules.set("capture_pattern", () =>
  Diagram(NT("pattern_capture_target"))
);

rules.set("pattern_capture_target", () =>
  Diagram(
    Sequence(T("NAME"), Comment("!('.' | '(' | '=')"))
  )
);

rules.set("wildcard_pattern", () =>
  Diagram(T("_"))
);

rules.set("value_pattern", () =>
  Diagram(NT("attr"))
);

rules.set("attr", () =>
  Diagram(
    Sequence(NT("name_or_attr"), T("."), T("NAME"))
  )
);

rules.set("name_or_attr", () =>
  Diagram(
    Choice(0,
      NT("attr"),
      T("NAME")
    )
  )
);

rules.set("group_pattern", () =>
  Diagram(
    Sequence(T("("), NT("pattern"), T(")"))
  )
);

rules.set("sequence_pattern", () =>
  Diagram(
    Choice(0,
      Sequence(T("["), Optional(NT("maybe_sequence_pattern")), T("]")),
      Sequence(T("("), Optional(NT("open_sequence_pattern")), T(")"))
    )
  )
);

rules.set("open_sequence_pattern", () =>
  Diagram(
    Sequence(NT("maybe_star_pattern"), T(","), Optional(NT("maybe_sequence_pattern")))
  )
);

rules.set("maybe_sequence_pattern", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("maybe_star_pattern"), T(",")),
      Optional(T(","))
    )
  )
);

rules.set("maybe_star_pattern", () =>
  Diagram(
    Choice(0,
      NT("star_pattern"),
      NT("pattern")
    )
  )
);

rules.set("star_pattern", () =>
  Diagram(
    Choice(0,
      Sequence(T("*"), NT("pattern_capture_target")),
      Sequence(T("*"), NT("wildcard_pattern"))
    )
  )
);

rules.set("mapping_pattern", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("double_star_pattern"), Optional(T(",")), T("}")),
      Sequence(
        T("{"),
        NT("items_pattern"),
        T(","),
        NT("double_star_pattern"),
        Optional(T(",")),
        T("}")
      ),
      Sequence(T("{"), NT("items_pattern"), Optional(T(",")), T("}"))
    )
  )
);

rules.set("items_pattern", () =>
  Diagram(
    OneOrMore(NT("key_value_pattern"), T(","))
  )
);

rules.set("key_value_pattern", () =>
  Diagram(
    Sequence(
      Choice(0, NT("literal_expr"), NT("attr")),
      T(":"),
      NT("pattern")
    )
  )
);

rules.set("double_star_pattern", () =>
  Diagram(
    Sequence(T("**"), NT("pattern_capture_target"))
  )
);

rules.set("class_pattern", () =>
  Diagram(
    Choice(0,
      Sequence(NT("name_or_attr"), T("("), T(")")),
      Sequence(NT("name_or_attr"), T("("), NT("positional_patterns"), Optional(T(",")), T(")")),
      Sequence(NT("name_or_attr"), T("("), NT("keyword_patterns"), Optional(T(",")), T(")")),
      Sequence(
        NT("name_or_attr"),
        T("("),
        NT("positional_patterns"),
        T(","),
        NT("keyword_patterns"),
        Optional(T(",")),
        T(")")
      )
    )
  )
);

rules.set("positional_patterns", () =>
  Diagram(
    OneOrMore(NT("pattern"), T(","))
  )
);

rules.set("keyword_patterns", () =>
  Diagram(
    OneOrMore(NT("keyword_pattern"), T(","))
  )
);

rules.set("keyword_pattern", () =>
  Diagram(
    Sequence(T("NAME"), T("="), NT("pattern"))
  )
);

// ============================================================================
// TYPE STATEMENTS (PEP 695)
// ============================================================================

rules.set("type_alias", () =>
  Diagram(
    Sequence(
      T('"type"'),
      T("NAME"),
      Optional(NT("type_params")),
      T("="),
      NT("expression")
    )
  )
);

rules.set("type_params", () =>
  Diagram(
    Sequence(
      T("["),
      NT("type_param_seq"),
      T("]")
    )
  )
);

rules.set("type_param_seq", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("type_param"), T(",")),
      Optional(T(","))
    )
  )
);

rules.set("type_param", () =>
  Diagram(
    Choice(0,
      Sequence(T("NAME"), Optional(NT("type_param_bound")), Optional(NT("type_param_default"))),
      Sequence(T("*"), T("NAME"), Optional(NT("type_param_starred_default"))),
      Sequence(T("**"), T("NAME"), Optional(NT("type_param_default")))
    )
  )
);

rules.set("type_param_bound", () =>
  Diagram(
    Sequence(T(":"), NT("expression"))
  )
);

rules.set("type_param_default", () =>
  Diagram(
    Sequence(T("="), NT("expression"))
  )
);

rules.set("type_param_starred_default", () =>
  Diagram(
    Sequence(T("="), NT("star_expression"))
  )
);

rules.set("type_expressions", () =>
  Diagram(
    Choice(0,
      Sequence(
        OneOrMore(NT("expression"), T(",")),
        T(","),
        T("*"),
        NT("expression"),
        T(","),
        T("**"),
        NT("expression")
      ),
      Sequence(
        OneOrMore(NT("expression"), T(",")),
        T(","),
        T("*"),
        NT("expression")
      ),
      Sequence(
        OneOrMore(NT("expression"), T(",")),
        T(","),
        T("**"),
        NT("expression")
      ),
      Sequence(T("*"), NT("expression"), T(","), T("**"), NT("expression")),
      Sequence(T("*"), NT("expression")),
      Sequence(T("**"), NT("expression")),
      OneOrMore(NT("expression"), T(","))
    )
  )
);

// ============================================================================
// EXPRESSIONS
// ============================================================================

rules.set("expression", () =>
  Diagram(
    Choice(0,
      Sequence(
        NT("disjunction"),
        T("if"),
        NT("disjunction"),
        T("else"),
        NT("expression")
      ),
      NT("disjunction"),
      NT("lambdef")
    )
  )
);

rules.set("yield_expr", () =>
  Diagram(
    Choice(0,
      Sequence(T("yield"), T("from"), NT("expression")),
      Sequence(T("yield"), Optional(NT("star_expressions")))
    )
  )
);

rules.set("expressions", () =>
  Diagram(
    Choice(0,
      Sequence(NT("expression"), OneOrMore(Sequence(T(","), NT("expression"))), Optional(T(","))),
      Sequence(NT("expression"), T(",")),
      NT("expression")
    )
  )
);

rules.set("star_expressions", () =>
  Diagram(
    Choice(0,
      Sequence(NT("star_expression"), OneOrMore(Sequence(T(","), NT("star_expression"))), Optional(T(","))),
      Sequence(NT("star_expression"), T(",")),
      NT("star_expression")
    )
  )
);

rules.set("star_expression", () =>
  Diagram(
    Choice(0,
      Sequence(T("*"), NT("bitwise_or")),
      NT("expression")
    )
  )
);

rules.set("star_named_expressions", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("star_named_expression"), T(",")),
      Optional(T(","))
    )
  )
);

rules.set("star_named_expression", () =>
  Diagram(
    Choice(0,
      Sequence(T("*"), NT("bitwise_or")),
      NT("named_expression")
    )
  )
);

rules.set("assignment_expression", () =>
  Diagram(
    Sequence(T("NAME"), T(":="), NT("expression"))
  )
);

rules.set("named_expression", () =>
  Diagram(
    Choice(0,
      NT("assignment_expression"),
      NT("expression")
    )
  )
);

rules.set("disjunction", () =>
  Diagram(
    Choice(0,
      Sequence(NT("conjunction"), OneOrMore(Sequence(T("or"), NT("conjunction")))),
      NT("conjunction")
    )
  )
);

rules.set("conjunction", () =>
  Diagram(
    Choice(0,
      Sequence(NT("inversion"), OneOrMore(Sequence(T("and"), NT("inversion")))),
      NT("inversion")
    )
  )
);

rules.set("inversion", () =>
  Diagram(
    Choice(0,
      Sequence(T("not"), NT("inversion")),
      NT("comparison")
    )
  )
);

// ============================================================================
// COMPARISON OPERATORS
// ============================================================================

rules.set("comparison", () =>
  Diagram(
    Sequence(
      NT("bitwise_or"),
      ZeroOrMore(NT("compare_op_bitwise_or_pair"))
    )
  )
);

rules.set("compare_op_bitwise_or_pair", () =>
  Diagram(
    Choice(0,
      NT("eq_bitwise_or"),
      NT("noteq_bitwise_or"),
      NT("lte_bitwise_or"),
      NT("lt_bitwise_or"),
      NT("gte_bitwise_or"),
      NT("gt_bitwise_or"),
      NT("notin_bitwise_or"),
      NT("in_bitwise_or"),
      NT("isnot_bitwise_or"),
      NT("is_bitwise_or")
    )
  )
);

rules.set("eq_bitwise_or", () =>
  Diagram(Sequence(T("=="), NT("bitwise_or")))
);

rules.set("noteq_bitwise_or", () =>
  Diagram(Sequence(T("!="), NT("bitwise_or")))
);

rules.set("lte_bitwise_or", () =>
  Diagram(Sequence(T("<="), NT("bitwise_or")))
);

rules.set("lt_bitwise_or", () =>
  Diagram(Sequence(T("<"), NT("bitwise_or")))
);

rules.set("gte_bitwise_or", () =>
  Diagram(Sequence(T(">="), NT("bitwise_or")))
);

rules.set("gt_bitwise_or", () =>
  Diagram(Sequence(T(">"), NT("bitwise_or")))
);

rules.set("notin_bitwise_or", () =>
  Diagram(Sequence(T("not"), T("in"), NT("bitwise_or")))
);

rules.set("in_bitwise_or", () =>
  Diagram(Sequence(T("in"), NT("bitwise_or")))
);

rules.set("isnot_bitwise_or", () =>
  Diagram(Sequence(T("is"), T("not"), NT("bitwise_or")))
);

rules.set("is_bitwise_or", () =>
  Diagram(Sequence(T("is"), NT("bitwise_or")))
);

// ============================================================================
// BITWISE OPERATORS
// ============================================================================

rules.set("bitwise_or", () =>
  Diagram(
    Choice(0,
      Sequence(NT("bitwise_or"), T("|"), NT("bitwise_xor")),
      NT("bitwise_xor")
    )
  )
);

rules.set("bitwise_xor", () =>
  Diagram(
    Choice(0,
      Sequence(NT("bitwise_xor"), T("^"), NT("bitwise_and")),
      NT("bitwise_and")
    )
  )
);

rules.set("bitwise_and", () =>
  Diagram(
    Choice(0,
      Sequence(NT("bitwise_and"), T("&"), NT("shift_expr")),
      NT("shift_expr")
    )
  )
);

rules.set("shift_expr", () =>
  Diagram(
    Choice(0,
      Sequence(NT("shift_expr"), T("<<"), NT("sum")),
      Sequence(NT("shift_expr"), T(">>"), NT("sum")),
      NT("sum")
    )
  )
);

// ============================================================================
// ARITHMETIC OPERATORS
// ============================================================================

rules.set("sum", () =>
  Diagram(
    Choice(0,
      Sequence(NT("sum"), T("+"), NT("term")),
      Sequence(NT("sum"), T("-"), NT("term")),
      NT("term")
    )
  )
);

rules.set("term", () =>
  Diagram(
    Choice(0,
      Sequence(NT("term"), T("*"), NT("factor")),
      Sequence(NT("term"), T("/"), NT("factor")),
      Sequence(NT("term"), T("//"), NT("factor")),
      Sequence(NT("term"), T("%"), NT("factor")),
      Sequence(NT("term"), T("@"), NT("factor")),
      NT("factor")
    )
  )
);

rules.set("factor", () =>
  Diagram(
    Choice(0,
      Sequence(T("+"), NT("factor")),
      Sequence(T("-"), NT("factor")),
      Sequence(T("~"), NT("factor")),
      NT("power")
    )
  )
);

rules.set("power", () =>
  Diagram(
    Choice(0,
      Sequence(NT("await_primary"), T("**"), NT("factor")),
      NT("await_primary")
    )
  )
);

// ============================================================================
// PRIMARY EXPRESSIONS
// ============================================================================

rules.set("await_primary", () =>
  Diagram(
    Choice(0,
      Sequence(T("await"), NT("primary")),
      NT("primary")
    )
  )
);

rules.set("primary", () =>
  Diagram(
    Choice(0,
      Sequence(NT("primary"), T("."), T("NAME")),
      Sequence(NT("primary"), NT("genexp")),
      Sequence(NT("primary"), T("("), Optional(NT("arguments")), T(")")),
      Sequence(NT("primary"), T("["), NT("slices"), T("]")),
      NT("atom")
    )
  )
);

rules.set("slices", () =>
  Diagram(
    Choice(0,
      NT("slice"),
      Sequence(
        OneOrMore(Choice(0, NT("slice"), NT("starred_expression")), T(",")),
        Optional(T(","))
      )
    )
  )
);

rules.set("slice", () =>
  Diagram(
    Choice(0,
      Sequence(
        Optional(NT("expression")),
        T(":"),
        Optional(NT("expression")),
        Optional(Sequence(T(":"), Optional(NT("expression"))))
      ),
      NT("named_expression")
    )
  )
);

rules.set("atom", () =>
  Diagram(
    Choice(0,
      T("NAME"),
      T("True"),
      T("False"),
      T("None"),
      NT("strings"),
      T("NUMBER"),
      NT("tuple"),
      NT("group"),
      NT("genexp"),
      NT("list"),
      NT("listcomp"),
      NT("dict"),
      NT("set"),
      NT("dictcomp"),
      NT("setcomp"),
      T("...")
    )
  )
);

rules.set("group", () =>
  Diagram(
    Sequence(
      T("("),
      Choice(0, NT("yield_expr"), NT("named_expression")),
      T(")")
    )
  )
);

// ============================================================================
// LAMBDA
// ============================================================================

rules.set("lambdef", () =>
  Diagram(
    Sequence(
      T("lambda"),
      Optional(NT("lambda_params")),
      T(":"),
      NT("expression")
    )
  )
);

rules.set("lambda_params", () =>
  Diagram(NT("lambda_parameters"))
);

rules.set("lambda_parameters", () =>
  Diagram(
    Choice(0,
      Sequence(
        NT("lambda_slash_no_default"),
        ZeroOrMore(NT("lambda_param_no_default")),
        ZeroOrMore(NT("lambda_param_with_default")),
        Optional(NT("lambda_star_etc"))
      ),
      Sequence(
        NT("lambda_slash_with_default"),
        ZeroOrMore(NT("lambda_param_with_default")),
        Optional(NT("lambda_star_etc"))
      ),
      Sequence(
        OneOrMore(NT("lambda_param_no_default")),
        ZeroOrMore(NT("lambda_param_with_default")),
        Optional(NT("lambda_star_etc"))
      ),
      Sequence(
        OneOrMore(NT("lambda_param_with_default")),
        Optional(NT("lambda_star_etc"))
      ),
      NT("lambda_star_etc")
    )
  )
);

rules.set("lambda_slash_no_default", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("lambda_param_no_default")),
      T("/"),
      Choice(0, T(","), Comment("&':'"))
    )
  )
);

rules.set("lambda_slash_with_default", () =>
  Diagram(
    Sequence(
      ZeroOrMore(NT("lambda_param_no_default")),
      OneOrMore(NT("lambda_param_with_default")),
      T("/"),
      Choice(0, T(","), Comment("&':'"))
    )
  )
);

rules.set("lambda_star_etc", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("*"),
        NT("lambda_param_no_default"),
        ZeroOrMore(NT("lambda_param_maybe_default")),
        Optional(NT("lambda_kwds"))
      ),
      Sequence(
        T("*"),
        T(","),
        OneOrMore(NT("lambda_param_maybe_default")),
        Optional(NT("lambda_kwds"))
      ),
      NT("lambda_kwds")
    )
  )
);

rules.set("lambda_kwds", () =>
  Diagram(
    Sequence(T("**"), NT("lambda_param_no_default"))
  )
);

rules.set("lambda_param_no_default", () =>
  Diagram(
    Sequence(NT("lambda_param"), Choice(0, T(","), Comment("&':'")))
  )
);

rules.set("lambda_param_with_default", () =>
  Diagram(
    Sequence(NT("lambda_param"), NT("default"), Choice(0, T(","), Comment("&':'")))
  )
);

rules.set("lambda_param_maybe_default", () =>
  Diagram(
    Sequence(NT("lambda_param"), Optional(NT("default")), Choice(0, T(","), Comment("&':'")))
  )
);

rules.set("lambda_param", () =>
  Diagram(T("NAME"))
);

// ============================================================================
// LITERALS
// ============================================================================

rules.set("strings", () =>
  Diagram(
    OneOrMore(
      Choice(0, NT("fstring"), NT("tstring"), NT("string"))
    )
  )
);

rules.set("string", () =>
  Diagram(T("STRING"))
);

rules.set("fstring", () =>
  Diagram(
    Sequence(
      T("FSTRING_START"),
      ZeroOrMore(NT("fstring_middle")),
      T("FSTRING_END")
    )
  )
);

rules.set("fstring_middle", () =>
  Diagram(
    Choice(0,
      NT("fstring_replacement_field"),
      T("FSTRING_MIDDLE")
    )
  )
);

rules.set("fstring_replacement_field", () =>
  Diagram(
    Sequence(
      T("{"),
      Choice(0, NT("yield_expr"), NT("star_expressions")),
      Optional(T("=")),
      Optional(NT("fstring_conversion")),
      Optional(NT("fstring_full_format_spec")),
      T("}")
    )
  )
);

rules.set("fstring_conversion", () =>
  Diagram(
    Sequence(T("!"), T("NAME"))
  )
);

rules.set("fstring_full_format_spec", () =>
  Diagram(
    Sequence(T(":"), ZeroOrMore(NT("fstring_format_spec")))
  )
);

rules.set("fstring_format_spec", () =>
  Diagram(
    Choice(0,
      T("FSTRING_MIDDLE"),
      NT("fstring_replacement_field")
    )
  )
);

rules.set("tstring", () =>
  Diagram(
    Sequence(
      T("TSTRING_START"),
      ZeroOrMore(NT("tstring_middle")),
      T("TSTRING_END")
    )
  )
);

rules.set("tstring_middle", () =>
  Diagram(
    Choice(0,
      NT("tstring_replacement_field"),
      T("TSTRING_MIDDLE")
    )
  )
);

rules.set("tstring_replacement_field", () =>
  Diagram(
    Sequence(
      T("{"),
      Choice(0, NT("yield_expr"), NT("star_expressions")),
      Optional(T("=")),
      Optional(NT("fstring_conversion")),
      Optional(NT("tstring_full_format_spec")),
      T("}")
    )
  )
);

rules.set("tstring_full_format_spec", () =>
  Diagram(
    Sequence(T(":"), ZeroOrMore(NT("tstring_format_spec")))
  )
);

rules.set("tstring_format_spec", () =>
  Diagram(
    Choice(0,
      T("TSTRING_MIDDLE"),
      NT("tstring_format_spec_replacement_field")
    )
  )
);

rules.set("tstring_format_spec_replacement_field", () =>
  Diagram(
    Sequence(
      T("{"),
      Choice(0, NT("yield_expr"), NT("star_expressions")),
      Optional(T("=")),
      Optional(NT("fstring_conversion")),
      Optional(NT("fstring_full_format_spec")),
      T("}")
    )
  )
);

// ============================================================================
// COLLECTIONS
// ============================================================================

rules.set("list", () =>
  Diagram(
    Sequence(
      T("["),
      Optional(NT("star_named_expressions")),
      T("]")
    )
  )
);

rules.set("tuple", () =>
  Diagram(
    Sequence(
      T("("),
      Optional(Sequence(NT("star_named_expression"), T(","), Optional(NT("star_named_expressions")))),
      T(")")
    )
  )
);

rules.set("set", () =>
  Diagram(
    Sequence(T("{"), NT("star_named_expressions"), T("}"))
  )
);

rules.set("dict", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("double_starred_kvpairs"), T("}"))
    )
  )
);

rules.set("double_starred_kvpairs", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("double_starred_kvpair"), T(",")),
      Optional(T(","))
    )
  )
);

rules.set("double_starred_kvpair", () =>
  Diagram(
    Choice(0,
      Sequence(T("**"), NT("bitwise_or")),
      NT("kvpair")
    )
  )
);

rules.set("kvpair", () =>
  Diagram(
    Sequence(NT("expression"), T(":"), NT("expression"))
  )
);

// ============================================================================
// COMPREHENSIONS
// ============================================================================

rules.set("for_if_clauses", () =>
  Diagram(
    OneOrMore(NT("for_if_clause"))
  )
);

rules.set("for_if_clause", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("async"),
        T("for"),
        NT("star_targets"),
        T("in"),
        NT("disjunction"),
        ZeroOrMore(Sequence(T("if"), NT("disjunction")))
      ),
      Sequence(
        T("for"),
        NT("star_targets"),
        T("in"),
        NT("disjunction"),
        ZeroOrMore(Sequence(T("if"), NT("disjunction")))
      )
    )
  )
);

rules.set("listcomp", () =>
  Diagram(
    Sequence(
      T("["),
      NT("named_expression"),
      NT("for_if_clauses"),
      T("]")
    )
  )
);

rules.set("setcomp", () =>
  Diagram(
    Sequence(
      T("{"),
      NT("named_expression"),
      NT("for_if_clauses"),
      T("}")
    )
  )
);

rules.set("genexp", () =>
  Diagram(
    Sequence(
      T("("),
      Choice(0, NT("assignment_expression"), Sequence(NT("expression"), Comment("!':='"))),
      NT("for_if_clauses"),
      T(")")
    )
  )
);

rules.set("dictcomp", () =>
  Diagram(
    Sequence(
      T("{"),
      NT("kvpair"),
      NT("for_if_clauses"),
      T("}")
    )
  )
);

// ============================================================================
// FUNCTION ARGUMENTS
// ============================================================================

rules.set("arguments", () =>
  Diagram(
    Sequence(NT("args"), Optional(T(",")))
  )
);

rules.set("args", () =>
  Diagram(
    Choice(0,
      Sequence(
        OneOrMore(Choice(0, NT("starred_expression"), NT("assignment_expression"), Sequence(NT("expression"), Comment("!':='"))), T(",")),
        Optional(Sequence(T(","), NT("kwargs")))
      ),
      NT("kwargs")
    )
  )
);

rules.set("kwargs", () =>
  Diagram(
    Choice(0,
      Sequence(
        OneOrMore(NT("kwarg_or_starred"), T(",")),
        T(","),
        OneOrMore(NT("kwarg_or_double_starred"), T(","))
      ),
      OneOrMore(NT("kwarg_or_starred"), T(",")),
      OneOrMore(NT("kwarg_or_double_starred"), T(","))
    )
  )
);

rules.set("starred_expression", () =>
  Diagram(
    Choice(0,
      Sequence(T("*"), NT("expression")),
      NT("expression")
    )
  )
);

rules.set("kwarg_or_starred", () =>
  Diagram(
    Choice(0,
      Sequence(T("NAME"), T("="), NT("expression")),
      NT("starred_expression")
    )
  )
);

rules.set("kwarg_or_double_starred", () =>
  Diagram(
    Choice(0,
      Sequence(T("NAME"), T("="), NT("expression")),
      Sequence(T("**"), NT("expression"))
    )
  )
);

// ============================================================================
// ASSIGNMENT TARGETS
// ============================================================================

rules.set("star_targets", () =>
  Diagram(
    Choice(0,
      Sequence(NT("star_target"), OneOrMore(Sequence(T(","), NT("star_target"))), Optional(T(","))),
      Sequence(NT("star_target"), T(",")),
      NT("star_target")
    )
  )
);

rules.set("star_targets_list_seq", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("star_target"), T(",")),
      Optional(T(","))
    )
  )
);

rules.set("star_targets_tuple_seq", () =>
  Diagram(
    Choice(0,
      Sequence(NT("star_target"), OneOrMore(Sequence(T(","), NT("star_target"))), Optional(T(","))),
      Sequence(NT("star_target"), T(","))
    )
  )
);

rules.set("star_target", () =>
  Diagram(
    Choice(0,
      Sequence(T("*"), NT("star_target")),
      NT("target_with_star_atom")
    )
  )
);

rules.set("target_with_star_atom", () =>
  Diagram(
    Choice(0,
      Sequence(NT("t_primary"), T("."), T("NAME")),
      Sequence(NT("t_primary"), T("["), NT("slices"), T("]")),
      NT("star_atom")
    )
  )
);

rules.set("star_atom", () =>
  Diagram(
    Choice(0,
      T("NAME"),
      Sequence(T("("), NT("target_with_star_atom"), T(")")),
      Sequence(T("("), Optional(NT("star_targets_tuple_seq")), T(")")),
      Sequence(T("["), Optional(NT("star_targets_list_seq")), T("]"))
    )
  )
);

rules.set("single_target", () =>
  Diagram(
    Choice(0,
      NT("single_subscript_attribute_target"),
      T("NAME"),
      Sequence(T("("), NT("single_target"), T(")"))
    )
  )
);

rules.set("single_subscript_attribute_target", () =>
  Diagram(
    Choice(0,
      Sequence(NT("t_primary"), T("."), T("NAME")),
      Sequence(NT("t_primary"), T("["), NT("slices"), T("]"))
    )
  )
);

rules.set("t_primary", () =>
  Diagram(
    Choice(0,
      Sequence(NT("t_primary"), T("."), T("NAME")),
      Sequence(NT("t_primary"), T("["), NT("slices"), T("]")),
      Sequence(NT("t_primary"), NT("genexp")),
      Sequence(NT("t_primary"), T("("), Optional(NT("arguments")), T(")")),
      NT("atom")
    )
  )
);

rules.set("t_lookahead", () =>
  Diagram(
    Choice(0, T("("), T("["), T("."))
  )
);

rules.set("del_targets", () =>
  Diagram(
    Sequence(
      OneOrMore(NT("del_target"), T(",")),
      Optional(T(","))
    )
  )
);

rules.set("del_target", () =>
  Diagram(
    Choice(0,
      Sequence(NT("t_primary"), T("."), T("NAME")),
      Sequence(NT("t_primary"), T("["), NT("slices"), T("]")),
      NT("del_t_atom")
    )
  )
);

rules.set("del_t_atom", () =>
  Diagram(
    Choice(0,
      T("NAME"),
      Sequence(T("("), NT("del_target"), T(")")),
      Sequence(T("("), Optional(NT("del_targets")), T(")")),
      Sequence(T("["), Optional(NT("del_targets")), T("]"))
    )
  )
);

// ============================================================================
// EXPORTS
// ============================================================================

// Section definitions for organized navigation
export const SECTION_ORDER = [
  "starting",
  "statements",
  "simple_stmts",
  "imports",
  "compound",
  "params",
  "control_if",
  "control_while",
  "control_for",
  "control_with",
  "control_try",
  "match",
  "types",
  "expressions",
  "comparison",
  "bitwise",
  "arithmetic",
  "primary",
  "lambda",
  "literals",
  "collections",
  "comprehensions",
  "arguments",
  "targets",
] as const;

export type SectionId = typeof SECTION_ORDER[number];

export const SECTION_TITLES: Record<SectionId, string> = {
  starting: "Starting Rules",
  statements: "General Statements",
  simple_stmts: "Simple Statements",
  imports: "Import Statements",
  compound: "Compound Statements",
  params: "Function Parameters",
  control_if: "If Statement",
  control_while: "While Statement",
  control_for: "For Statement",
  control_with: "With Statement",
  control_try: "Try Statement",
  match: "Pattern Matching",
  types: "Type Statements",
  expressions: "Expressions",
  comparison: "Comparison Operators",
  bitwise: "Bitwise Operators",
  arithmetic: "Arithmetic Operators",
  primary: "Primary Expressions",
  lambda: "Lambda Expressions",
  literals: "Literals & Strings",
  collections: "Collections",
  comprehensions: "Comprehensions",
  arguments: "Function Arguments",
  targets: "Assignment Targets",
};

export const SECTION_RULES: Record<SectionId, RuleName[]> = {
  starting: ["file", "interactive", "eval", "func_type"],
  statements: ["statements", "statement", "single_compound_stmt", "statement_newline", "simple_stmts", "simple_stmt", "compound_stmt"],
  simple_stmts: ["assignment", "annotated_rhs", "augassign", "return_stmt", "raise_stmt", "pass_stmt", "break_stmt", "continue_stmt", "global_stmt", "nonlocal_stmt", "del_stmt", "yield_stmt", "assert_stmt"],
  imports: ["import_stmt", "import_name", "import_from", "import_from_targets", "import_from_as_names", "import_from_as_name", "dotted_as_names", "dotted_as_name", "dotted_name"],
  compound: ["block", "decorators", "class_def", "class_def_raw", "function_def", "function_def_raw", "func_type_comment"],
  params: ["params", "parameters", "slash_no_default", "slash_with_default", "star_etc", "kwds", "param_no_default", "param_no_default_star_annotation", "param_with_default", "param_maybe_default", "param", "param_star_annotation", "annotation", "star_annotation", "default"],
  control_if: ["if_stmt", "elif_stmt", "else_block"],
  control_while: ["while_stmt"],
  control_for: ["for_stmt"],
  control_with: ["with_stmt", "with_item"],
  control_try: ["try_stmt", "except_block", "except_star_block", "finally_block"],
  match: ["match_stmt", "subject_expr", "case_block", "guard", "patterns", "pattern", "as_pattern", "or_pattern", "closed_pattern", "literal_pattern", "literal_expr", "complex_number", "signed_number", "signed_real_number", "real_number", "imaginary_number", "capture_pattern", "pattern_capture_target", "wildcard_pattern", "value_pattern", "attr", "name_or_attr", "group_pattern", "sequence_pattern", "open_sequence_pattern", "maybe_sequence_pattern", "maybe_star_pattern", "star_pattern", "mapping_pattern", "items_pattern", "key_value_pattern", "double_star_pattern", "class_pattern", "positional_patterns", "keyword_patterns", "keyword_pattern"],
  types: ["type_alias", "type_params", "type_param_seq", "type_param", "type_param_bound", "type_param_default", "type_param_starred_default", "type_expressions"],
  expressions: ["expression", "expressions", "yield_expr", "star_expressions", "star_expression", "star_named_expressions", "star_named_expression", "assignment_expression", "named_expression", "disjunction", "conjunction", "inversion"],
  comparison: ["comparison", "compare_op_bitwise_or_pair", "eq_bitwise_or", "noteq_bitwise_or", "lte_bitwise_or", "lt_bitwise_or", "gte_bitwise_or", "gt_bitwise_or", "notin_bitwise_or", "in_bitwise_or", "isnot_bitwise_or", "is_bitwise_or"],
  bitwise: ["bitwise_or", "bitwise_xor", "bitwise_and", "shift_expr"],
  arithmetic: ["sum", "term", "factor", "power"],
  primary: ["await_primary", "primary", "slices", "slice", "atom", "group"],
  lambda: ["lambdef", "lambda_params", "lambda_parameters", "lambda_slash_no_default", "lambda_slash_with_default", "lambda_star_etc", "lambda_kwds", "lambda_param_no_default", "lambda_param_with_default", "lambda_param_maybe_default", "lambda_param"],
  literals: ["strings", "string", "fstring", "fstring_middle", "fstring_replacement_field", "fstring_conversion", "fstring_full_format_spec", "fstring_format_spec", "tstring", "tstring_middle", "tstring_replacement_field", "tstring_full_format_spec", "tstring_format_spec", "tstring_format_spec_replacement_field"],
  collections: ["list", "tuple", "set", "dict", "double_starred_kvpairs", "double_starred_kvpair", "kvpair"],
  comprehensions: ["for_if_clauses", "for_if_clause", "listcomp", "setcomp", "genexp", "dictcomp"],
  arguments: ["arguments", "args", "kwargs", "starred_expression", "kwarg_or_starred", "kwarg_or_double_starred"],
  targets: ["star_targets", "star_targets_list_seq", "star_targets_tuple_seq", "star_target", "target_with_star_atom", "star_atom", "single_target", "single_subscript_attribute_target", "t_primary", "t_lookahead", "del_targets", "del_target", "del_t_atom"],
};

/**
 * Get all rule names
 */
export function getRuleNames(): RuleName[] {
  return Array.from(rules.keys());
}

/**
 * Create a diagram for a given rule name
 */
export function createRuleDiagram(ruleName: RuleName): ReturnType<typeof Diagram> | null {
  const factory = rules.get(ruleName);
  return factory ? factory() : null;
}

/**
 * Check if a rule exists
 */
export function hasRule(ruleName: RuleName): boolean {
  return rules.has(ruleName);
}

export default rules;
