/**
 * Java 25 Grammar – Railroad Diagram Factories
 *
 * This file defines diagram factories for each Java 25 grammar rule.
 * Based on Java Language Specification SE 25, Chapter 19.
 *
 * Each rule is a factory function: () => D(...).
 * Use createRuleDiagram(name) to get the diagram object.
 */

import {
  Diagram,
  Sequence,
  Choice,
  Optional,
  OneOrMore,
  ZeroOrMore,
  Terminal,
  NonTerminal,
  Stack,
  Comment,
} from "@prantlf/railroad-diagrams/lib/index.mjs";

// Shorthand helpers
// NOTE: @prantlf/railroad-diagrams has shipped both factory-function and ES-class APIs
// across versions/build targets. Calling a class without `new` throws:
//   "Class constructor X cannot be invoked without 'new'"
// This wrapper supports either shape at runtime.
const __isClass = (fn: any): fn is new (...args: any[]) => any =>
  typeof fn === "function" && /^class\s/.test(Function.prototype.toString.call(fn));

const rr = (fn: any, ...args: any[]) => {
  if (__isClass(fn)) return new fn(...args);

  try {
    return fn(...args);
  } catch (err: any) {
    const msg = String(err?.message ?? err);
    if (
      msg.includes("without 'new'") ||
      msg.includes("Class constructor") ||
      msg.includes("Cannot call a class as a function")
    ) {
      return new fn(...args);
    }
    throw err;
  }
};

const D = (...items: any[]) => rr(Diagram, ...items);
const Seq = (...items: any[]) => rr(Sequence, ...items);
const Ch = (...items: any[]) => rr(Choice, ...items);
const Opt = (...items: any[]) => rr(Optional, ...items);
const OOM = (...items: any[]) => rr(OneOrMore, ...items);
const ZOM = (...items: any[]) => rr(ZeroOrMore, ...items);
const Stk = (...items: any[]) => rr(Stack, ...items);
const Cmt = (text: string, ...rest: any[]) => rr(Comment, text, ...rest);
const T = (text: string, ...rest: any[]) => rr(Terminal, text, ...rest);
const NT = (text: string, ...rest: any[]) => rr(NonTerminal, text, ...rest);

// ============================================================

// Section IDs and titles (for navigation)
// ============================================================

export type SectionId =
  | "lexical"
  | "types"
  | "names"
  | "packages"
  | "classes"
  | "interfaces"
  | "arrays"
  | "statements"
  | "expressions";

export const SECTION_ORDER: SectionId[] = [
  "lexical",
  "types",
  "names",
  "packages",
  "classes",
  "interfaces",
  "arrays",
  "statements",
  "expressions",
];

export const SECTION_TITLES: Record<SectionId, string> = {
  lexical: "§3 Lexical Structure",
  types: "§4 Types, Values, and Variables",
  names: "§6 Names",
  packages: "§7 Packages and Modules",
  classes: "§8 Classes",
  interfaces: "§9 Interfaces",
  arrays: "§10 Arrays",
  statements: "§14 Blocks, Statements, and Patterns",
  expressions: "§15 Expressions",
};

export const SECTION_RULES: Record<SectionId, string[]> = {
  lexical: [
    "Identifier",
    "IdentifierChars",
    "JavaLetter",
    "JavaLetterOrDigit",
    "TypeIdentifier",
    "UnqualifiedMethodIdentifier",
    "Literal",
  ],
  types: [
    "Type",
    "PrimitiveType",
    "NumericType",
    "IntegralType",
    "FloatingPointType",
    "ReferenceType",
    "ClassOrInterfaceType",
    "ClassType",
    "InterfaceType",
    "TypeVariable",
    "ArrayType",
    "Dims",
    "TypeParameter",
    "TypeParameterModifier",
    "TypeBound",
    "AdditionalBound",
    "TypeArguments",
    "TypeArgumentList",
    "TypeArgument",
    "Wildcard",
    "WildcardBounds",
  ],
  names: [
    "ModuleName",
    "PackageName",
    "TypeName",
    "ExpressionName",
    "MethodName",
    "PackageOrTypeName",
    "AmbiguousName",
  ],
  packages: [
    "CompilationUnit",
    "OrdinaryCompilationUnit",
    "ModularCompilationUnit",
    "PackageDeclaration",
    "PackageModifier",
    "ImportDeclaration",
    "SingleTypeImportDeclaration",
    "TypeImportOnDemandDeclaration",
    "SingleStaticImportDeclaration",
    "StaticImportOnDemandDeclaration",
    "SingleModuleImportDeclaration",
    "TopLevelClassOrInterfaceDeclaration",
    "ModuleDeclaration",
    "ModuleDirective",
    "RequiresModifier",
  ],
  classes: [
    "ClassDeclaration",
    "NormalClassDeclaration",
    "ClassModifier",
    "TypeParameters",
    "TypeParameterList",
    "ClassExtends",
    "ClassImplements",
    "InterfaceTypeList",
    "ClassPermits",
    "ClassBody",
    "ClassBodyDeclaration",
    "ClassMemberDeclaration",
    "FieldDeclaration",
    "FieldModifier",
    "VariableDeclaratorList",
    "VariableDeclarator",
    "VariableDeclaratorId",
    "VariableInitializer",
    "UnannType",
    "UnannPrimitiveType",
    "UnannReferenceType",
    "UnannClassOrInterfaceType",
    "UnannClassType",
    "UnannInterfaceType",
    "UnannTypeVariable",
    "UnannArrayType",
    "MethodDeclaration",
    "MethodModifier",
    "MethodHeader",
    "Result",
    "MethodDeclarator",
    "ReceiverParameter",
    "FormalParameterList",
    "FormalParameter",
    "VariableArityParameter",
    "VariableModifier",
    "Throws",
    "ExceptionTypeList",
    "ExceptionType",
    "MethodBody",
    "InstanceInitializer",
    "StaticInitializer",
    "ConstructorDeclaration",
    "ConstructorModifier",
    "ConstructorDeclarator",
    "SimpleTypeName",
    "ConstructorBody",
    "ConstructorInvocation",
    "EnumDeclaration",
    "EnumBody",
    "EnumConstantList",
    "EnumConstant",
    "EnumConstantModifier",
    "EnumBodyDeclarations",
    "RecordDeclaration",
    "RecordHeader",
    "RecordComponentList",
    "RecordComponent",
    "VariableArityRecordComponent",
    "RecordComponentModifier",
    "RecordBody",
    "RecordBodyDeclaration",
    "CompactConstructorDeclaration",
  ],
  interfaces: [
    "InterfaceDeclaration",
    "NormalInterfaceDeclaration",
    "InterfaceModifier",
    "InterfaceExtends",
    "InterfacePermits",
    "InterfaceBody",
    "InterfaceMemberDeclaration",
    "ConstantDeclaration",
    "ConstantModifier",
    "InterfaceMethodDeclaration",
    "InterfaceMethodModifier",
    "AnnotationInterfaceDeclaration",
    "AnnotationInterfaceBody",
    "AnnotationInterfaceMemberDeclaration",
    "AnnotationInterfaceElementDeclaration",
    "AnnotationInterfaceElementModifier",
    "DefaultValue",
    "Annotation",
    "NormalAnnotation",
    "ElementValuePairList",
    "ElementValuePair",
    "ElementValue",
    "ElementValueArrayInitializer",
    "ElementValueList",
    "MarkerAnnotation",
    "SingleElementAnnotation",
  ],
  arrays: [
    "ArrayInitializer",
    "VariableInitializerList",
  ],
  statements: [
    "Block",
    "BlockStatements",
    "BlockStatement",
    "LocalClassOrInterfaceDeclaration",
    "LocalVariableDeclarationStatement",
    "LocalVariableDeclaration",
    "LocalVariableType",
    "Statement",
    "StatementNoShortIf",
    "StatementWithoutTrailingSubstatement",
    "EmptyStatement",
    "LabeledStatement",
    "LabeledStatementNoShortIf",
    "ExpressionStatement",
    "StatementExpression",
    "IfThenStatement",
    "IfThenElseStatement",
    "IfThenElseStatementNoShortIf",
    "AssertStatement",
    "SwitchStatement",
    "SwitchBlock",
    "SwitchRule",
    "SwitchBlockStatementGroup",
    "SwitchLabel",
    "CaseConstant",
    "CasePattern",
    "Guard",
    "WhileStatement",
    "WhileStatementNoShortIf",
    "DoStatement",
    "ForStatement",
    "ForStatementNoShortIf",
    "BasicForStatement",
    "BasicForStatementNoShortIf",
    "ForInit",
    "ForUpdate",
    "StatementExpressionList",
    "EnhancedForStatement",
    "EnhancedForStatementNoShortIf",
    "BreakStatement",
    "YieldStatement",
    "ContinueStatement",
    "ReturnStatement",
    "ThrowStatement",
    "SynchronizedStatement",
    "TryStatement",
    "Catches",
    "CatchClause",
    "CatchFormalParameter",
    "CatchType",
    "Finally",
    "TryWithResourcesStatement",
    "ResourceSpecification",
    "ResourceList",
    "Resource",
    "VariableAccess",
    "Pattern",
    "TypePattern",
    "RecordPattern",
    "ComponentPatternList",
    "ComponentPattern",
    "MatchAllPattern",
  ],
  expressions: [
    "Primary",
    "PrimaryNoNewArray",
    "ClassLiteral",
    "ClassInstanceCreationExpression",
    "UnqualifiedClassInstanceCreationExpression",
    "ClassOrInterfaceTypeToInstantiate",
    "TypeArgumentsOrDiamond",
    "ArrayCreationExpression",
    "ArrayCreationExpressionWithoutInitializer",
    "ArrayCreationExpressionWithInitializer",
    "DimExprs",
    "DimExpr",
    "ArrayAccess",
    "FieldAccess",
    "MethodInvocation",
    "ArgumentList",
    "MethodReference",
    "Expression",
    "LambdaExpression",
    "LambdaParameters",
    "LambdaParameterList",
    "NormalLambdaParameter",
    "LambdaParameterType",
    "ConciseLambdaParameter",
    "LambdaBody",
    "AssignmentExpression",
    "Assignment",
    "LeftHandSide",
    "AssignmentOperator",
    "ConditionalExpression",
    "ConditionalOrExpression",
    "ConditionalAndExpression",
    "InclusiveOrExpression",
    "ExclusiveOrExpression",
    "AndExpression",
    "EqualityExpression",
    "RelationalExpression",
    "InstanceofExpression",
    "ShiftExpression",
    "AdditiveExpression",
    "MultiplicativeExpression",
    "UnaryExpression",
    "PreIncrementExpression",
    "PreDecrementExpression",
    "UnaryExpressionNotPlusMinus",
    "PostfixExpression",
    "PostIncrementExpression",
    "PostDecrementExpression",
    "CastExpression",
    "SwitchExpression",
  ],
};

