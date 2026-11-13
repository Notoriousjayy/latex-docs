/**
 * C++23 Grammar Definitions
 * 
 * ES module that defines the C++ grammar as railroad diagrams.
 * Based on the C++ Standard Grammar Summary (Annex A).
 * Reference: https://eel.is/c++draft/gram
 * 
 * Many rules are rendered in diagram-friendly equivalent form 
 * (e.g., left recursion -> repetition).
 */

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

// ===== A.2 Keywords [gram.key] =====

rules.set("typedef-name", () =>
  Diagram(
    Choice(0,
      NT("identifier"),
      NT("simple-template-id")
    )
  )
);

rules.set("namespace-name", () =>
  Diagram(
    Choice(0,
      NT("identifier"),
      NT("namespace-alias")
    )
  )
);

rules.set("namespace-alias", () =>
  Diagram(NT("identifier"))
);

rules.set("class-name", () =>
  Diagram(
    Choice(0,
      NT("identifier"),
      NT("simple-template-id")
    )
  )
);

rules.set("enum-name", () =>
  Diagram(NT("identifier"))
);

rules.set("template-name", () =>
  Diagram(NT("identifier"))
);

// ===== A.3 Lexical conventions [gram.lex] =====

rules.set("n-char", () =>
  Diagram(Comment("any member of the translation character set except } or new-line"))
);

rules.set("n-char-sequence", () =>
  Diagram(OneOrMore(NT("n-char")))
);

rules.set("named-universal-character", () =>
  Diagram(Sequence(T("\\N{"), NT("n-char-sequence"), T("}")))
);

rules.set("hex-quad", () =>
  Diagram(
    Sequence(
      NT("hexadecimal-digit"),
      NT("hexadecimal-digit"),
      NT("hexadecimal-digit"),
      NT("hexadecimal-digit")
    )
  )
);

rules.set("simple-hexadecimal-digit-sequence", () =>
  Diagram(OneOrMore(NT("hexadecimal-digit")))
);

rules.set("universal-character-name", () =>
  Diagram(
    Choice(0,
      Sequence(T("\\u"), NT("hex-quad")),
      Sequence(T("\\U"), NT("hex-quad"), NT("hex-quad")),
      Sequence(T("\\u{"), NT("simple-hexadecimal-digit-sequence"), T("}")),
      NT("named-universal-character")
    )
  )
);

rules.set("preprocessing-token", () =>
  Diagram(
    Choice(0,
      NT("header-name"),
      NT("import-keyword"),
      NT("module-keyword"),
      NT("export-keyword"),
      NT("identifier"),
      NT("pp-number"),
      NT("character-literal"),
      NT("user-defined-character-literal"),
      NT("string-literal"),
      NT("user-defined-string-literal"),
      NT("preprocessing-op-or-punc"),
      Comment("other non-whitespace")
    )
  )
);

rules.set("token", () =>
  Diagram(
    Choice(0,
      NT("identifier"),
      NT("keyword"),
      NT("literal"),
      NT("operator-or-punctuator")
    )
  )
);

rules.set("header-name", () =>
  Diagram(
    Choice(0,
      Sequence(T("<"), NT("h-char-sequence"), T(">")),
      Sequence(T('"'), NT("q-char-sequence"), T('"'))
    )
  )
);

rules.set("h-char-sequence", () =>
  Diagram(OneOrMore(NT("h-char")))
);

rules.set("h-char", () =>
  Diagram(Comment("any character except new-line and >"))
);

rules.set("q-char-sequence", () =>
  Diagram(OneOrMore(NT("q-char")))
);

rules.set("q-char", () =>
  Diagram(Comment('any character except new-line and "'))
);

rules.set("pp-number", () =>
  Diagram(
    Choice(0,
      NT("digit"),
      Sequence(T("."), NT("digit"))
    ),
    ZeroOrMore(
      Choice(0,
        NT("identifier-continue"),
        Sequence(T("'"), NT("digit")),
        Sequence(T("'"), NT("nondigit")),
        Sequence(Choice(0, T("e"), T("E"), T("p"), T("P")), NT("sign")),
        T(".")
      )
    )
  )
);

rules.set("identifier", () =>
  Diagram(
    Sequence(
      NT("identifier-start"),
      ZeroOrMore(NT("identifier-continue"))
    )
  )
);

rules.set("identifier-start", () =>
  Diagram(
    Choice(0,
      NT("nondigit"),
      Comment("XID_Start character")
    )
  )
);

rules.set("identifier-continue", () =>
  Diagram(
    Choice(0,
      NT("digit"),
      NT("nondigit"),
      Comment("XID_Continue character")
    )
  )
);

rules.set("nondigit", () =>
  Diagram(
    Choice(0,
      T("a-z"),
      T("A-Z"),
      T("_")
    )
  )
);

rules.set("digit", () =>
  Diagram(T("0-9"))
);

rules.set("keyword", () =>
  Diagram(
    Choice(0,
      Comment("any identifier listed in Table 5"),
      NT("import-keyword"),
      NT("module-keyword"),
      NT("export-keyword")
    )
  )
);

rules.set("preprocessing-op-or-punc", () =>
  Diagram(
    Choice(0,
      NT("preprocessing-operator"),
      NT("operator-or-punctuator")
    )
  )
);

rules.set("preprocessing-operator", () =>
  Diagram(
    Choice(0, T("#"), T("##"), T("%:"), T("%:%:"))
  )
);

rules.set("operator-or-punctuator", () =>
  Diagram(
    Stack(
      Choice(0, T("{"), T("}"), T("["), T("]"), T("("), T(")"), T("<:"), T(":>"), T("<%"), T("%>")),
      Choice(0, T(";"), T(":"), T("..."), T("?"), T("::"), T("."), T(".*"), T("->"), T("->*"), T("~")),
      Choice(0, T("!"), T("+"), T("-"), T("*"), T("/"), T("%"), T("^"), T("&"), T("|")),
      Choice(0, T("="), T("+="), T("-="), T("*="), T("/="), T("%="), T("^="), T("&="), T("|=")),
      Choice(0, T("=="), T("!="), T("<"), T(">"), T("<="), T(">="), T("<=>"), T("&&"), T("||")),
      Choice(0, T("<<"), T(">>"), T("<<="), T(">>="), T("++"), T("--"), T(","))
    )
  )
);

// ===== A.3 Literals =====

rules.set("literal", () =>
  Diagram(
    Choice(0,
      NT("integer-literal"),
      NT("character-literal"),
      NT("floating-point-literal"),
      NT("string-literal"),
      NT("boolean-literal"),
      NT("pointer-literal"),
      NT("user-defined-literal")
    )
  )
);

rules.set("integer-literal", () =>
  Diagram(
    Choice(0,
      NT("binary-literal"),
      NT("octal-literal"),
      NT("decimal-literal"),
      NT("hexadecimal-literal")
    ),
    Optional(NT("integer-suffix"))
  )
);

rules.set("binary-literal", () =>
  Diagram(
    Choice(0, T("0b"), T("0B")),
    NT("binary-digit"),
    ZeroOrMore(Sequence(Optional(T("'")), NT("binary-digit")))
  )
);

rules.set("octal-literal", () =>
  Diagram(
    T("0"),
    ZeroOrMore(Sequence(Optional(T("'")), NT("octal-digit")))
  )
);

rules.set("decimal-literal", () =>
  Diagram(
    NT("nonzero-digit"),
    ZeroOrMore(Sequence(Optional(T("'")), NT("digit")))
  )
);

rules.set("hexadecimal-literal", () =>
  Diagram(
    NT("hexadecimal-prefix"),
    NT("hexadecimal-digit-sequence")
  )
);

rules.set("binary-digit", () =>
  Diagram(Choice(0, T("0"), T("1")))
);

rules.set("octal-digit", () =>
  Diagram(T("0-7"))
);

rules.set("nonzero-digit", () =>
  Diagram(T("1-9"))
);

rules.set("hexadecimal-prefix", () =>
  Diagram(Choice(0, T("0x"), T("0X")))
);

rules.set("hexadecimal-digit-sequence", () =>
  Diagram(
    NT("hexadecimal-digit"),
    ZeroOrMore(Sequence(Optional(T("'")), NT("hexadecimal-digit")))
  )
);

rules.set("hexadecimal-digit", () =>
  Diagram(Choice(0, T("0-9"), T("a-f"), T("A-F")))
);

rules.set("integer-suffix", () =>
  Diagram(
    Choice(0,
      Sequence(NT("unsigned-suffix"), Optional(Choice(0, NT("long-suffix"), NT("long-long-suffix"), NT("size-suffix")))),
      Sequence(NT("long-suffix"), Optional(NT("unsigned-suffix"))),
      Sequence(NT("long-long-suffix"), Optional(NT("unsigned-suffix"))),
      Sequence(NT("size-suffix"), Optional(NT("unsigned-suffix")))
    )
  )
);

rules.set("unsigned-suffix", () =>
  Diagram(Choice(0, T("u"), T("U")))
);

rules.set("long-suffix", () =>
  Diagram(Choice(0, T("l"), T("L")))
);

rules.set("long-long-suffix", () =>
  Diagram(Choice(0, T("ll"), T("LL")))
);

rules.set("size-suffix", () =>
  Diagram(Choice(0, T("z"), T("Z")))
);

rules.set("character-literal", () =>
  Diagram(
    Optional(NT("encoding-prefix")),
    T("'"),
    NT("c-char-sequence"),
    T("'")
  )
);

rules.set("encoding-prefix", () =>
  Diagram(Choice(0, T("u8"), T("u"), T("U"), T("L")))
);

rules.set("c-char-sequence", () =>
  Diagram(OneOrMore(NT("c-char")))
);

rules.set("c-char", () =>
  Diagram(
    Choice(0,
      NT("basic-c-char"),
      NT("escape-sequence"),
      NT("universal-character-name")
    )
  )
);

rules.set("basic-c-char", () =>
  Diagram(Comment("any character except ', \\, or new-line"))
);

rules.set("escape-sequence", () =>
  Diagram(
    Choice(0,
      NT("simple-escape-sequence"),
      NT("numeric-escape-sequence"),
      NT("conditional-escape-sequence")
    )
  )
);

rules.set("simple-escape-sequence", () =>
  Diagram(
    T("\\"),
    NT("simple-escape-sequence-char")
  )
);

rules.set("simple-escape-sequence-char", () =>
  Diagram(
    Choice(0, T("'"), T('"'), T("?"), T("\\"), T("a"), T("b"), T("f"), T("n"), T("r"), T("t"), T("v"))
  )
);

