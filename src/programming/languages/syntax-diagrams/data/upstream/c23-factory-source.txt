// c23-syntax-diagrams.mjs
//
// ES module that defines a practical subset of Annex A grammar as railroad diagrams.
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

// ===== A.2 Lexical grammar (condensed) =====

rules.set("token", () =>
  Diagram(
    Choice(0,
      NT("keyword"),
      NT("identifier"),
      NT("constant"),
      NT("string-literal"),
      NT("punctuator")
    )
  )
);

rules.set("preprocessing-token", () =>
  Diagram(
    Choice(0,
      NT("header-name"),
      NT("identifier"),
      NT("pp-number"),
      NT("character-constant"),
      NT("string-literal"),
      NT("punctuator"),
      NT("universal-character-name"),
      NT("non-white-space-character")
    )
  )
);

// identifier: identifier-start identifier-continue*
rules.set("identifier", () =>
  Diagram(
    Sequence(
      NT("identifier-start"),
      ZeroOrMore(NT("identifier-continue"))
    )
  )
);

rules.set("universal-character-name", () =>
  Diagram(
    Choice(0,
      Sequence(T("\\u"), NT("hex-quad")),
      Sequence(T("\\U"), NT("hex-quad"), NT("hex-quad"))
    )
  )
);

// constant: integer | floating | enumeration | character | predefined
rules.set("constant", () =>
  Diagram(
    Choice(0,
      NT("integer-constant"),
      NT("floating-constant"),
      NT("enumeration-constant"),
      NT("character-constant"),
      NT("predefined-constant")
    )
  )
);

// ===== A.3.1 Expressions =====

// primary-expression:
// identifier | constant | string-literal | ( expression ) | generic-selection
rules.set("primary-expression", () =>
  Diagram(
    Choice(0,
      NT("identifier"),
      NT("constant"),
      NT("string-literal"),
      Sequence(T("("), NT("expression"), T(")")),
      NT("generic-selection")
    )
  )
);

// generic-selection: _Generic ( assignment-expression , generic-assoc-list )
rules.set("generic-selection", () =>
  Diagram(
    Sequence(
      T("_Generic"),
      T("("),
      NT("assignment-expression"),
      T(","),
      NT("generic-assoc-list"),
      T(")")
    )
  )
);

// generic-assoc-list: generic-association ( , generic-association )*
rules.set("generic-assoc-list", () =>
  Diagram(
    Sequence(
      NT("generic-association"),
      ZeroOrMore(Sequence(T(","), NT("generic-association")))
    )
  )
);

// generic-association: type-name : assignment-expression | default : assignment-expression
rules.set("generic-association", () =>
  Diagram(
    Choice(0,
      Sequence(NT("type-name"), T(":"), NT("assignment-expression")),
      Sequence(T("default"), T(":"), NT("assignment-expression"))
    )
  )
);

// postfix-expression (diagram-friendly):
// (primary-expression | compound-literal) postfix-suffix*
rules.set("postfix-expression", () => {
  const postfixSuffix =
    Choice(0,
      Sequence(T("["), NT("expression"), T("]")),
      Sequence(T("("), Optional(NT("argument-expression-list")), T(")")),
      Sequence(T("."), NT("identifier")),
      Sequence(T("->"), NT("identifier")),
      T("++"),
      T("--")
    );

  return Diagram(
    Sequence(
      Choice(0, NT("primary-expression"), NT("compound-literal")),
      ZeroOrMore(postfixSuffix)
    )
  );
});

// unary-operator: & * + - ~ !
rules.set("unary-operator", () =>
  Diagram(
    Choice(0, T("&"), T("*"), T("+"), T("-"), T("~"), T("!"))
  )
);