// ============================================================
// Diagram factory map
// ============================================================

type DiagramFactory = () => any;
const rules = new Map<string, DiagramFactory>();

// ------------------------------------------------------------
// §3 Lexical Structure
// ------------------------------------------------------------

rules.set("Identifier", () =>
  D(
    Seq(
      NT("IdentifierChars"),
      Cmt("but not ReservedKeyword, BooleanLiteral, or NullLiteral")
    )
  )
);

rules.set("IdentifierChars", () =>
  D(
    Seq(NT("JavaLetter"), ZOM(NT("JavaLetterOrDigit")))
  )
);

rules.set("JavaLetter", () =>
  D(Cmt("any Unicode character that is a Java letter"))
);

rules.set("JavaLetterOrDigit", () =>
  D(Cmt("any Unicode character that is a Java letter-or-digit"))
);

rules.set("TypeIdentifier", () =>
  D(
    Seq(
      NT("Identifier"),
      Cmt("but not permits, record, sealed, var, or yield")
    )
  )
);

rules.set("UnqualifiedMethodIdentifier", () =>
  D(
    Seq(NT("Identifier"), Cmt("but not yield"))
  )
);

rules.set("Literal", () =>
  D(
    Ch(0,
      NT("IntegerLiteral"),
      NT("FloatingPointLiteral"),
      NT("BooleanLiteral"),
      NT("CharacterLiteral"),
      NT("StringLiteral"),
      NT("TextBlock"),
      NT("NullLiteral")
    )
  )
);

// ------------------------------------------------------------
// §4 Types, Values, and Variables
// ------------------------------------------------------------

rules.set("Type", () =>
  D(Ch(0, NT("PrimitiveType"), NT("ReferenceType")))
);

rules.set("PrimitiveType", () =>
  D(
    Ch(0,
      Seq(ZOM(NT("Annotation")), NT("NumericType")),
      Seq(ZOM(NT("Annotation")), T("boolean"))
    )
  )
);

rules.set("NumericType", () =>
  D(Ch(0, NT("IntegralType"), NT("FloatingPointType")))
);

rules.set("IntegralType", () =>
  D(Ch(0, T("byte"), T("short"), T("int"), T("long"), T("char")))
);

rules.set("FloatingPointType", () =>
  D(Ch(0, T("float"), T("double")))
);

rules.set("ReferenceType", () =>
  D(Ch(0, NT("ClassOrInterfaceType"), NT("TypeVariable"), NT("ArrayType")))
);

rules.set("ClassOrInterfaceType", () =>
  D(Ch(0, NT("ClassType"), NT("InterfaceType")))
);

rules.set("ClassType", () =>
  D(
    Ch(0,
      Seq(ZOM(NT("Annotation")), NT("TypeIdentifier"), Opt(NT("TypeArguments"))),
      Seq(NT("PackageName"), T("."), ZOM(NT("Annotation")), NT("TypeIdentifier"), Opt(NT("TypeArguments"))),
      Seq(NT("ClassOrInterfaceType"), T("."), ZOM(NT("Annotation")), NT("TypeIdentifier"), Opt(NT("TypeArguments")))
    )
  )
);

rules.set("InterfaceType", () =>
  D(NT("ClassType"))
);

rules.set("TypeVariable", () =>
  D(Seq(ZOM(NT("Annotation")), NT("TypeIdentifier")))
);

rules.set("ArrayType", () =>
  D(
    Ch(0,
      Seq(NT("PrimitiveType"), NT("Dims")),
      Seq(NT("ClassOrInterfaceType"), NT("Dims")),
      Seq(NT("TypeVariable"), NT("Dims"))
    )
  )
);

rules.set("Dims", () =>
  D(
    OOM(Seq(ZOM(NT("Annotation")), T("["), T("]")))
  )
);

rules.set("TypeParameter", () =>
  D(
    Seq(ZOM(NT("TypeParameterModifier")), NT("TypeIdentifier"), Opt(NT("TypeBound")))
  )
);

rules.set("TypeParameterModifier", () =>
  D(NT("Annotation"))
);

rules.set("TypeBound", () =>
  D(
    Ch(0,
      Seq(T("extends"), NT("TypeVariable")),
      Seq(T("extends"), NT("ClassOrInterfaceType"), ZOM(NT("AdditionalBound")))
    )
  )
);

rules.set("AdditionalBound", () =>
  D(Seq(T("&"), NT("InterfaceType")))
);

rules.set("TypeArguments", () =>
  D(Seq(T("<"), NT("TypeArgumentList"), T(">")))
);

rules.set("TypeArgumentList", () =>
  D(Seq(NT("TypeArgument"), ZOM(Seq(T(","), NT("TypeArgument")))))
);

rules.set("TypeArgument", () =>
  D(Ch(0, NT("ReferenceType"), NT("Wildcard")))
);

rules.set("Wildcard", () =>
  D(Seq(ZOM(NT("Annotation")), T("?"), Opt(NT("WildcardBounds"))))
);