rules.set("numeric-escape-sequence", () =>
  Diagram(
    Choice(0,
      NT("octal-escape-sequence"),
      NT("hexadecimal-escape-sequence")
    )
  )
);

rules.set("simple-octal-digit-sequence", () =>
  Diagram(OneOrMore(NT("octal-digit")))
);

rules.set("octal-escape-sequence", () =>
  Diagram(
    Choice(0,
      Sequence(T("\\"), NT("octal-digit"), Optional(NT("octal-digit")), Optional(NT("octal-digit"))),
      Sequence(T("\\o{"), NT("simple-octal-digit-sequence"), T("}"))
    )
  )
);

rules.set("hexadecimal-escape-sequence", () =>
  Diagram(
    Choice(0,
      Sequence(T("\\x"), NT("simple-hexadecimal-digit-sequence")),
      Sequence(T("\\x{"), NT("simple-hexadecimal-digit-sequence"), T("}"))
    )
  )
);

rules.set("conditional-escape-sequence", () =>
  Diagram(
    T("\\"),
    NT("conditional-escape-sequence-char")
  )
);

rules.set("conditional-escape-sequence-char", () =>
  Diagram(Comment("any basic char not octal-digit, escape-char, N, o, u, U, x"))
);

rules.set("floating-point-literal", () =>
  Diagram(
    Choice(0,
      NT("decimal-floating-point-literal"),
      NT("hexadecimal-floating-point-literal")
    )
  )
);

rules.set("decimal-floating-point-literal", () =>
  Diagram(
    Choice(0,
      Sequence(NT("fractional-constant"), Optional(NT("exponent-part"))),
      Sequence(NT("digit-sequence"), NT("exponent-part"))
    ),
    Optional(NT("floating-point-suffix"))
  )
);

rules.set("hexadecimal-floating-point-literal", () =>
  Diagram(
    NT("hexadecimal-prefix"),
    Choice(0,
      NT("hexadecimal-fractional-constant"),
      NT("hexadecimal-digit-sequence")
    ),
    NT("binary-exponent-part"),
    Optional(NT("floating-point-suffix"))
  )
);

rules.set("fractional-constant", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("digit-sequence")), T("."), NT("digit-sequence")),
      Sequence(NT("digit-sequence"), T("."))
    )
  )
);

rules.set("hexadecimal-fractional-constant", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("hexadecimal-digit-sequence")), T("."), NT("hexadecimal-digit-sequence")),
      Sequence(NT("hexadecimal-digit-sequence"), T("."))
    )
  )
);

rules.set("exponent-part", () =>
  Diagram(
    Choice(0, T("e"), T("E")),
    Optional(NT("sign")),
    NT("digit-sequence")
  )
);

rules.set("binary-exponent-part", () =>
  Diagram(
    Choice(0, T("p"), T("P")),
    Optional(NT("sign")),
    NT("digit-sequence")
  )
);

rules.set("sign", () =>
  Diagram(Choice(0, T("+"), T("-")))
);

rules.set("digit-sequence", () =>
  Diagram(
    NT("digit"),
    ZeroOrMore(Sequence(Optional(T("'")), NT("digit")))
  )
);

rules.set("floating-point-suffix", () =>
  Diagram(
    Choice(0,
      T("f"), T("l"), T("f16"), T("f32"), T("f64"), T("f128"), T("bf16"),
      T("F"), T("L"), T("F16"), T("F32"), T("F64"), T("F128"), T("BF16")
    )
  )
);

rules.set("string-literal", () =>
  Diagram(
    Optional(NT("encoding-prefix")),
    Choice(0,
      Sequence(T('"'), Optional(NT("s-char-sequence")), T('"')),
      Sequence(T("R"), NT("raw-string"))
    )
  )
);

rules.set("s-char-sequence", () =>
  Diagram(OneOrMore(NT("s-char")))
);

rules.set("s-char", () =>
  Diagram(
    Choice(0,
      NT("basic-s-char"),
      NT("escape-sequence"),
      NT("universal-character-name")
    )
  )
);

rules.set("basic-s-char", () =>
  Diagram(Comment('any character except ", \\, or new-line'))
);

rules.set("raw-string", () =>
  Diagram(
    T('"'),
    Optional(NT("d-char-sequence")),
    T("("),
    Optional(NT("r-char-sequence")),
    T(")"),
    Optional(NT("d-char-sequence")),
    T('"')
  )
);

rules.set("r-char-sequence", () =>
  Diagram(OneOrMore(NT("r-char")))
);

rules.set("r-char", () =>
  Diagram(Comment("any character except ) followed by d-char-sequence and \""))
);

rules.set("d-char-sequence", () =>
  Diagram(OneOrMore(NT("d-char")))
);

rules.set("d-char", () =>
  Diagram(Comment("any basic char except space, (, ), \\, tab, newline"))
);

rules.set("boolean-literal", () =>
  Diagram(Choice(0, T("false"), T("true")))
);

rules.set("pointer-literal", () =>
  Diagram(T("nullptr"))
);

rules.set("user-defined-literal", () =>
  Diagram(
    Choice(0,
      NT("user-defined-integer-literal"),
      NT("user-defined-floating-point-literal"),
      NT("user-defined-string-literal"),
      NT("user-defined-character-literal")
    )
  )
);

rules.set("user-defined-integer-literal", () =>
  Diagram(
    Choice(0,
      NT("decimal-literal"),
      NT("octal-literal"),
      NT("hexadecimal-literal"),
      NT("binary-literal")
    ),
    NT("ud-suffix")
  )
);

rules.set("user-defined-floating-point-literal", () =>
  Diagram(
    Choice(0,
      Sequence(NT("fractional-constant"), Optional(NT("exponent-part"))),
      Sequence(NT("digit-sequence"), NT("exponent-part")),
      Sequence(NT("hexadecimal-prefix"), NT("hexadecimal-fractional-constant"), NT("binary-exponent-part")),
      Sequence(NT("hexadecimal-prefix"), NT("hexadecimal-digit-sequence"), NT("binary-exponent-part"))
    ),
    NT("ud-suffix")
  )
);

rules.set("user-defined-string-literal", () =>
  Diagram(NT("string-literal"), NT("ud-suffix"))
);

rules.set("user-defined-character-literal", () =>
  Diagram(NT("character-literal"), NT("ud-suffix"))
);

rules.set("ud-suffix", () =>
  Diagram(NT("identifier"))
);

// ===== A.4 Basics [gram.basic] =====

rules.set("translation-unit", () =>
  Diagram(
    Choice(0,
      Optional(NT("declaration-seq")),
      Sequence(
        Optional(NT("global-module-fragment")),
        NT("module-declaration"),
        Optional(NT("declaration-seq")),
        Optional(NT("private-module-fragment"))
      )
    )
  )
);

// ===== A.5 Expressions [gram.expr] =====

rules.set("primary-expression", () =>
  Diagram(
    Choice(0,
      NT("literal"),
      T("this"),
      Sequence(T("("), NT("expression"), T(")")),
      NT("id-expression"),
      NT("lambda-expression"),
      NT("fold-expression"),
      NT("requires-expression")
    )
  )
);

rules.set("id-expression", () =>
  Diagram(
    Choice(0,
      NT("unqualified-id"),
      NT("qualified-id")
    )
  )
);

rules.set("unqualified-id", () =>
  Diagram(
    Choice(0,
      NT("identifier"),
      NT("operator-function-id"),
      NT("conversion-function-id"),
      NT("literal-operator-id"),
      Sequence(T("~"), NT("type-name")),
      Sequence(T("~"), NT("decltype-specifier")),
      NT("template-id")
    )
  )
);

rules.set("qualified-id", () =>
  Diagram(
    NT("nested-name-specifier"),
    Optional(T("template")),
    NT("unqualified-id")
  )
);

rules.set("nested-name-specifier", () =>
  Diagram(
    Choice(0,
      T("::"),
      Sequence(NT("type-name"), T("::")),
      Sequence(NT("namespace-name"), T("::")),
      Sequence(NT("decltype-specifier"), T("::"))
    ),
    ZeroOrMore(
      Choice(0,
        Sequence(NT("identifier"), T("::")),
        Sequence(Optional(T("template")), NT("simple-template-id"), T("::"))
      )
    )
  )
);

rules.set("lambda-expression", () =>
  Diagram(
    NT("lambda-introducer"),
    Optional(
      Sequence(
        T("<"),
        NT("template-parameter-list"),
        T(">"),
        Optional(NT("requires-clause"))
      )
    ),
    Optional(NT("attribute-specifier-seq")),
    NT("lambda-declarator"),
    NT("compound-statement")
  )
);

rules.set("lambda-introducer", () =>
  Diagram(
    T("["),
    Optional(NT("lambda-capture")),
    T("]")
  )
);

rules.set("lambda-declarator", () =>
  Diagram(
    Choice(0,
      Sequence(
        Optional(NT("lambda-specifier-seq")),
        Optional(NT("noexcept-specifier")),
        Optional(NT("attribute-specifier-seq")),
        Optional(NT("trailing-return-type"))
      ),
      Sequence(
        T("("),
        NT("parameter-declaration-clause"),
        T(")"),
        Optional(NT("lambda-specifier-seq")),
        Optional(NT("noexcept-specifier")),
        Optional(NT("attribute-specifier-seq")),
        Optional(NT("trailing-return-type")),
        Optional(NT("requires-clause"))
      )
    )
  )
);

rules.set("lambda-specifier", () =>
  Diagram(
    Choice(0,
      T("consteval"),
      T("constexpr"),
      T("mutable"),
      T("static")
    )
  )
);

rules.set("lambda-specifier-seq", () =>
  Diagram(OneOrMore(NT("lambda-specifier")))
);

rules.set("lambda-capture", () =>
  Diagram(
    Choice(0,
      NT("capture-default"),
      NT("capture-list"),
      Sequence(NT("capture-default"), T(","), NT("capture-list"))
    )
  )
);

rules.set("capture-default", () =>
  Diagram(Choice(0, T("&"), T("=")))
);

rules.set("capture-list", () =>
  Diagram(
    NT("capture"),
    ZeroOrMore(Sequence(T(","), NT("capture")))
  )
);

rules.set("capture", () =>
  Diagram(
    Choice(0,
      NT("simple-capture"),
      NT("init-capture")
    )
  )
);

rules.set("simple-capture", () =>
  Diagram(
    Choice(0,
      Sequence(NT("identifier"), Optional(T("..."))),
      Sequence(T("&"), NT("identifier"), Optional(T("..."))),
      T("this"),
      Sequence(T("*"), T("this"))
    )
  )
);

rules.set("init-capture", () =>
  Diagram(
    Optional(T("...")),
    Optional(T("&")),
    NT("identifier"),
    NT("initializer")
  )
);

