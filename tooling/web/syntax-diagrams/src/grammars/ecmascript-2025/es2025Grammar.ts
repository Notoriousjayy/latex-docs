// es2025Grammar.ts
//
// ES module that defines ECMAScript 2025 grammar as railroad diagrams.
// Many rules are rendered in diagram-friendly equivalent form (e.g., left recursion -> repetition).

import * as RR from "@prantlf/railroad-diagrams/lib/index.mjs";

// Convenience wrappers ------------------------------------------------------
//
// The @prantlf/railroad-diagrams package has shipped in builds where the exported
// primitives are factory functions and builds where they are ES class constructors.
// Calling a class constructor without `new` throws:
//   "Class constructor X cannot be invoked without 'new'"
//
// `callOrNew` lets us treat everything as a callable, regardless of how it is exported.
function callOrNew(Ctor: any, ...args: any[]) {
  try {
    return Ctor(...args);
  } catch (e) {
    if (e instanceof TypeError && /without 'new'/.test((e as Error).message)) {
      return new Ctor(...args);
    }
    throw e;
  }
}

// Wrapped primitives (use these throughout the file)
const Diagram    = (...a: any[]) => callOrNew(RR.Diagram, ...a);
const Sequence   = (...a: any[]) => callOrNew(RR.Sequence, ...a);
const Choice     = (...a: any[]) => callOrNew(RR.Choice, ...a);
const Optional   = (...a: any[]) => callOrNew(RR.Optional, ...a);
const OneOrMore  = (...a: any[]) => callOrNew(RR.OneOrMore, ...a);
const ZeroOrMore = (...a: any[]) => callOrNew(RR.ZeroOrMore, ...a);
const Terminal   = (...a: any[]) => callOrNew(RR.Terminal, ...a);
const NonTerminal = (...a: any[]) => callOrNew(RR.NonTerminal, ...a);
const Stack      = (...a: any[]) => callOrNew(RR.Stack, ...a);
const Comment    = (...a: any[]) => callOrNew(RR.Comment, ...a);

const T  = (s: string) => Terminal(s);
const NT = (s: string) => NonTerminal(s);

// --- Grammar rules (diagram factories) ----------------------------------------

const rules = new Map<string, () => any>();

// ===== A.1 Lexical Grammar =====

rules.set("SourceCharacter", () =>
  Diagram(
    Comment("any Unicode code point")
  )
);

rules.set("InputElementDiv", () =>
  Diagram(
    Choice(0,
      NT("WhiteSpace"),
      NT("LineTerminator"),
      NT("Comment"),
      NT("CommonToken"),
      NT("DivPunctuator"),
      NT("RightBracePunctuator")
    )
  )
);

rules.set("InputElementRegExp", () =>
  Diagram(
    Choice(0,
      NT("WhiteSpace"),
      NT("LineTerminator"),
      NT("Comment"),
      NT("CommonToken"),
      NT("RightBracePunctuator"),
      NT("RegularExpressionLiteral")
    )
  )
);

rules.set("InputElementRegExpOrTemplateTail", () =>
  Diagram(
    Choice(0,
      NT("WhiteSpace"),
      NT("LineTerminator"),
      NT("Comment"),
      NT("CommonToken"),
      NT("RegularExpressionLiteral"),
      NT("TemplateSubstitutionTail")
    )
  )
);

rules.set("InputElementTemplateTail", () =>
  Diagram(
    Choice(0,
      NT("WhiteSpace"),
      NT("LineTerminator"),
      NT("Comment"),
      NT("CommonToken"),
      NT("DivPunctuator"),
      NT("TemplateSubstitutionTail")
    )
  )
);

rules.set("WhiteSpace", () =>
  Diagram(
    Choice(0,
      T("<TAB>"),
      T("<VT>"),
      T("<FF>"),
      T("<ZWNBSP>"),
      T("<USP>")
    )
  )
);

rules.set("LineTerminator", () =>
  Diagram(
    Choice(0,
      T("<LF>"),
      T("<CR>"),
      T("<LS>"),
      T("<PS>")
    )
  )
);

rules.set("LineTerminatorSequence", () =>
  Diagram(
    Choice(0,
      T("<LF>"),
      Sequence(T("<CR>"), Comment("[lookahead ≠ <LF>]")),
      T("<LS>"),
      T("<PS>"),
      Sequence(T("<CR>"), T("<LF>"))
    )
  )
);

rules.set("Comment", () =>
  Diagram(
    Choice(0,
      NT("MultiLineComment"),
      NT("SingleLineComment")
    )
  )
);

rules.set("MultiLineComment", () =>
  Diagram(
    Sequence(
      T("/*"),
      Optional(NT("MultiLineCommentChars")),
      T("*/")
    )
  )
);

rules.set("SingleLineComment", () =>
  Diagram(
    Sequence(
      T("//"),
      Optional(NT("SingleLineCommentChars"))
    )
  )
);

rules.set("HashbangComment", () =>
  Diagram(
    Sequence(
      T("#!"),
      Optional(NT("SingleLineCommentChars"))
    )
  )
);

rules.set("CommonToken", () =>
  Diagram(
    Choice(0,
      NT("IdentifierName"),
      NT("PrivateIdentifier"),
      NT("Punctuator"),
      NT("NumericLiteral"),
      NT("StringLiteral"),
      NT("Template")
    )
  )
);

rules.set("PrivateIdentifier", () =>
  Diagram(
    Sequence(T("#"), NT("IdentifierName"))
  )
);

rules.set("IdentifierName", () =>
  Diagram(
    Sequence(
      NT("IdentifierStart"),
      ZeroOrMore(NT("IdentifierPart"))
    )
  )
);

rules.set("IdentifierStart", () =>
  Diagram(
    Choice(0,
      NT("IdentifierStartChar"),
      Sequence(T("\\"), NT("UnicodeEscapeSequence"))
    )
  )
);

rules.set("IdentifierPart", () =>
  Diagram(
    Choice(0,
      NT("IdentifierPartChar"),
      Sequence(T("\\"), NT("UnicodeEscapeSequence"))
    )
  )
);

rules.set("IdentifierStartChar", () =>
  Diagram(
    Choice(0,
      NT("UnicodeIDStart"),
      T("$"),
      T("_")
    )
  )
);

rules.set("IdentifierPartChar", () =>
  Diagram(
    Choice(0,
      NT("UnicodeIDContinue"),
      T("$")
    )
  )
);

rules.set("UnicodeIDStart", () =>
  Diagram(
    Comment("any Unicode code point with property \"ID_Start\"")
  )
);

rules.set("UnicodeIDContinue", () =>
  Diagram(
    Comment("any Unicode code point with property \"ID_Continue\"")
  )
);

rules.set("ReservedWord", () =>
  Diagram(
    Choice(0,
      T("await"), T("break"), T("case"), T("catch"), T("class"),
      T("const"), T("continue"), T("debugger"), T("default"), T("delete"),
      T("do"), T("else"), T("enum"), T("export"), T("extends"),
      T("false"), T("finally"), T("for"), T("function"), T("if"),
      T("import"), T("in"), T("instanceof"), T("new"), T("null"),
      T("return"), T("super"), T("switch"), T("this"), T("throw"),
      T("true"), T("try"), T("typeof"), T("var"), T("void"),
      T("while"), T("with"), T("yield")
    )
  )
);

rules.set("Punctuator", () =>
  Diagram(
    Choice(0,
      NT("OptionalChainingPunctuator"),
      NT("OtherPunctuator")
    )
  )
);

rules.set("OptionalChainingPunctuator", () =>
  Diagram(
    Sequence(T("?."), Comment("[lookahead ∉ DecimalDigit]"))
  )
);

rules.set("DivPunctuator", () =>
  Diagram(
    Choice(0, T("/"), T("/="))
  )
);

rules.set("RightBracePunctuator", () =>
  Diagram(T("}"))
);

rules.set("NullLiteral", () =>
  Diagram(T("null"))
);

rules.set("BooleanLiteral", () =>
  Diagram(
    Choice(0, T("true"), T("false"))
  )
);

rules.set("NumericLiteral", () =>
  Diagram(
    Choice(0,
      NT("DecimalLiteral"),
      NT("DecimalBigIntegerLiteral"),
      NT("NonDecimalIntegerLiteral"),
      Sequence(NT("NonDecimalIntegerLiteral"), NT("BigIntLiteralSuffix")),
      NT("LegacyOctalIntegerLiteral")
    )
  )
);

rules.set("DecimalLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(NT("DecimalIntegerLiteral"), T("."), Optional(NT("DecimalDigits")), Optional(NT("ExponentPart"))),
      Sequence(T("."), NT("DecimalDigits"), Optional(NT("ExponentPart"))),
      Sequence(NT("DecimalIntegerLiteral"), Optional(NT("ExponentPart")))
    )
  )
);