rules.set("WildcardBounds", () =>
  D(
    Ch(0,
      Seq(T("extends"), NT("ReferenceType")),
      Seq(T("super"), NT("ReferenceType"))
    )
  )
);

// ------------------------------------------------------------
// §6 Names
// ------------------------------------------------------------

rules.set("ModuleName", () =>
  D(Seq(NT("Identifier"), ZOM(Seq(T("."), NT("Identifier")))))
);

rules.set("PackageName", () =>
  D(Seq(NT("Identifier"), ZOM(Seq(T("."), NT("Identifier")))))
);

rules.set("TypeName", () =>
  D(
    Ch(0,
      NT("TypeIdentifier"),
      Seq(NT("PackageOrTypeName"), T("."), NT("TypeIdentifier"))
    )
  )
);

rules.set("ExpressionName", () =>
  D(
    Ch(0,
      NT("Identifier"),
      Seq(NT("AmbiguousName"), T("."), NT("Identifier"))
    )
  )
);

rules.set("MethodName", () =>
  D(NT("UnqualifiedMethodIdentifier"))
);

rules.set("PackageOrTypeName", () =>
  D(Seq(NT("Identifier"), ZOM(Seq(T("."), NT("Identifier")))))
);

rules.set("AmbiguousName", () =>
  D(Seq(NT("Identifier"), ZOM(Seq(T("."), NT("Identifier")))))
);

// ------------------------------------------------------------
// §7 Packages and Modules
// ------------------------------------------------------------

rules.set("CompilationUnit", () =>
  D(
    Ch(0,
      NT("OrdinaryCompilationUnit"),
      NT("CompactCompilationUnit"),
      NT("ModularCompilationUnit")
    )
  )
);

rules.set("OrdinaryCompilationUnit", () =>
  D(
    Seq(
      Opt(NT("PackageDeclaration")),
      ZOM(NT("ImportDeclaration")),
      ZOM(NT("TopLevelClassOrInterfaceDeclaration"))
    )
  )
);

rules.set("ModularCompilationUnit", () =>
  D(Seq(ZOM(NT("ImportDeclaration")), NT("ModuleDeclaration")))
);

rules.set("PackageDeclaration", () =>
  D(
    Seq(
      ZOM(NT("PackageModifier")),
      T("package"),
      NT("Identifier"),
      ZOM(Seq(T("."), NT("Identifier"))),
      T(";")
    )
  )
);

rules.set("PackageModifier", () =>
  D(NT("Annotation"))
);

rules.set("ImportDeclaration", () =>
  D(
    Ch(0,
      NT("SingleTypeImportDeclaration"),
      NT("TypeImportOnDemandDeclaration"),
      NT("SingleStaticImportDeclaration"),
      NT("StaticImportOnDemandDeclaration"),
      NT("SingleModuleImportDeclaration")
    )
  )
);

rules.set("SingleTypeImportDeclaration", () =>
  D(Seq(T("import"), NT("TypeName"), T(";")))
);

rules.set("TypeImportOnDemandDeclaration", () =>
  D(Seq(T("import"), NT("PackageOrTypeName"), T("."), T("*"), T(";")))
);

rules.set("SingleStaticImportDeclaration", () =>
  D(Seq(T("import"), T("static"), NT("TypeName"), T("."), NT("Identifier"), T(";")))
);

rules.set("StaticImportOnDemandDeclaration", () =>
  D(Seq(T("import"), T("static"), NT("TypeName"), T("."), T("*"), T(";")))
);

rules.set("SingleModuleImportDeclaration", () =>
  D(Seq(T("import"), T("module"), NT("ModuleName"), T(";")))
);

rules.set("TopLevelClassOrInterfaceDeclaration", () =>
  D(Ch(0, NT("ClassDeclaration"), NT("InterfaceDeclaration"), T(";")))
);

rules.set("ModuleDeclaration", () =>
  D(
    Seq(
      ZOM(NT("Annotation")),
      Opt(T("open")),
      T("module"),
      NT("Identifier"),
      ZOM(Seq(T("."), NT("Identifier"))),
      T("{"),
      ZOM(NT("ModuleDirective")),
      T("}")
    )
  )
);

rules.set("ModuleDirective", () =>
  D(
    Ch(0,
      Seq(T("requires"), ZOM(NT("RequiresModifier")), NT("ModuleName"), T(";")),
      Seq(T("exports"), NT("PackageName"), Opt(Seq(T("to"), NT("ModuleName"), ZOM(Seq(T(","), NT("ModuleName"))))), T(";")),
      Seq(T("opens"), NT("PackageName"), Opt(Seq(T("to"), NT("ModuleName"), ZOM(Seq(T(","), NT("ModuleName"))))), T(";")),
      Seq(T("uses"), NT("TypeName"), T(";")),
      Seq(T("provides"), NT("TypeName"), T("with"), NT("TypeName"), ZOM(Seq(T(","), NT("TypeName"))), T(";"))
    )
  )
);

rules.set("RequiresModifier", () =>
  D(Ch(0, T("transitive"), T("static")))
);

// ------------------------------------------------------------
// §8 Classes
// ------------------------------------------------------------

rules.set("ClassDeclaration", () =>
  D(Ch(0, NT("NormalClassDeclaration"), NT("EnumDeclaration"), NT("RecordDeclaration")))
);

rules.set("NormalClassDeclaration", () =>
  D(
    Seq(
      ZOM(NT("ClassModifier")),
      T("class"),
      NT("TypeIdentifier"),
      Opt(NT("TypeParameters")),
      Opt(NT("ClassExtends")),
      Opt(NT("ClassImplements")),
      Opt(NT("ClassPermits")),
      NT("ClassBody")
    )
  )
);

rules.set("ClassModifier", () =>
  D(
    Ch(0,
      NT("Annotation"),
      T("public"),
      T("protected"),
      T("private"),
      T("abstract"),
      T("static"),
      T("final"),
      T("sealed"),
      T("non-sealed"),
      T("strictfp")
    )
  )
);

rules.set("TypeParameters", () =>
  D(Seq(T("<"), NT("TypeParameterList"), T(">")))
);

rules.set("TypeParameterList", () =>
  D(Seq(NT("TypeParameter"), ZOM(Seq(T(","), NT("TypeParameter")))))
);

rules.set("ClassExtends", () =>
  D(Seq(T("extends"), NT("ClassType")))
);

rules.set("ClassImplements", () =>
  D(Seq(T("implements"), NT("InterfaceTypeList")))
);

rules.set("InterfaceTypeList", () =>
  D(Seq(NT("InterfaceType"), ZOM(Seq(T(","), NT("InterfaceType")))))
);

rules.set("ClassPermits", () =>
  D(Seq(T("permits"), NT("TypeName"), ZOM(Seq(T(","), NT("TypeName")))))
);

rules.set("ClassBody", () =>
  D(Seq(T("{"), ZOM(NT("ClassBodyDeclaration")), T("}")))
);

rules.set("ClassBodyDeclaration", () =>
  D(
    Ch(0,
      NT("ClassMemberDeclaration"),
      NT("InstanceInitializer"),
      NT("StaticInitializer"),
      NT("ConstructorDeclaration")
    )
  )
);

rules.set("ClassMemberDeclaration", () =>
  D(
    Ch(0,
      NT("FieldDeclaration"),
      NT("MethodDeclaration"),
      NT("ClassDeclaration"),
      NT("InterfaceDeclaration"),
      T(";")
    )
  )
);

rules.set("FieldDeclaration", () =>
  D(Seq(ZOM(NT("FieldModifier")), NT("UnannType"), NT("VariableDeclaratorList"), T(";")))
);

rules.set("FieldModifier", () =>
  D(
    Ch(0,
      NT("Annotation"),
      T("public"),
      T("protected"),
      T("private"),
      T("static"),
      T("final"),
      T("transient"),
      T("volatile")
    )
  )
);