rules.set("fold-expression", () =>
  Diagram(
    T("("),
    Choice(0,
      Sequence(NT("cast-expression"), NT("fold-operator"), T("...")),
      Sequence(T("..."), NT("fold-operator"), NT("cast-expression")),
      Sequence(NT("cast-expression"), NT("fold-operator"), T("..."), NT("fold-operator"), NT("cast-expression"))
    ),
    T(")")
  )
);

rules.set("fold-operator", () =>
  Diagram(
    Choice(0,
      T("+"), T("-"), T("*"), T("/"), T("%"), T("^"), T("&"), T("|"),
      T("<<"), T(">>"), T("+="), T("-="), T("*="), T("/="), T("%="),
      T("^="), T("&="), T("|="), T("<<="), T(">>="), T("="),
      T("=="), T("!="), T("<"), T(">"), T("<="), T(">="),
      T("&&"), T("||"), T(","), T(".*"), T("->*")
    )
  )
);

rules.set("requires-expression", () =>
  Diagram(
    T("requires"),
    Optional(NT("requirement-parameter-list")),
    NT("requirement-body")
  )
);

rules.set("requirement-parameter-list", () =>
  Diagram(
    T("("),
    NT("parameter-declaration-clause"),
    T(")")
  )
);

rules.set("requirement-body", () =>
  Diagram(
    T("{"),
    NT("requirement-seq"),
    T("}")
  )
);

rules.set("requirement-seq", () =>
  Diagram(OneOrMore(NT("requirement")))
);

rules.set("requirement", () =>
  Diagram(
    Choice(0,
      NT("simple-requirement"),
      NT("type-requirement"),
      NT("compound-requirement"),
      NT("nested-requirement")
    )
  )
);

rules.set("simple-requirement", () =>
  Diagram(NT("expression"), T(";"))
);

rules.set("type-requirement", () =>
  Diagram(
    T("typename"),
    Optional(NT("nested-name-specifier")),
    NT("type-name"),
    T(";")
  )
);

rules.set("compound-requirement", () =>
  Diagram(
    T("{"),
    NT("expression"),
    T("}"),
    Optional(T("noexcept")),
    Optional(NT("return-type-requirement")),
    T(";")
  )
);

rules.set("return-type-requirement", () =>
  Diagram(T("->"), NT("type-constraint"))
);

rules.set("nested-requirement", () =>
  Diagram(T("requires"), NT("constraint-expression"), T(";"))
);

rules.set("postfix-expression", () => {
  const postfixSuffix = Choice(0,
    Sequence(T("["), Optional(NT("expression-list")), T("]")),
    Sequence(T("("), Optional(NT("expression-list")), T(")")),
    Sequence(T("."), Optional(T("template")), NT("id-expression")),
    Sequence(T("->"), Optional(T("template")), NT("id-expression")),
    T("++"),
    T("--")
  );

  return Diagram(
    Choice(0,
      NT("primary-expression"),
      Sequence(NT("simple-type-specifier"), T("("), Optional(NT("expression-list")), T(")")),
      Sequence(NT("typename-specifier"), T("("), Optional(NT("expression-list")), T(")")),
      Sequence(NT("simple-type-specifier"), NT("braced-init-list")),
      Sequence(NT("typename-specifier"), NT("braced-init-list")),
      Sequence(T("dynamic_cast"), T("<"), NT("type-id"), T(">"), T("("), NT("expression"), T(")")),
      Sequence(T("static_cast"), T("<"), NT("type-id"), T(">"), T("("), NT("expression"), T(")")),
      Sequence(T("reinterpret_cast"), T("<"), NT("type-id"), T(">"), T("("), NT("expression"), T(")")),
      Sequence(T("const_cast"), T("<"), NT("type-id"), T(">"), T("("), NT("expression"), T(")")),
      Sequence(T("typeid"), T("("), Choice(0, NT("expression"), NT("type-id")), T(")"))
    ),
    ZeroOrMore(postfixSuffix)
  );
});

rules.set("expression-list", () =>
  Diagram(NT("initializer-list"))
);

rules.set("unary-expression", () =>
  Diagram(
    Choice(0,
      NT("postfix-expression"),
      Sequence(NT("unary-operator"), NT("cast-expression")),
      Sequence(T("++"), NT("cast-expression")),
      Sequence(T("--"), NT("cast-expression")),
      NT("await-expression"),
      Sequence(T("sizeof"), NT("unary-expression")),
      Sequence(T("sizeof"), T("("), NT("type-id"), T(")")),
      Sequence(T("sizeof"), T("..."), T("("), NT("identifier"), T(")")),
      Sequence(T("alignof"), T("("), NT("type-id"), T(")")),
      NT("noexcept-expression"),
      NT("new-expression"),
      NT("delete-expression")
    )
  )
);

rules.set("unary-operator", () =>
  Diagram(Choice(0, T("*"), T("&"), T("+"), T("-"), T("!"), T("~")))
);

rules.set("await-expression", () =>
  Diagram(T("co_await"), NT("cast-expression"))
);

rules.set("noexcept-expression", () =>
  Diagram(T("noexcept"), T("("), NT("expression"), T(")"))
);

rules.set("new-expression", () =>
  Diagram(
    Optional(T("::")),
    T("new"),
    Optional(NT("new-placement")),
    Choice(0,
      NT("new-type-id"),
      Sequence(T("("), NT("type-id"), T(")"))
    ),
    Optional(NT("new-initializer"))
  )
);

rules.set("new-placement", () =>
  Diagram(T("("), NT("expression-list"), T(")"))
);

rules.set("new-type-id", () =>
  Diagram(NT("type-specifier-seq"), Optional(NT("new-declarator")))
);

rules.set("new-declarator", () =>
  Diagram(
    Choice(0,
      Sequence(NT("ptr-operator"), Optional(NT("new-declarator"))),
      NT("noptr-new-declarator")
    )
  )
);

rules.set("noptr-new-declarator", () =>
  Diagram(
    T("["),
    Optional(NT("expression")),
    T("]"),
    Optional(NT("attribute-specifier-seq")),
    ZeroOrMore(
      Sequence(T("["), NT("constant-expression"), T("]"), Optional(NT("attribute-specifier-seq")))
    )
  )
);

rules.set("new-initializer", () =>
  Diagram(
    Choice(0,
      Sequence(T("("), Optional(NT("expression-list")), T(")")),
      NT("braced-init-list")
    )
  )
);

rules.set("delete-expression", () =>
  Diagram(
    Optional(T("::")),
    T("delete"),
    Optional(Sequence(T("["), T("]"))),
    NT("cast-expression")
  )
);

rules.set("cast-expression", () =>
  Diagram(
    ZeroOrMore(Sequence(T("("), NT("type-id"), T(")"))),
    NT("unary-expression")
  )
);

rules.set("pm-expression", () =>
  Diagram(
    NT("cast-expression"),
    ZeroOrMore(
      Sequence(Choice(0, T(".*"), T("->*")), NT("cast-expression"))
    )
  )
);

// precedence-chain helper
function chain(base: string, ops: string[]) {
  return Sequence(
    NT(base),
    ZeroOrMore(Sequence(Choice(0, ...ops.map(T)), NT(base)))
  );
}

rules.set("multiplicative-expression", () => Diagram(chain("pm-expression", ["*", "/", "%"])));
rules.set("additive-expression", () => Diagram(chain("multiplicative-expression", ["+", "-"])));
rules.set("shift-expression", () => Diagram(chain("additive-expression", ["<<", ">>"])));
rules.set("compare-expression", () => Diagram(chain("shift-expression", ["<=>"])));
rules.set("relational-expression", () => Diagram(chain("compare-expression", ["<", ">", "<=", ">="])));
rules.set("equality-expression", () => Diagram(chain("relational-expression", ["==", "!="])));
rules.set("and-expression", () => Diagram(chain("equality-expression", ["&"])));
rules.set("exclusive-or-expression", () => Diagram(chain("and-expression", ["^"])));
rules.set("inclusive-or-expression", () => Diagram(chain("exclusive-or-expression", ["|"])));
rules.set("logical-and-expression", () => Diagram(chain("inclusive-or-expression", ["&&"])));
rules.set("logical-or-expression", () => Diagram(chain("logical-and-expression", ["||"])));

rules.set("conditional-expression", () =>
  Diagram(
    NT("logical-or-expression"),
    Optional(Sequence(T("?"), NT("expression"), T(":"), NT("assignment-expression")))
  )
);

rules.set("yield-expression", () =>
  Diagram(
    T("co_yield"),
    Choice(0,
      NT("assignment-expression"),
      NT("braced-init-list")
    )
  )
);

rules.set("throw-expression", () =>
  Diagram(T("throw"), Optional(NT("assignment-expression")))
);

rules.set("assignment-expression", () =>
  Diagram(
    Choice(0,
      NT("conditional-expression"),
      NT("yield-expression"),
      NT("throw-expression"),
      Sequence(NT("logical-or-expression"), NT("assignment-operator"), NT("initializer-clause"))
    )
  )
);

rules.set("assignment-operator", () =>
  Diagram(
    Choice(0,
      T("="), T("*="), T("/="), T("%="), T("+="), T("-="),
      T(">>="), T("<<="), T("&="), T("^="), T("|=")
    )
  )
);

rules.set("expression", () =>
  Diagram(
    NT("assignment-expression"),
    ZeroOrMore(Sequence(T(","), NT("assignment-expression")))
  )
);

rules.set("constant-expression", () =>
  Diagram(NT("conditional-expression"))
);

// ===== A.6 Statements [gram.stmt] =====

rules.set("statement", () =>
  Diagram(
    Choice(0,
      NT("labeled-statement"),
      Sequence(Optional(NT("attribute-specifier-seq")), NT("expression-statement")),
      Sequence(Optional(NT("attribute-specifier-seq")), NT("compound-statement")),
      Sequence(Optional(NT("attribute-specifier-seq")), NT("selection-statement")),
      Sequence(Optional(NT("attribute-specifier-seq")), NT("iteration-statement")),
      Sequence(Optional(NT("attribute-specifier-seq")), NT("jump-statement")),
      NT("declaration-statement"),
      Sequence(Optional(NT("attribute-specifier-seq")), NT("try-block"))
    )
  )
);

rules.set("init-statement", () =>
  Diagram(
    Choice(0,
      NT("expression-statement"),
      NT("simple-declaration"),
      NT("alias-declaration")
    )
  )
);

rules.set("condition", () =>
  Diagram(
    Choice(0,
      NT("expression"),
      Sequence(
        Optional(NT("attribute-specifier-seq")),
        NT("decl-specifier-seq"),
        NT("declarator"),
        NT("brace-or-equal-initializer")
      )
    )
  )
);