rules.set("DecimalIntegerLiteral", () =>
  Diagram(
    Choice(0,
      T("0"),
      NT("NonZeroDigit"),
      Sequence(NT("NonZeroDigit"), Optional(NT("NumericLiteralSeparator")), NT("DecimalDigits")),
      NT("NonOctalDecimalIntegerLiteral")
    )
  )
);

rules.set("DecimalDigits", () =>
  Diagram(
    OneOrMore(
      NT("DecimalDigit"),
      Optional(NT("NumericLiteralSeparator"))
    )
  )
);

rules.set("DecimalDigit", () =>
  Diagram(
    Choice(0, T("0"), T("1"), T("2"), T("3"), T("4"), T("5"), T("6"), T("7"), T("8"), T("9"))
  )
);

rules.set("NonZeroDigit", () =>
  Diagram(
    Choice(0, T("1"), T("2"), T("3"), T("4"), T("5"), T("6"), T("7"), T("8"), T("9"))
  )
);

rules.set("NumericLiteralSeparator", () =>
  Diagram(T("_"))
);

rules.set("ExponentPart", () =>
  Diagram(
    Sequence(NT("ExponentIndicator"), NT("SignedInteger"))
  )
);

rules.set("ExponentIndicator", () =>
  Diagram(
    Choice(0, T("e"), T("E"))
  )
);

rules.set("SignedInteger", () =>
  Diagram(
    Choice(0,
      NT("DecimalDigits"),
      Sequence(T("+"), NT("DecimalDigits")),
      Sequence(T("-"), NT("DecimalDigits"))
    )
  )
);

rules.set("BigIntLiteralSuffix", () =>
  Diagram(T("n"))
);

rules.set("DecimalBigIntegerLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(T("0"), NT("BigIntLiteralSuffix")),
      Sequence(NT("NonZeroDigit"), Optional(NT("DecimalDigits")), NT("BigIntLiteralSuffix")),
      Sequence(NT("NonZeroDigit"), NT("NumericLiteralSeparator"), NT("DecimalDigits"), NT("BigIntLiteralSuffix"))
    )
  )
);

rules.set("NonDecimalIntegerLiteral", () =>
  Diagram(
    Choice(0,
      NT("BinaryIntegerLiteral"),
      NT("OctalIntegerLiteral"),
      NT("HexIntegerLiteral")
    )
  )
);

rules.set("BinaryIntegerLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(T("0b"), NT("BinaryDigits")),
      Sequence(T("0B"), NT("BinaryDigits"))
    )
  )
);

rules.set("BinaryDigits", () =>
  Diagram(
    OneOrMore(NT("BinaryDigit"), Optional(NT("NumericLiteralSeparator")))
  )
);

rules.set("BinaryDigit", () =>
  Diagram(
    Choice(0, T("0"), T("1"))
  )
);

rules.set("OctalIntegerLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(T("0o"), NT("OctalDigits")),
      Sequence(T("0O"), NT("OctalDigits"))
    )
  )
);

rules.set("OctalDigits", () =>
  Diagram(
    OneOrMore(NT("OctalDigit"), Optional(NT("NumericLiteralSeparator")))
  )
);

rules.set("OctalDigit", () =>
  Diagram(
    Choice(0, T("0"), T("1"), T("2"), T("3"), T("4"), T("5"), T("6"), T("7"))
  )
);

rules.set("HexIntegerLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(T("0x"), NT("HexDigits")),
      Sequence(T("0X"), NT("HexDigits"))
    )
  )
);

rules.set("HexDigits", () =>
  Diagram(
    OneOrMore(NT("HexDigit"), Optional(NT("NumericLiteralSeparator")))
  )
);

rules.set("HexDigit", () =>
  Diagram(
    Choice(0,
      T("0"), T("1"), T("2"), T("3"), T("4"), T("5"), T("6"), T("7"), T("8"), T("9"),
      T("a"), T("b"), T("c"), T("d"), T("e"), T("f"),
      T("A"), T("B"), T("C"), T("D"), T("E"), T("F")
    )
  )
);

rules.set("LegacyOctalIntegerLiteral", () =>
  Diagram(
    Sequence(T("0"), OneOrMore(NT("OctalDigit")))
  )
);

rules.set("StringLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(T('"'), Optional(NT("DoubleStringCharacters")), T('"')),
      Sequence(T("'"), Optional(NT("SingleStringCharacters")), T("'"))
    )
  )
);

rules.set("DoubleStringCharacters", () =>
  Diagram(
    OneOrMore(NT("DoubleStringCharacter"))
  )
);

rules.set("SingleStringCharacters", () =>
  Diagram(
    OneOrMore(NT("SingleStringCharacter"))
  )
);

rules.set("DoubleStringCharacter", () =>
  Diagram(
    Choice(0,
      Comment('SourceCharacter but not " or \\ or LineTerminator'),
      T("<LS>"),
      T("<PS>"),
      Sequence(T("\\"), NT("EscapeSequence")),
      NT("LineContinuation")
    )
  )
);

rules.set("SingleStringCharacter", () =>
  Diagram(
    Choice(0,
      Comment("SourceCharacter but not ' or \\ or LineTerminator"),
      T("<LS>"),
      T("<PS>"),
      Sequence(T("\\"), NT("EscapeSequence")),
      NT("LineContinuation")
    )
  )
);

rules.set("LineContinuation", () =>
  Diagram(
    Sequence(T("\\"), NT("LineTerminatorSequence"))
  )
);

rules.set("EscapeSequence", () =>
  Diagram(
    Choice(0,
      NT("CharacterEscapeSequence"),
      Sequence(T("0"), Comment("[lookahead ∉ DecimalDigit]")),
      NT("LegacyOctalEscapeSequence"),
      NT("NonOctalDecimalEscapeSequence"),
      NT("HexEscapeSequence"),
      NT("UnicodeEscapeSequence")
    )
  )
);

rules.set("CharacterEscapeSequence", () =>
  Diagram(
    Choice(0,
      NT("SingleEscapeCharacter"),
      NT("NonEscapeCharacter")
    )
  )
);

rules.set("SingleEscapeCharacter", () =>
  Diagram(
    Choice(0,
      T("'"), T('"'), T("\\"), T("b"), T("f"), T("n"), T("r"), T("t"), T("v")
    )
  )
);

rules.set("HexEscapeSequence", () =>
  Diagram(
    Sequence(T("x"), NT("HexDigit"), NT("HexDigit"))
  )
);

rules.set("UnicodeEscapeSequence", () =>
  Diagram(
    Choice(0,
      Sequence(T("u"), NT("Hex4Digits")),
      Sequence(T("u{"), NT("CodePoint"), T("}"))
    )
  )
);

rules.set("Hex4Digits", () =>
  Diagram(
    Sequence(NT("HexDigit"), NT("HexDigit"), NT("HexDigit"), NT("HexDigit"))
  )
);

rules.set("RegularExpressionLiteral", () =>
  Diagram(
    Sequence(
      T("/"),
      NT("RegularExpressionBody"),
      T("/"),
      NT("RegularExpressionFlags")
    )
  )
);

rules.set("RegularExpressionBody", () =>
  Diagram(
    Sequence(NT("RegularExpressionFirstChar"), NT("RegularExpressionChars"))
  )
);

rules.set("RegularExpressionChars", () =>
  Diagram(
    ZeroOrMore(NT("RegularExpressionChar"))
  )
);

rules.set("RegularExpressionFlags", () =>
  Diagram(
    ZeroOrMore(NT("IdentifierPartChar"))
  )
);

rules.set("Template", () =>
  Diagram(
    Choice(0,
      NT("NoSubstitutionTemplate"),
      NT("TemplateHead")
    )
  )
);

rules.set("NoSubstitutionTemplate", () =>
  Diagram(
    Sequence(T("`"), Optional(NT("TemplateCharacters")), T("`"))
  )
);

rules.set("TemplateHead", () =>
  Diagram(
    Sequence(T("`"), Optional(NT("TemplateCharacters")), T("${"))
  )
);

rules.set("TemplateSubstitutionTail", () =>
  Diagram(
    Choice(0,
      NT("TemplateMiddle"),
      NT("TemplateTail")
    )
  )
);

rules.set("TemplateMiddle", () =>
  Diagram(
    Sequence(T("}"), Optional(NT("TemplateCharacters")), T("${"))
  )
);

rules.set("TemplateTail", () =>
  Diagram(
    Sequence(T("}"), Optional(NT("TemplateCharacters")), T("`"))
  )
);

rules.set("TemplateCharacters", () =>
  Diagram(
    OneOrMore(NT("TemplateCharacter"))
  )
);

// ===== A.2 Expressions =====