rules.set("VariableDeclaratorList", () =>
  D(Seq(NT("VariableDeclarator"), ZOM(Seq(T(","), NT("VariableDeclarator")))))
);

rules.set("VariableDeclarator", () =>
  D(Seq(NT("VariableDeclaratorId"), Opt(Seq(T("="), NT("VariableInitializer")))))
);

rules.set("VariableDeclaratorId", () =>
  D(Ch(0, Seq(NT("Identifier"), Opt(NT("Dims"))), T("_")))
);

rules.set("VariableInitializer", () =>
  D(Ch(0, NT("Expression"), NT("ArrayInitializer")))
);

rules.set("UnannType", () =>
  D(Ch(0, NT("UnannPrimitiveType"), NT("UnannReferenceType")))
);

rules.set("UnannPrimitiveType", () =>
  D(Ch(0, NT("NumericType"), T("boolean")))
);

rules.set("UnannReferenceType", () =>
  D(Ch(0, NT("UnannClassOrInterfaceType"), NT("UnannTypeVariable"), NT("UnannArrayType")))
);

rules.set("UnannClassOrInterfaceType", () =>
  D(Ch(0, NT("UnannClassType"), NT("UnannInterfaceType")))
);

rules.set("UnannClassType", () =>
  D(
    Ch(0,
      Seq(NT("TypeIdentifier"), Opt(NT("TypeArguments"))),
      Seq(NT("PackageName"), T("."), ZOM(NT("Annotation")), NT("TypeIdentifier"), Opt(NT("TypeArguments"))),
      Seq(NT("UnannClassOrInterfaceType"), T("."), ZOM(NT("Annotation")), NT("TypeIdentifier"), Opt(NT("TypeArguments")))
    )
  )
);

rules.set("UnannInterfaceType", () =>
  D(NT("UnannClassType"))
);

rules.set("UnannTypeVariable", () =>
  D(NT("TypeIdentifier"))
);

rules.set("UnannArrayType", () =>
  D(
    Ch(0,
      Seq(NT("UnannPrimitiveType"), NT("Dims")),
      Seq(NT("UnannClassOrInterfaceType"), NT("Dims")),
      Seq(NT("UnannTypeVariable"), NT("Dims"))
    )
  )
);

rules.set("MethodDeclaration", () =>
  D(Seq(ZOM(NT("MethodModifier")), NT("MethodHeader"), NT("MethodBody")))
);

rules.set("MethodModifier", () =>
  D(
    Ch(0,
      NT("Annotation"),
      T("public"),
      T("protected"),
      T("private"),
      T("abstract"),
      T("static"),
      T("final"),
      T("synchronized"),
      T("native"),
      T("strictfp")
    )
  )
);

rules.set("MethodHeader", () =>
  D(
    Ch(0,
      Seq(NT("Result"), NT("MethodDeclarator"), Opt(NT("Throws"))),
      Seq(NT("TypeParameters"), ZOM(NT("Annotation")), NT("Result"), NT("MethodDeclarator"), Opt(NT("Throws")))
    )
  )
);

rules.set("Result", () =>
  D(Ch(0, NT("UnannType"), T("void")))
);

rules.set("MethodDeclarator", () =>
  D(
    Seq(
      NT("Identifier"),
      T("("),
      Opt(Seq(NT("ReceiverParameter"), T(","))),
      Opt(NT("FormalParameterList")),
      T(")"),
      Opt(NT("Dims"))
    )
  )
);

rules.set("ReceiverParameter", () =>
  D(Seq(ZOM(NT("Annotation")), NT("UnannType"), Opt(Seq(NT("Identifier"), T("."))), T("this")))
);

rules.set("FormalParameterList", () =>
  D(Seq(NT("FormalParameter"), ZOM(Seq(T(","), NT("FormalParameter")))))
);

rules.set("FormalParameter", () =>
  D(
    Ch(0,
      Seq(ZOM(NT("VariableModifier")), NT("UnannType"), NT("VariableDeclaratorId")),
      NT("VariableArityParameter")
    )
  )
);

rules.set("VariableArityParameter", () =>
  D(Seq(ZOM(NT("VariableModifier")), NT("UnannType"), ZOM(NT("Annotation")), T("..."), NT("Identifier")))
);

rules.set("VariableModifier", () =>
  D(Ch(0, NT("Annotation"), T("final")))
);

rules.set("Throws", () =>
  D(Seq(T("throws"), NT("ExceptionTypeList")))
);

rules.set("ExceptionTypeList", () =>
  D(Seq(NT("ExceptionType"), ZOM(Seq(T(","), NT("ExceptionType")))))
);

rules.set("ExceptionType", () =>
  D(Ch(0, NT("ClassType"), NT("TypeVariable")))
);

rules.set("MethodBody", () =>
  D(Ch(0, NT("Block"), T(";")))
);

rules.set("InstanceInitializer", () =>
  D(NT("Block"))
);

rules.set("StaticInitializer", () =>
  D(Seq(T("static"), NT("Block")))
);

rules.set("ConstructorDeclaration", () =>
  D(Seq(ZOM(NT("ConstructorModifier")), NT("ConstructorDeclarator"), Opt(NT("Throws")), NT("ConstructorBody")))
);

rules.set("ConstructorModifier", () =>
  D(Ch(0, NT("Annotation"), T("public"), T("protected"), T("private")))
);

rules.set("ConstructorDeclarator", () =>
  D(
    Seq(
      Opt(NT("TypeParameters")),
      NT("SimpleTypeName"),
      T("("),
      Opt(Seq(NT("ReceiverParameter"), T(","))),
      Opt(NT("FormalParameterList")),
      T(")")
    )
  )
);

rules.set("SimpleTypeName", () =>
  D(NT("TypeIdentifier"))
);

rules.set("ConstructorBody", () =>
  D(
    Ch(0,
      Seq(T("{"), Opt(NT("BlockStatements")), NT("ConstructorInvocation"), Opt(NT("BlockStatements")), T("}")),
      Seq(T("{"), Opt(NT("BlockStatements")), T("}"))
    )
  )
);

rules.set("ConstructorInvocation", () =>
  D(
    Ch(0,
      Seq(Opt(NT("TypeArguments")), T("this"), T("("), Opt(NT("ArgumentList")), T(")"), T(";")),
      Seq(Opt(NT("TypeArguments")), T("super"), T("("), Opt(NT("ArgumentList")), T(")"), T(";")),
      Seq(NT("ExpressionName"), T("."), Opt(NT("TypeArguments")), T("super"), T("("), Opt(NT("ArgumentList")), T(")"), T(";")),
      Seq(NT("Primary"), T("."), Opt(NT("TypeArguments")), T("super"), T("("), Opt(NT("ArgumentList")), T(")"), T(";"))
    )
  )
);

rules.set("EnumDeclaration", () =>
  D(Seq(ZOM(NT("ClassModifier")), T("enum"), NT("TypeIdentifier"), Opt(NT("ClassImplements")), NT("EnumBody")))
);

rules.set("EnumBody", () =>
  D(Seq(T("{"), Opt(NT("EnumConstantList")), Opt(T(",")), Opt(NT("EnumBodyDeclarations")), T("}")))
);

rules.set("EnumConstantList", () =>
  D(Seq(NT("EnumConstant"), ZOM(Seq(T(","), NT("EnumConstant")))))
);

rules.set("EnumConstant", () =>
  D(Seq(ZOM(NT("EnumConstantModifier")), NT("Identifier"), Opt(Seq(T("("), Opt(NT("ArgumentList")), T(")"))), Opt(NT("ClassBody"))))
);

rules.set("EnumConstantModifier", () =>
  D(NT("Annotation"))
);

rules.set("EnumBodyDeclarations", () =>
  D(Seq(T(";"), ZOM(NT("ClassBodyDeclaration"))))
);