rules.set("label", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    Choice(0,
      Sequence(NT("identifier"), T(":")),
      Sequence(T("case"), NT("constant-expression"), T(":")),
      Sequence(T("default"), T(":"))
    )
  )
);

rules.set("labeled-statement", () =>
  Diagram(NT("label"), NT("statement"))
);

rules.set("expression-statement", () =>
  Diagram(Optional(NT("expression")), T(";"))
);

rules.set("compound-statement", () =>
  Diagram(
    T("{"),
    Optional(NT("statement-seq")),
    Optional(NT("label-seq")),
    T("}")
  )
);

rules.set("statement-seq", () =>
  Diagram(OneOrMore(NT("statement")))
);

rules.set("label-seq", () =>
  Diagram(OneOrMore(NT("label")))
);

rules.set("selection-statement", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("if"),
        Optional(T("constexpr")),
        T("("),
        Optional(NT("init-statement")),
        NT("condition"),
        T(")"),
        NT("statement"),
        Optional(Sequence(T("else"), NT("statement")))
      ),
      Sequence(
        T("if"),
        Optional(T("!")),
        T("consteval"),
        NT("compound-statement"),
        Optional(Sequence(T("else"), NT("statement")))
      ),
      Sequence(
        T("switch"),
        T("("),
        Optional(NT("init-statement")),
        NT("condition"),
        T(")"),
        NT("statement")
      )
    )
  )
);

rules.set("iteration-statement", () =>
  Diagram(
    Choice(0,
      Sequence(T("while"), T("("), NT("condition"), T(")"), NT("statement")),
      Sequence(T("do"), NT("statement"), T("while"), T("("), NT("expression"), T(")"), T(";")),
      Sequence(
        T("for"),
        T("("),
        NT("init-statement"),
        Optional(NT("condition")),
        T(";"),
        Optional(NT("expression")),
        T(")"),
        NT("statement")
      ),
      Sequence(
        T("for"),
        T("("),
        Optional(NT("init-statement")),
        NT("for-range-declaration"),
        T(":"),
        NT("for-range-initializer"),
        T(")"),
        NT("statement")
      )
    )
  )
);

rules.set("for-range-declaration", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    NT("decl-specifier-seq"),
    Choice(0,
      NT("declarator"),
      Sequence(Optional(NT("ref-qualifier")), T("["), NT("identifier-list"), T("]"))
    )
  )
);

rules.set("for-range-initializer", () =>
  Diagram(NT("expr-or-braced-init-list"))
);

rules.set("jump-statement", () =>
  Diagram(
    Choice(0,
      Sequence(T("break"), T(";")),
      Sequence(T("continue"), T(";")),
      Sequence(T("return"), Optional(NT("expr-or-braced-init-list")), T(";")),
      NT("coroutine-return-statement"),
      Sequence(T("goto"), NT("identifier"), T(";"))
    )
  )
);

rules.set("coroutine-return-statement", () =>
  Diagram(T("co_return"), Optional(NT("expr-or-braced-init-list")), T(";"))
);

rules.set("declaration-statement", () =>
  Diagram(NT("block-declaration"))
);

// ===== A.7 Declarations [gram.dcl] =====

rules.set("declaration-seq", () =>
  Diagram(OneOrMore(NT("declaration")))
);

rules.set("declaration", () =>
  Diagram(
    Choice(0,
      NT("name-declaration"),
      NT("special-declaration")
    )
  )
);

rules.set("name-declaration", () =>
  Diagram(
    Choice(0,
      NT("block-declaration"),
      NT("nodeclspec-function-declaration"),
      NT("function-definition"),
      NT("template-declaration"),
      NT("deduction-guide"),
      NT("linkage-specification"),
      NT("namespace-definition"),
      NT("empty-declaration"),
      NT("attribute-declaration"),
      NT("module-import-declaration")
    )
  )
);

rules.set("special-declaration", () =>
  Diagram(
    Choice(0,
      NT("explicit-instantiation"),
      NT("explicit-specialization"),
      NT("export-declaration")
    )
  )
);

rules.set("block-declaration", () =>
  Diagram(
    Choice(0,
      NT("simple-declaration"),
      NT("asm-declaration"),
      NT("namespace-alias-definition"),
      NT("using-declaration"),
      NT("using-enum-declaration"),
      NT("using-directive"),
      NT("static_assert-declaration"),
      NT("alias-declaration"),
      NT("opaque-enum-declaration")
    )
  )
);

rules.set("nodeclspec-function-declaration", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    NT("declarator"),
    T(";")
  )
);

rules.set("alias-declaration", () =>
  Diagram(
    T("using"),
    NT("identifier"),
    Optional(NT("attribute-specifier-seq")),
    T("="),
    NT("defining-type-id"),
    T(";")
  )
);

rules.set("simple-declaration", () =>
  Diagram(
    Choice(0,
      Sequence(NT("decl-specifier-seq"), Optional(NT("init-declarator-list")), T(";")),
      Sequence(NT("attribute-specifier-seq"), NT("decl-specifier-seq"), NT("init-declarator-list"), T(";")),
      Sequence(
        Optional(NT("attribute-specifier-seq")),
        NT("decl-specifier-seq"),
        Optional(NT("ref-qualifier")),
        T("["),
        NT("identifier-list"),
        T("]"),
        NT("initializer"),
        T(";")
      )
    )
  )
);

rules.set("static_assert-declaration", () =>
  Diagram(
    T("static_assert"),
    T("("),
    NT("constant-expression"),
    Optional(Sequence(T(","), NT("string-literal"))),
    T(")"),
    T(";")
  )
);

rules.set("empty-declaration", () =>
  Diagram(T(";"))
);

rules.set("attribute-declaration", () =>
  Diagram(NT("attribute-specifier-seq"), T(";"))
);

rules.set("decl-specifier", () =>
  Diagram(
    Choice(0,
      NT("storage-class-specifier"),
      NT("defining-type-specifier"),
      NT("function-specifier"),
      T("friend"),
      T("typedef"),
      T("constexpr"),
      T("consteval"),
      T("constinit"),
      T("inline")
    )
  )
);

rules.set("decl-specifier-seq", () =>
  Diagram(
    NT("decl-specifier"),
    Choice(0,
      Optional(NT("attribute-specifier-seq")),
      NT("decl-specifier-seq")
    )
  )
);

rules.set("storage-class-specifier", () =>
  Diagram(
    Choice(0,
      T("static"),
      T("thread_local"),
      T("extern"),
      T("mutable")
    )
  )
);

rules.set("function-specifier", () =>
  Diagram(
    Choice(0,
      T("virtual"),
      NT("explicit-specifier")
    )
  )
);

rules.set("explicit-specifier", () =>
  Diagram(
    T("explicit"),
    Optional(Sequence(T("("), NT("constant-expression"), T(")")))
  )
);

rules.set("type-specifier", () =>
  Diagram(
    Choice(0,
      NT("simple-type-specifier"),
      NT("elaborated-type-specifier"),
      NT("typename-specifier"),
      NT("cv-qualifier")
    )
  )
);

rules.set("type-specifier-seq", () =>
  Diagram(
    NT("type-specifier"),
    Choice(0,
      Optional(NT("attribute-specifier-seq")),
      NT("type-specifier-seq")
    )
  )
);

rules.set("defining-type-specifier", () =>
  Diagram(
    Choice(0,
      NT("type-specifier"),
      NT("class-specifier"),
      NT("enum-specifier")
    )
  )
);

rules.set("defining-type-specifier-seq", () =>
  Diagram(
    NT("defining-type-specifier"),
    Choice(0,
      Optional(NT("attribute-specifier-seq")),
      NT("defining-type-specifier-seq")
    )
  )
);

rules.set("simple-type-specifier", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("nested-name-specifier")), NT("type-name")),
      Sequence(NT("nested-name-specifier"), T("template"), NT("simple-template-id")),
      NT("decltype-specifier"),
      NT("placeholder-type-specifier"),
      Sequence(Optional(NT("nested-name-specifier")), NT("template-name")),
      T("char"), T("char8_t"), T("char16_t"), T("char32_t"), T("wchar_t"),
      T("bool"), T("short"), T("int"), T("long"),
      T("signed"), T("unsigned"), T("float"), T("double"), T("void")
    )
  )
);

rules.set("type-name", () =>
  Diagram(
    Choice(0,
      NT("class-name"),
      NT("enum-name"),
      NT("typedef-name")
    )
  )
);

rules.set("elaborated-type-specifier", () =>
  Diagram(
    Choice(0,
      Sequence(
        NT("class-key"),
        Optional(NT("attribute-specifier-seq")),
        Optional(NT("nested-name-specifier")),
        NT("identifier")
      ),
      Sequence(NT("class-key"), NT("simple-template-id")),
      Sequence(
        NT("class-key"),
        NT("nested-name-specifier"),
        Optional(T("template")),
        NT("simple-template-id")
      ),
      Sequence(T("enum"), Optional(NT("nested-name-specifier")), NT("identifier"))
    )
  )
);

rules.set("decltype-specifier", () =>
  Diagram(T("decltype"), T("("), NT("expression"), T(")"))
);

rules.set("placeholder-type-specifier", () =>
  Diagram(
    Optional(NT("type-constraint")),
    Choice(0,
      T("auto"),
      Sequence(T("decltype"), T("("), T("auto"), T(")"))
    )
  )
);

rules.set("init-declarator-list", () =>
  Diagram(
    NT("init-declarator"),
    ZeroOrMore(Sequence(T(","), NT("init-declarator")))
  )
);

rules.set("init-declarator", () =>
  Diagram(
    NT("declarator"),
    Choice(0,
      Optional(NT("initializer")),
      NT("requires-clause")
    )
  )
);

rules.set("declarator", () =>
  Diagram(
    Choice(0,
      NT("ptr-declarator"),
      Sequence(NT("noptr-declarator"), NT("parameters-and-qualifiers"), NT("trailing-return-type"))
    )
  )
);

rules.set("ptr-declarator", () =>
  Diagram(
    ZeroOrMore(NT("ptr-operator")),
    NT("noptr-declarator")
  )
);

rules.set("noptr-declarator", () =>
  Diagram(
    Choice(0,
      Sequence(NT("declarator-id"), Optional(NT("attribute-specifier-seq"))),
      Sequence(T("("), NT("ptr-declarator"), T(")"))
    ),
    ZeroOrMore(
      Choice(0,
        NT("parameters-and-qualifiers"),
        Sequence(T("["), Optional(NT("constant-expression")), T("]"), Optional(NT("attribute-specifier-seq")))
      )
    )
  )
);