// unary-expression (diagram-friendly, flattened):
rules.set("unary-expression", () => {
  const prefixOps = ZeroOrMore(Choice(0, T("++"), T("--"), T("sizeof")));
  const core =
    Choice(0,
      NT("postfix-expression"),
      Sequence(NT("unary-operator"), NT("cast-expression"))
    );

  return Diagram(
    Choice(0,
      Sequence(prefixOps, core),
      Sequence(T("sizeof"), T("("), NT("type-name"), T(")")),
      Sequence(T("alignof"), T("("), NT("type-name"), T(")"))
    )
  );
});

// cast-expression (diagram-friendly):
rules.set("cast-expression", () =>
  Diagram(
    Sequence(
      ZeroOrMore(Sequence(T("("), NT("type-name"), T(")"))),
      NT("unary-expression")
    )
  )
);

// precedence-chain helper: BASE ( (op) BASE )*
function chain(base: string, ops: string[]) {
  return Sequence(
    NT(base),
    ZeroOrMore(Sequence(Choice(0, ...ops.map(T)), NT(base)))
  );
}

rules.set("multiplicative-expression", () => Diagram(chain("cast-expression", ["*", "/", "%"])));
rules.set("additive-expression",       () => Diagram(chain("multiplicative-expression", ["+", "-"])));
rules.set("shift-expression",          () => Diagram(chain("additive-expression", ["<<", ">>"])));
rules.set("relational-expression",     () => Diagram(chain("shift-expression", ["<", ">", "<=", ">="])));
rules.set("equality-expression",       () => Diagram(chain("relational-expression", ["==", "!="])));
rules.set("AND-expression",            () => Diagram(chain("equality-expression", ["&"])));
rules.set("exclusive-OR-expression",   () => Diagram(chain("AND-expression", ["^"])));
rules.set("inclusive-OR-expression",   () => Diagram(chain("exclusive-OR-expression", ["|"])));
rules.set("logical-AND-expression",    () => Diagram(chain("inclusive-OR-expression", ["&&"])));
rules.set("logical-OR-expression",     () => Diagram(chain("logical-AND-expression", ["||"])));

// conditional-expression:
rules.set("conditional-expression", () =>
  Diagram(
    Sequence(
      NT("logical-OR-expression"),
      Optional(Sequence(T("?"), NT("expression"), T(":"), NT("conditional-expression")))
    )
  )
);

// assignment-operator: = *= /= %= += -= <<= >>= &= ^= |=
rules.set("assignment-operator", () =>
  Diagram(
    Choice(0,
      T("="), T("*="), T("/="), T("%="), T("+="), T("-="),
      T("<<="), T(">>="), T("&="), T("^="), T("|=")
    )
  )
);

// assignment-expression (diagram-friendly):
rules.set("assignment-expression", () =>
  Diagram(
    Choice(0,
      NT("conditional-expression"),
      Sequence(NT("unary-expression"), NT("assignment-operator"), NT("assignment-expression"))
    )
  )
);

// expression: assignment-expression ( , assignment-expression )*
rules.set("expression", () =>
  Diagram(
    Sequence(
      NT("assignment-expression"),
      ZeroOrMore(Sequence(T(","), NT("assignment-expression")))
    )
  )
);

// constant-expression: conditional-expression
rules.set("constant-expression", () => Diagram(NT("conditional-expression")));

// ===== A.3.2 Declarations (condensed where needed) =====

rules.set("declaration", () =>
  Diagram(
    Choice(0,
      Sequence(NT("declaration-specifiers"), Optional(NT("init-declarator-list")), T(";")),
      Sequence(NT("attribute-specifier-sequence"), NT("declaration-specifiers"), NT("init-declarator-list"), T(";")),
      NT("static_assert-declaration"),
      NT("attribute-declaration")
    )
  )
);

rules.set("declaration-specifiers", () =>
  Diagram(
    OneOrMore(
      Sequence(NT("declaration-specifier"), Optional(NT("attribute-specifier-sequence"))),
      Comment("one or more")
    )
  )
);

rules.set("declaration-specifier", () =>
  Diagram(
    Choice(0,
      NT("storage-class-specifier"),
      NT("type-specifier-qualifier"),
      NT("function-specifier")
    )
  )
);

