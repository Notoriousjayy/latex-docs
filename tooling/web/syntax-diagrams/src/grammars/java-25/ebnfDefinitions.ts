/**
 * EBNF Definitions for Java 25 Grammar
 * 
 * This file contains the textual EBNF representation of each grammar rule,
 * displayed below the corresponding railroad diagram.
 * 
 * Based on Java Language Specification SE 25, Chapter 19.
 * 
 * Naming convention: Rule names use kebab-case (e.g., "class-declaration")
 * to match the diagram factory keys in java25Grammar.ts.
 */

/** Union type of all rule names for type safety */
export type RuleName = keyof typeof EBNF_DEFINITIONS;

/**
 * EBNF definitions keyed by rule name.
 * Each value is a multi-line string showing the grammar production.
 */
export const EBNF_DEFINITIONS: Record<string, string> = {
  // ============================================================
  // §3 Lexical Structure
  // ============================================================

  "Identifier": `Identifier:
    IdentifierChars but not a ReservedKeyword or BooleanLiteral or NullLiteral`,

  "IdentifierChars": `IdentifierChars:
    JavaLetter {JavaLetterOrDigit}`,

  "JavaLetter": `JavaLetter:
    any Unicode character that is a "Java letter"`,

  "JavaLetterOrDigit": `JavaLetterOrDigit:
    any Unicode character that is a "Java letter-or-digit"`,

  "TypeIdentifier": `TypeIdentifier:
    Identifier but not permits, record, sealed, var, or yield`,

  "UnqualifiedMethodIdentifier": `UnqualifiedMethodIdentifier:
    Identifier but not yield`,

  "Literal": `Literal:
    IntegerLiteral
    FloatingPointLiteral
    BooleanLiteral
    CharacterLiteral
    StringLiteral
    TextBlock
    NullLiteral`,

  // ============================================================
  // §4 Types, Values, and Variables
  // ============================================================

  "Type": `Type:
    PrimitiveType
    ReferenceType`,

  "PrimitiveType": `PrimitiveType:
    {Annotation} NumericType
    {Annotation} boolean`,

  "NumericType": `NumericType:
    IntegralType
    FloatingPointType`,

  "IntegralType": `IntegralType:
    (one of) byte short int long char`,

  "FloatingPointType": `FloatingPointType:
    (one of) float double`,

  "ReferenceType": `ReferenceType:
    ClassOrInterfaceType
    TypeVariable
    ArrayType`,

  "ClassOrInterfaceType": `ClassOrInterfaceType:
    ClassType
    InterfaceType`,

  "ClassType": `ClassType:
    {Annotation} TypeIdentifier [TypeArguments]
    PackageName . {Annotation} TypeIdentifier [TypeArguments]
    ClassOrInterfaceType . {Annotation} TypeIdentifier [TypeArguments]`,

  "InterfaceType": `InterfaceType:
    ClassType`,

  "TypeVariable": `TypeVariable:
    {Annotation} TypeIdentifier`,

  "ArrayType": `ArrayType:
    PrimitiveType Dims
    ClassOrInterfaceType Dims
    TypeVariable Dims`,

  "Dims": `Dims:
    {Annotation} [ ] {{Annotation} [ ]}`,

  "TypeParameter": `TypeParameter:
    {TypeParameterModifier} TypeIdentifier [TypeBound]`,

  "TypeParameterModifier": `TypeParameterModifier:
    Annotation`,

  "TypeBound": `TypeBound:
    extends TypeVariable
    extends ClassOrInterfaceType {AdditionalBound}`,

  "AdditionalBound": `AdditionalBound:
    & InterfaceType`,

  "TypeArguments": `TypeArguments:
    < TypeArgumentList >`,

  "TypeArgumentList": `TypeArgumentList:
    TypeArgument {, TypeArgument}`,

  "TypeArgument": `TypeArgument:
    ReferenceType
    Wildcard`,

  "Wildcard": `Wildcard:
    {Annotation} ? [WildcardBounds]`,

  "WildcardBounds": `WildcardBounds:
    extends ReferenceType
    super ReferenceType`,

  // ============================================================
  // §6 Names
  // ============================================================

  "ModuleName": `ModuleName:
    Identifier
    ModuleName . Identifier`,

  "PackageName": `PackageName:
    Identifier
    PackageName . Identifier`,

  "TypeName": `TypeName:
    TypeIdentifier
    PackageOrTypeName . TypeIdentifier`,

  "ExpressionName": `ExpressionName:
    Identifier
    AmbiguousName . Identifier`,

  "MethodName": `MethodName:
    UnqualifiedMethodIdentifier`,

  "PackageOrTypeName": `PackageOrTypeName:
    Identifier
    PackageOrTypeName . Identifier`,

  "AmbiguousName": `AmbiguousName:
    Identifier
    AmbiguousName . Identifier`,

  // ============================================================
  // §7 Packages and Modules
  // ============================================================

  "CompilationUnit": `CompilationUnit:
    OrdinaryCompilationUnit
    CompactCompilationUnit
    ModularCompilationUnit`,

  "OrdinaryCompilationUnit": `OrdinaryCompilationUnit:
    [PackageDeclaration] {ImportDeclaration} {TopLevelClassOrInterfaceDeclaration}`,

  "ModularCompilationUnit": `ModularCompilationUnit:
    {ImportDeclaration} ModuleDeclaration`,

  "PackageDeclaration": `PackageDeclaration:
    {PackageModifier} package Identifier {. Identifier} ;`,

  "PackageModifier": `PackageModifier:
    Annotation`,

  "ImportDeclaration": `ImportDeclaration:
    SingleTypeImportDeclaration
    TypeImportOnDemandDeclaration
    SingleStaticImportDeclaration
    StaticImportOnDemandDeclaration
    SingleModuleImportDeclaration`,

  "SingleTypeImportDeclaration": `SingleTypeImportDeclaration:
    import TypeName ;`,

  "TypeImportOnDemandDeclaration": `TypeImportOnDemandDeclaration:
    import PackageOrTypeName . * ;`,

  "SingleStaticImportDeclaration": `SingleStaticImportDeclaration:
    import static TypeName . Identifier ;`,

  "StaticImportOnDemandDeclaration": `StaticImportOnDemandDeclaration:
    import static TypeName . * ;`,

  "SingleModuleImportDeclaration": `SingleModuleImportDeclaration:
    import module ModuleName ;`,

  "TopLevelClassOrInterfaceDeclaration": `TopLevelClassOrInterfaceDeclaration:
    ClassDeclaration
    InterfaceDeclaration
    ;`,

  "ModuleDeclaration": `ModuleDeclaration:
    {Annotation} [open] module Identifier {. Identifier} { {ModuleDirective} }`,

  "ModuleDirective": `ModuleDirective:
    requires {RequiresModifier} ModuleName ;
    exports PackageName [to ModuleName {, ModuleName}] ;
    opens PackageName [to ModuleName {, ModuleName}] ;
    uses TypeName ;
    provides TypeName with TypeName {, TypeName} ;`,

  "RequiresModifier": `RequiresModifier:
    (one of) transitive static`,

  // ============================================================
  // §8 Classes
  // ============================================================

  "ClassDeclaration": `ClassDeclaration:
    NormalClassDeclaration
    EnumDeclaration
    RecordDeclaration`,

  "NormalClassDeclaration": `NormalClassDeclaration:
    {ClassModifier} class TypeIdentifier [TypeParameters] [ClassExtends] [ClassImplements] [ClassPermits] ClassBody`,

  "ClassModifier": `ClassModifier:
    (one of) Annotation public protected private
    abstract static final sealed non-sealed strictfp`,

  "TypeParameters": `TypeParameters:
    < TypeParameterList >`,

  "TypeParameterList": `TypeParameterList:
    TypeParameter {, TypeParameter}`,

  "ClassExtends": `ClassExtends:
    extends ClassType`,

  "ClassImplements": `ClassImplements:
    implements InterfaceTypeList`,

  "InterfaceTypeList": `InterfaceTypeList:
    InterfaceType {, InterfaceType}`,

  "ClassPermits": `ClassPermits:
    permits TypeName {, TypeName}`,

  "ClassBody": `ClassBody:
    { {ClassBodyDeclaration} }`,

  "ClassBodyDeclaration": `ClassBodyDeclaration:
    ClassMemberDeclaration
    InstanceInitializer
    StaticInitializer
    ConstructorDeclaration`,

  "ClassMemberDeclaration": `ClassMemberDeclaration:
    FieldDeclaration
    MethodDeclaration
    ClassDeclaration
    InterfaceDeclaration
    ;`,

  "FieldDeclaration": `FieldDeclaration:
    {FieldModifier} UnannType VariableDeclaratorList ;`,

  "FieldModifier": `FieldModifier:
    (one of) Annotation public protected private
    static final transient volatile`,

  "VariableDeclaratorList": `VariableDeclaratorList:
    VariableDeclarator {, VariableDeclarator}`,

  "VariableDeclarator": `VariableDeclarator:
    VariableDeclaratorId [= VariableInitializer]`,

  "VariableDeclaratorId": `VariableDeclaratorId:
    Identifier [Dims]
    _`,

  "VariableInitializer": `VariableInitializer:
    Expression
    ArrayInitializer`,

  "UnannType": `UnannType:
    UnannPrimitiveType
    UnannReferenceType`,

  "UnannPrimitiveType": `UnannPrimitiveType:
    NumericType
    boolean`,

  "UnannReferenceType": `UnannReferenceType:
    UnannClassOrInterfaceType
    UnannTypeVariable
    UnannArrayType`,

  "UnannClassOrInterfaceType": `UnannClassOrInterfaceType:
    UnannClassType
    UnannInterfaceType`,

  "UnannClassType": `UnannClassType:
    TypeIdentifier [TypeArguments]
    PackageName . {Annotation} TypeIdentifier [TypeArguments]
    UnannClassOrInterfaceType . {Annotation} TypeIdentifier [TypeArguments]`,

  "UnannInterfaceType": `UnannInterfaceType:
    UnannClassType`,

  "UnannTypeVariable": `UnannTypeVariable:
    TypeIdentifier`,

  "UnannArrayType": `UnannArrayType:
    UnannPrimitiveType Dims
    UnannClassOrInterfaceType Dims
    UnannTypeVariable Dims`,

  "MethodDeclaration": `MethodDeclaration:
    {MethodModifier} MethodHeader MethodBody`,

  "MethodModifier": `MethodModifier:
    (one of) Annotation public protected private
    abstract static final synchronized native strictfp`,

  "MethodHeader": `MethodHeader:
    Result MethodDeclarator [Throws]
    TypeParameters {Annotation} Result MethodDeclarator [Throws]`,

  "Result": `Result:
    UnannType
    void`,

  "MethodDeclarator": `MethodDeclarator:
    Identifier ( [ReceiverParameter ,] [FormalParameterList] ) [Dims]`,

  "ReceiverParameter": `ReceiverParameter:
    {Annotation} UnannType [Identifier .] this`,

  "FormalParameterList": `FormalParameterList:
    FormalParameter {, FormalParameter}`,

  "FormalParameter": `FormalParameter:
    {VariableModifier} UnannType VariableDeclaratorId
    VariableArityParameter`,

  "VariableArityParameter": `VariableArityParameter:
    {VariableModifier} UnannType {Annotation} ... Identifier`,

  "VariableModifier": `VariableModifier:
    Annotation
    final`,

  "Throws": `Throws:
    throws ExceptionTypeList`,

  "ExceptionTypeList": `ExceptionTypeList:
    ExceptionType {, ExceptionType}`,

  "ExceptionType": `ExceptionType:
    ClassType
    TypeVariable`,

  "MethodBody": `MethodBody:
    Block
    ;`,

  "InstanceInitializer": `InstanceInitializer:
    Block`,

  "StaticInitializer": `StaticInitializer:
    static Block`,

  "ConstructorDeclaration": `ConstructorDeclaration:
    {ConstructorModifier} ConstructorDeclarator [Throws] ConstructorBody`,

  "ConstructorModifier": `ConstructorModifier:
    (one of) Annotation public protected private`,

  "ConstructorDeclarator": `ConstructorDeclarator:
    [TypeParameters] SimpleTypeName ( [ReceiverParameter ,] [FormalParameterList] )`,

  "SimpleTypeName": `SimpleTypeName:
    TypeIdentifier`,

  "ConstructorBody": `ConstructorBody:
    { [BlockStatements] ConstructorInvocation [BlockStatements] }
    { [BlockStatements] }`,

  "ConstructorInvocation": `ConstructorInvocation:
    [TypeArguments] this ( [ArgumentList] ) ;
    [TypeArguments] super ( [ArgumentList] ) ;
    ExpressionName . [TypeArguments] super ( [ArgumentList] ) ;
    Primary . [TypeArguments] super ( [ArgumentList] ) ;`,

  "EnumDeclaration": `EnumDeclaration:
    {ClassModifier} enum TypeIdentifier [ClassImplements] EnumBody`,

  "EnumBody": `EnumBody:
    { [EnumConstantList] [,] [EnumBodyDeclarations] }`,

  "EnumConstantList": `EnumConstantList:
    EnumConstant {, EnumConstant}`,

  "EnumConstant": `EnumConstant:
    {EnumConstantModifier} Identifier [( [ArgumentList] )] [ClassBody]`,

  "EnumConstantModifier": `EnumConstantModifier:
    Annotation`,

  "EnumBodyDeclarations": `EnumBodyDeclarations:
    ; {ClassBodyDeclaration}`,

  "RecordDeclaration": `RecordDeclaration:
    {ClassModifier} record TypeIdentifier [TypeParameters] RecordHeader [ClassImplements] RecordBody`,

  "RecordHeader": `RecordHeader:
    ( [RecordComponentList] )`,

  "RecordComponentList": `RecordComponentList:
    RecordComponent {, RecordComponent}`,

  "RecordComponent": `RecordComponent:
    {RecordComponentModifier} UnannType Identifier
    VariableArityRecordComponent`,

  "VariableArityRecordComponent": `VariableArityRecordComponent:
    {RecordComponentModifier} UnannType {Annotation} ... Identifier`,

  "RecordComponentModifier": `RecordComponentModifier:
    Annotation`,

  "RecordBody": `RecordBody:
    { {RecordBodyDeclaration} }`,

  "RecordBodyDeclaration": `RecordBodyDeclaration:
    ClassBodyDeclaration
    CompactConstructorDeclaration`,

  "CompactConstructorDeclaration": `CompactConstructorDeclaration:
    {ConstructorModifier} SimpleTypeName ConstructorBody`,

  // ============================================================
  // §9 Interfaces
  // ============================================================

  "InterfaceDeclaration": `InterfaceDeclaration:
    NormalInterfaceDeclaration
    AnnotationInterfaceDeclaration`,

  "NormalInterfaceDeclaration": `NormalInterfaceDeclaration:
    {InterfaceModifier} interface TypeIdentifier [TypeParameters] [InterfaceExtends] [InterfacePermits] InterfaceBody`,

  "InterfaceModifier": `InterfaceModifier:
    (one of) Annotation public protected private
    abstract static sealed non-sealed strictfp`,

  "InterfaceExtends": `InterfaceExtends:
    extends InterfaceTypeList`,

  "InterfacePermits": `InterfacePermits:
    permits TypeName {, TypeName}`,

  "InterfaceBody": `InterfaceBody:
    { {InterfaceMemberDeclaration} }`,

  "InterfaceMemberDeclaration": `InterfaceMemberDeclaration:
    ConstantDeclaration
    InterfaceMethodDeclaration
    ClassDeclaration
    InterfaceDeclaration
    ;`,

  "ConstantDeclaration": `ConstantDeclaration:
    {ConstantModifier} UnannType VariableDeclaratorList ;`,

  "ConstantModifier": `ConstantModifier:
    (one of) Annotation public
    static final`,

  "InterfaceMethodDeclaration": `InterfaceMethodDeclaration:
    {InterfaceMethodModifier} MethodHeader MethodBody`,

  "InterfaceMethodModifier": `InterfaceMethodModifier:
    (one of) Annotation public private
    abstract default static strictfp`,

  "AnnotationInterfaceDeclaration": `AnnotationInterfaceDeclaration:
    {InterfaceModifier} @ interface TypeIdentifier AnnotationInterfaceBody`,

  "AnnotationInterfaceBody": `AnnotationInterfaceBody:
    { {AnnotationInterfaceMemberDeclaration} }`,

  "AnnotationInterfaceMemberDeclaration": `AnnotationInterfaceMemberDeclaration:
    AnnotationInterfaceElementDeclaration
    ConstantDeclaration
    ClassDeclaration
    InterfaceDeclaration
    ;`,

  "AnnotationInterfaceElementDeclaration": `AnnotationInterfaceElementDeclaration:
    {AnnotationInterfaceElementModifier} UnannType Identifier ( ) [Dims] [DefaultValue] ;`,

  "AnnotationInterfaceElementModifier": `AnnotationInterfaceElementModifier:
    (one of) Annotation public
    abstract`,

  "DefaultValue": `DefaultValue:
    default ElementValue`,

  "Annotation": `Annotation:
    NormalAnnotation
    MarkerAnnotation
    SingleElementAnnotation`,

  "NormalAnnotation": `NormalAnnotation:
    @ TypeName ( [ElementValuePairList] )`,

  "ElementValuePairList": `ElementValuePairList:
    ElementValuePair {, ElementValuePair}`,

  "ElementValuePair": `ElementValuePair:
    Identifier = ElementValue`,

  "ElementValue": `ElementValue:
    ConditionalExpression
    ElementValueArrayInitializer
    Annotation`,

  "ElementValueArrayInitializer": `ElementValueArrayInitializer:
    { [ElementValueList] [,] }`,

  "ElementValueList": `ElementValueList:
    ElementValue {, ElementValue}`,

  "MarkerAnnotation": `MarkerAnnotation:
    @ TypeName`,

  "SingleElementAnnotation": `SingleElementAnnotation:
    @ TypeName ( ElementValue )`,

  // ============================================================
  // §10 Arrays
  // ============================================================

  "ArrayInitializer": `ArrayInitializer:
    { [VariableInitializerList] [,] }`,

  "VariableInitializerList": `VariableInitializerList:
    VariableInitializer {, VariableInitializer}`,

  // ============================================================
  // §14 Blocks, Statements, and Patterns
  // ============================================================

  "Block": `Block:
    { [BlockStatements] }`,

  "BlockStatements": `BlockStatements:
    BlockStatement {BlockStatement}`,

  "BlockStatement": `BlockStatement:
    LocalClassOrInterfaceDeclaration
    LocalVariableDeclarationStatement
    Statement`,

  "LocalClassOrInterfaceDeclaration": `LocalClassOrInterfaceDeclaration:
    ClassDeclaration
    NormalInterfaceDeclaration`,

  "LocalVariableDeclarationStatement": `LocalVariableDeclarationStatement:
    LocalVariableDeclaration ;`,

  "LocalVariableDeclaration": `LocalVariableDeclaration:
    {VariableModifier} LocalVariableType VariableDeclaratorList`,

  "LocalVariableType": `LocalVariableType:
    UnannType
    var`,

  "Statement": `Statement:
    StatementWithoutTrailingSubstatement
    LabeledStatement
    IfThenStatement
    IfThenElseStatement
    WhileStatement
    ForStatement`,

  "StatementNoShortIf": `StatementNoShortIf:
    StatementWithoutTrailingSubstatement
    LabeledStatementNoShortIf
    IfThenElseStatementNoShortIf
    WhileStatementNoShortIf
    ForStatementNoShortIf`,

  "StatementWithoutTrailingSubstatement": `StatementWithoutTrailingSubstatement:
    Block
    EmptyStatement
    ExpressionStatement
    AssertStatement
    SwitchStatement
    DoStatement
    BreakStatement
    ContinueStatement
    ReturnStatement
    SynchronizedStatement
    ThrowStatement
    TryStatement
    YieldStatement`,

  "EmptyStatement": `EmptyStatement:
    ;`,

  "LabeledStatement": `LabeledStatement:
    Identifier : Statement`,

  "LabeledStatementNoShortIf": `LabeledStatementNoShortIf:
    Identifier : StatementNoShortIf`,

  "ExpressionStatement": `ExpressionStatement:
    StatementExpression ;`,

  "StatementExpression": `StatementExpression:
    Assignment
    PreIncrementExpression
    PreDecrementExpression
    PostIncrementExpression
    PostDecrementExpression
    MethodInvocation
    ClassInstanceCreationExpression`,

  "IfThenStatement": `IfThenStatement:
    if ( Expression ) Statement`,

  "IfThenElseStatement": `IfThenElseStatement:
    if ( Expression ) StatementNoShortIf else Statement`,

  "IfThenElseStatementNoShortIf": `IfThenElseStatementNoShortIf:
    if ( Expression ) StatementNoShortIf else StatementNoShortIf`,

  "AssertStatement": `AssertStatement:
    assert Expression ;
    assert Expression : Expression ;`,

  "SwitchStatement": `SwitchStatement:
    switch ( Expression ) SwitchBlock`,

  "SwitchBlock": `SwitchBlock:
    { SwitchRule {SwitchRule} }
    { {SwitchBlockStatementGroup} {SwitchLabel :} }`,

  "SwitchRule": `SwitchRule:
    SwitchLabel -> Expression ;
    SwitchLabel -> Block
    SwitchLabel -> ThrowStatement`,

  "SwitchBlockStatementGroup": `SwitchBlockStatementGroup:
    SwitchLabel : {SwitchLabel :} BlockStatements`,

  "SwitchLabel": `SwitchLabel:
    case CaseConstant {, CaseConstant}
    case null [, default]
    case CasePattern {, CasePattern} [Guard]
    default`,

  "CaseConstant": `CaseConstant:
    ConditionalExpression`,

  "CasePattern": `CasePattern:
    Pattern`,

  "Guard": `Guard:
    when Expression`,

  "WhileStatement": `WhileStatement:
    while ( Expression ) Statement`,

  "WhileStatementNoShortIf": `WhileStatementNoShortIf:
    while ( Expression ) StatementNoShortIf`,

  "DoStatement": `DoStatement:
    do Statement while ( Expression ) ;`,

  "ForStatement": `ForStatement:
    BasicForStatement
    EnhancedForStatement`,

  "ForStatementNoShortIf": `ForStatementNoShortIf:
    BasicForStatementNoShortIf
    EnhancedForStatementNoShortIf`,

  "BasicForStatement": `BasicForStatement:
    for ( [ForInit] ; [Expression] ; [ForUpdate] ) Statement`,

  "BasicForStatementNoShortIf": `BasicForStatementNoShortIf:
    for ( [ForInit] ; [Expression] ; [ForUpdate] ) StatementNoShortIf`,

  "ForInit": `ForInit:
    StatementExpressionList
    LocalVariableDeclaration`,

  "ForUpdate": `ForUpdate:
    StatementExpressionList`,

  "StatementExpressionList": `StatementExpressionList:
    StatementExpression {, StatementExpression}`,

  "EnhancedForStatement": `EnhancedForStatement:
    for ( LocalVariableDeclaration : Expression ) Statement`,

  "EnhancedForStatementNoShortIf": `EnhancedForStatementNoShortIf:
    for ( LocalVariableDeclaration : Expression ) StatementNoShortIf`,

  "BreakStatement": `BreakStatement:
    break [Identifier] ;`,

  "YieldStatement": `YieldStatement:
    yield Expression ;`,

  "ContinueStatement": `ContinueStatement:
    continue [Identifier] ;`,

  "ReturnStatement": `ReturnStatement:
    return [Expression] ;`,

  "ThrowStatement": `ThrowStatement:
    throw Expression ;`,

  "SynchronizedStatement": `SynchronizedStatement:
    synchronized ( Expression ) Block`,

  "TryStatement": `TryStatement:
    try Block Catches
    try Block [Catches] Finally
    TryWithResourcesStatement`,

  "Catches": `Catches:
    CatchClause {CatchClause}`,

  "CatchClause": `CatchClause:
    catch ( CatchFormalParameter ) Block`,

  "CatchFormalParameter": `CatchFormalParameter:
    {VariableModifier} CatchType VariableDeclaratorId`,

  "CatchType": `CatchType:
    UnannClassType {| ClassType}`,

  "Finally": `Finally:
    finally Block`,

  "TryWithResourcesStatement": `TryWithResourcesStatement:
    try ResourceSpecification Block [Catches] [Finally]`,

  "ResourceSpecification": `ResourceSpecification:
    ( ResourceList [;] )`,

  "ResourceList": `ResourceList:
    Resource {; Resource}`,

  "Resource": `Resource:
    LocalVariableDeclaration
    VariableAccess`,

  "VariableAccess": `VariableAccess:
    ExpressionName
    FieldAccess`,

  "Pattern": `Pattern:
    TypePattern
    RecordPattern`,

  "TypePattern": `TypePattern:
    LocalVariableDeclaration`,

  "RecordPattern": `RecordPattern:
    ReferenceType ( [ComponentPatternList] )`,

  "ComponentPatternList": `ComponentPatternList:
    ComponentPattern {, ComponentPattern}`,

  "ComponentPattern": `ComponentPattern:
    Pattern
    MatchAllPattern`,

  "MatchAllPattern": `MatchAllPattern:
    _`,

  // ============================================================
  // §15 Expressions
  // ============================================================

  "Primary": `Primary:
    PrimaryNoNewArray
    ArrayCreationExpression`,

  "PrimaryNoNewArray": `PrimaryNoNewArray:
    Literal
    ClassLiteral
    this
    TypeName . this
    ( Expression )
    ClassInstanceCreationExpression
    FieldAccess
    ArrayAccess
    MethodInvocation
    MethodReference`,

  "ClassLiteral": `ClassLiteral:
    TypeName {[ ]} . class
    NumericType {[ ]} . class
    boolean {[ ]} . class
    void . class`,

  "ClassInstanceCreationExpression": `ClassInstanceCreationExpression:
    UnqualifiedClassInstanceCreationExpression
    ExpressionName . UnqualifiedClassInstanceCreationExpression
    Primary . UnqualifiedClassInstanceCreationExpression`,

  "UnqualifiedClassInstanceCreationExpression": `UnqualifiedClassInstanceCreationExpression:
    new [TypeArguments] ClassOrInterfaceTypeToInstantiate ( [ArgumentList] ) [ClassBody]`,

  "ClassOrInterfaceTypeToInstantiate": `ClassOrInterfaceTypeToInstantiate:
    {Annotation} Identifier {. {Annotation} Identifier} [TypeArgumentsOrDiamond]`,

  "TypeArgumentsOrDiamond": `TypeArgumentsOrDiamond:
    TypeArguments
    <>`,

  "ArrayCreationExpression": `ArrayCreationExpression:
    ArrayCreationExpressionWithoutInitializer
    ArrayCreationExpressionWithInitializer`,

  "ArrayCreationExpressionWithoutInitializer": `ArrayCreationExpressionWithoutInitializer:
    new PrimitiveType DimExprs [Dims]
    new ClassOrInterfaceType DimExprs [Dims]`,

  "ArrayCreationExpressionWithInitializer": `ArrayCreationExpressionWithInitializer:
    new PrimitiveType Dims ArrayInitializer
    new ClassOrInterfaceType Dims ArrayInitializer`,

  "DimExprs": `DimExprs:
    DimExpr {DimExpr}`,

  "DimExpr": `DimExpr:
    {Annotation} [ Expression ]`,

  "ArrayAccess": `ArrayAccess:
    ExpressionName [ Expression ]
    PrimaryNoNewArray [ Expression ]
    ArrayCreationExpressionWithInitializer [ Expression ]`,

  "FieldAccess": `FieldAccess:
    Primary . Identifier
    super . Identifier
    TypeName . super . Identifier`,

  "MethodInvocation": `MethodInvocation:
    MethodName ( [ArgumentList] )
    TypeName . [TypeArguments] Identifier ( [ArgumentList] )
    ExpressionName . [TypeArguments] Identifier ( [ArgumentList] )
    Primary . [TypeArguments] Identifier ( [ArgumentList] )
    super . [TypeArguments] Identifier ( [ArgumentList] )
    TypeName . super . [TypeArguments] Identifier ( [ArgumentList] )`,

  "ArgumentList": `ArgumentList:
    Expression {, Expression}`,

  "MethodReference": `MethodReference:
    ExpressionName :: [TypeArguments] Identifier
    Primary :: [TypeArguments] Identifier
    ReferenceType :: [TypeArguments] Identifier
    super :: [TypeArguments] Identifier
    TypeName . super :: [TypeArguments] Identifier
    ClassType :: [TypeArguments] new
    ArrayType :: new`,

  "Expression": `Expression:
    LambdaExpression
    AssignmentExpression`,

  "LambdaExpression": `LambdaExpression:
    LambdaParameters -> LambdaBody`,

  "LambdaParameters": `LambdaParameters:
    ( [LambdaParameterList] )
    ConciseLambdaParameter`,

  "LambdaParameterList": `LambdaParameterList:
    NormalLambdaParameter {, NormalLambdaParameter}
    ConciseLambdaParameter {, ConciseLambdaParameter}`,

  "NormalLambdaParameter": `NormalLambdaParameter:
    {VariableModifier} LambdaParameterType VariableDeclaratorId
    VariableArityParameter`,

  "LambdaParameterType": `LambdaParameterType:
    UnannType
    var`,

  "ConciseLambdaParameter": `ConciseLambdaParameter:
    Identifier
    _`,

  "LambdaBody": `LambdaBody:
    Expression
    Block`,

  "AssignmentExpression": `AssignmentExpression:
    ConditionalExpression
    Assignment`,

  "Assignment": `Assignment:
    LeftHandSide AssignmentOperator Expression`,

  "LeftHandSide": `LeftHandSide:
    ExpressionName
    FieldAccess
    ArrayAccess`,

  "AssignmentOperator": `AssignmentOperator:
    (one of) =  *=  /=  %=  +=  -=  <<=  >>=  >>>=  &=  ^=  |=`,

  "ConditionalExpression": `ConditionalExpression:
    ConditionalOrExpression
    ConditionalOrExpression ? Expression : ConditionalExpression
    ConditionalOrExpression ? Expression : LambdaExpression`,

  "ConditionalOrExpression": `ConditionalOrExpression:
    ConditionalAndExpression
    ConditionalOrExpression || ConditionalAndExpression`,

  "ConditionalAndExpression": `ConditionalAndExpression:
    InclusiveOrExpression
    ConditionalAndExpression && InclusiveOrExpression`,

  "InclusiveOrExpression": `InclusiveOrExpression:
    ExclusiveOrExpression
    InclusiveOrExpression | ExclusiveOrExpression`,

  "ExclusiveOrExpression": `ExclusiveOrExpression:
    AndExpression
    ExclusiveOrExpression ^ AndExpression`,

  "AndExpression": `AndExpression:
    EqualityExpression
    AndExpression & EqualityExpression`,

  "EqualityExpression": `EqualityExpression:
    RelationalExpression
    EqualityExpression == RelationalExpression
    EqualityExpression != RelationalExpression`,

  "RelationalExpression": `RelationalExpression:
    ShiftExpression
    RelationalExpression < ShiftExpression
    RelationalExpression > ShiftExpression
    RelationalExpression <= ShiftExpression
    RelationalExpression >= ShiftExpression
    InstanceofExpression`,

  "InstanceofExpression": `InstanceofExpression:
    RelationalExpression instanceof ReferenceType
    RelationalExpression instanceof Pattern`,

  "ShiftExpression": `ShiftExpression:
    AdditiveExpression
    ShiftExpression << AdditiveExpression
    ShiftExpression >> AdditiveExpression
    ShiftExpression >>> AdditiveExpression`,

  "AdditiveExpression": `AdditiveExpression:
    MultiplicativeExpression
    AdditiveExpression + MultiplicativeExpression
    AdditiveExpression - MultiplicativeExpression`,

  "MultiplicativeExpression": `MultiplicativeExpression:
    UnaryExpression
    MultiplicativeExpression * UnaryExpression
    MultiplicativeExpression / UnaryExpression
    MultiplicativeExpression % UnaryExpression`,

  "UnaryExpression": `UnaryExpression:
    PreIncrementExpression
    PreDecrementExpression
    + UnaryExpression
    - UnaryExpression
    UnaryExpressionNotPlusMinus`,

  "PreIncrementExpression": `PreIncrementExpression:
    ++ UnaryExpression`,

  "PreDecrementExpression": `PreDecrementExpression:
    -- UnaryExpression`,

  "UnaryExpressionNotPlusMinus": `UnaryExpressionNotPlusMinus:
    PostfixExpression
    ~ UnaryExpression
    ! UnaryExpression
    CastExpression
    SwitchExpression`,

  "PostfixExpression": `PostfixExpression:
    Primary
    ExpressionName
    PostIncrementExpression
    PostDecrementExpression`,

  "PostIncrementExpression": `PostIncrementExpression:
    PostfixExpression ++`,

  "PostDecrementExpression": `PostDecrementExpression:
    PostfixExpression --`,

  "CastExpression": `CastExpression:
    ( PrimitiveType ) UnaryExpression
    ( ReferenceType {AdditionalBound} ) UnaryExpressionNotPlusMinus
    ( ReferenceType {AdditionalBound} ) LambdaExpression`,

  "SwitchExpression": `SwitchExpression:
    switch ( Expression ) SwitchBlock`,
};

/**
 * Gets the EBNF definition for a given rule name.
 * Returns undefined if not found.
 */
export function getEbnfDefinition(name: string): string | undefined {
  return EBNF_DEFINITIONS[name];
}

/**
 * Get all EBNF rule names for grammar coverage checking.
 */
export function getEbnfRuleNames(): string[] {
  return Object.keys(EBNF_DEFINITIONS);
}