rules.set("IdentifierReference", () =>
  Diagram(
    Choice(0,
      NT("Identifier"),
      T("yield"),
      T("await")
    )
  )
);

rules.set("BindingIdentifier", () =>
  Diagram(
    Choice(0,
      NT("Identifier"),
      T("yield"),
      T("await")
    )
  )
);

rules.set("LabelIdentifier", () =>
  Diagram(
    Choice(0,
      NT("Identifier"),
      T("yield"),
      T("await")
    )
  )
);

rules.set("Identifier", () =>
  Diagram(
    Sequence(NT("IdentifierName"), Comment("but not ReservedWord"))
  )
);

rules.set("PrimaryExpression", () =>
  Diagram(
    Choice(0,
      T("this"),
      NT("IdentifierReference"),
      NT("Literal"),
      NT("ArrayLiteral"),
      NT("ObjectLiteral"),
      NT("FunctionExpression"),
      NT("ClassExpression"),
      NT("GeneratorExpression"),
      NT("AsyncFunctionExpression"),
      NT("AsyncGeneratorExpression"),
      NT("RegularExpressionLiteral"),
      NT("TemplateLiteral"),
      NT("CoverParenthesizedExpressionAndArrowParameterList")
    )
  )
);

rules.set("CoverParenthesizedExpressionAndArrowParameterList", () =>
  Diagram(
    Choice(0,
      Sequence(T("("), NT("Expression"), T(")")),
      Sequence(T("("), NT("Expression"), T(","), T(")")),
      Sequence(T("("), T(")")),
      Sequence(T("("), T("..."), NT("BindingIdentifier"), T(")")),
      Sequence(T("("), T("..."), NT("BindingPattern"), T(")")),
      Sequence(T("("), NT("Expression"), T(","), T("..."), NT("BindingIdentifier"), T(")")),
      Sequence(T("("), NT("Expression"), T(","), T("..."), NT("BindingPattern"), T(")"))
    )
  )
);

rules.set("ParenthesizedExpression", () =>
  Diagram(
    Sequence(T("("), NT("Expression"), T(")"))
  )
);

rules.set("Literal", () =>
  Diagram(
    Choice(0,
      NT("NullLiteral"),
      NT("BooleanLiteral"),
      NT("NumericLiteral"),
      NT("StringLiteral")
    )
  )
);

rules.set("ArrayLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(T("["), Optional(NT("Elision")), T("]")),
      Sequence(T("["), NT("ElementList"), T("]")),
      Sequence(T("["), NT("ElementList"), T(","), Optional(NT("Elision")), T("]"))
    )
  )
);

rules.set("ElementList", () =>
  Diagram(
    Sequence(
      Optional(NT("Elision")),
      Choice(0, NT("AssignmentExpression"), NT("SpreadElement")),
      ZeroOrMore(
        Sequence(T(","), Optional(NT("Elision")), Choice(0, NT("AssignmentExpression"), NT("SpreadElement")))
      )
    )
  )
);

rules.set("Elision", () =>
  Diagram(
    OneOrMore(T(","))
  )
);

rules.set("SpreadElement", () =>
  Diagram(
    Sequence(T("..."), NT("AssignmentExpression"))
  )
);

rules.set("ObjectLiteral", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("PropertyDefinitionList"), T("}")),
      Sequence(T("{"), NT("PropertyDefinitionList"), T(","), T("}"))
    )
  )
);

rules.set("PropertyDefinitionList", () =>
  Diagram(
    Sequence(
      NT("PropertyDefinition"),
      ZeroOrMore(Sequence(T(","), NT("PropertyDefinition")))
    )
  )
);

rules.set("PropertyDefinition", () =>
  Diagram(
    Choice(0,
      NT("IdentifierReference"),
      NT("CoverInitializedName"),
      Sequence(NT("PropertyName"), T(":"), NT("AssignmentExpression")),
      NT("MethodDefinition"),
      Sequence(T("..."), NT("AssignmentExpression"))
    )
  )
);

rules.set("PropertyName", () =>
  Diagram(
    Choice(0,
      NT("LiteralPropertyName"),
      NT("ComputedPropertyName")
    )
  )
);

rules.set("LiteralPropertyName", () =>
  Diagram(
    Choice(0,
      NT("IdentifierName"),
      NT("StringLiteral"),
      NT("NumericLiteral")
    )
  )
);

rules.set("ComputedPropertyName", () =>
  Diagram(
    Sequence(T("["), NT("AssignmentExpression"), T("]"))
  )
);

rules.set("CoverInitializedName", () =>
  Diagram(
    Sequence(NT("IdentifierReference"), NT("Initializer"))
  )
);

rules.set("Initializer", () =>
  Diagram(
    Sequence(T("="), NT("AssignmentExpression"))
  )
);

rules.set("TemplateLiteral", () =>
  Diagram(
    Choice(0,
      NT("NoSubstitutionTemplate"),
      NT("SubstitutionTemplate")
    )
  )
);

rules.set("SubstitutionTemplate", () =>
  Diagram(
    Sequence(NT("TemplateHead"), NT("Expression"), NT("TemplateSpans"))
  )
);

rules.set("TemplateSpans", () =>
  Diagram(
    Choice(0,
      NT("TemplateTail"),
      Sequence(NT("TemplateMiddleList"), NT("TemplateTail"))
    )
  )
);

rules.set("TemplateMiddleList", () =>
  Diagram(
    OneOrMore(Sequence(NT("TemplateMiddle"), NT("Expression")))
  )
);

rules.set("MemberExpression", () =>
  Diagram(
    Sequence(
      Choice(0,
        NT("PrimaryExpression"),
        NT("SuperProperty"),
        NT("MetaProperty"),
        Sequence(T("new"), NT("MemberExpression"), NT("Arguments"))
      ),
      ZeroOrMore(
        Choice(0,
          Sequence(T("["), NT("Expression"), T("]")),
          Sequence(T("."), NT("IdentifierName")),
          NT("TemplateLiteral"),
          Sequence(T("."), NT("PrivateIdentifier"))
        )
      )
    )
  )
);

rules.set("SuperProperty", () =>
  Diagram(
    Choice(0,
      Sequence(T("super"), T("["), NT("Expression"), T("]")),
      Sequence(T("super"), T("."), NT("IdentifierName"))
    )
  )
);

rules.set("MetaProperty", () =>
  Diagram(
    Choice(0,
      NT("NewTarget"),
      NT("ImportMeta")
    )
  )
);

rules.set("NewTarget", () =>
  Diagram(
    Sequence(T("new"), T("."), T("target"))
  )
);

rules.set("ImportMeta", () =>
  Diagram(
    Sequence(T("import"), T("."), T("meta"))
  )
);

rules.set("NewExpression", () =>
  Diagram(
    Choice(0,
      NT("MemberExpression"),
      Sequence(T("new"), NT("NewExpression"))
    )
  )
);

rules.set("CallExpression", () =>
  Diagram(
    Sequence(
      Choice(0,
        NT("CoverCallExpressionAndAsyncArrowHead"),
        NT("SuperCall"),
        NT("ImportCall"),
        Sequence(NT("CallExpression"), NT("Arguments"))
      ),
      ZeroOrMore(
        Choice(0,
          NT("Arguments"),
          Sequence(T("["), NT("Expression"), T("]")),
          Sequence(T("."), NT("IdentifierName")),
          NT("TemplateLiteral"),
          Sequence(T("."), NT("PrivateIdentifier"))
        )
      )
    )
  )
);

rules.set("SuperCall", () =>
  Diagram(
    Sequence(T("super"), NT("Arguments"))
  )
);

rules.set("ImportCall", () =>
  Diagram(
    Choice(0,
      Sequence(T("import"), T("("), NT("AssignmentExpression"), Optional(T(",")), T(")")),
      Sequence(T("import"), T("("), NT("AssignmentExpression"), T(","), NT("AssignmentExpression"), Optional(T(",")), T(")"))
    )
  )
);

rules.set("Arguments", () =>
  Diagram(
    Choice(0,
      Sequence(T("("), T(")")),
      Sequence(T("("), NT("ArgumentList"), T(")")),
      Sequence(T("("), NT("ArgumentList"), T(","), T(")"))
    )
  )
);

rules.set("ArgumentList", () =>
  Diagram(
    Sequence(
      Choice(0, NT("AssignmentExpression"), Sequence(T("..."), NT("AssignmentExpression"))),
      ZeroOrMore(
        Sequence(T(","), Choice(0, NT("AssignmentExpression"), Sequence(T("..."), NT("AssignmentExpression"))))
      )
    )
  )
);

rules.set("OptionalExpression", () =>
  Diagram(
    Sequence(
      Choice(0, NT("MemberExpression"), NT("CallExpression"), NT("OptionalExpression")),
      NT("OptionalChain")
    )
  )
);