rules.set("RecordDeclaration", () =>
  D(
    Seq(
      ZOM(NT("ClassModifier")),
      T("record"),
      NT("TypeIdentifier"),
      Opt(NT("TypeParameters")),
      NT("RecordHeader"),
      Opt(NT("ClassImplements")),
      NT("RecordBody")
    )
  )
);

rules.set("RecordHeader", () =>
  D(Seq(T("("), Opt(NT("RecordComponentList")), T(")")))
);

rules.set("RecordComponentList", () =>
  D(Seq(NT("RecordComponent"), ZOM(Seq(T(","), NT("RecordComponent")))))
);

rules.set("RecordComponent", () =>
  D(
    Ch(0,
      Seq(ZOM(NT("RecordComponentModifier")), NT("UnannType"), NT("Identifier")),
      NT("VariableArityRecordComponent")
    )
  )
);

rules.set("VariableArityRecordComponent", () =>
  D(Seq(ZOM(NT("RecordComponentModifier")), NT("UnannType"), ZOM(NT("Annotation")), T("..."), NT("Identifier")))
);

rules.set("RecordComponentModifier", () =>
  D(NT("Annotation"))
);

rules.set("RecordBody", () =>
  D(Seq(T("{"), ZOM(NT("RecordBodyDeclaration")), T("}")))
);

rules.set("RecordBodyDeclaration", () =>
  D(Ch(0, NT("ClassBodyDeclaration"), NT("CompactConstructorDeclaration")))
);

rules.set("CompactConstructorDeclaration", () =>
  D(Seq(ZOM(NT("ConstructorModifier")), NT("SimpleTypeName"), NT("ConstructorBody")))
);

// ------------------------------------------------------------
// §9 Interfaces
// ------------------------------------------------------------

rules.set("InterfaceDeclaration", () =>
  D(Ch(0, NT("NormalInterfaceDeclaration"), NT("AnnotationInterfaceDeclaration")))
);

rules.set("NormalInterfaceDeclaration", () =>
  D(
    Seq(
      ZOM(NT("InterfaceModifier")),
      T("interface"),
      NT("TypeIdentifier"),
      Opt(NT("TypeParameters")),
      Opt(NT("InterfaceExtends")),
      Opt(NT("InterfacePermits")),
      NT("InterfaceBody")
    )
  )
);

rules.set("InterfaceModifier", () =>
  D(
    Ch(0,
      NT("Annotation"),
      T("public"),
      T("protected"),
      T("private"),
      T("abstract"),
      T("static"),
      T("sealed"),
      T("non-sealed"),
      T("strictfp")
    )
  )
);

rules.set("InterfaceExtends", () =>
  D(Seq(T("extends"), NT("InterfaceTypeList")))
);

rules.set("InterfacePermits", () =>
  D(Seq(T("permits"), NT("TypeName"), ZOM(Seq(T(","), NT("TypeName")))))
);

rules.set("InterfaceBody", () =>
  D(Seq(T("{"), ZOM(NT("InterfaceMemberDeclaration")), T("}")))
);

rules.set("InterfaceMemberDeclaration", () =>
  D(
    Ch(0,
      NT("ConstantDeclaration"),
      NT("InterfaceMethodDeclaration"),
      NT("ClassDeclaration"),
      NT("InterfaceDeclaration"),
      T(";")
    )
  )
);

rules.set("ConstantDeclaration", () =>
  D(Seq(ZOM(NT("ConstantModifier")), NT("UnannType"), NT("VariableDeclaratorList"), T(";")))
);

rules.set("ConstantModifier", () =>
  D(Ch(0, NT("Annotation"), T("public"), T("static"), T("final")))
);

rules.set("InterfaceMethodDeclaration", () =>
  D(Seq(ZOM(NT("InterfaceMethodModifier")), NT("MethodHeader"), NT("MethodBody")))
);

rules.set("InterfaceMethodModifier", () =>
  D(Ch(0, NT("Annotation"), T("public"), T("private"), T("abstract"), T("default"), T("static"), T("strictfp")))
);

rules.set("AnnotationInterfaceDeclaration", () =>
  D(Seq(ZOM(NT("InterfaceModifier")), T("@"), T("interface"), NT("TypeIdentifier"), NT("AnnotationInterfaceBody")))
);

rules.set("AnnotationInterfaceBody", () =>
  D(Seq(T("{"), ZOM(NT("AnnotationInterfaceMemberDeclaration")), T("}")))
);

rules.set("AnnotationInterfaceMemberDeclaration", () =>
  D(
    Ch(0,
      NT("AnnotationInterfaceElementDeclaration"),
      NT("ConstantDeclaration"),
      NT("ClassDeclaration"),
      NT("InterfaceDeclaration"),
      T(";")
    )
  )
);

rules.set("AnnotationInterfaceElementDeclaration", () =>
  D(
    Seq(
      ZOM(NT("AnnotationInterfaceElementModifier")),
      NT("UnannType"),
      NT("Identifier"),
      T("("),
      T(")"),
      Opt(NT("Dims")),
      Opt(NT("DefaultValue")),
      T(";")
    )
  )
);

rules.set("AnnotationInterfaceElementModifier", () =>
  D(Ch(0, NT("Annotation"), T("public"), T("abstract")))
);

rules.set("DefaultValue", () =>
  D(Seq(T("default"), NT("ElementValue")))
);

rules.set("Annotation", () =>
  D(Ch(0, NT("NormalAnnotation"), NT("MarkerAnnotation"), NT("SingleElementAnnotation")))
);

rules.set("NormalAnnotation", () =>
  D(Seq(T("@"), NT("TypeName"), T("("), Opt(NT("ElementValuePairList")), T(")")))
);

rules.set("ElementValuePairList", () =>
  D(Seq(NT("ElementValuePair"), ZOM(Seq(T(","), NT("ElementValuePair")))))
);

rules.set("ElementValuePair", () =>
  D(Seq(NT("Identifier"), T("="), NT("ElementValue")))
);

rules.set("ElementValue", () =>
  D(Ch(0, NT("ConditionalExpression"), NT("ElementValueArrayInitializer"), NT("Annotation")))
);

rules.set("ElementValueArrayInitializer", () =>
  D(Seq(T("{"), Opt(NT("ElementValueList")), Opt(T(",")), T("}")))
);

rules.set("ElementValueList", () =>
  D(Seq(NT("ElementValue"), ZOM(Seq(T(","), NT("ElementValue")))))
);

rules.set("MarkerAnnotation", () =>
  D(Seq(T("@"), NT("TypeName")))
);

rules.set("SingleElementAnnotation", () =>
  D(Seq(T("@"), NT("TypeName"), T("("), NT("ElementValue"), T(")")))
);

// ------------------------------------------------------------
// §10 Arrays
// ------------------------------------------------------------

rules.set("ArrayInitializer", () =>
  D(Seq(T("{"), Opt(NT("VariableInitializerList")), Opt(T(",")), T("}")))
);

rules.set("VariableInitializerList", () =>
  D(Seq(NT("VariableInitializer"), ZOM(Seq(T(","), NT("VariableInitializer")))))
);

// ------------------------------------------------------------
// §14 Blocks, Statements, and Patterns
// ------------------------------------------------------------

rules.set("Block", () =>
  D(Seq(T("{"), Opt(NT("BlockStatements")), T("}")))
);

rules.set("BlockStatements", () =>
  D(OOM(NT("BlockStatement")))
);

rules.set("BlockStatement", () =>
  D(Ch(0, NT("LocalClassOrInterfaceDeclaration"), NT("LocalVariableDeclarationStatement"), NT("Statement")))
);

rules.set("LocalClassOrInterfaceDeclaration", () =>
  D(Ch(0, NT("ClassDeclaration"), NT("NormalInterfaceDeclaration")))
);

rules.set("LocalVariableDeclarationStatement", () =>
  D(Seq(NT("LocalVariableDeclaration"), T(";")))
);

rules.set("LocalVariableDeclaration", () =>
  D(Seq(ZOM(NT("VariableModifier")), NT("LocalVariableType"), NT("VariableDeclaratorList")))
);