rules.set("parameters-and-qualifiers", () =>
  Diagram(
    T("("),
    NT("parameter-declaration-clause"),
    T(")"),
    Optional(NT("cv-qualifier-seq")),
    Optional(NT("ref-qualifier")),
    Optional(NT("noexcept-specifier")),
    Optional(NT("attribute-specifier-seq"))
  )
);

rules.set("trailing-return-type", () =>
  Diagram(T("->"), NT("type-id"))
);

rules.set("ptr-operator", () =>
  Diagram(
    Choice(0,
      Sequence(T("*"), Optional(NT("attribute-specifier-seq")), Optional(NT("cv-qualifier-seq"))),
      Sequence(T("&"), Optional(NT("attribute-specifier-seq"))),
      Sequence(T("&&"), Optional(NT("attribute-specifier-seq"))),
      Sequence(NT("nested-name-specifier"), T("*"), Optional(NT("attribute-specifier-seq")), Optional(NT("cv-qualifier-seq")))
    )
  )
);

rules.set("cv-qualifier-seq", () =>
  Diagram(OneOrMore(NT("cv-qualifier")))
);

rules.set("cv-qualifier", () =>
  Diagram(Choice(0, T("const"), T("volatile")))
);

rules.set("ref-qualifier", () =>
  Diagram(Choice(0, T("&"), T("&&")))
);

rules.set("declarator-id", () =>
  Diagram(Optional(T("...")), NT("id-expression"))
);

rules.set("type-id", () =>
  Diagram(NT("type-specifier-seq"), Optional(NT("abstract-declarator")))
);

rules.set("defining-type-id", () =>
  Diagram(NT("defining-type-specifier-seq"), Optional(NT("abstract-declarator")))
);

rules.set("abstract-declarator", () =>
  Diagram(
    Choice(0,
      NT("ptr-abstract-declarator"),
      Sequence(Optional(NT("noptr-abstract-declarator")), NT("parameters-and-qualifiers"), NT("trailing-return-type")),
      NT("abstract-pack-declarator")
    )
  )
);

rules.set("ptr-abstract-declarator", () =>
  Diagram(
    ZeroOrMore(NT("ptr-operator")),
    Optional(NT("noptr-abstract-declarator"))
  )
);

rules.set("noptr-abstract-declarator", () =>
  Diagram(
    Optional(Sequence(T("("), NT("ptr-abstract-declarator"), T(")"))),
    ZeroOrMore(
      Choice(0,
        NT("parameters-and-qualifiers"),
        Sequence(T("["), Optional(NT("constant-expression")), T("]"), Optional(NT("attribute-specifier-seq")))
      )
    )
  )
);

rules.set("abstract-pack-declarator", () =>
  Diagram(
    ZeroOrMore(NT("ptr-operator")),
    NT("noptr-abstract-pack-declarator")
  )
);

rules.set("noptr-abstract-pack-declarator", () =>
  Diagram(
    T("..."),
    ZeroOrMore(
      Choice(0,
        NT("parameters-and-qualifiers"),
        Sequence(T("["), Optional(NT("constant-expression")), T("]"), Optional(NT("attribute-specifier-seq")))
      )
    )
  )
);

rules.set("parameter-declaration-clause", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("parameter-declaration-list")), Optional(T("..."))),
      Sequence(NT("parameter-declaration-list"), T(","), T("..."))
    )
  )
);

rules.set("parameter-declaration-list", () =>
  Diagram(
    NT("parameter-declaration"),
    ZeroOrMore(Sequence(T(","), NT("parameter-declaration")))
  )
);

rules.set("parameter-declaration", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    Optional(T("this")),
    NT("decl-specifier-seq"),
    Choice(0,
      Sequence(NT("declarator"), Optional(Sequence(T("="), NT("initializer-clause")))),
      Sequence(Optional(NT("abstract-declarator")), Optional(Sequence(T("="), NT("initializer-clause"))))
    )
  )
);

rules.set("initializer", () =>
  Diagram(
    Choice(0,
      NT("brace-or-equal-initializer"),
      Sequence(T("("), NT("expression-list"), T(")"))
    )
  )
);

rules.set("brace-or-equal-initializer", () =>
  Diagram(
    Choice(0,
      Sequence(T("="), NT("initializer-clause")),
      NT("braced-init-list")
    )
  )
);

rules.set("initializer-clause", () =>
  Diagram(
    Choice(0,
      NT("assignment-expression"),
      NT("braced-init-list")
    )
  )
);

rules.set("braced-init-list", () =>
  Diagram(
    T("{"),
    Choice(0,
      Sequence(NT("initializer-list"), Optional(T(","))),
      Sequence(NT("designated-initializer-list"), Optional(T(","))),
      Comment("empty")
    ),
    T("}")
  )
);

rules.set("initializer-list", () =>
  Diagram(
    NT("initializer-clause"),
    Optional(T("...")),
    ZeroOrMore(Sequence(T(","), NT("initializer-clause"), Optional(T("..."))))
  )
);

rules.set("designated-initializer-list", () =>
  Diagram(
    NT("designated-initializer-clause"),
    ZeroOrMore(Sequence(T(","), NT("designated-initializer-clause")))
  )
);

rules.set("designated-initializer-clause", () =>
  Diagram(NT("designator"), NT("brace-or-equal-initializer"))
);

rules.set("designator", () =>
  Diagram(T("."), NT("identifier"))
);

rules.set("expr-or-braced-init-list", () =>
  Diagram(
    Choice(0,
      NT("expression"),
      NT("braced-init-list")
    )
  )
);

rules.set("function-definition", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    Optional(NT("decl-specifier-seq")),
    NT("declarator"),
    Choice(0,
      Sequence(Optional(NT("virt-specifier-seq")), NT("function-body")),
      Sequence(NT("requires-clause"), NT("function-body"))
    )
  )
);

rules.set("function-body", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("ctor-initializer")), NT("compound-statement")),
      NT("function-try-block"),
      Sequence(T("="), T("default"), T(";")),
      Sequence(T("="), T("delete"), T(";"))
    )
  )
);

rules.set("enum-specifier", () =>
  Diagram(
    NT("enum-head"),
    T("{"),
    Choice(0,
      Optional(NT("enumerator-list")),
      Sequence(NT("enumerator-list"), T(","))
    ),
    T("}")
  )
);

rules.set("enum-head", () =>
  Diagram(
    NT("enum-key"),
    Optional(NT("attribute-specifier-seq")),
    Optional(NT("enum-head-name")),
    Optional(NT("enum-base"))
  )
);

rules.set("enum-head-name", () =>
  Diagram(Optional(NT("nested-name-specifier")), NT("identifier"))
);

rules.set("opaque-enum-declaration", () =>
  Diagram(
    NT("enum-key"),
    Optional(NT("attribute-specifier-seq")),
    NT("enum-head-name"),
    Optional(NT("enum-base")),
    T(";")
  )
);

rules.set("enum-key", () =>
  Diagram(
    Choice(0,
      T("enum"),
      Sequence(T("enum"), T("class")),
      Sequence(T("enum"), T("struct"))
    )
  )
);

rules.set("enum-base", () =>
  Diagram(T(":"), NT("type-specifier-seq"))
);

rules.set("enumerator-list", () =>
  Diagram(
    NT("enumerator-definition"),
    ZeroOrMore(Sequence(T(","), NT("enumerator-definition")))
  )
);

rules.set("enumerator-definition", () =>
  Diagram(
    NT("enumerator"),
    Optional(Sequence(T("="), NT("constant-expression")))
  )
);

rules.set("enumerator", () =>
  Diagram(NT("identifier"), Optional(NT("attribute-specifier-seq")))
);

rules.set("using-enum-declaration", () =>
  Diagram(T("using"), T("enum"), NT("using-enum-declarator"), T(";"))
);

rules.set("using-enum-declarator", () =>
  Diagram(
    Optional(NT("nested-name-specifier")),
    Choice(0,
      NT("identifier"),
      NT("simple-template-id")
    )
  )
);

rules.set("namespace-definition", () =>
  Diagram(
    Choice(0,
      NT("named-namespace-definition"),
      NT("unnamed-namespace-definition"),
      NT("nested-namespace-definition")
    )
  )
);

rules.set("named-namespace-definition", () =>
  Diagram(
    Optional(T("inline")),
    T("namespace"),
    Optional(NT("attribute-specifier-seq")),
    NT("identifier"),
    T("{"),
    NT("namespace-body"),
    T("}")
  )
);

rules.set("unnamed-namespace-definition", () =>
  Diagram(
    Optional(T("inline")),
    T("namespace"),
    Optional(NT("attribute-specifier-seq")),
    T("{"),
    NT("namespace-body"),
    T("}")
  )
);

rules.set("nested-namespace-definition", () =>
  Diagram(
    T("namespace"),
    NT("enclosing-namespace-specifier"),
    T("::"),
    Optional(T("inline")),
    NT("identifier"),
    T("{"),
    NT("namespace-body"),
    T("}")
  )
);

rules.set("enclosing-namespace-specifier", () =>
  Diagram(
    NT("identifier"),
    ZeroOrMore(Sequence(T("::"), Optional(T("inline")), NT("identifier")))
  )
);

rules.set("namespace-body", () =>
  Diagram(Optional(NT("declaration-seq")))
);

rules.set("namespace-alias-definition", () =>
  Diagram(
    T("namespace"),
    NT("identifier"),
    T("="),
    NT("qualified-namespace-specifier"),
    T(";")
  )
);

rules.set("qualified-namespace-specifier", () =>
  Diagram(Optional(NT("nested-name-specifier")), NT("namespace-name"))
);

rules.set("using-directive", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    T("using"),
    T("namespace"),
    Optional(NT("nested-name-specifier")),
    NT("namespace-name"),
    T(";")
  )
);

rules.set("using-declaration", () =>
  Diagram(T("using"), NT("using-declarator-list"), T(";"))
);

rules.set("using-declarator-list", () =>
  Diagram(
    NT("using-declarator"),
    Optional(T("...")),
    ZeroOrMore(Sequence(T(","), NT("using-declarator"), Optional(T("..."))))
  )
);

rules.set("using-declarator", () =>
  Diagram(
    Optional(T("typename")),
    NT("nested-name-specifier"),
    NT("unqualified-id")
  )
);

rules.set("asm-declaration", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    T("asm"),
    T("("),
    NT("string-literal"),
    T(")"),
    T(";")
  )
);

rules.set("linkage-specification", () =>
  Diagram(
    T("extern"),
    NT("string-literal"),
    Choice(0,
      Sequence(T("{"), Optional(NT("declaration-seq")), T("}")),
      NT("name-declaration")
    )
  )
);