rules.set("OptionalChain", () =>
  Diagram(
    Sequence(
      Choice(0,
        Sequence(T("?."), NT("Arguments")),
        Sequence(T("?."), T("["), NT("Expression"), T("]")),
        Sequence(T("?."), NT("IdentifierName")),
        Sequence(T("?."), NT("TemplateLiteral")),
        Sequence(T("?."), NT("PrivateIdentifier"))
      ),
      ZeroOrMore(
        Choice(0,
          NT("Arguments"),
          Sequence(T("["), NT("Expression"), T("]")),
          Sequence(T("."), NT("IdentifierName")),
          NT("TemplateLiteral"),
          Sequence(T("."), NT("PrivateIdentifier"))
        )
      )
    )
  )
);

rules.set("LeftHandSideExpression", () =>
  Diagram(
    Choice(0,
      NT("NewExpression"),
      NT("CallExpression"),
      NT("OptionalExpression")
    )
  )
);

rules.set("UpdateExpression", () =>
  Diagram(
    Choice(0,
      NT("LeftHandSideExpression"),
      Sequence(NT("LeftHandSideExpression"), Comment("[no LineTerminator]"), T("++")),
      Sequence(NT("LeftHandSideExpression"), Comment("[no LineTerminator]"), T("--")),
      Sequence(T("++"), NT("UnaryExpression")),
      Sequence(T("--"), NT("UnaryExpression"))
    )
  )
);

rules.set("UnaryExpression", () =>
  Diagram(
    Choice(0,
      NT("UpdateExpression"),
      Sequence(T("delete"), NT("UnaryExpression")),
      Sequence(T("void"), NT("UnaryExpression")),
      Sequence(T("typeof"), NT("UnaryExpression")),
      Sequence(T("+"), NT("UnaryExpression")),
      Sequence(T("-"), NT("UnaryExpression")),
      Sequence(T("~"), NT("UnaryExpression")),
      Sequence(T("!"), NT("UnaryExpression")),
      NT("AwaitExpression")
    )
  )
);

rules.set("ExponentiationExpression", () =>
  Diagram(
    Choice(0,
      NT("UnaryExpression"),
      Sequence(NT("UpdateExpression"), T("**"), NT("ExponentiationExpression"))
    )
  )
);

rules.set("MultiplicativeExpression", () =>
  Diagram(
    Sequence(
      NT("ExponentiationExpression"),
      ZeroOrMore(Sequence(NT("MultiplicativeOperator"), NT("ExponentiationExpression")))
    )
  )
);

rules.set("MultiplicativeOperator", () =>
  Diagram(
    Choice(0, T("*"), T("/"), T("%"))
  )
);

rules.set("AdditiveExpression", () =>
  Diagram(
    Sequence(
      NT("MultiplicativeExpression"),
      ZeroOrMore(
        Choice(0,
          Sequence(T("+"), NT("MultiplicativeExpression")),
          Sequence(T("-"), NT("MultiplicativeExpression"))
        )
      )
    )
  )
);

rules.set("ShiftExpression", () =>
  Diagram(
    Sequence(
      NT("AdditiveExpression"),
      ZeroOrMore(
        Choice(0,
          Sequence(T("<<"), NT("AdditiveExpression")),
          Sequence(T(">>"), NT("AdditiveExpression")),
          Sequence(T(">>>"), NT("AdditiveExpression"))
        )
      )
    )
  )
);

rules.set("RelationalExpression", () =>
  Diagram(
    Sequence(
      NT("ShiftExpression"),
      ZeroOrMore(
        Choice(0,
          Sequence(T("<"), NT("ShiftExpression")),
          Sequence(T(">"), NT("ShiftExpression")),
          Sequence(T("<="), NT("ShiftExpression")),
          Sequence(T(">="), NT("ShiftExpression")),
          Sequence(T("instanceof"), NT("ShiftExpression")),
          Sequence(T("in"), NT("ShiftExpression")),
          Sequence(NT("PrivateIdentifier"), T("in"), NT("ShiftExpression"))
        )
      )
    )
  )
);

rules.set("EqualityExpression", () =>
  Diagram(
    Sequence(
      NT("RelationalExpression"),
      ZeroOrMore(
        Choice(0,
          Sequence(T("=="), NT("RelationalExpression")),
          Sequence(T("!="), NT("RelationalExpression")),
          Sequence(T("==="), NT("RelationalExpression")),
          Sequence(T("!=="), NT("RelationalExpression"))
        )
      )
    )
  )
);

rules.set("BitwiseANDExpression", () =>
  Diagram(
    Sequence(
      NT("EqualityExpression"),
      ZeroOrMore(Sequence(T("&"), NT("EqualityExpression")))
    )
  )
);

rules.set("BitwiseXORExpression", () =>
  Diagram(
    Sequence(
      NT("BitwiseANDExpression"),
      ZeroOrMore(Sequence(T("^"), NT("BitwiseANDExpression")))
    )
  )
);

rules.set("BitwiseORExpression", () =>
  Diagram(
    Sequence(
      NT("BitwiseXORExpression"),
      ZeroOrMore(Sequence(T("|"), NT("BitwiseXORExpression")))
    )
  )
);

rules.set("LogicalANDExpression", () =>
  Diagram(
    Sequence(
      NT("BitwiseORExpression"),
      ZeroOrMore(Sequence(T("&&"), NT("BitwiseORExpression")))
    )
  )
);

rules.set("LogicalORExpression", () =>
  Diagram(
    Sequence(
      NT("LogicalANDExpression"),
      ZeroOrMore(Sequence(T("||"), NT("LogicalANDExpression")))
    )
  )
);

rules.set("CoalesceExpression", () =>
  Diagram(
    Sequence(NT("CoalesceExpressionHead"), T("??"), NT("BitwiseORExpression"))
  )
);

rules.set("CoalesceExpressionHead", () =>
  Diagram(
    Choice(0,
      NT("CoalesceExpression"),
      NT("BitwiseORExpression")
    )
  )
);

rules.set("ShortCircuitExpression", () =>
  Diagram(
    Choice(0,
      NT("LogicalORExpression"),
      NT("CoalesceExpression")
    )
  )
);

rules.set("ConditionalExpression", () =>
  Diagram(
    Choice(0,
      NT("ShortCircuitExpression"),
      Sequence(NT("ShortCircuitExpression"), T("?"), NT("AssignmentExpression"), T(":"), NT("AssignmentExpression"))
    )
  )
);

rules.set("AssignmentExpression", () =>
  Diagram(
    Choice(0,
      NT("ConditionalExpression"),
      NT("YieldExpression"),
      NT("ArrowFunction"),
      NT("AsyncArrowFunction"),
      Sequence(NT("LeftHandSideExpression"), T("="), NT("AssignmentExpression")),
      Sequence(NT("LeftHandSideExpression"), NT("AssignmentOperator"), NT("AssignmentExpression")),
      Sequence(NT("LeftHandSideExpression"), T("&&="), NT("AssignmentExpression")),
      Sequence(NT("LeftHandSideExpression"), T("||="), NT("AssignmentExpression")),
      Sequence(NT("LeftHandSideExpression"), T("??="), NT("AssignmentExpression"))
    )
  )
);

rules.set("AssignmentOperator", () =>
  Diagram(
    Choice(0,
      T("*="), T("/="), T("%="), T("+="), T("-="),
      T("<<="), T(">>="), T(">>>="), T("&="), T("^="), T("|="), T("**=")
    )
  )
);

rules.set("AssignmentPattern", () =>
  Diagram(
    Choice(0,
      NT("ObjectAssignmentPattern"),
      NT("ArrayAssignmentPattern")
    )
  )
);

rules.set("ObjectAssignmentPattern", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("AssignmentRestProperty"), T("}")),
      Sequence(T("{"), NT("AssignmentPropertyList"), T("}")),
      Sequence(T("{"), NT("AssignmentPropertyList"), T(","), Optional(NT("AssignmentRestProperty")), T("}"))
    )
  )
);

rules.set("ArrayAssignmentPattern", () =>
  Diagram(
    Choice(0,
      Sequence(T("["), Optional(NT("Elision")), Optional(NT("AssignmentRestElement")), T("]")),
      Sequence(T("["), NT("AssignmentElementList"), T("]")),
      Sequence(T("["), NT("AssignmentElementList"), T(","), Optional(NT("Elision")), Optional(NT("AssignmentRestElement")), T("]"))
    )
  )
);

rules.set("Expression", () =>
  Diagram(
    Sequence(
      NT("AssignmentExpression"),
      ZeroOrMore(Sequence(T(","), NT("AssignmentExpression")))
    )
  )
);

// ===== A.3 Statements =====