rules.set("init-declarator-list", () =>
  Diagram(
    Sequence(
      NT("init-declarator"),
      ZeroOrMore(Sequence(T(","), NT("init-declarator")))
    )
  )
);

rules.set("init-declarator", () =>
  Diagram(
    Choice(0,
      NT("declarator"),
      Sequence(NT("declarator"), T("="), NT("initializer"))
    )
  )
);

// storage-class-specifiers: one or more storage-class-specifier
rules.set("storage-class-specifiers", () =>
  Diagram(OneOrMore(NT("storage-class-specifier")))
);

rules.set("storage-class-specifier", () =>
  Diagram(
    Choice(0, T("auto"), T("constexpr"), T("extern"), T("register"), T("static"), T("thread_local"), T("typedef"))
  )
);

rules.set("type-specifier-qualifier", () =>
  Diagram(
    Choice(0, NT("type-specifier"), NT("type-qualifier"), NT("alignment-specifier"))
  )
);

rules.set("type-specifier", () =>
  Diagram(
    Choice(0,
      T("void"), T("char"), T("short"), T("int"), T("long"),
      T("float"), T("double"), T("signed"), T("unsigned"),
      Sequence(T("_BitInt"), T("("), NT("constant-expression"), T(")")),
      T("bool"), T("_Complex"),
      T("_Decimal32"), T("_Decimal64"), T("_Decimal128"),
      NT("atomic-type-specifier"),
      NT("struct-or-union-specifier"),
      NT("enum-specifier"),
      NT("typedef-name"),
      NT("typeof-specifier")
    )
  )
);

rules.set("struct-or-union-specifier", () =>
  Diagram(
    Choice(0,
      Sequence(NT("struct-or-union"), Optional(NT("attribute-specifier-sequence")), Optional(NT("identifier")),
        T("{"), NT("member-declaration-list"), T("}")
      ),
      Sequence(NT("struct-or-union"), Optional(NT("attribute-specifier-sequence")), NT("identifier"))
    )
  )
);

rules.set("member-declaration-list", () =>
  Diagram(OneOrMore(NT("member-declaration")))
);

rules.set("member-declaration", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("attribute-specifier-sequence")), NT("specifier-qualifier-list"),
        Optional(NT("member-declarator-list")), T(";")
      ),
      NT("static_assert-declaration")
    )
  )
);

rules.set("specifier-qualifier-list", () =>
  Diagram(
    OneOrMore(Sequence(NT("type-specifier-qualifier"), Optional(NT("attribute-specifier-sequence"))))
  )
);

rules.set("enum-specifier", () =>
  Diagram(
    Choice(0,
      Sequence(T("enum"), Optional(NT("attribute-specifier-sequence")), Optional(NT("identifier")),
        Optional(NT("enum-type-specifier")), T("{"), NT("enumerator-list"), T("}")
      ),
      Sequence(T("enum"), Optional(NT("attribute-specifier-sequence")), Optional(NT("identifier")),
        Optional(NT("enum-type-specifier")), T("{"), NT("enumerator-list"), T(","), T("}")
      ),
      Sequence(T("enum"), NT("identifier"), Optional(NT("enum-type-specifier")))
    )
  )
);

rules.set("enumerator-list", () =>
  Diagram(Sequence(NT("enumerator"), ZeroOrMore(Sequence(T(","), NT("enumerator")))))
);

rules.set("enumerator", () =>
  Diagram(
    Choice(0,
      Sequence(NT("enumeration-constant"), Optional(NT("attribute-specifier-sequence"))),
      Sequence(NT("enumeration-constant"), Optional(NT("attribute-specifier-sequence")), T("="), NT("constant-expression"))
    )
  )
);

rules.set("atomic-type-specifier", () =>
  Diagram(Sequence(T("_Atomic"), T("("), NT("type-name"), T(")")))
);