rules.set("attribute-specifier-seq", () =>
  Diagram(OneOrMore(NT("attribute-specifier")))
);

rules.set("attribute-specifier", () =>
  Diagram(
    Choice(0,
      Sequence(
        T("["),
        T("["),
        Optional(NT("attribute-using-prefix")),
        NT("attribute-list"),
        T("]"),
        T("]")
      ),
      NT("alignment-specifier")
    )
  )
);

rules.set("alignment-specifier", () =>
  Diagram(
    T("alignas"),
    T("("),
    Choice(0, NT("type-id"), NT("constant-expression")),
    Optional(T("...")),
    T(")")
  )
);

rules.set("attribute-using-prefix", () =>
  Diagram(T("using"), NT("attribute-namespace"), T(":"))
);

rules.set("attribute-list", () =>
  Diagram(
    Optional(NT("attribute")),
    ZeroOrMore(
      Sequence(
        T(","),
        Choice(0,
          Optional(NT("attribute")),
          Sequence(NT("attribute"), T("..."))
        )
      )
    )
  )
);

rules.set("attribute", () =>
  Diagram(NT("attribute-token"), Optional(NT("attribute-argument-clause")))
);

rules.set("attribute-token", () =>
  Diagram(
    Choice(0,
      NT("identifier"),
      NT("attribute-scoped-token")
    )
  )
);

rules.set("attribute-scoped-token", () =>
  Diagram(NT("attribute-namespace"), T("::"), NT("identifier"))
);

rules.set("attribute-namespace", () =>
  Diagram(NT("identifier"))
);

rules.set("attribute-argument-clause", () =>
  Diagram(T("("), Optional(NT("balanced-token-seq")), T(")"))
);

rules.set("balanced-token-seq", () =>
  Diagram(OneOrMore(NT("balanced-token")))
);

rules.set("balanced-token", () =>
  Diagram(
    Choice(0,
      Sequence(T("("), Optional(NT("balanced-token-seq")), T(")")),
      Sequence(T("["), Optional(NT("balanced-token-seq")), T("]")),
      Sequence(T("{"), Optional(NT("balanced-token-seq")), T("}")),
      Comment("any token except ( ) [ ] { }")
    )
  )
);

// ===== A.8 Modules [gram.module] =====

rules.set("module-declaration", () =>
  Diagram(
    Optional(T("export")),
    T("module"),
    NT("module-name"),
    Optional(NT("module-partition")),
    Optional(NT("attribute-specifier-seq")),
    T(";")
  )
);

rules.set("module-name", () =>
  Diagram(Optional(NT("module-name-qualifier")), NT("identifier"))
);

rules.set("module-partition", () =>
  Diagram(T(":"), Optional(NT("module-name-qualifier")), NT("identifier"))
);

rules.set("module-name-qualifier", () =>
  Diagram(
    NT("identifier"),
    T("."),
    ZeroOrMore(Sequence(NT("identifier"), T(".")))
  )
);

rules.set("export-declaration", () =>
  Diagram(
    Choice(0,
      Sequence(T("export"), NT("name-declaration")),
      Sequence(T("export"), T("{"), Optional(NT("declaration-seq")), T("}")),
      Sequence(T("export"), NT("module-import-declaration"))
    )
  )
);

rules.set("module-import-declaration", () =>
  Diagram(
    T("import"),
    Choice(0,
      NT("module-name"),
      NT("module-partition"),
      NT("header-name")
    ),
    Optional(NT("attribute-specifier-seq")),
    T(";")
  )
);

rules.set("global-module-fragment", () =>
  Diagram(T("module"), T(";"), Optional(NT("declaration-seq")))
);

rules.set("private-module-fragment", () =>
  Diagram(T("module"), T(":"), T("private"), T(";"), Optional(NT("declaration-seq")))
);

// ===== A.9 Classes [gram.class] =====

rules.set("class-specifier", () =>
  Diagram(
    NT("class-head"),
    T("{"),
    Optional(NT("member-specification")),
    T("}")
  )
);

rules.set("class-head", () =>
  Diagram(
    NT("class-key"),
    Optional(NT("attribute-specifier-seq")),
    Optional(
      Sequence(
        NT("class-head-name"),
        Optional(NT("class-virt-specifier"))
      )
    ),
    Optional(NT("base-clause"))
  )
);

rules.set("class-head-name", () =>
  Diagram(Optional(NT("nested-name-specifier")), NT("class-name"))
);

rules.set("class-virt-specifier", () =>
  Diagram(T("final"))
);

rules.set("class-key", () =>
  Diagram(Choice(0, T("class"), T("struct"), T("union")))
);

rules.set("member-specification", () =>
  Diagram(
    OneOrMore(
      Choice(0,
        NT("member-declaration"),
        Sequence(NT("access-specifier"), T(":"))
      )
    )
  )
);

rules.set("member-declaration", () =>
  Diagram(
    Choice(0,
      Sequence(
        Optional(NT("attribute-specifier-seq")),
        Optional(NT("decl-specifier-seq")),
        Optional(NT("member-declarator-list")),
        T(";")
      ),
      NT("function-definition"),
      NT("using-declaration"),
      NT("using-enum-declaration"),
      NT("static_assert-declaration"),
      NT("template-declaration"),
      NT("explicit-specialization"),
      NT("deduction-guide"),
      NT("alias-declaration"),
      NT("opaque-enum-declaration"),
      NT("empty-declaration")
    )
  )
);

rules.set("member-declarator-list", () =>
  Diagram(
    NT("member-declarator"),
    ZeroOrMore(Sequence(T(","), NT("member-declarator")))
  )
);

rules.set("member-declarator", () =>
  Diagram(
    Choice(0,
      Sequence(
        NT("declarator"),
        Choice(0,
          Sequence(Optional(NT("virt-specifier-seq")), Optional(NT("pure-specifier"))),
          NT("requires-clause"),
          Optional(NT("brace-or-equal-initializer"))
        )
      ),
      Sequence(
        Optional(NT("identifier")),
        Optional(NT("attribute-specifier-seq")),
        T(":"),
        NT("constant-expression"),
        Optional(NT("brace-or-equal-initializer"))
      )
    )
  )
);

rules.set("virt-specifier-seq", () =>
  Diagram(OneOrMore(NT("virt-specifier")))
);

rules.set("virt-specifier", () =>
  Diagram(Choice(0, T("override"), T("final")))
);

rules.set("pure-specifier", () =>
  Diagram(T("="), T("0"))
);

rules.set("conversion-function-id", () =>
  Diagram(T("operator"), NT("conversion-type-id"))
);

rules.set("conversion-type-id", () =>
  Diagram(NT("type-specifier-seq"), Optional(NT("conversion-declarator")))
);

rules.set("conversion-declarator", () =>
  Diagram(NT("ptr-operator"), Optional(NT("conversion-declarator")))
);

rules.set("base-clause", () =>
  Diagram(T(":"), NT("base-specifier-list"))
);

rules.set("base-specifier-list", () =>
  Diagram(
    NT("base-specifier"),
    Optional(T("...")),
    ZeroOrMore(Sequence(T(","), NT("base-specifier"), Optional(T("..."))))
  )
);

rules.set("base-specifier", () =>
  Diagram(
    Optional(NT("attribute-specifier-seq")),
    Choice(0,
      NT("class-or-decltype"),
      Sequence(T("virtual"), Optional(NT("access-specifier")), NT("class-or-decltype")),
      Sequence(NT("access-specifier"), Optional(T("virtual")), NT("class-or-decltype"))
    )
  )
);

rules.set("class-or-decltype", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("nested-name-specifier")), NT("type-name")),
      Sequence(NT("nested-name-specifier"), T("template"), NT("simple-template-id")),
      NT("decltype-specifier")
    )
  )
);

rules.set("access-specifier", () =>
  Diagram(Choice(0, T("private"), T("protected"), T("public")))
);

rules.set("ctor-initializer", () =>
  Diagram(T(":"), NT("mem-initializer-list"))
);

rules.set("mem-initializer-list", () =>
  Diagram(
    NT("mem-initializer"),
    Optional(T("...")),
    ZeroOrMore(Sequence(T(","), NT("mem-initializer"), Optional(T("..."))))
  )
);

rules.set("mem-initializer", () =>
  Diagram(
    NT("mem-initializer-id"),
    Choice(0,
      Sequence(T("("), Optional(NT("expression-list")), T(")")),
      NT("braced-init-list")
    )
  )
);

rules.set("mem-initializer-id", () =>
  Diagram(
    Choice(0,
      NT("class-or-decltype"),
      NT("identifier")
    )
  )
);

// ===== A.10 Overloading [gram.over] =====

rules.set("operator-function-id", () =>
  Diagram(T("operator"), NT("operator"))
);

rules.set("operator", () =>
  Diagram(
    Choice(0,
      T("new"), T("delete"), T("new[]"), T("delete[]"), T("co_await"),
      T("()"), T("[]"), T("->"), T("->*"),
      T("~"), T("!"), T("+"), T("-"), T("*"), T("/"), T("%"), T("^"), T("&"),
      T("|"), T("="), T("+="), T("-="), T("*="), T("/="), T("%="), T("^="), T("&="),
      T("|="), T("=="), T("!="), T("<"), T(">"), T("<="), T(">="), T("<=>"),
      T("&&"), T("||"), T("<<"), T(">>"), T("<<="), T(">>="), T("++"), T("--"), T(",")
    )
  )
);

rules.set("literal-operator-id", () =>
  Diagram(
    T("operator"),
    Choice(0,
      Sequence(NT("string-literal"), NT("identifier")),
      NT("user-defined-string-literal")
    )
  )
);

// ===== A.11 Templates [gram.temp] =====

rules.set("template-declaration", () =>
  Diagram(
    NT("template-head"),
    Choice(0,
      NT("declaration"),
      NT("concept-definition")
    )
  )
);

rules.set("template-head", () =>
  Diagram(
    T("template"),
    T("<"),
    NT("template-parameter-list"),
    T(">"),
    Optional(NT("requires-clause"))
  )
);

rules.set("template-parameter-list", () =>
  Diagram(
    NT("template-parameter"),
    ZeroOrMore(Sequence(T(","), NT("template-parameter")))
  )
);

rules.set("requires-clause", () =>
  Diagram(T("requires"), NT("constraint-logical-or-expression"))
);

rules.set("constraint-logical-or-expression", () =>
  Diagram(
    NT("constraint-logical-and-expression"),
    ZeroOrMore(Sequence(T("||"), NT("constraint-logical-and-expression")))
  )
);