rules.set("Statement", () =>
  Diagram(
    Choice(0,
      NT("BlockStatement"),
      NT("VariableStatement"),
      NT("EmptyStatement"),
      NT("ExpressionStatement"),
      NT("IfStatement"),
      NT("BreakableStatement"),
      NT("ContinueStatement"),
      NT("BreakStatement"),
      NT("ReturnStatement"),
      NT("WithStatement"),
      NT("LabelledStatement"),
      NT("ThrowStatement"),
      NT("TryStatement"),
      NT("DebuggerStatement")
    )
  )
);

rules.set("Declaration", () =>
  Diagram(
    Choice(0,
      NT("HoistableDeclaration"),
      NT("ClassDeclaration"),
      NT("LexicalDeclaration")
    )
  )
);

rules.set("HoistableDeclaration", () =>
  Diagram(
    Choice(0,
      NT("FunctionDeclaration"),
      NT("GeneratorDeclaration"),
      NT("AsyncFunctionDeclaration"),
      NT("AsyncGeneratorDeclaration")
    )
  )
);

rules.set("BreakableStatement", () =>
  Diagram(
    Choice(0,
      NT("IterationStatement"),
      NT("SwitchStatement")
    )
  )
);

rules.set("BlockStatement", () =>
  Diagram(NT("Block"))
);

rules.set("Block", () =>
  Diagram(
    Sequence(T("{"), Optional(NT("StatementList")), T("}"))
  )
);

rules.set("StatementList", () =>
  Diagram(
    OneOrMore(NT("StatementListItem"))
  )
);

rules.set("StatementListItem", () =>
  Diagram(
    Choice(0,
      NT("Statement"),
      NT("Declaration")
    )
  )
);

rules.set("LexicalDeclaration", () =>
  Diagram(
    Sequence(NT("LetOrConst"), NT("BindingList"), T(";"))
  )
);

rules.set("LetOrConst", () =>
  Diagram(
    Choice(0, T("let"), T("const"))
  )
);

rules.set("BindingList", () =>
  Diagram(
    Sequence(
      NT("LexicalBinding"),
      ZeroOrMore(Sequence(T(","), NT("LexicalBinding")))
    )
  )
);

rules.set("LexicalBinding", () =>
  Diagram(
    Choice(0,
      Sequence(NT("BindingIdentifier"), Optional(NT("Initializer"))),
      Sequence(NT("BindingPattern"), NT("Initializer"))
    )
  )
);

rules.set("VariableStatement", () =>
  Diagram(
    Sequence(T("var"), NT("VariableDeclarationList"), T(";"))
  )
);

rules.set("VariableDeclarationList", () =>
  Diagram(
    Sequence(
      NT("VariableDeclaration"),
      ZeroOrMore(Sequence(T(","), NT("VariableDeclaration")))
    )
  )
);

rules.set("VariableDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(NT("BindingIdentifier"), Optional(NT("Initializer"))),
      Sequence(NT("BindingPattern"), NT("Initializer"))
    )
  )
);

rules.set("BindingPattern", () =>
  Diagram(
    Choice(0,
      NT("ObjectBindingPattern"),
      NT("ArrayBindingPattern")
    )
  )
);

rules.set("ObjectBindingPattern", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("BindingRestProperty"), T("}")),
      Sequence(T("{"), NT("BindingPropertyList"), T("}")),
      Sequence(T("{"), NT("BindingPropertyList"), T(","), Optional(NT("BindingRestProperty")), T("}"))
    )
  )
);

rules.set("ArrayBindingPattern", () =>
  Diagram(
    Choice(0,
      Sequence(T("["), Optional(NT("Elision")), Optional(NT("BindingRestElement")), T("]")),
      Sequence(T("["), NT("BindingElementList"), T("]")),
      Sequence(T("["), NT("BindingElementList"), T(","), Optional(NT("Elision")), Optional(NT("BindingRestElement")), T("]"))
    )
  )
);

rules.set("BindingRestProperty", () =>
  Diagram(
    Sequence(T("..."), NT("BindingIdentifier"))
  )
);

rules.set("BindingPropertyList", () =>
  Diagram(
    Sequence(
      NT("BindingProperty"),
      ZeroOrMore(Sequence(T(","), NT("BindingProperty")))
    )
  )
);

rules.set("BindingElementList", () =>
  Diagram(
    Sequence(
      NT("BindingElisionElement"),
      ZeroOrMore(Sequence(T(","), NT("BindingElisionElement")))
    )
  )
);

rules.set("BindingElisionElement", () =>
  Diagram(
    Sequence(Optional(NT("Elision")), NT("BindingElement"))
  )
);

rules.set("BindingProperty", () =>
  Diagram(
    Choice(0,
      NT("SingleNameBinding"),
      Sequence(NT("PropertyName"), T(":"), NT("BindingElement"))
    )
  )
);

rules.set("BindingElement", () =>
  Diagram(
    Choice(0,
      NT("SingleNameBinding"),
      Sequence(NT("BindingPattern"), Optional(NT("Initializer")))
    )
  )
);

rules.set("SingleNameBinding", () =>
  Diagram(
    Sequence(NT("BindingIdentifier"), Optional(NT("Initializer")))
  )
);

rules.set("BindingRestElement", () =>
  Diagram(
    Choice(0,
      Sequence(T("..."), NT("BindingIdentifier")),
      Sequence(T("..."), NT("BindingPattern"))
    )
  )
);

rules.set("EmptyStatement", () =>
  Diagram(T(";"))
);

rules.set("ExpressionStatement", () =>
  Diagram(
    Sequence(
      Comment("[lookahead ∉ {, function, async function, class, let [}"),
      NT("Expression"),
      T(";")
    )
  )
);

rules.set("IfStatement", () =>
  Diagram(
    Choice(0,
      Sequence(T("if"), T("("), NT("Expression"), T(")"), NT("Statement"), T("else"), NT("Statement")),
      Sequence(T("if"), T("("), NT("Expression"), T(")"), NT("Statement"), Comment("[lookahead ≠ else]"))
    )
  )
);

rules.set("IterationStatement", () =>
  Diagram(
    Choice(0,
      NT("DoWhileStatement"),
      NT("WhileStatement"),
      NT("ForStatement"),
      NT("ForInOfStatement")
    )
  )
);

rules.set("DoWhileStatement", () =>
  Diagram(
    Sequence(T("do"), NT("Statement"), T("while"), T("("), NT("Expression"), T(")"), T(";"))
  )
);

rules.set("WhileStatement", () =>
  Diagram(
    Sequence(T("while"), T("("), NT("Expression"), T(")"), NT("Statement"))
  )
);

rules.set("ForStatement", () =>
  Diagram(
    Choice(0,
      Sequence(T("for"), T("("), Optional(NT("Expression")), T(";"), Optional(NT("Expression")), T(";"), Optional(NT("Expression")), T(")"), NT("Statement")),
      Sequence(T("for"), T("("), T("var"), NT("VariableDeclarationList"), T(";"), Optional(NT("Expression")), T(";"), Optional(NT("Expression")), T(")"), NT("Statement")),
      Sequence(T("for"), T("("), NT("LexicalDeclaration"), Optional(NT("Expression")), T(";"), Optional(NT("Expression")), T(")"), NT("Statement"))
    )
  )
);