rules.set("LocalVariableType", () =>
  D(Ch(0, NT("UnannType"), T("var")))
);

rules.set("Statement", () =>
  D(
    Ch(0,
      NT("StatementWithoutTrailingSubstatement"),
      NT("LabeledStatement"),
      NT("IfThenStatement"),
      NT("IfThenElseStatement"),
      NT("WhileStatement"),
      NT("ForStatement")
    )
  )
);

rules.set("StatementNoShortIf", () =>
  D(
    Ch(0,
      NT("StatementWithoutTrailingSubstatement"),
      NT("LabeledStatementNoShortIf"),
      NT("IfThenElseStatementNoShortIf"),
      NT("WhileStatementNoShortIf"),
      NT("ForStatementNoShortIf")
    )
  )
);

rules.set("StatementWithoutTrailingSubstatement", () =>
  D(
    Ch(0,
      NT("Block"),
      NT("EmptyStatement"),
      NT("ExpressionStatement"),
      NT("AssertStatement"),
      NT("SwitchStatement"),
      NT("DoStatement"),
      NT("BreakStatement"),
      NT("ContinueStatement"),
      NT("ReturnStatement"),
      NT("SynchronizedStatement"),
      NT("ThrowStatement"),
      NT("TryStatement"),
      NT("YieldStatement")
    )
  )
);

rules.set("EmptyStatement", () =>
  D(T(";"))
);

rules.set("LabeledStatement", () =>
  D(Seq(NT("Identifier"), T(":"), NT("Statement")))
);

rules.set("LabeledStatementNoShortIf", () =>
  D(Seq(NT("Identifier"), T(":"), NT("StatementNoShortIf")))
);

rules.set("ExpressionStatement", () =>
  D(Seq(NT("StatementExpression"), T(";")))
);

rules.set("StatementExpression", () =>
  D(
    Ch(0,
      NT("Assignment"),
      NT("PreIncrementExpression"),
      NT("PreDecrementExpression"),
      NT("PostIncrementExpression"),
      NT("PostDecrementExpression"),
      NT("MethodInvocation"),
      NT("ClassInstanceCreationExpression")
    )
  )
);

rules.set("IfThenStatement", () =>
  D(Seq(T("if"), T("("), NT("Expression"), T(")"), NT("Statement")))
);

rules.set("IfThenElseStatement", () =>
  D(Seq(T("if"), T("("), NT("Expression"), T(")"), NT("StatementNoShortIf"), T("else"), NT("Statement")))
);

rules.set("IfThenElseStatementNoShortIf", () =>
  D(Seq(T("if"), T("("), NT("Expression"), T(")"), NT("StatementNoShortIf"), T("else"), NT("StatementNoShortIf")))
);

rules.set("AssertStatement", () =>
  D(
    Ch(0,
      Seq(T("assert"), NT("Expression"), T(";")),
      Seq(T("assert"), NT("Expression"), T(":"), NT("Expression"), T(";"))
    )
  )
);

rules.set("SwitchStatement", () =>
  D(Seq(T("switch"), T("("), NT("Expression"), T(")"), NT("SwitchBlock")))
);

rules.set("SwitchBlock", () =>
  D(
    Ch(0,
      Seq(T("{"), OOM(NT("SwitchRule")), T("}")),
      Seq(T("{"), ZOM(NT("SwitchBlockStatementGroup")), ZOM(Seq(NT("SwitchLabel"), T(":"))), T("}"))
    )
  )
);

rules.set("SwitchRule", () =>
  D(
    Ch(0,
      Seq(NT("SwitchLabel"), T("->"), NT("Expression"), T(";")),
      Seq(NT("SwitchLabel"), T("->"), NT("Block")),
      Seq(NT("SwitchLabel"), T("->"), NT("ThrowStatement"))
    )
  )
);

rules.set("SwitchBlockStatementGroup", () =>
  D(Seq(NT("SwitchLabel"), T(":"), ZOM(Seq(NT("SwitchLabel"), T(":"))), NT("BlockStatements")))
);

rules.set("SwitchLabel", () =>
  D(
    Ch(0,
      Seq(T("case"), NT("CaseConstant"), ZOM(Seq(T(","), NT("CaseConstant")))),
      Seq(T("case"), T("null"), Opt(Seq(T(","), T("default")))),
      Seq(T("case"), NT("CasePattern"), ZOM(Seq(T(","), NT("CasePattern"))), Opt(NT("Guard"))),
      T("default")
    )
  )
);

rules.set("CaseConstant", () =>
  D(NT("ConditionalExpression"))
);

rules.set("CasePattern", () =>
  D(NT("Pattern"))
);

rules.set("Guard", () =>
  D(Seq(T("when"), NT("Expression")))
);

rules.set("WhileStatement", () =>
  D(Seq(T("while"), T("("), NT("Expression"), T(")"), NT("Statement")))
);

rules.set("WhileStatementNoShortIf", () =>
  D(Seq(T("while"), T("("), NT("Expression"), T(")"), NT("StatementNoShortIf")))
);

rules.set("DoStatement", () =>
  D(Seq(T("do"), NT("Statement"), T("while"), T("("), NT("Expression"), T(")"), T(";")))
);

rules.set("ForStatement", () =>
  D(Ch(0, NT("BasicForStatement"), NT("EnhancedForStatement")))
);

rules.set("ForStatementNoShortIf", () =>
  D(Ch(0, NT("BasicForStatementNoShortIf"), NT("EnhancedForStatementNoShortIf")))
);

rules.set("BasicForStatement", () =>
  D(Seq(T("for"), T("("), Opt(NT("ForInit")), T(";"), Opt(NT("Expression")), T(";"), Opt(NT("ForUpdate")), T(")"), NT("Statement")))
);

rules.set("BasicForStatementNoShortIf", () =>
  D(Seq(T("for"), T("("), Opt(NT("ForInit")), T(";"), Opt(NT("Expression")), T(";"), Opt(NT("ForUpdate")), T(")"), NT("StatementNoShortIf")))
);

rules.set("ForInit", () =>
  D(Ch(0, NT("StatementExpressionList"), NT("LocalVariableDeclaration")))
);

rules.set("ForUpdate", () =>
  D(NT("StatementExpressionList"))
);

rules.set("StatementExpressionList", () =>
  D(Seq(NT("StatementExpression"), ZOM(Seq(T(","), NT("StatementExpression")))))
);

rules.set("EnhancedForStatement", () =>
  D(Seq(T("for"), T("("), NT("LocalVariableDeclaration"), T(":"), NT("Expression"), T(")"), NT("Statement")))
);

rules.set("EnhancedForStatementNoShortIf", () =>
  D(Seq(T("for"), T("("), NT("LocalVariableDeclaration"), T(":"), NT("Expression"), T(")"), NT("StatementNoShortIf")))
);

rules.set("BreakStatement", () =>
  D(Seq(T("break"), Opt(NT("Identifier")), T(";")))
);

rules.set("YieldStatement", () =>
  D(Seq(T("yield"), NT("Expression"), T(";")))
);

rules.set("ContinueStatement", () =>
  D(Seq(T("continue"), Opt(NT("Identifier")), T(";")))
);

rules.set("ReturnStatement", () =>
  D(Seq(T("return"), Opt(NT("Expression")), T(";")))
);

rules.set("ThrowStatement", () =>
  D(Seq(T("throw"), NT("Expression"), T(";")))
);

rules.set("SynchronizedStatement", () =>
  D(Seq(T("synchronized"), T("("), NT("Expression"), T(")"), NT("Block")))
);

rules.set("TryStatement", () =>
  D(
    Ch(0,
      Seq(T("try"), NT("Block"), NT("Catches")),
      Seq(T("try"), NT("Block"), Opt(NT("Catches")), NT("Finally")),
      NT("TryWithResourcesStatement")
    )
  )
);