rules.set("constraint-logical-and-expression", () =>
  Diagram(
    NT("primary-expression"),
    ZeroOrMore(Sequence(T("&&"), NT("primary-expression")))
  )
);

rules.set("template-parameter", () =>
  Diagram(
    Choice(0,
      NT("type-parameter"),
      NT("parameter-declaration")
    )
  )
);

rules.set("type-parameter", () =>
  Diagram(
    Choice(0,
      Sequence(NT("type-parameter-key"), Optional(T("...")), Optional(NT("identifier"))),
      Sequence(NT("type-parameter-key"), Optional(NT("identifier")), T("="), NT("type-id")),
      Sequence(NT("type-constraint"), Optional(T("...")), Optional(NT("identifier"))),
      Sequence(NT("type-constraint"), Optional(NT("identifier")), T("="), NT("type-id")),
      Sequence(NT("template-head"), NT("type-parameter-key"), Optional(T("...")), Optional(NT("identifier"))),
      Sequence(NT("template-head"), NT("type-parameter-key"), Optional(NT("identifier")), T("="), NT("id-expression"))
    )
  )
);

rules.set("type-parameter-key", () =>
  Diagram(Choice(0, T("class"), T("typename")))
);

rules.set("type-constraint", () =>
  Diagram(
    Optional(NT("nested-name-specifier")),
    NT("concept-name"),
    Optional(Sequence(T("<"), Optional(NT("template-argument-list")), T(">")))
  )
);

rules.set("simple-template-id", () =>
  Diagram(
    NT("template-name"),
    T("<"),
    Optional(NT("template-argument-list")),
    T(">")
  )
);

rules.set("template-id", () =>
  Diagram(
    Choice(0,
      NT("simple-template-id"),
      Sequence(NT("operator-function-id"), T("<"), Optional(NT("template-argument-list")), T(">")),
      Sequence(NT("literal-operator-id"), T("<"), Optional(NT("template-argument-list")), T(">"))
    )
  )
);

rules.set("template-argument-list", () =>
  Diagram(
    NT("template-argument"),
    Optional(T("...")),
    ZeroOrMore(Sequence(T(","), NT("template-argument"), Optional(T("..."))))
  )
);

rules.set("template-argument", () =>
  Diagram(
    Choice(0,
      NT("constant-expression"),
      NT("type-id"),
      NT("id-expression")
    )
  )
);

rules.set("constraint-expression", () =>
  Diagram(NT("logical-or-expression"))
);

rules.set("deduction-guide", () =>
  Diagram(
    Optional(NT("explicit-specifier")),
    NT("template-name"),
    T("("),
    NT("parameter-declaration-clause"),
    T(")"),
    T("->"),
    NT("simple-template-id"),
    T(";")
  )
);

rules.set("concept-definition", () =>
  Diagram(
    T("concept"),
    NT("concept-name"),
    Optional(NT("attribute-specifier-seq")),
    T("="),
    NT("constraint-expression"),
    T(";")
  )
);

rules.set("concept-name", () =>
  Diagram(NT("identifier"))
);

rules.set("typename-specifier", () =>
  Diagram(
    T("typename"),
    NT("nested-name-specifier"),
    Choice(0,
      NT("identifier"),
      Sequence(Optional(T("template")), NT("simple-template-id"))
    )
  )
);

rules.set("explicit-instantiation", () =>
  Diagram(Optional(T("extern")), T("template"), NT("declaration"))
);

rules.set("explicit-specialization", () =>
  Diagram(T("template"), T("<"), T(">"), NT("declaration"))
);

// ===== A.12 Exception handling [gram.except] =====

rules.set("try-block", () =>
  Diagram(T("try"), NT("compound-statement"), NT("handler-seq"))
);

rules.set("function-try-block", () =>
  Diagram(
    T("try"),
    Optional(NT("ctor-initializer")),
    NT("compound-statement"),
    NT("handler-seq")
  )
);

rules.set("handler-seq", () =>
  Diagram(OneOrMore(NT("handler")))
);

rules.set("handler", () =>
  Diagram(
    T("catch"),
    T("("),
    NT("exception-declaration"),
    T(")"),
    NT("compound-statement")
  )
);

rules.set("exception-declaration", () =>
  Diagram(
    Choice(0,
      Sequence(
        Optional(NT("attribute-specifier-seq")),
        NT("type-specifier-seq"),
        Choice(0, NT("declarator"), Optional(NT("abstract-declarator")))
      ),
      T("...")
    )
  )
);

rules.set("noexcept-specifier", () =>
  Diagram(
    T("noexcept"),
    Optional(Sequence(T("("), NT("constant-expression"), T(")")))
  )
);

// ===== A.13 Preprocessing directives [gram.cpp] =====

rules.set("preprocessing-file", () =>
  Diagram(
    Choice(0,
      Optional(NT("group")),
      NT("module-file")
    )
  )
);

rules.set("module-file", () =>
  Diagram(
    Optional(NT("pp-global-module-fragment")),
    NT("pp-module"),
    Optional(NT("group")),
    Optional(NT("pp-private-module-fragment"))
  )
);

rules.set("pp-global-module-fragment", () =>
  Diagram(T("module"), T(";"), NT("new-line"), Optional(NT("group")))
);

rules.set("pp-private-module-fragment", () =>
  Diagram(T("module"), T(":"), T("private"), T(";"), NT("new-line"), Optional(NT("group")))
);

rules.set("group", () =>
  Diagram(OneOrMore(NT("group-part")))
);

rules.set("group-part", () =>
  Diagram(
    Choice(0,
      NT("control-line"),
      NT("if-section"),
      NT("text-line"),
      Sequence(T("#"), NT("conditionally-supported-directive"))
    )
  )
);

rules.set("control-line", () =>
  Diagram(
    Choice(0,
      Sequence(T("#"), T("include"), NT("pp-tokens"), NT("new-line")),
      NT("pp-import"),
      Sequence(T("#"), T("define"), NT("identifier"), NT("replacement-list"), NT("new-line")),
      Sequence(T("#"), T("define"), NT("identifier"), NT("lparen"), Optional(NT("identifier-list")), T(")"), NT("replacement-list"), NT("new-line")),
      Sequence(T("#"), T("define"), NT("identifier"), NT("lparen"), T("..."), T(")"), NT("replacement-list"), NT("new-line")),
      Sequence(T("#"), T("define"), NT("identifier"), NT("lparen"), NT("identifier-list"), T(","), T("..."), T(")"), NT("replacement-list"), NT("new-line")),
      Sequence(T("#"), T("undef"), NT("identifier"), NT("new-line")),
      Sequence(T("#"), T("line"), NT("pp-tokens"), NT("new-line")),
      Sequence(T("#"), T("error"), Optional(NT("pp-tokens")), NT("new-line")),
      Sequence(T("#"), T("warning"), Optional(NT("pp-tokens")), NT("new-line")),
      Sequence(T("#"), T("pragma"), Optional(NT("pp-tokens")), NT("new-line")),
      Sequence(T("#"), NT("new-line"))
    )
  )
);

rules.set("if-section", () =>
  Diagram(
    NT("if-group"),
    Optional(NT("elif-groups")),
    Optional(NT("else-group")),
    NT("endif-line")
  )
);

rules.set("if-group", () =>
  Diagram(
    T("#"),
    Choice(0,
      Sequence(T("if"), NT("constant-expression")),
      Sequence(T("ifdef"), NT("identifier")),
      Sequence(T("ifndef"), NT("identifier"))
    ),
    NT("new-line"),
    Optional(NT("group"))
  )
);

rules.set("elif-groups", () =>
  Diagram(OneOrMore(NT("elif-group")))
);

rules.set("elif-group", () =>
  Diagram(
    T("#"),
    Choice(0,
      Sequence(T("elif"), NT("constant-expression")),
      Sequence(T("elifdef"), NT("identifier")),
      Sequence(T("elifndef"), NT("identifier"))
    ),
    NT("new-line"),
    Optional(NT("group"))
  )
);

rules.set("else-group", () =>
  Diagram(T("#"), T("else"), NT("new-line"), Optional(NT("group")))
);

rules.set("endif-line", () =>
  Diagram(T("#"), T("endif"), NT("new-line"))
);

rules.set("text-line", () =>
  Diagram(Optional(NT("pp-tokens")), NT("new-line"))
);

rules.set("conditionally-supported-directive", () =>
  Diagram(NT("pp-tokens"), NT("new-line"))
);

rules.set("lparen", () =>
  Diagram(Comment("( not preceded by whitespace"))
);

rules.set("identifier-list", () =>
  Diagram(
    NT("identifier"),
    ZeroOrMore(Sequence(T(","), NT("identifier")))
  )
);

rules.set("replacement-list", () =>
  Diagram(Optional(NT("pp-tokens")))
);

rules.set("pp-tokens", () =>
  Diagram(OneOrMore(NT("preprocessing-token")))
);

rules.set("new-line", () =>
  Diagram(Comment("the new-line character"))
);

rules.set("defined-macro-expression", () =>
  Diagram(
    T("defined"),
    Choice(0,
      NT("identifier"),
      Sequence(T("("), NT("identifier"), T(")"))
    )
  )
);

rules.set("h-preprocessing-token", () =>
  Diagram(Comment("any preprocessing-token other than >"))
);

rules.set("h-pp-tokens", () =>
  Diagram(OneOrMore(NT("h-preprocessing-token")))
);

rules.set("header-name-tokens", () =>
  Diagram(
    Choice(0,
      NT("string-literal"),
      Sequence(T("<"), NT("h-pp-tokens"), T(">"))
    )
  )
);

rules.set("has-include-expression", () =>
  Diagram(
    T("__has_include"),
    T("("),
    Choice(0,
      NT("header-name"),
      NT("header-name-tokens")
    ),
    T(")")
  )
);

rules.set("has-attribute-expression", () =>
  Diagram(T("__has_cpp_attribute"), T("("), NT("pp-tokens"), T(")"))
);

rules.set("pp-module", () =>
  Diagram(
    Optional(T("export")),
    T("module"),
    Optional(NT("pp-tokens")),
    T(";"),
    NT("new-line")
  )
);

rules.set("pp-import", () =>
  Diagram(
    Optional(T("export")),
    T("import"),
    Choice(0,
      NT("header-name"),
      NT("header-name-tokens"),
      NT("pp-tokens")
    ),
    Optional(NT("pp-tokens")),
    T(";"),
    NT("new-line")
  )
);

rules.set("va-opt-replacement", () =>
  Diagram(T("__VA_OPT__"), T("("), Optional(NT("pp-tokens")), T(")"))
);


// --- Section definitions --------------------------------------------------------