rules.set("ForInOfStatement", () =>
  Diagram(
    Choice(0,
      Sequence(T("for"), T("("), NT("LeftHandSideExpression"), T("in"), NT("Expression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("("), T("var"), NT("ForBinding"), T("in"), NT("Expression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("("), NT("ForDeclaration"), T("in"), NT("Expression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("("), NT("LeftHandSideExpression"), T("of"), NT("AssignmentExpression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("("), T("var"), NT("ForBinding"), T("of"), NT("AssignmentExpression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("("), NT("ForDeclaration"), T("of"), NT("AssignmentExpression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("await"), T("("), NT("LeftHandSideExpression"), T("of"), NT("AssignmentExpression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("await"), T("("), T("var"), NT("ForBinding"), T("of"), NT("AssignmentExpression"), T(")"), NT("Statement")),
      Sequence(T("for"), T("await"), T("("), NT("ForDeclaration"), T("of"), NT("AssignmentExpression"), T(")"), NT("Statement"))
    )
  )
);

rules.set("ForDeclaration", () =>
  Diagram(
    Sequence(NT("LetOrConst"), NT("ForBinding"))
  )
);

rules.set("ForBinding", () =>
  Diagram(
    Choice(0,
      NT("BindingIdentifier"),
      NT("BindingPattern")
    )
  )
);

rules.set("ContinueStatement", () =>
  Diagram(
    Choice(0,
      Sequence(T("continue"), T(";")),
      Sequence(T("continue"), Comment("[no LineTerminator]"), NT("LabelIdentifier"), T(";"))
    )
  )
);

rules.set("BreakStatement", () =>
  Diagram(
    Choice(0,
      Sequence(T("break"), T(";")),
      Sequence(T("break"), Comment("[no LineTerminator]"), NT("LabelIdentifier"), T(";"))
    )
  )
);

rules.set("ReturnStatement", () =>
  Diagram(
    Choice(0,
      Sequence(T("return"), T(";")),
      Sequence(T("return"), Comment("[no LineTerminator]"), NT("Expression"), T(";"))
    )
  )
);

rules.set("WithStatement", () =>
  Diagram(
    Sequence(T("with"), T("("), NT("Expression"), T(")"), NT("Statement"))
  )
);

rules.set("SwitchStatement", () =>
  Diagram(
    Sequence(T("switch"), T("("), NT("Expression"), T(")"), NT("CaseBlock"))
  )
);

rules.set("CaseBlock", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), Optional(NT("CaseClauses")), T("}")),
      Sequence(T("{"), Optional(NT("CaseClauses")), NT("DefaultClause"), Optional(NT("CaseClauses")), T("}"))
    )
  )
);

rules.set("CaseClauses", () =>
  Diagram(
    OneOrMore(NT("CaseClause"))
  )
);

rules.set("CaseClause", () =>
  Diagram(
    Sequence(T("case"), NT("Expression"), T(":"), Optional(NT("StatementList")))
  )
);

rules.set("DefaultClause", () =>
  Diagram(
    Sequence(T("default"), T(":"), Optional(NT("StatementList")))
  )
);

rules.set("LabelledStatement", () =>
  Diagram(
    Sequence(NT("LabelIdentifier"), T(":"), NT("LabelledItem"))
  )
);

rules.set("LabelledItem", () =>
  Diagram(
    Choice(0,
      NT("Statement"),
      NT("FunctionDeclaration")
    )
  )
);

rules.set("ThrowStatement", () =>
  Diagram(
    Sequence(T("throw"), Comment("[no LineTerminator]"), NT("Expression"), T(";"))
  )
);

rules.set("TryStatement", () =>
  Diagram(
    Choice(0,
      Sequence(T("try"), NT("Block"), NT("Catch")),
      Sequence(T("try"), NT("Block"), NT("Finally")),
      Sequence(T("try"), NT("Block"), NT("Catch"), NT("Finally"))
    )
  )
);

rules.set("Catch", () =>
  Diagram(
    Choice(0,
      Sequence(T("catch"), T("("), NT("CatchParameter"), T(")"), NT("Block")),
      Sequence(T("catch"), NT("Block"))
    )
  )
);

rules.set("Finally", () =>
  Diagram(
    Sequence(T("finally"), NT("Block"))
  )
);

rules.set("CatchParameter", () =>
  Diagram(
    Choice(0,
      NT("BindingIdentifier"),
      NT("BindingPattern")
    )
  )
);

rules.set("DebuggerStatement", () =>
  Diagram(
    Sequence(T("debugger"), T(";"))
  )
);

// ===== A.4 Functions and Classes =====

rules.set("UniqueFormalParameters", () =>
  Diagram(NT("FormalParameters"))
);

rules.set("FormalParameters", () =>
  Diagram(
    Choice(0,
      Comment("[empty]"),
      NT("FunctionRestParameter"),
      NT("FormalParameterList"),
      Sequence(NT("FormalParameterList"), T(",")),
      Sequence(NT("FormalParameterList"), T(","), NT("FunctionRestParameter"))
    )
  )
);

rules.set("FormalParameterList", () =>
  Diagram(
    Sequence(
      NT("FormalParameter"),
      ZeroOrMore(Sequence(T(","), NT("FormalParameter")))
    )
  )
);

rules.set("FunctionRestParameter", () =>
  Diagram(NT("BindingRestElement"))
);

rules.set("FormalParameter", () =>
  Diagram(NT("BindingElement"))
);

rules.set("FunctionDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("function"), NT("BindingIdentifier"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("FunctionBody"), T("}")),
      Sequence(T("function"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("FunctionBody"), T("}"))
    )
  )
);

rules.set("FunctionExpression", () =>
  Diagram(
    Sequence(T("function"), Optional(NT("BindingIdentifier")), T("("), NT("FormalParameters"), T(")"), T("{"), NT("FunctionBody"), T("}"))
  )
);

rules.set("FunctionBody", () =>
  Diagram(NT("FunctionStatementList"))
);

rules.set("FunctionStatementList", () =>
  Diagram(Optional(NT("StatementList")))
);

rules.set("ArrowFunction", () =>
  Diagram(
    Sequence(NT("ArrowParameters"), Comment("[no LineTerminator]"), T("=>"), NT("ConciseBody"))
  )
);

rules.set("ArrowParameters", () =>
  Diagram(
    Choice(0,
      NT("BindingIdentifier"),
      NT("CoverParenthesizedExpressionAndArrowParameterList")
    )
  )
);

rules.set("ConciseBody", () =>
  Diagram(
    Choice(0,
      Sequence(Comment("[lookahead ≠ {]"), NT("ExpressionBody")),
      Sequence(T("{"), NT("FunctionBody"), T("}"))
    )
  )
);

rules.set("ExpressionBody", () =>
  Diagram(NT("AssignmentExpression"))
);

rules.set("ArrowFormalParameters", () =>
  Diagram(
    Sequence(T("("), NT("UniqueFormalParameters"), T(")"))
  )
);

rules.set("AsyncArrowFunction", () =>
  Diagram(
    Choice(0,
      Sequence(T("async"), Comment("[no LineTerminator]"), NT("AsyncArrowBindingIdentifier"), Comment("[no LineTerminator]"), T("=>"), NT("AsyncConciseBody")),
      Sequence(NT("CoverCallExpressionAndAsyncArrowHead"), Comment("[no LineTerminator]"), T("=>"), NT("AsyncConciseBody"))
    )
  )
);

rules.set("AsyncConciseBody", () =>
  Diagram(
    Choice(0,
      Sequence(Comment("[lookahead ≠ {]"), NT("ExpressionBody")),
      Sequence(T("{"), NT("AsyncFunctionBody"), T("}"))
    )
  )
);

rules.set("AsyncArrowBindingIdentifier", () =>
  Diagram(NT("BindingIdentifier"))
);

rules.set("CoverCallExpressionAndAsyncArrowHead", () =>
  Diagram(
    Sequence(NT("MemberExpression"), NT("Arguments"))
  )
);

rules.set("AsyncArrowHead", () =>
  Diagram(
    Sequence(T("async"), Comment("[no LineTerminator]"), NT("ArrowFormalParameters"))
  )
);

rules.set("MethodDefinition", () =>
  Diagram(
    Choice(0,
      Sequence(NT("ClassElementName"), T("("), NT("UniqueFormalParameters"), T(")"), T("{"), NT("FunctionBody"), T("}")),
      NT("GeneratorMethod"),
      NT("AsyncMethod"),
      NT("AsyncGeneratorMethod"),
      Sequence(T("get"), NT("ClassElementName"), T("("), T(")"), T("{"), NT("FunctionBody"), T("}")),
      Sequence(T("set"), NT("ClassElementName"), T("("), NT("PropertySetParameterList"), T(")"), T("{"), NT("FunctionBody"), T("}"))
    )
  )
);

rules.set("PropertySetParameterList", () =>
  Diagram(NT("FormalParameter"))
);

rules.set("GeneratorDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("function"), T("*"), NT("BindingIdentifier"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("GeneratorBody"), T("}")),
      Sequence(T("function"), T("*"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("GeneratorBody"), T("}"))
    )
  )
);

rules.set("GeneratorExpression", () =>
  Diagram(
    Sequence(T("function"), T("*"), Optional(NT("BindingIdentifier")), T("("), NT("FormalParameters"), T(")"), T("{"), NT("GeneratorBody"), T("}"))
  )
);

rules.set("GeneratorMethod", () =>
  Diagram(
    Sequence(T("*"), NT("ClassElementName"), T("("), NT("UniqueFormalParameters"), T(")"), T("{"), NT("GeneratorBody"), T("}"))
  )
);

rules.set("GeneratorBody", () =>
  Diagram(NT("FunctionBody"))
);

rules.set("YieldExpression", () =>
  Diagram(
    Choice(0,
      T("yield"),
      Sequence(T("yield"), Comment("[no LineTerminator]"), NT("AssignmentExpression")),
      Sequence(T("yield"), Comment("[no LineTerminator]"), T("*"), NT("AssignmentExpression"))
    )
  )
);

rules.set("AsyncGeneratorDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("async"), Comment("[no LineTerminator]"), T("function"), T("*"), NT("BindingIdentifier"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("AsyncGeneratorBody"), T("}")),
      Sequence(T("async"), Comment("[no LineTerminator]"), T("function"), T("*"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("AsyncGeneratorBody"), T("}"))
    )
  )
);