rules.set("Catches", () =>
  D(OOM(NT("CatchClause")))
);

rules.set("CatchClause", () =>
  D(Seq(T("catch"), T("("), NT("CatchFormalParameter"), T(")"), NT("Block")))
);

rules.set("CatchFormalParameter", () =>
  D(Seq(ZOM(NT("VariableModifier")), NT("CatchType"), NT("VariableDeclaratorId")))
);

rules.set("CatchType", () =>
  D(Seq(NT("UnannClassType"), ZOM(Seq(T("|"), NT("ClassType")))))
);

rules.set("Finally", () =>
  D(Seq(T("finally"), NT("Block")))
);

rules.set("TryWithResourcesStatement", () =>
  D(Seq(T("try"), NT("ResourceSpecification"), NT("Block"), Opt(NT("Catches")), Opt(NT("Finally"))))
);

rules.set("ResourceSpecification", () =>
  D(Seq(T("("), NT("ResourceList"), Opt(T(";")), T(")")))
);

rules.set("ResourceList", () =>
  D(Seq(NT("Resource"), ZOM(Seq(T(";"), NT("Resource")))))
);

rules.set("Resource", () =>
  D(Ch(0, NT("LocalVariableDeclaration"), NT("VariableAccess")))
);

rules.set("VariableAccess", () =>
  D(Ch(0, NT("ExpressionName"), NT("FieldAccess")))
);

rules.set("Pattern", () =>
  D(Ch(0, NT("TypePattern"), NT("RecordPattern")))
);

rules.set("TypePattern", () =>
  D(NT("LocalVariableDeclaration"))
);

rules.set("RecordPattern", () =>
  D(Seq(NT("ReferenceType"), T("("), Opt(NT("ComponentPatternList")), T(")")))
);

rules.set("ComponentPatternList", () =>
  D(Seq(NT("ComponentPattern"), ZOM(Seq(T(","), NT("ComponentPattern")))))
);

rules.set("ComponentPattern", () =>
  D(Ch(0, NT("Pattern"), NT("MatchAllPattern")))
);

rules.set("MatchAllPattern", () =>
  D(T("_"))
);

// ------------------------------------------------------------
// §15 Expressions
// ------------------------------------------------------------

rules.set("Primary", () =>
  D(Ch(0, NT("PrimaryNoNewArray"), NT("ArrayCreationExpression")))
);

rules.set("PrimaryNoNewArray", () =>
  D(
    Ch(0,
      NT("Literal"),
      NT("ClassLiteral"),
      T("this"),
      Seq(NT("TypeName"), T("."), T("this")),
      Seq(T("("), NT("Expression"), T(")")),
      NT("ClassInstanceCreationExpression"),
      NT("FieldAccess"),
      NT("ArrayAccess"),
      NT("MethodInvocation"),
      NT("MethodReference")
    )
  )
);

rules.set("ClassLiteral", () =>
  D(
    Ch(0,
      Seq(NT("TypeName"), ZOM(Seq(T("["), T("]"))), T("."), T("class")),
      Seq(NT("NumericType"), ZOM(Seq(T("["), T("]"))), T("."), T("class")),
      Seq(T("boolean"), ZOM(Seq(T("["), T("]"))), T("."), T("class")),
      Seq(T("void"), T("."), T("class"))
    )
  )
);

rules.set("ClassInstanceCreationExpression", () =>
  D(
    Ch(0,
      NT("UnqualifiedClassInstanceCreationExpression"),
      Seq(NT("ExpressionName"), T("."), NT("UnqualifiedClassInstanceCreationExpression")),
      Seq(NT("Primary"), T("."), NT("UnqualifiedClassInstanceCreationExpression"))
    )
  )
);

rules.set("UnqualifiedClassInstanceCreationExpression", () =>
  D(Seq(T("new"), Opt(NT("TypeArguments")), NT("ClassOrInterfaceTypeToInstantiate"), T("("), Opt(NT("ArgumentList")), T(")"), Opt(NT("ClassBody"))))
);

rules.set("ClassOrInterfaceTypeToInstantiate", () =>
  D(
    Seq(
      ZOM(NT("Annotation")),
      NT("Identifier"),
      ZOM(Seq(T("."), ZOM(NT("Annotation")), NT("Identifier"))),
      Opt(NT("TypeArgumentsOrDiamond"))
    )
  )
);

rules.set("TypeArgumentsOrDiamond", () =>
  D(Ch(0, NT("TypeArguments"), Seq(T("<"), T(">"))))
);

rules.set("ArrayCreationExpression", () =>
  D(Ch(0, NT("ArrayCreationExpressionWithoutInitializer"), NT("ArrayCreationExpressionWithInitializer")))
);

rules.set("ArrayCreationExpressionWithoutInitializer", () =>
  D(
    Ch(0,
      Seq(T("new"), NT("PrimitiveType"), NT("DimExprs"), Opt(NT("Dims"))),
      Seq(T("new"), NT("ClassOrInterfaceType"), NT("DimExprs"), Opt(NT("Dims")))
    )
  )
);

rules.set("ArrayCreationExpressionWithInitializer", () =>
  D(
    Ch(0,
      Seq(T("new"), NT("PrimitiveType"), NT("Dims"), NT("ArrayInitializer")),
      Seq(T("new"), NT("ClassOrInterfaceType"), NT("Dims"), NT("ArrayInitializer"))
    )
  )
);

rules.set("DimExprs", () =>
  D(OOM(NT("DimExpr")))
);

rules.set("DimExpr", () =>
  D(Seq(ZOM(NT("Annotation")), T("["), NT("Expression"), T("]")))
);

rules.set("ArrayAccess", () =>
  D(
    Ch(0,
      Seq(NT("ExpressionName"), T("["), NT("Expression"), T("]")),
      Seq(NT("PrimaryNoNewArray"), T("["), NT("Expression"), T("]")),
      Seq(NT("ArrayCreationExpressionWithInitializer"), T("["), NT("Expression"), T("]"))
    )
  )
);

rules.set("FieldAccess", () =>
  D(
    Ch(0,
      Seq(NT("Primary"), T("."), NT("Identifier")),
      Seq(T("super"), T("."), NT("Identifier")),
      Seq(NT("TypeName"), T("."), T("super"), T("."), NT("Identifier"))
    )
  )
);

rules.set("MethodInvocation", () =>
  D(
    Ch(0,
      Seq(NT("MethodName"), T("("), Opt(NT("ArgumentList")), T(")")),
      Seq(NT("TypeName"), T("."), Opt(NT("TypeArguments")), NT("Identifier"), T("("), Opt(NT("ArgumentList")), T(")")),
      Seq(NT("ExpressionName"), T("."), Opt(NT("TypeArguments")), NT("Identifier"), T("("), Opt(NT("ArgumentList")), T(")")),
      Seq(NT("Primary"), T("."), Opt(NT("TypeArguments")), NT("Identifier"), T("("), Opt(NT("ArgumentList")), T(")")),
      Seq(T("super"), T("."), Opt(NT("TypeArguments")), NT("Identifier"), T("("), Opt(NT("ArgumentList")), T(")")),
      Seq(NT("TypeName"), T("."), T("super"), T("."), Opt(NT("TypeArguments")), NT("Identifier"), T("("), Opt(NT("ArgumentList")), T(")"))
    )
  )
);

rules.set("ArgumentList", () =>
  D(Seq(NT("Expression"), ZOM(Seq(T(","), NT("Expression")))))
);

rules.set("MethodReference", () =>
  D(
    Ch(0,
      Seq(NT("ExpressionName"), T("::"), Opt(NT("TypeArguments")), NT("Identifier")),
      Seq(NT("Primary"), T("::"), Opt(NT("TypeArguments")), NT("Identifier")),
      Seq(NT("ReferenceType"), T("::"), Opt(NT("TypeArguments")), NT("Identifier")),
      Seq(T("super"), T("::"), Opt(NT("TypeArguments")), NT("Identifier")),
      Seq(NT("TypeName"), T("."), T("super"), T("::"), Opt(NT("TypeArguments")), NT("Identifier")),
      Seq(NT("ClassType"), T("::"), Opt(NT("TypeArguments")), T("new")),
      Seq(NT("ArrayType"), T("::"), T("new"))
    )
  )
);