rules.set("typeof-specifier", () =>
  Diagram(
    Choice(0,
      Sequence(T("typeof"), T("("), NT("typeof-specifier-argument"), T(")")),
      Sequence(T("typeof_unqual"), T("("), NT("typeof-specifier-argument"), T(")"))
    )
  )
);

rules.set("type-qualifier", () =>
  Diagram(Choice(0, T("const"), T("restrict"), T("volatile"), T("_Atomic")))
);

rules.set("type-qualifier-list", () =>
  Diagram(OneOrMore(NT("type-qualifier")))
);

rules.set("function-specifier", () =>
  Diagram(Choice(0, T("inline"), T("_Noreturn")))
);

rules.set("alignment-specifier", () =>
  Diagram(
    Choice(0,
      Sequence(T("alignas"), T("("), NT("type-name"), T(")")),
      Sequence(T("alignas"), T("("), NT("constant-expression"), T(")"))
    )
  )
);

// declarator: pointer? direct-declarator
rules.set("declarator", () =>
  Diagram(Sequence(Optional(NT("pointer")), NT("direct-declarator")))
);

// pointer (diagram-friendly): ("*" attr? type-qualifier-list?)+
rules.set("pointer", () =>
  Diagram(
    OneOrMore(
      Sequence(T("*"), Optional(NT("attribute-specifier-sequence")), Optional(NT("type-qualifier-list")))
    )
  )
);

// direct-declarator (diagram-friendly):
rules.set("direct-declarator", () => {
  const base = Choice(0,
    Sequence(NT("identifier"), Optional(NT("attribute-specifier-sequence"))),
    Sequence(T("("), NT("declarator"), T(")"))
  );

  const arrayBracket = Choice(0,
    Sequence(Optional(NT("type-qualifier-list")), Optional(NT("assignment-expression"))),
    Sequence(T("static"), Optional(NT("type-qualifier-list")), NT("assignment-expression")),
    Sequence(NT("type-qualifier-list"), T("static"), NT("assignment-expression")),
    Sequence(Optional(NT("type-qualifier-list")), T("*"))
  );

  const arraySuffix = Sequence(T("["), arrayBracket, T("]"), Optional(NT("attribute-specifier-sequence")));
  const funcSuffix = Sequence(T("("), Optional(NT("parameter-type-list")), T(")"), Optional(NT("attribute-specifier-sequence")));

  return Diagram(
    Sequence(base, ZeroOrMore(Choice(0, arraySuffix, funcSuffix)))
  );
});

rules.set("parameter-type-list", () =>
  Diagram(
    Choice(0,
      NT("parameter-list"),
      Sequence(NT("parameter-list"), T(","), T("...")),
      T("...")
    )
  )
);

rules.set("parameter-list", () =>
  Diagram(
    Sequence(
      NT("parameter-declaration"),
      ZeroOrMore(Sequence(T(","), NT("parameter-declaration")))
    )
  )
);

rules.set("parameter-declaration", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("attribute-specifier-sequence")), NT("declaration-specifiers"), NT("declarator")),
      Sequence(Optional(NT("attribute-specifier-sequence")), NT("declaration-specifiers"), Optional(NT("abstract-declarator")))
    )
  )
);

rules.set("type-name", () =>
  Diagram(Sequence(NT("specifier-qualifier-list"), Optional(NT("abstract-declarator"))))
);

rules.set("abstract-declarator", () =>
  Diagram(
    Choice(0,
      NT("pointer"),
      Sequence(Optional(NT("pointer")), NT("direct-abstract-declarator"))
    )
  )
);