rules.set("AsyncGeneratorExpression", () =>
  Diagram(
    Sequence(T("async"), Comment("[no LineTerminator]"), T("function"), T("*"), Optional(NT("BindingIdentifier")), T("("), NT("FormalParameters"), T(")"), T("{"), NT("AsyncGeneratorBody"), T("}"))
  )
);

rules.set("AsyncGeneratorMethod", () =>
  Diagram(
    Sequence(T("async"), Comment("[no LineTerminator]"), T("*"), NT("ClassElementName"), T("("), NT("UniqueFormalParameters"), T(")"), T("{"), NT("AsyncGeneratorBody"), T("}"))
  )
);

rules.set("AsyncGeneratorBody", () =>
  Diagram(NT("FunctionBody"))
);

rules.set("AsyncFunctionDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("async"), Comment("[no LineTerminator]"), T("function"), NT("BindingIdentifier"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("AsyncFunctionBody"), T("}")),
      Sequence(T("async"), Comment("[no LineTerminator]"), T("function"), T("("), NT("FormalParameters"), T(")"), T("{"), NT("AsyncFunctionBody"), T("}"))
    )
  )
);

rules.set("AsyncFunctionExpression", () =>
  Diagram(
    Sequence(T("async"), Comment("[no LineTerminator]"), T("function"), Optional(NT("BindingIdentifier")), T("("), NT("FormalParameters"), T(")"), T("{"), NT("AsyncFunctionBody"), T("}"))
  )
);

rules.set("AsyncMethod", () =>
  Diagram(
    Sequence(T("async"), Comment("[no LineTerminator]"), NT("ClassElementName"), T("("), NT("UniqueFormalParameters"), T(")"), T("{"), NT("AsyncFunctionBody"), T("}"))
  )
);

rules.set("AsyncFunctionBody", () =>
  Diagram(NT("FunctionBody"))
);

rules.set("AwaitExpression", () =>
  Diagram(
    Sequence(T("await"), NT("UnaryExpression"))
  )
);

rules.set("ClassDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("class"), NT("BindingIdentifier"), NT("ClassTail")),
      Sequence(T("class"), NT("ClassTail"))
    )
  )
);

rules.set("ClassExpression", () =>
  Diagram(
    Sequence(T("class"), Optional(NT("BindingIdentifier")), NT("ClassTail"))
  )
);

rules.set("ClassTail", () =>
  Diagram(
    Sequence(Optional(NT("ClassHeritage")), T("{"), Optional(NT("ClassBody")), T("}"))
  )
);

rules.set("ClassHeritage", () =>
  Diagram(
    Sequence(T("extends"), NT("LeftHandSideExpression"))
  )
);

rules.set("ClassBody", () =>
  Diagram(NT("ClassElementList"))
);

rules.set("ClassElementList", () =>
  Diagram(
    OneOrMore(NT("ClassElement"))
  )
);

rules.set("ClassElement", () =>
  Diagram(
    Choice(0,
      NT("MethodDefinition"),
      Sequence(T("static"), NT("MethodDefinition")),
      Sequence(NT("FieldDefinition"), T(";")),
      Sequence(T("static"), NT("FieldDefinition"), T(";")),
      NT("ClassStaticBlock"),
      T(";")
    )
  )
);

rules.set("FieldDefinition", () =>
  Diagram(
    Sequence(NT("ClassElementName"), Optional(NT("Initializer")))
  )
);

rules.set("ClassElementName", () =>
  Diagram(
    Choice(0,
      NT("PropertyName"),
      NT("PrivateIdentifier")
    )
  )
);

rules.set("ClassStaticBlock", () =>
  Diagram(
    Sequence(T("static"), T("{"), NT("ClassStaticBlockBody"), T("}"))
  )
);

rules.set("ClassStaticBlockBody", () =>
  Diagram(NT("ClassStaticBlockStatementList"))
);

rules.set("ClassStaticBlockStatementList", () =>
  Diagram(Optional(NT("StatementList")))
);

// ===== A.5 Scripts and Modules =====

rules.set("Script", () =>
  Diagram(Optional(NT("ScriptBody")))
);

rules.set("ScriptBody", () =>
  Diagram(NT("StatementList"))
);

rules.set("Module", () =>
  Diagram(Optional(NT("ModuleBody")))
);

rules.set("ModuleBody", () =>
  Diagram(NT("ModuleItemList"))
);

rules.set("ModuleItemList", () =>
  Diagram(
    OneOrMore(NT("ModuleItem"))
  )
);

rules.set("ModuleItem", () =>
  Diagram(
    Choice(0,
      NT("ImportDeclaration"),
      NT("ExportDeclaration"),
      NT("StatementListItem")
    )
  )
);

rules.set("ModuleExportName", () =>
  Diagram(
    Choice(0,
      NT("IdentifierName"),
      NT("StringLiteral")
    )
  )
);

rules.set("ImportDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("import"), NT("ImportClause"), NT("FromClause"), Optional(NT("WithClause")), T(";")),
      Sequence(T("import"), NT("ModuleSpecifier"), Optional(NT("WithClause")), T(";"))
    )
  )
);

rules.set("ImportClause", () =>
  Diagram(
    Choice(0,
      NT("ImportedDefaultBinding"),
      NT("NameSpaceImport"),
      NT("NamedImports"),
      Sequence(NT("ImportedDefaultBinding"), T(","), NT("NameSpaceImport")),
      Sequence(NT("ImportedDefaultBinding"), T(","), NT("NamedImports"))
    )
  )
);

rules.set("ImportedDefaultBinding", () =>
  Diagram(NT("ImportedBinding"))
);

rules.set("NameSpaceImport", () =>
  Diagram(
    Sequence(T("*"), T("as"), NT("ImportedBinding"))
  )
);

rules.set("NamedImports", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("ImportsList"), T("}")),
      Sequence(T("{"), NT("ImportsList"), T(","), T("}"))
    )
  )
);

rules.set("FromClause", () =>
  Diagram(
    Sequence(T("from"), NT("ModuleSpecifier"))
  )
);

rules.set("ImportsList", () =>
  Diagram(
    Sequence(
      NT("ImportSpecifier"),
      ZeroOrMore(Sequence(T(","), NT("ImportSpecifier")))
    )
  )
);

rules.set("ImportSpecifier", () =>
  Diagram(
    Choice(0,
      NT("ImportedBinding"),
      Sequence(NT("ModuleExportName"), T("as"), NT("ImportedBinding"))
    )
  )
);

rules.set("ModuleSpecifier", () =>
  Diagram(NT("StringLiteral"))
);

rules.set("ImportedBinding", () =>
  Diagram(NT("BindingIdentifier"))
);

rules.set("WithClause", () =>
  Diagram(
    Choice(0,
      Sequence(T("with"), T("{"), T("}")),
      Sequence(T("with"), T("{"), NT("WithEntries"), Optional(T(",")), T("}"))
    )
  )
);

rules.set("WithEntries", () =>
  Diagram(
    Sequence(
      NT("AttributeKey"), T(":"), NT("StringLiteral"),
      ZeroOrMore(Sequence(T(","), NT("AttributeKey"), T(":"), NT("StringLiteral")))
    )
  )
);

rules.set("AttributeKey", () =>
  Diagram(
    Choice(0,
      NT("IdentifierName"),
      NT("StringLiteral")
    )
  )
);

rules.set("ExportDeclaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("export"), NT("ExportFromClause"), NT("FromClause"), Optional(NT("WithClause")), T(";")),
      Sequence(T("export"), NT("NamedExports"), T(";")),
      Sequence(T("export"), NT("VariableStatement")),
      Sequence(T("export"), NT("Declaration")),
      Sequence(T("export"), T("default"), NT("HoistableDeclaration")),
      Sequence(T("export"), T("default"), NT("ClassDeclaration")),
      Sequence(T("export"), T("default"), Comment("[lookahead ∉ {function, async function, class}]"), NT("AssignmentExpression"), T(";"))
    )
  )
);

rules.set("ExportFromClause", () =>
  Diagram(
    Choice(0,
      T("*"),
      Sequence(T("*"), T("as"), NT("ModuleExportName")),
      NT("NamedExports")
    )
  )
);

rules.set("NamedExports", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("ExportsList"), T("}")),
      Sequence(T("{"), NT("ExportsList"), T(","), T("}"))
    )
  )
);

rules.set("ExportsList", () =>
  Diagram(
    Sequence(
      NT("ExportSpecifier"),
      ZeroOrMore(Sequence(T(","), NT("ExportSpecifier")))
    )
  )
);

rules.set("ExportSpecifier", () =>
  Diagram(
    Choice(0,
      NT("ModuleExportName"),
      Sequence(NT("ModuleExportName"), T("as"), NT("ModuleExportName"))
    )
  )
);

// --- Section organization ---