rules.set("Expression", () =>
  D(Ch(0, NT("LambdaExpression"), NT("AssignmentExpression")))
);

rules.set("LambdaExpression", () =>
  D(Seq(NT("LambdaParameters"), T("->"), NT("LambdaBody")))
);

rules.set("LambdaParameters", () =>
  D(Ch(0, Seq(T("("), Opt(NT("LambdaParameterList")), T(")")), NT("ConciseLambdaParameter")))
);

rules.set("LambdaParameterList", () =>
  D(
    Ch(0,
      Seq(NT("NormalLambdaParameter"), ZOM(Seq(T(","), NT("NormalLambdaParameter")))),
      Seq(NT("ConciseLambdaParameter"), ZOM(Seq(T(","), NT("ConciseLambdaParameter"))))
    )
  )
);

rules.set("NormalLambdaParameter", () =>
  D(
    Ch(0,
      Seq(ZOM(NT("VariableModifier")), NT("LambdaParameterType"), NT("VariableDeclaratorId")),
      NT("VariableArityParameter")
    )
  )
);

rules.set("LambdaParameterType", () =>
  D(Ch(0, NT("UnannType"), T("var")))
);

rules.set("ConciseLambdaParameter", () =>
  D(Ch(0, NT("Identifier"), T("_")))
);

rules.set("LambdaBody", () =>
  D(Ch(0, NT("Expression"), NT("Block")))
);

rules.set("AssignmentExpression", () =>
  D(Ch(0, NT("ConditionalExpression"), NT("Assignment")))
);

rules.set("Assignment", () =>
  D(Seq(NT("LeftHandSide"), NT("AssignmentOperator"), NT("Expression")))
);

rules.set("LeftHandSide", () =>
  D(Ch(0, NT("ExpressionName"), NT("FieldAccess"), NT("ArrayAccess")))
);

rules.set("AssignmentOperator", () =>
  D(Ch(0, T("="), T("*="), T("/="), T("%="), T("+="), T("-="), T("<<="), T(">>="), T(">>>="), T("&="), T("^="), T("|=")))
);

rules.set("ConditionalExpression", () =>
  D(
    Ch(0,
      NT("ConditionalOrExpression"),
      Seq(NT("ConditionalOrExpression"), T("?"), NT("Expression"), T(":"), NT("ConditionalExpression")),
      Seq(NT("ConditionalOrExpression"), T("?"), NT("Expression"), T(":"), NT("LambdaExpression"))
    )
  )
);

rules.set("ConditionalOrExpression", () =>
  D(Seq(NT("ConditionalAndExpression"), ZOM(Seq(T("||"), NT("ConditionalAndExpression")))))
);

rules.set("ConditionalAndExpression", () =>
  D(Seq(NT("InclusiveOrExpression"), ZOM(Seq(T("&&"), NT("InclusiveOrExpression")))))
);

rules.set("InclusiveOrExpression", () =>
  D(Seq(NT("ExclusiveOrExpression"), ZOM(Seq(T("|"), NT("ExclusiveOrExpression")))))
);

rules.set("ExclusiveOrExpression", () =>
  D(Seq(NT("AndExpression"), ZOM(Seq(T("^"), NT("AndExpression")))))
);

rules.set("AndExpression", () =>
  D(Seq(NT("EqualityExpression"), ZOM(Seq(T("&"), NT("EqualityExpression")))))
);

rules.set("EqualityExpression", () =>
  D(Seq(NT("RelationalExpression"), ZOM(Ch(0, Seq(T("=="), NT("RelationalExpression")), Seq(T("!="), NT("RelationalExpression"))))))
);

rules.set("RelationalExpression", () =>
  D(
    Ch(0,
      NT("ShiftExpression"),
      Seq(NT("RelationalExpression"), T("<"), NT("ShiftExpression")),
      Seq(NT("RelationalExpression"), T(">"), NT("ShiftExpression")),
      Seq(NT("RelationalExpression"), T("<="), NT("ShiftExpression")),
      Seq(NT("RelationalExpression"), T(">="), NT("ShiftExpression")),
      NT("InstanceofExpression")
    )
  )
);

rules.set("InstanceofExpression", () =>
  D(
    Ch(0,
      Seq(NT("RelationalExpression"), T("instanceof"), NT("ReferenceType")),
      Seq(NT("RelationalExpression"), T("instanceof"), NT("Pattern"))
    )
  )
);

rules.set("ShiftExpression", () =>
  D(Seq(NT("AdditiveExpression"), ZOM(Ch(0, Seq(T("<<"), NT("AdditiveExpression")), Seq(T(">>"), NT("AdditiveExpression")), Seq(T(">>>"), NT("AdditiveExpression"))))))
);

rules.set("AdditiveExpression", () =>
  D(Seq(NT("MultiplicativeExpression"), ZOM(Ch(0, Seq(T("+"), NT("MultiplicativeExpression")), Seq(T("-"), NT("MultiplicativeExpression"))))))
);

rules.set("MultiplicativeExpression", () =>
  D(Seq(NT("UnaryExpression"), ZOM(Ch(0, Seq(T("*"), NT("UnaryExpression")), Seq(T("/"), NT("UnaryExpression")), Seq(T("%"), NT("UnaryExpression"))))))
);

rules.set("UnaryExpression", () =>
  D(
    Ch(0,
      NT("PreIncrementExpression"),
      NT("PreDecrementExpression"),
      Seq(T("+"), NT("UnaryExpression")),
      Seq(T("-"), NT("UnaryExpression")),
      NT("UnaryExpressionNotPlusMinus")
    )
  )
);

rules.set("PreIncrementExpression", () =>
  D(Seq(T("++"), NT("UnaryExpression")))
);

rules.set("PreDecrementExpression", () =>
  D(Seq(T("--"), NT("UnaryExpression")))
);

rules.set("UnaryExpressionNotPlusMinus", () =>
  D(
    Ch(0,
      NT("PostfixExpression"),
      Seq(T("~"), NT("UnaryExpression")),
      Seq(T("!"), NT("UnaryExpression")),
      NT("CastExpression"),
      NT("SwitchExpression")
    )
  )
);

rules.set("PostfixExpression", () =>
  D(Ch(0, NT("Primary"), NT("ExpressionName"), NT("PostIncrementExpression"), NT("PostDecrementExpression")))
);

rules.set("PostIncrementExpression", () =>
  D(Seq(NT("PostfixExpression"), T("++")))
);

rules.set("PostDecrementExpression", () =>
  D(Seq(NT("PostfixExpression"), T("--")))
);

rules.set("CastExpression", () =>
  D(
    Ch(0,
      Seq(T("("), NT("PrimitiveType"), T(")"), NT("UnaryExpression")),
      Seq(T("("), NT("ReferenceType"), ZOM(NT("AdditionalBound")), T(")"), NT("UnaryExpressionNotPlusMinus")),
      Seq(T("("), NT("ReferenceType"), ZOM(NT("AdditionalBound")), T(")"), NT("LambdaExpression"))
    )
  )
);

rules.set("SwitchExpression", () =>
  D(Seq(T("switch"), T("("), NT("Expression"), T(")"), NT("SwitchBlock")))
);

// ============================================================
// Public API
// ============================================================

/**
 * Creates a railroad diagram for the given rule name.
 * Returns undefined if no diagram factory exists for that name.
 */
export function createRuleDiagram(name: string): any {
  const factory = rules.get(name);
  return factory ? factory() : undefined;
}

/**
 * Get all diagram rule names for grammar coverage checking.
 */
export function getDiagramRuleNames(): string[] {
  return Array.from(rules.keys());
}