// direct-abstract-declarator (diagram-friendly):
rules.set("direct-abstract-declarator", () => {
  const base = Choice(0,
    Sequence(T("("), NT("abstract-declarator"), T(")")),
    Comment("or empty base for suffix-only forms")
  );

  const arrayBracket = Choice(0,
    Sequence(Optional(NT("type-qualifier-list")), Optional(NT("assignment-expression"))),
    Sequence(T("static"), Optional(NT("type-qualifier-list")), NT("assignment-expression")),
    Sequence(NT("type-qualifier-list"), T("static"), NT("assignment-expression")),
    Sequence(T("*"))
  );

  const arraySuffix = Sequence(T("["), arrayBracket, T("]"), Optional(NT("attribute-specifier-sequence")));
  const funcSuffix  = Sequence(T("("), Optional(NT("parameter-type-list")), T(")"), Optional(NT("attribute-specifier-sequence")));

  return Diagram(Sequence(base, ZeroOrMore(Choice(0, arraySuffix, funcSuffix))));
});

rules.set("braced-initializer", () =>
  Diagram(
    Choice(0,
      Sequence(T("{"), T("}")),
      Sequence(T("{"), NT("initializer-list"), T("}")),
      Sequence(T("{"), NT("initializer-list"), T(","), T("}"))
    )
  )
);

rules.set("initializer", () =>
  Diagram(Choice(0, NT("assignment-expression"), NT("braced-initializer")))
);

rules.set("initializer-list", () =>
  Diagram(
    Sequence(
      Optional(NT("designation")),
      NT("initializer"),
      ZeroOrMore(Sequence(T(","), Optional(NT("designation")), NT("initializer")))
    )
  )
);

rules.set("designation", () =>
  Diagram(Sequence(NT("designator-list"), T("=")))
);

rules.set("designator-list", () =>
  Diagram(OneOrMore(NT("designator")))
);

rules.set("designator", () =>
  Diagram(
    Choice(0,
      Sequence(T("["), NT("constant-expression"), T("]")),
      Sequence(T("."), NT("identifier"))
    )
  )
);

// ===== A.3.3 Statements =====

rules.set("statement", () =>
  Diagram(Choice(0, NT("labeled-statement"), NT("unlabeled-statement")))
);

rules.set("label", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("attribute-specifier-sequence")), NT("identifier"), T(":")),
      Sequence(Optional(NT("attribute-specifier-sequence")), T("case"), NT("constant-expression"), T(":")),
      Sequence(Optional(NT("attribute-specifier-sequence")), T("default"), T(":"))
    )
  )
);

rules.set("labeled-statement", () =>
  Diagram(Sequence(NT("label"), NT("statement")))
);

rules.set("unlabeled-statement", () =>
  Diagram(
    Choice(0,
      NT("expression-statement"),
      Sequence(Optional(NT("attribute-specifier-sequence")), NT("primary-block")),
      Sequence(Optional(NT("attribute-specifier-sequence")), NT("jump-statement"))
    )
  )
);

rules.set("compound-statement", () =>
  Diagram(Sequence(T("{"), Optional(NT("block-item-list")), T("}")))
);

rules.set("block-item-list", () =>
  Diagram(OneOrMore(NT("block-item")))
);

rules.set("block-item", () =>
  Diagram(Choice(0, NT("declaration"), NT("unlabeled-statement"), NT("label")))
);

rules.set("expression-statement", () =>
  Diagram(
    Choice(0,
      Sequence(Optional(NT("expression")), T(";")),
      Sequence(NT("attribute-specifier-sequence"), NT("expression"), T(";"))
    )
  )
);

rules.set("selection-statement", () =>
  Diagram(
    Choice(0,
      Sequence(T("if"), T("("), NT("expression"), T(")"), NT("secondary-block")),
      Sequence(T("if"), T("("), NT("expression"), T(")"), NT("secondary-block"), T("else"), NT("secondary-block")),
      Sequence(T("switch"), T("("), NT("expression"), T(")"), NT("secondary-block"))
    )
  )
);