export type SectionId = "lexical" | "expressions" | "statements" | "functions" | "modules";

export const SECTION_ORDER: SectionId[] = [
  "lexical",
  "expressions",
  "statements",
  "functions",
  "modules"
];

export const SECTION_TITLES: Record<SectionId, string> = {
  lexical: "A.1 Lexical Grammar",
  expressions: "A.2 Expressions",
  statements: "A.3 Statements",
  functions: "A.4 Functions and Classes",
  modules: "A.5 Scripts and Modules"
};

export const SECTION_RULES: Record<SectionId, string[]> = {
  lexical: [
    "SourceCharacter",
    "InputElementDiv",
    "InputElementRegExp",
    "InputElementRegExpOrTemplateTail",
    "InputElementTemplateTail",
    "WhiteSpace",
    "LineTerminator",
    "LineTerminatorSequence",
    "Comment",
    "MultiLineComment",
    "SingleLineComment",
    "HashbangComment",
    "CommonToken",
    "PrivateIdentifier",
    "IdentifierName",
    "IdentifierStart",
    "IdentifierPart",
    "IdentifierStartChar",
    "IdentifierPartChar",
    "UnicodeIDStart",
    "UnicodeIDContinue",
    "ReservedWord",
    "Punctuator",
    "OptionalChainingPunctuator",
    "DivPunctuator",
    "RightBracePunctuator",
    "NullLiteral",
    "BooleanLiteral",
    "NumericLiteral",
    "DecimalLiteral",
    "DecimalIntegerLiteral",
    "DecimalDigits",
    "DecimalDigit",
    "NonZeroDigit",
    "NumericLiteralSeparator",
    "ExponentPart",
    "ExponentIndicator",
    "SignedInteger",
    "BigIntLiteralSuffix",
    "DecimalBigIntegerLiteral",
    "NonDecimalIntegerLiteral",
    "BinaryIntegerLiteral",
    "BinaryDigits",
    "BinaryDigit",
    "OctalIntegerLiteral",
    "OctalDigits",
    "OctalDigit",
    "HexIntegerLiteral",
    "HexDigits",
    "HexDigit",
    "LegacyOctalIntegerLiteral",
    "StringLiteral",
    "DoubleStringCharacters",
    "SingleStringCharacters",
    "DoubleStringCharacter",
    "SingleStringCharacter",
    "LineContinuation",
    "EscapeSequence",
    "CharacterEscapeSequence",
    "SingleEscapeCharacter",
    "HexEscapeSequence",
    "UnicodeEscapeSequence",
    "Hex4Digits",
    "RegularExpressionLiteral",
    "RegularExpressionBody",
    "RegularExpressionChars",
    "RegularExpressionFlags",
    "Template",
    "NoSubstitutionTemplate",
    "TemplateHead",
    "TemplateSubstitutionTail",
    "TemplateMiddle",
    "TemplateTail",
    "TemplateCharacters"
  ],
  expressions: [
    "IdentifierReference",
    "BindingIdentifier",
    "LabelIdentifier",
    "Identifier",
    "PrimaryExpression",
    "CoverParenthesizedExpressionAndArrowParameterList",
    "ParenthesizedExpression",
    "Literal",
    "ArrayLiteral",
    "ElementList",
    "Elision",
    "SpreadElement",
    "ObjectLiteral",
    "PropertyDefinitionList",
    "PropertyDefinition",
    "PropertyName",
    "LiteralPropertyName",
    "ComputedPropertyName",
    "CoverInitializedName",
    "Initializer",
    "TemplateLiteral",
    "SubstitutionTemplate",
    "TemplateSpans",
    "TemplateMiddleList",
    "MemberExpression",
    "SuperProperty",
    "MetaProperty",
    "NewTarget",
    "ImportMeta",
    "NewExpression",
    "CallExpression",
    "SuperCall",
    "ImportCall",
    "Arguments",
    "ArgumentList",
    "OptionalExpression",
    "OptionalChain",
    "LeftHandSideExpression",
    "UpdateExpression",
    "UnaryExpression",
    "ExponentiationExpression",
    "MultiplicativeExpression",
    "MultiplicativeOperator",
    "AdditiveExpression",
    "ShiftExpression",
    "RelationalExpression",
    "EqualityExpression",
    "BitwiseANDExpression",
    "BitwiseXORExpression",
    "BitwiseORExpression",
    "LogicalANDExpression",
    "LogicalORExpression",
    "CoalesceExpression",
    "CoalesceExpressionHead",
    "ShortCircuitExpression",
    "ConditionalExpression",
    "AssignmentExpression",
    "AssignmentOperator",
    "AssignmentPattern",
    "ObjectAssignmentPattern",
    "ArrayAssignmentPattern",
    "Expression"
  ],
  statements: [
    "Statement",
    "Declaration",
    "HoistableDeclaration",
    "BreakableStatement",
    "BlockStatement",
    "Block",
    "StatementList",
    "StatementListItem",
    "LexicalDeclaration",
    "LetOrConst",
    "BindingList",
    "LexicalBinding",
    "VariableStatement",
    "VariableDeclarationList",
    "VariableDeclaration",
    "BindingPattern",
    "ObjectBindingPattern",
    "ArrayBindingPattern",
    "BindingRestProperty",
    "BindingPropertyList",
    "BindingElementList",
    "BindingElisionElement",
    "BindingProperty",
    "BindingElement",
    "SingleNameBinding",
    "BindingRestElement",
    "EmptyStatement",
    "ExpressionStatement",
    "IfStatement",
    "IterationStatement",
    "DoWhileStatement",
    "WhileStatement",
    "ForStatement",
    "ForInOfStatement",
    "ForDeclaration",
    "ForBinding",
    "ContinueStatement",
    "BreakStatement",
    "ReturnStatement",
    "WithStatement",
    "SwitchStatement",
    "CaseBlock",
    "CaseClauses",
    "CaseClause",
    "DefaultClause",
    "LabelledStatement",
    "LabelledItem",
    "ThrowStatement",
    "TryStatement",
    "Catch",
    "Finally",
    "CatchParameter",
    "DebuggerStatement"
  ],
  functions: [
    "UniqueFormalParameters",
    "FormalParameters",
    "FormalParameterList",
    "FunctionRestParameter",
    "FormalParameter",
    "FunctionDeclaration",
    "FunctionExpression",
    "FunctionBody",
    "FunctionStatementList",
    "ArrowFunction",
    "ArrowParameters",
    "ConciseBody",
    "ExpressionBody",
    "ArrowFormalParameters",
    "AsyncArrowFunction",
    "AsyncConciseBody",
    "AsyncArrowBindingIdentifier",
    "CoverCallExpressionAndAsyncArrowHead",
    "AsyncArrowHead",
    "MethodDefinition",
    "PropertySetParameterList",
    "GeneratorDeclaration",
    "GeneratorExpression",
    "GeneratorMethod",
    "GeneratorBody",
    "YieldExpression",
    "AsyncGeneratorDeclaration",
    "AsyncGeneratorExpression",
    "AsyncGeneratorMethod",
    "AsyncGeneratorBody",
    "AsyncFunctionDeclaration",
    "AsyncFunctionExpression",
    "AsyncMethod",
    "AsyncFunctionBody",
    "AwaitExpression",
    "ClassDeclaration",
    "ClassExpression",
    "ClassTail",
    "ClassHeritage",
    "ClassBody",
    "ClassElementList",
    "ClassElement",
    "FieldDefinition",
    "ClassElementName",
    "ClassStaticBlock",
    "ClassStaticBlockBody",
    "ClassStaticBlockStatementList"
  ],
  modules: [
    "Script",
    "ScriptBody",
    "Module",
    "ModuleBody",
    "ModuleItemList",
    "ModuleItem",
    "ModuleExportName",
    "ImportDeclaration",
    "ImportClause",
    "ImportedDefaultBinding",
    "NameSpaceImport",
    "NamedImports",
    "FromClause",
    "ImportsList",
    "ImportSpecifier",
    "ModuleSpecifier",
    "ImportedBinding",
    "WithClause",
    "WithEntries",
    "AttributeKey",
    "ExportDeclaration",
    "ExportFromClause",
    "NamedExports",
    "ExportsList",
    "ExportSpecifier"
  ]
};

// Rule name type for type safety
export type RuleName = string;

// Expose safe accessors for React UI.
export function getRuleFactory(name: RuleName): (() => any) | undefined {
  return rules.get(name);
}

export function createRuleDiagram(name: RuleName): any {
  const factory = rules.get(name);
  if (!factory) {
    return Diagram(Comment(`No factory defined for ${name}`));
  }
  return factory();
}

/**
 * Get all diagram rule names for grammar coverage checking.
 */
export function getDiagramRuleNames(): string[] {
  return Array.from(rules.keys());
}