export const SECTION_ORDER = [
  "keywords",
  "lexical",
  "literals",
  "basics",
  "expressions",
  "statements",
  "declarations",
  "modules",
  "classes",
  "overloading",
  "templates",
  "exceptions",
  "preprocessing",
] as const;

export type SectionId = (typeof SECTION_ORDER)[number];

export const SECTION_TITLES: Record<SectionId, string> = {
  keywords: "A.2 Keywords",
  lexical: "A.3 Lexical Conventions",
  literals: "A.3 Literals",
  basics: "A.4 Basics",
  expressions: "A.5 Expressions",
  statements: "A.6 Statements",
  declarations: "A.7 Declarations",
  modules: "A.8 Modules",
  classes: "A.9 Classes",
  overloading: "A.10 Overloading",
  templates: "A.11 Templates",
  exceptions: "A.12 Exception Handling",
  preprocessing: "A.13 Preprocessing Directives",
};

export const SECTION_RULES: Record<SectionId, string[]> = {
  keywords: [
    "typedef-name",
    "namespace-name",
    "namespace-alias",
    "class-name",
    "enum-name",
    "template-name",
  ],
  lexical: [
    "n-char",
    "n-char-sequence",
    "named-universal-character",
    "hex-quad",
    "simple-hexadecimal-digit-sequence",
    "universal-character-name",
    "preprocessing-token",
    "token",
    "header-name",
    "h-char-sequence",
    "h-char",
    "q-char-sequence",
    "q-char",
    "pp-number",
    "identifier",
    "identifier-start",
    "identifier-continue",
    "nondigit",
    "digit",
    "keyword",
    "preprocessing-op-or-punc",
    "preprocessing-operator",
    "operator-or-punctuator",
  ],
  literals: [
    "literal",
    "integer-literal",
    "binary-literal",
    "octal-literal",
    "decimal-literal",
    "hexadecimal-literal",
    "binary-digit",
    "octal-digit",
    "nonzero-digit",
    "hexadecimal-prefix",
    "hexadecimal-digit-sequence",
    "hexadecimal-digit",
    "integer-suffix",
    "unsigned-suffix",
    "long-suffix",
    "long-long-suffix",
    "size-suffix",
    "character-literal",
    "encoding-prefix",
    "c-char-sequence",
    "c-char",
    "basic-c-char",
    "escape-sequence",
    "simple-escape-sequence",
    "simple-escape-sequence-char",
    "numeric-escape-sequence",
    "simple-octal-digit-sequence",
    "octal-escape-sequence",
    "hexadecimal-escape-sequence",
    "conditional-escape-sequence",
    "conditional-escape-sequence-char",
    "floating-point-literal",
    "decimal-floating-point-literal",
    "hexadecimal-floating-point-literal",
    "fractional-constant",
    "hexadecimal-fractional-constant",
    "exponent-part",
    "binary-exponent-part",
    "sign",
    "digit-sequence",
    "floating-point-suffix",
    "string-literal",
    "s-char-sequence",
    "s-char",
    "basic-s-char",
    "raw-string",
    "r-char-sequence",
    "r-char",
    "d-char-sequence",
    "d-char",
    "boolean-literal",
    "pointer-literal",
    "user-defined-literal",
    "user-defined-integer-literal",
    "user-defined-floating-point-literal",
    "user-defined-string-literal",
    "user-defined-character-literal",
    "ud-suffix",
  ],
  basics: [
    "translation-unit",
  ],
  expressions: [
    "primary-expression",
    "id-expression",
    "unqualified-id",
    "qualified-id",
    "nested-name-specifier",
    "lambda-expression",
    "lambda-introducer",
    "lambda-declarator",
    "lambda-specifier",
    "lambda-specifier-seq",
    "lambda-capture",
    "capture-default",
    "capture-list",
    "capture",
    "simple-capture",
    "init-capture",
    "fold-expression",
    "fold-operator",
    "requires-expression",
    "requirement-parameter-list",
    "requirement-body",
    "requirement-seq",
    "requirement",
    "simple-requirement",
    "type-requirement",
    "compound-requirement",
    "return-type-requirement",
    "nested-requirement",
    "postfix-expression",
    "expression-list",
    "unary-expression",
    "unary-operator",
    "await-expression",
    "noexcept-expression",
    "new-expression",
    "new-placement",
    "new-type-id",
    "new-declarator",
    "noptr-new-declarator",
    "new-initializer",
    "delete-expression",
    "cast-expression",
    "pm-expression",
    "multiplicative-expression",
    "additive-expression",
    "shift-expression",
    "compare-expression",
    "relational-expression",
    "equality-expression",
    "and-expression",
    "exclusive-or-expression",
    "inclusive-or-expression",
    "logical-and-expression",
    "logical-or-expression",
    "conditional-expression",
    "yield-expression",
    "throw-expression",
    "assignment-expression",
    "assignment-operator",
    "expression",
    "constant-expression",
  ],
  statements: [
    "statement",
    "init-statement",
    "condition",
    "label",
    "labeled-statement",
    "expression-statement",
    "compound-statement",
    "statement-seq",
    "label-seq",
    "selection-statement",
    "iteration-statement",
    "for-range-declaration",
    "for-range-initializer",
    "jump-statement",
    "coroutine-return-statement",
    "declaration-statement",
  ],
  declarations: [
    "declaration-seq",
    "declaration",
    "name-declaration",
    "special-declaration",
    "block-declaration",
    "nodeclspec-function-declaration",
    "alias-declaration",
    "simple-declaration",
    "static_assert-declaration",
    "empty-declaration",
    "attribute-declaration",
    "decl-specifier",
    "decl-specifier-seq",
    "storage-class-specifier",
    "function-specifier",
    "explicit-specifier",
    "type-specifier",
    "type-specifier-seq",
    "defining-type-specifier",
    "defining-type-specifier-seq",
    "simple-type-specifier",
    "type-name",
    "elaborated-type-specifier",
    "decltype-specifier",
    "placeholder-type-specifier",
    "init-declarator-list",
    "init-declarator",
    "declarator",
    "ptr-declarator",
    "noptr-declarator",
    "parameters-and-qualifiers",
    "trailing-return-type",
    "ptr-operator",
    "cv-qualifier-seq",
    "cv-qualifier",
    "ref-qualifier",
    "declarator-id",
    "type-id",
    "defining-type-id",
    "abstract-declarator",
    "ptr-abstract-declarator",
    "noptr-abstract-declarator",
    "abstract-pack-declarator",
    "noptr-abstract-pack-declarator",
    "parameter-declaration-clause",
    "parameter-declaration-list",
    "parameter-declaration",
    "initializer",
    "brace-or-equal-initializer",
    "initializer-clause",
    "braced-init-list",
    "initializer-list",
    "designated-initializer-list",
    "designated-initializer-clause",
    "designator",
    "expr-or-braced-init-list",
    "function-definition",
    "function-body",
    "enum-specifier",
    "enum-head",
    "enum-head-name",
    "opaque-enum-declaration",
    "enum-key",
    "enum-base",
    "enumerator-list",
    "enumerator-definition",
    "enumerator",
    "using-enum-declaration",
    "using-enum-declarator",
    "namespace-definition",
    "named-namespace-definition",
    "unnamed-namespace-definition",
    "nested-namespace-definition",
    "enclosing-namespace-specifier",
    "namespace-body",
    "namespace-alias-definition",
    "qualified-namespace-specifier",
    "using-directive",
    "using-declaration",
    "using-declarator-list",
    "using-declarator",
    "asm-declaration",
    "linkage-specification",
    "attribute-specifier-seq",
    "attribute-specifier",
    "alignment-specifier",
    "attribute-using-prefix",
    "attribute-list",
    "attribute",
    "attribute-token",
    "attribute-scoped-token",
    "attribute-namespace",
    "attribute-argument-clause",
    "balanced-token-seq",
    "balanced-token",
  ],
  modules: [
    "module-declaration",
    "module-name",
    "module-partition",
    "module-name-qualifier",
    "export-declaration",
    "module-import-declaration",
    "global-module-fragment",
    "private-module-fragment",
  ],
  classes: [
    "class-specifier",
    "class-head",
    "class-head-name",
    "class-virt-specifier",
    "class-key",
    "member-specification",
    "member-declaration",
    "member-declarator-list",
    "member-declarator",
    "virt-specifier-seq",
    "virt-specifier",
    "pure-specifier",
    "conversion-function-id",
    "conversion-type-id",
    "conversion-declarator",
    "base-clause",
    "base-specifier-list",
    "base-specifier",
    "class-or-decltype",
    "access-specifier",
    "ctor-initializer",
    "mem-initializer-list",
    "mem-initializer",
    "mem-initializer-id",
  ],
  overloading: [
    "operator-function-id",
    "operator",
    "literal-operator-id",
  ],
  templates: [
    "template-declaration",
    "template-head",
    "template-parameter-list",
    "requires-clause",
    "constraint-logical-or-expression",
    "constraint-logical-and-expression",
    "template-parameter",
    "type-parameter",
    "type-parameter-key",
    "type-constraint",
    "simple-template-id",
    "template-id",
    "template-argument-list",
    "template-argument",
    "constraint-expression",
    "deduction-guide",
    "concept-definition",
    "concept-name",
    "typename-specifier",
    "explicit-instantiation",
    "explicit-specialization",
  ],
  exceptions: [
    "try-block",
    "function-try-block",
    "handler-seq",
    "handler",
    "exception-declaration",
    "noexcept-specifier",
  ],
  preprocessing: [
    "preprocessing-file",
    "module-file",
    "pp-global-module-fragment",
    "pp-private-module-fragment",
    "group",
    "group-part",
    "control-line",
    "if-section",
    "if-group",
    "elif-groups",
    "elif-group",
    "else-group",
    "endif-line",
    "text-line",
    "conditionally-supported-directive",
    "lparen",
    "identifier-list",
    "replacement-list",
    "pp-tokens",
    "new-line",
    "defined-macro-expression",
    "h-preprocessing-token",
    "h-pp-tokens",
    "header-name-tokens",
    "has-include-expression",
    "has-attribute-expression",
    "pp-module",
    "pp-import",
    "va-opt-replacement",
  ],
};

// --- Exports ----------------------------------------------------------------

/**
 * Union type of all rule names for type safety.
 */
export type RuleName = string;

/**
 * Creates a railroad diagram for a given rule name.
 * Returns undefined if the rule is not found.
 */
export function createRuleDiagram(name: string): any {
  const factory = rules.get(name);
  return factory ? factory() : undefined;
}

/**
 * Get all rule names for grammar coverage checking.
 */
export function getRuleNames(): string[] {
  return Array.from(rules.keys());
}