rules.set("iteration-statement", () =>
  Diagram(
    Choice(0,
      Sequence(T("while"), T("("), NT("expression"), T(")"), NT("secondary-block")),
      Sequence(T("do"), NT("secondary-block"), T("while"), T("("), NT("expression"), T(")"), T(";")),
      Sequence(T("for"), T("("), Optional(NT("expression")), T(";"), Optional(NT("expression")), T(";"), Optional(NT("expression")), T(")"), NT("secondary-block")),
      Sequence(T("for"), T("("), NT("declaration"), Optional(NT("expression")), T(";"), Optional(NT("expression")), T(")"), NT("secondary-block"))
    )
  )
);

rules.set("jump-statement", () =>
  Diagram(
    Choice(0,
      Sequence(T("goto"), NT("identifier"), T(";")),
      Sequence(T("continue"), T(";")),
      Sequence(T("break"), T(";")),
      Sequence(T("return"), Optional(NT("expression")), T(";"))
    )
  )
);

// ===== A.3.4 External definitions =====

rules.set("translation-unit", () =>
  Diagram(OneOrMore(NT("external-declaration")))
);

rules.set("external-declaration", () =>
  Diagram(Choice(0, NT("function-definition"), NT("declaration")))
);

rules.set("function-definition", () =>
  Diagram(
    Sequence(
      Optional(NT("attribute-specifier-sequence")),
      NT("declaration-specifiers"),
      NT("declarator"),
      NT("function-body")
    )
  )
);

rules.set("function-body", () =>
  Diagram(NT("compound-statement"))
);

// ===== A.4 Preprocessing directives (condensed) =====

rules.set("preprocessing-file", () =>
  Diagram(Optional(NT("group")))
);

rules.set("group", () =>
  Diagram(OneOrMore(NT("group-part")))
);

rules.set("group-part", () =>
  Diagram(
    Choice(0,
      NT("if-section"),
      NT("control-line"),
      NT("text-line"),
      Sequence(T("#"), NT("non-directive"))
    )
  )
);

rules.set("if-section", () =>
  Diagram(
    Sequence(
      NT("if-group"),
      Optional(NT("elif-groups")),
      Optional(NT("else-group")),
      NT("endif-line")
    )
  )
);

rules.set("if-group", () =>
  Diagram(
    Choice(0,
      Sequence(T("#"), T("if"), NT("constant-expression"), NT("new-line"), Optional(NT("group"))),
      Sequence(T("#"), T("ifdef"), NT("identifier"), NT("new-line"), Optional(NT("group"))),
      Sequence(T("#"), T("ifndef"), NT("identifier"), NT("new-line"), Optional(NT("group")))
    )
  )
);

rules.set("elif-groups", () => Diagram(OneOrMore(NT("elif-group"))));

rules.set("elif-group", () =>
  Diagram(
    Choice(0,
      Sequence(T("#"), T("elif"), NT("constant-expression"), NT("new-line"), Optional(NT("group"))),
      Sequence(T("#"), T("elifdef"), NT("identifier"), NT("new-line"), Optional(NT("group"))),
      Sequence(T("#"), T("elifndef"), NT("identifier"), NT("new-line"), Optional(NT("group")))
    )
  )
);

rules.set("else-group", () =>
  Diagram(Sequence(T("#"), T("else"), NT("new-line"), Optional(NT("group"))))
);

rules.set("endif-line", () =>
  Diagram(Sequence(T("#"), T("endif"), NT("new-line")))
);

rules.set("control-line", () =>
  Diagram(
    Choice(0,
      Sequence(T("#"), T("include"), NT("pp-tokens"), NT("new-line")),
      Sequence(T("#"), T("embed"), NT("pp-tokens"), NT("new-line")),
      Sequence(T("#"), T("define"), NT("identifier"), NT("replacement-list"), NT("new-line")),
      Sequence(T("#"), T("undef"), NT("identifier"), NT("new-line")),
      Sequence(T("#"), T("line"), NT("pp-tokens"), NT("new-line")),
      Sequence(T("#"), T("error"), Optional(NT("pp-tokens")), NT("new-line")),
      Sequence(T("#"), T("warning"), Optional(NT("pp-tokens")), NT("new-line")),
      Sequence(T("#"), T("pragma"), Optional(NT("pp-tokens")), NT("new-line")),
      Sequence(T("#"), NT("new-line"))
    )
  )
);

rules.set("text-line", () =>
  Diagram(Sequence(Optional(NT("pp-tokens")), NT("new-line")))
);

rules.set("non-directive", () =>
  Diagram(Sequence(NT("pp-tokens"), NT("new-line")))
);

rules.set("pp-tokens", () =>
  Diagram(OneOrMore(NT("preprocessing-token")))
);

rules.set("replacement-list", () =>
  Diagram(Optional(NT("pp-tokens")))
);

// --- React/TS integration exports --------------------------------------------

export type SectionId = "lexical" | "expressions" | "declarations" | "statements" | "external" | "preprocessor";
export type RuleName = string;

// Source-of-truth: which rules belong to which section (extracted from the old DOM renderer).
export const SECTION_ORDER: SectionId[] = [
  "lexical",
  "expressions",
  "declarations",
  "statements",
  "external",
  "preprocessor"
];

export const SECTION_TITLES: Record<SectionId, string> = {
  lexical: "Lexical Grammar",
  expressions: "Expressions",
  declarations: "Declarations",
  statements: "Statements",
  external: "External Definitions",
  preprocessor: "Preprocessing Directives",
};

export const SECTION_RULES: Record<SectionId, RuleName[]> = {
  "lexical": [
    "token",
    "preprocessing-token",
    "identifier",
    "universal-character-name",
    "constant"
  ],
  "expressions": [
    "primary-expression",
    "generic-selection",
    "generic-assoc-list",
    "generic-association",
    "postfix-expression",
    "unary-operator",
    "unary-expression",
    "cast-expression",
    "multiplicative-expression",
    "additive-expression",
    "shift-expression",
    "relational-expression",
    "equality-expression",
    "AND-expression",
    "exclusive-OR-expression",
    "inclusive-OR-expression",
    "logical-AND-expression",
    "logical-OR-expression",
    "conditional-expression",
    "assignment-operator",
    "assignment-expression",
    "expression",
    "constant-expression"
  ],
  "declarations": [
    "declaration",
    "declaration-specifiers",
    "declaration-specifier",
    "init-declarator-list",
    "init-declarator",
    "storage-class-specifiers",
    "storage-class-specifier",
    "type-specifier-qualifier",
    "type-specifier",
    "struct-or-union-specifier",
    "member-declaration-list",
    "member-declaration",
    "specifier-qualifier-list",
    "enum-specifier",
    "enumerator-list",
    "enumerator",
    "atomic-type-specifier",
    "typeof-specifier",
    "type-qualifier",
    "type-qualifier-list",
    "function-specifier",
    "alignment-specifier",
    "declarator",
    "pointer",
    "direct-declarator",
    "parameter-type-list",
    "parameter-list",
    "parameter-declaration",
    "type-name",
    "abstract-declarator",
    "direct-abstract-declarator",
    "braced-initializer",
    "initializer",
    "initializer-list",
    "designation",
    "designator-list",
    "designator"
  ],
  "statements": [
    "statement",
    "label",
    "labeled-statement",
    "unlabeled-statement",
    "compound-statement",
    "block-item-list",
    "block-item",
    "expression-statement",
    "selection-statement",
    "iteration-statement",
    "jump-statement"
  ],
  "external": [
    "translation-unit",
    "external-declaration",
    "function-definition",
    "function-body"
  ],
  "preprocessor": [
    "preprocessing-file",
    "group",
    "group-part",
    "if-section",
    "if-group",
    "elif-groups",
    "elif-group",
    "else-group",
    "endif-line",
    "control-line",
    "text-line",
    "non-directive",
    "pp-tokens",
    "replacement-list"
  ]
};

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

// Export rules map for grammar coverage checking
export function getRuleNames(): string[] {
  return Array.from(rules.keys());
}
