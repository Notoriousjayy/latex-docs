// ebnfDefinitions.ts
//
// EBNF text definitions for ECMAScript 2025 grammar rules.
// These are displayed below each railroad diagram.

import type { RuleName } from "./es2025Grammar";

/**
 * EBNF definitions keyed by rule name.
 * Format follows ECMAScript specification conventions.
 */
export const EBNF_DEFINITIONS: Record<string, string> = {
  // ===== A.1 Lexical Grammar =====
  
  "SourceCharacter": `SourceCharacter ::
    any Unicode code point`,

  "InputElementDiv": `InputElementDiv ::
    WhiteSpace
    LineTerminator
    Comment
    CommonToken
    DivPunctuator
    RightBracePunctuator`,

  "InputElementRegExp": `InputElementRegExp ::
    WhiteSpace
    LineTerminator
    Comment
    CommonToken
    RightBracePunctuator
    RegularExpressionLiteral`,

  "InputElementRegExpOrTemplateTail": `InputElementRegExpOrTemplateTail ::
    WhiteSpace
    LineTerminator
    Comment
    CommonToken
    RegularExpressionLiteral
    TemplateSubstitutionTail`,

  "InputElementTemplateTail": `InputElementTemplateTail ::
    WhiteSpace
    LineTerminator
    Comment
    CommonToken
    DivPunctuator
    TemplateSubstitutionTail`,

  "WhiteSpace": `WhiteSpace ::
    <TAB>
    <VT>
    <FF>
    <ZWNBSP>
    <USP>`,

  "LineTerminator": `LineTerminator ::
    <LF>
    <CR>
    <LS>
    <PS>`,

  "LineTerminatorSequence": `LineTerminatorSequence ::
    <LF>
    <CR> [lookahead ≠ <LF>]
    <LS>
    <PS>
    <CR> <LF>`,

  "Comment": `Comment ::
    MultiLineComment
    SingleLineComment`,

  "MultiLineComment": `MultiLineComment ::
    /* MultiLineCommentChars_opt */`,

  "SingleLineComment": `SingleLineComment ::
    // SingleLineCommentChars_opt`,

  "HashbangComment": `HashbangComment ::
    #! SingleLineCommentChars_opt`,

  "CommonToken": `CommonToken ::
    IdentifierName
    PrivateIdentifier
    Punctuator
    NumericLiteral
    StringLiteral
    Template`,

  "PrivateIdentifier": `PrivateIdentifier ::
    # IdentifierName`,

  "IdentifierName": `IdentifierName ::
    IdentifierStart
    IdentifierName IdentifierPart`,

  "IdentifierStart": `IdentifierStart ::
    IdentifierStartChar
    \\ UnicodeEscapeSequence`,

  "IdentifierPart": `IdentifierPart ::
    IdentifierPartChar
    \\ UnicodeEscapeSequence`,

  "IdentifierStartChar": `IdentifierStartChar ::
    UnicodeIDStart
    $
    _`,

  "IdentifierPartChar": `IdentifierPartChar ::
    UnicodeIDContinue
    $`,

  "UnicodeIDStart": `UnicodeIDStart ::
    any Unicode code point with the Unicode property "ID_Start"`,

  "UnicodeIDContinue": `UnicodeIDContinue ::
    any Unicode code point with the Unicode property "ID_Continue"`,

  "ReservedWord": `ReservedWord :: one of
    await break case catch class const continue debugger default delete
    do else enum export extends false finally for function if import in
    instanceof new null return super switch this throw true try typeof
    var void while with yield`,

  "Punctuator": `Punctuator ::
    OptionalChainingPunctuator
    OtherPunctuator`,

  "OptionalChainingPunctuator": `OptionalChainingPunctuator ::
    ?. [lookahead ∉ DecimalDigit]`,

  "DivPunctuator": `DivPunctuator ::
    /
    /=`,

  "RightBracePunctuator": `RightBracePunctuator ::
    }`,

  "NullLiteral": `NullLiteral ::
    null`,

  "BooleanLiteral": `BooleanLiteral ::
    true
    false`,

  "NumericLiteral": `NumericLiteral ::
    DecimalLiteral
    DecimalBigIntegerLiteral
    NonDecimalIntegerLiteral[+Sep]
    NonDecimalIntegerLiteral[+Sep] BigIntLiteralSuffix
    LegacyOctalIntegerLiteral`,

  "DecimalLiteral": `DecimalLiteral ::
    DecimalIntegerLiteral . DecimalDigits[+Sep]_opt ExponentPart[+Sep]_opt
    . DecimalDigits[+Sep] ExponentPart[+Sep]_opt
    DecimalIntegerLiteral ExponentPart[+Sep]_opt`,

  "DecimalIntegerLiteral": `DecimalIntegerLiteral ::
    0
    NonZeroDigit
    NonZeroDigit NumericLiteralSeparator_opt DecimalDigits[+Sep]
    NonOctalDecimalIntegerLiteral`,

  "DecimalDigits": `DecimalDigits[Sep] ::
    DecimalDigit
    DecimalDigits[?Sep] DecimalDigit
    [+Sep] DecimalDigits[+Sep] NumericLiteralSeparator DecimalDigit`,

  "DecimalDigit": `DecimalDigit :: one of
    0 1 2 3 4 5 6 7 8 9`,

  "NonZeroDigit": `NonZeroDigit :: one of
    1 2 3 4 5 6 7 8 9`,

  "NumericLiteralSeparator": `NumericLiteralSeparator ::
    _`,

  "ExponentPart": `ExponentPart[Sep] ::
    ExponentIndicator SignedInteger[?Sep]`,

  "ExponentIndicator": `ExponentIndicator :: one of
    e E`,

  "SignedInteger": `SignedInteger[Sep] ::
    DecimalDigits[?Sep]
    + DecimalDigits[?Sep]
    - DecimalDigits[?Sep]`,

  "BigIntLiteralSuffix": `BigIntLiteralSuffix ::
    n`,

  "DecimalBigIntegerLiteral": `DecimalBigIntegerLiteral ::
    0 BigIntLiteralSuffix
    NonZeroDigit DecimalDigits[+Sep]_opt BigIntLiteralSuffix
    NonZeroDigit NumericLiteralSeparator DecimalDigits[+Sep] BigIntLiteralSuffix`,

  "NonDecimalIntegerLiteral": `NonDecimalIntegerLiteral[Sep] ::
    BinaryIntegerLiteral[?Sep]
    OctalIntegerLiteral[?Sep]
    HexIntegerLiteral[?Sep]`,

  "BinaryIntegerLiteral": `BinaryIntegerLiteral[Sep] ::
    0b BinaryDigits[?Sep]
    0B BinaryDigits[?Sep]`,

  "BinaryDigits": `BinaryDigits[Sep] ::
    BinaryDigit
    BinaryDigits[?Sep] BinaryDigit
    [+Sep] BinaryDigits[+Sep] NumericLiteralSeparator BinaryDigit`,

  "BinaryDigit": `BinaryDigit :: one of
    0 1`,

  "OctalIntegerLiteral": `OctalIntegerLiteral[Sep] ::
    0o OctalDigits[?Sep]
    0O OctalDigits[?Sep]`,

  "OctalDigits": `OctalDigits[Sep] ::
    OctalDigit
    OctalDigits[?Sep] OctalDigit
    [+Sep] OctalDigits[+Sep] NumericLiteralSeparator OctalDigit`,

  "OctalDigit": `OctalDigit :: one of
    0 1 2 3 4 5 6 7`,

  "HexIntegerLiteral": `HexIntegerLiteral[Sep] ::
    0x HexDigits[?Sep]
    0X HexDigits[?Sep]`,

  "HexDigits": `HexDigits[Sep] ::
    HexDigit
    HexDigits[?Sep] HexDigit
    [+Sep] HexDigits[+Sep] NumericLiteralSeparator HexDigit`,

  "HexDigit": `HexDigit :: one of
    0 1 2 3 4 5 6 7 8 9 a b c d e f A B C D E F`,

  "LegacyOctalIntegerLiteral": `LegacyOctalIntegerLiteral ::
    0 OctalDigit
    LegacyOctalIntegerLiteral OctalDigit`,

  "StringLiteral": `StringLiteral ::
    " DoubleStringCharacters_opt "
    ' SingleStringCharacters_opt '`,

  "DoubleStringCharacters": `DoubleStringCharacters ::
    DoubleStringCharacter DoubleStringCharacters_opt`,

  "SingleStringCharacters": `SingleStringCharacters ::
    SingleStringCharacter SingleStringCharacters_opt`,

  "DoubleStringCharacter": `DoubleStringCharacter ::
    SourceCharacter but not one of " or \\ or LineTerminator
    <LS>
    <PS>
    \\ EscapeSequence
    LineContinuation`,

  "SingleStringCharacter": `SingleStringCharacter ::
    SourceCharacter but not one of ' or \\ or LineTerminator
    <LS>
    <PS>
    \\ EscapeSequence
    LineContinuation`,

  "LineContinuation": `LineContinuation ::
    \\ LineTerminatorSequence`,

  "EscapeSequence": `EscapeSequence ::
    CharacterEscapeSequence
    0 [lookahead ∉ DecimalDigit]
    LegacyOctalEscapeSequence
    NonOctalDecimalEscapeSequence
    HexEscapeSequence
    UnicodeEscapeSequence`,

  "CharacterEscapeSequence": `CharacterEscapeSequence ::
    SingleEscapeCharacter
    NonEscapeCharacter`,

  "SingleEscapeCharacter": `SingleEscapeCharacter :: one of
    ' " \\ b f n r t v`,

  "HexEscapeSequence": `HexEscapeSequence ::
    x HexDigit HexDigit`,

  "UnicodeEscapeSequence": `UnicodeEscapeSequence ::
    u Hex4Digits
    u{ CodePoint }`,

  "Hex4Digits": `Hex4Digits ::
    HexDigit HexDigit HexDigit HexDigit`,

  "RegularExpressionLiteral": `RegularExpressionLiteral ::
    / RegularExpressionBody / RegularExpressionFlags`,

  "RegularExpressionBody": `RegularExpressionBody ::
    RegularExpressionFirstChar RegularExpressionChars`,

  "RegularExpressionChars": `RegularExpressionChars ::
    [empty]
    RegularExpressionChars RegularExpressionChar`,

  "RegularExpressionFlags": `RegularExpressionFlags ::
    [empty]
    RegularExpressionFlags IdentifierPartChar`,

  "Template": `Template ::
    NoSubstitutionTemplate
    TemplateHead`,

  "NoSubstitutionTemplate": `NoSubstitutionTemplate ::
    \` TemplateCharacters_opt \``,

  "TemplateHead": `TemplateHead ::
    \` TemplateCharacters_opt \${`,

  "TemplateSubstitutionTail": `TemplateSubstitutionTail ::
    TemplateMiddle
    TemplateTail`,

  "TemplateMiddle": `TemplateMiddle ::
    } TemplateCharacters_opt \${`,

  "TemplateTail": `TemplateTail ::
    } TemplateCharacters_opt \``,

  "TemplateCharacters": `TemplateCharacters ::
    TemplateCharacter TemplateCharacters_opt`,

  // ===== A.2 Expressions =====

  "IdentifierReference": `IdentifierReference[Yield, Await] :
    Identifier
    [~Yield] yield
    [~Await] await`,

  "BindingIdentifier": `BindingIdentifier[Yield, Await] :
    Identifier
    yield
    await`,

  "LabelIdentifier": `LabelIdentifier[Yield, Await] :
    Identifier
    [~Yield] yield
    [~Await] await`,

  "Identifier": `Identifier :
    IdentifierName but not ReservedWord`,

  "PrimaryExpression": `PrimaryExpression[Yield, Await] :
    this
    IdentifierReference[?Yield, ?Await]
    Literal
    ArrayLiteral[?Yield, ?Await]
    ObjectLiteral[?Yield, ?Await]
    FunctionExpression
    ClassExpression[?Yield, ?Await]
    GeneratorExpression
    AsyncFunctionExpression
    AsyncGeneratorExpression
    RegularExpressionLiteral
    TemplateLiteral[?Yield, ?Await, ~Tagged]
    CoverParenthesizedExpressionAndArrowParameterList[?Yield, ?Await]`,

  "CoverParenthesizedExpressionAndArrowParameterList": `CoverParenthesizedExpressionAndArrowParameterList[Yield, Await] :
    ( Expression[+In, ?Yield, ?Await] )
    ( Expression[+In, ?Yield, ?Await] , )
    ( )
    ( ... BindingIdentifier[?Yield, ?Await] )
    ( ... BindingPattern[?Yield, ?Await] )
    ( Expression[+In, ?Yield, ?Await] , ... BindingIdentifier[?Yield, ?Await] )
    ( Expression[+In, ?Yield, ?Await] , ... BindingPattern[?Yield, ?Await] )`,

  "ParenthesizedExpression": `ParenthesizedExpression[Yield, Await] :
    ( Expression[+In, ?Yield, ?Await] )`,

  "Literal": `Literal :
    NullLiteral
    BooleanLiteral
    NumericLiteral
    StringLiteral`,

  "ArrayLiteral": `ArrayLiteral[Yield, Await] :
    [ Elision_opt ]
    [ ElementList[?Yield, ?Await] ]
    [ ElementList[?Yield, ?Await] , Elision_opt ]`,

  "ElementList": `ElementList[Yield, Await] :
    Elision_opt AssignmentExpression[+In, ?Yield, ?Await]
    Elision_opt SpreadElement[?Yield, ?Await]
    ElementList[?Yield, ?Await] , Elision_opt AssignmentExpression[+In, ?Yield, ?Await]
    ElementList[?Yield, ?Await] , Elision_opt SpreadElement[?Yield, ?Await]`,

  "Elision": `Elision :
    ,
    Elision ,`,

  "SpreadElement": `SpreadElement[Yield, Await] :
    ... AssignmentExpression[+In, ?Yield, ?Await]`,

  "ObjectLiteral": `ObjectLiteral[Yield, Await] :
    { }
    { PropertyDefinitionList[?Yield, ?Await] }
    { PropertyDefinitionList[?Yield, ?Await] , }`,

  "PropertyDefinitionList": `PropertyDefinitionList[Yield, Await] :
    PropertyDefinition[?Yield, ?Await]
    PropertyDefinitionList[?Yield, ?Await] , PropertyDefinition[?Yield, ?Await]`,

  "PropertyDefinition": `PropertyDefinition[Yield, Await] :
    IdentifierReference[?Yield, ?Await]
    CoverInitializedName[?Yield, ?Await]
    PropertyName[?Yield, ?Await] : AssignmentExpression[+In, ?Yield, ?Await]
    MethodDefinition[?Yield, ?Await]
    ... AssignmentExpression[+In, ?Yield, ?Await]`,

  "PropertyName": `PropertyName[Yield, Await] :
    LiteralPropertyName
    ComputedPropertyName[?Yield, ?Await]`,

  "LiteralPropertyName": `LiteralPropertyName :
    IdentifierName
    StringLiteral
    NumericLiteral`,

  "ComputedPropertyName": `ComputedPropertyName[Yield, Await] :
    [ AssignmentExpression[+In, ?Yield, ?Await] ]`,

  "CoverInitializedName": `CoverInitializedName[Yield, Await] :
    IdentifierReference[?Yield, ?Await] Initializer[+In, ?Yield, ?Await]`,

  "Initializer": `Initializer[In, Yield, Await] :
    = AssignmentExpression[?In, ?Yield, ?Await]`,

  "TemplateLiteral": `TemplateLiteral[Yield, Await, Tagged] :
    NoSubstitutionTemplate
    SubstitutionTemplate[?Yield, ?Await, ?Tagged]`,

  "SubstitutionTemplate": `SubstitutionTemplate[Yield, Await, Tagged] :
    TemplateHead Expression[+In, ?Yield, ?Await] TemplateSpans[?Yield, ?Await, ?Tagged]`,

  "TemplateSpans": `TemplateSpans[Yield, Await, Tagged] :
    TemplateTail
    TemplateMiddleList[?Yield, ?Await, ?Tagged] TemplateTail`,

  "TemplateMiddleList": `TemplateMiddleList[Yield, Await, Tagged] :
    TemplateMiddle Expression[+In, ?Yield, ?Await]
    TemplateMiddleList[?Yield, ?Await, ?Tagged] TemplateMiddle Expression[+In, ?Yield, ?Await]`,

  "MemberExpression": `MemberExpression[Yield, Await] :
    PrimaryExpression[?Yield, ?Await]
    MemberExpression[?Yield, ?Await] [ Expression[+In, ?Yield, ?Await] ]
    MemberExpression[?Yield, ?Await] . IdentifierName
    MemberExpression[?Yield, ?Await] TemplateLiteral[?Yield, ?Await, +Tagged]
    SuperProperty[?Yield, ?Await]
    MetaProperty
    new MemberExpression[?Yield, ?Await] Arguments[?Yield, ?Await]
    MemberExpression[?Yield, ?Await] . PrivateIdentifier`,

  "SuperProperty": `SuperProperty[Yield, Await] :
    super [ Expression[+In, ?Yield, ?Await] ]
    super . IdentifierName`,

  "MetaProperty": `MetaProperty :
    NewTarget
    ImportMeta`,

  "NewTarget": `NewTarget :
    new . target`,

  "ImportMeta": `ImportMeta :
    import . meta`,

  "NewExpression": `NewExpression[Yield, Await] :
    MemberExpression[?Yield, ?Await]
    new NewExpression[?Yield, ?Await]`,

  "CallExpression": `CallExpression[Yield, Await] :
    CoverCallExpressionAndAsyncArrowHead[?Yield, ?Await]
    SuperCall[?Yield, ?Await]
    ImportCall[?Yield, ?Await]
    CallExpression[?Yield, ?Await] Arguments[?Yield, ?Await]
    CallExpression[?Yield, ?Await] [ Expression[+In, ?Yield, ?Await] ]
    CallExpression[?Yield, ?Await] . IdentifierName
    CallExpression[?Yield, ?Await] TemplateLiteral[?Yield, ?Await, +Tagged]
    CallExpression[?Yield, ?Await] . PrivateIdentifier`,

  "SuperCall": `SuperCall[Yield, Await] :
    super Arguments[?Yield, ?Await]`,

  "ImportCall": `ImportCall[Yield, Await] :
    import ( AssignmentExpression[+In, ?Yield, ?Await] ,_opt )
    import ( AssignmentExpression[+In, ?Yield, ?Await] , AssignmentExpression[+In, ?Yield, ?Await] ,_opt )`,

  "Arguments": `Arguments[Yield, Await] :
    ( )
    ( ArgumentList[?Yield, ?Await] )
    ( ArgumentList[?Yield, ?Await] , )`,

  "ArgumentList": `ArgumentList[Yield, Await] :
    AssignmentExpression[+In, ?Yield, ?Await]
    ... AssignmentExpression[+In, ?Yield, ?Await]
    ArgumentList[?Yield, ?Await] , AssignmentExpression[+In, ?Yield, ?Await]
    ArgumentList[?Yield, ?Await] , ... AssignmentExpression[+In, ?Yield, ?Await]`,

  "OptionalExpression": `OptionalExpression[Yield, Await] :
    MemberExpression[?Yield, ?Await] OptionalChain[?Yield, ?Await]
    CallExpression[?Yield, ?Await] OptionalChain[?Yield, ?Await]
    OptionalExpression[?Yield, ?Await] OptionalChain[?Yield, ?Await]`,

  "OptionalChain": `OptionalChain[Yield, Await] :
    ?. Arguments[?Yield, ?Await]
    ?. [ Expression[+In, ?Yield, ?Await] ]
    ?. IdentifierName
    ?. TemplateLiteral[?Yield, ?Await, +Tagged]
    ?. PrivateIdentifier
    OptionalChain[?Yield, ?Await] Arguments[?Yield, ?Await]
    OptionalChain[?Yield, ?Await] [ Expression[+In, ?Yield, ?Await] ]
    OptionalChain[?Yield, ?Await] . IdentifierName
    OptionalChain[?Yield, ?Await] TemplateLiteral[?Yield, ?Await, +Tagged]
    OptionalChain[?Yield, ?Await] . PrivateIdentifier`,

  "LeftHandSideExpression": `LeftHandSideExpression[Yield, Await] :
    NewExpression[?Yield, ?Await]
    CallExpression[?Yield, ?Await]
    OptionalExpression[?Yield, ?Await]`,

  "UpdateExpression": `UpdateExpression[Yield, Await] :
    LeftHandSideExpression[?Yield, ?Await]
    LeftHandSideExpression[?Yield, ?Await] [no LineTerminator here] ++
    LeftHandSideExpression[?Yield, ?Await] [no LineTerminator here] --
    ++ UnaryExpression[?Yield, ?Await]
    -- UnaryExpression[?Yield, ?Await]`,

  "UnaryExpression": `UnaryExpression[Yield, Await] :
    UpdateExpression[?Yield, ?Await]
    delete UnaryExpression[?Yield, ?Await]
    void UnaryExpression[?Yield, ?Await]
    typeof UnaryExpression[?Yield, ?Await]
    + UnaryExpression[?Yield, ?Await]
    - UnaryExpression[?Yield, ?Await]
    ~ UnaryExpression[?Yield, ?Await]
    ! UnaryExpression[?Yield, ?Await]
    [+Await] AwaitExpression[?Yield]`,

  "ExponentiationExpression": `ExponentiationExpression[Yield, Await] :
    UnaryExpression[?Yield, ?Await]
    UpdateExpression[?Yield, ?Await] ** ExponentiationExpression[?Yield, ?Await]`,

  "MultiplicativeExpression": `MultiplicativeExpression[Yield, Await] :
    ExponentiationExpression[?Yield, ?Await]
    MultiplicativeExpression[?Yield, ?Await] MultiplicativeOperator ExponentiationExpression[?Yield, ?Await]`,

  "MultiplicativeOperator": `MultiplicativeOperator : one of
    * / %`,

  "AdditiveExpression": `AdditiveExpression[Yield, Await] :
    MultiplicativeExpression[?Yield, ?Await]
    AdditiveExpression[?Yield, ?Await] + MultiplicativeExpression[?Yield, ?Await]
    AdditiveExpression[?Yield, ?Await] - MultiplicativeExpression[?Yield, ?Await]`,

  "ShiftExpression": `ShiftExpression[Yield, Await] :
    AdditiveExpression[?Yield, ?Await]
    ShiftExpression[?Yield, ?Await] << AdditiveExpression[?Yield, ?Await]
    ShiftExpression[?Yield, ?Await] >> AdditiveExpression[?Yield, ?Await]
    ShiftExpression[?Yield, ?Await] >>> AdditiveExpression[?Yield, ?Await]`,

  "RelationalExpression": `RelationalExpression[In, Yield, Await] :
    ShiftExpression[?Yield, ?Await]
    RelationalExpression[?In, ?Yield, ?Await] < ShiftExpression[?Yield, ?Await]
    RelationalExpression[?In, ?Yield, ?Await] > ShiftExpression[?Yield, ?Await]
    RelationalExpression[?In, ?Yield, ?Await] <= ShiftExpression[?Yield, ?Await]
    RelationalExpression[?In, ?Yield, ?Await] >= ShiftExpression[?Yield, ?Await]
    RelationalExpression[?In, ?Yield, ?Await] instanceof ShiftExpression[?Yield, ?Await]
    [+In] RelationalExpression[+In, ?Yield, ?Await] in ShiftExpression[?Yield, ?Await]
    [+In] PrivateIdentifier in ShiftExpression[?Yield, ?Await]`,

  "EqualityExpression": `EqualityExpression[In, Yield, Await] :
    RelationalExpression[?In, ?Yield, ?Await]
    EqualityExpression[?In, ?Yield, ?Await] == RelationalExpression[?In, ?Yield, ?Await]
    EqualityExpression[?In, ?Yield, ?Await] != RelationalExpression[?In, ?Yield, ?Await]
    EqualityExpression[?In, ?Yield, ?Await] === RelationalExpression[?In, ?Yield, ?Await]
    EqualityExpression[?In, ?Yield, ?Await] !== RelationalExpression[?In, ?Yield, ?Await]`,

  "BitwiseANDExpression": `BitwiseANDExpression[In, Yield, Await] :
    EqualityExpression[?In, ?Yield, ?Await]
    BitwiseANDExpression[?In, ?Yield, ?Await] & EqualityExpression[?In, ?Yield, ?Await]`,

  "BitwiseXORExpression": `BitwiseXORExpression[In, Yield, Await] :
    BitwiseANDExpression[?In, ?Yield, ?Await]
    BitwiseXORExpression[?In, ?Yield, ?Await] ^ BitwiseANDExpression[?In, ?Yield, ?Await]`,

  "BitwiseORExpression": `BitwiseORExpression[In, Yield, Await] :
    BitwiseXORExpression[?In, ?Yield, ?Await]
    BitwiseORExpression[?In, ?Yield, ?Await] | BitwiseXORExpression[?In, ?Yield, ?Await]`,

  "LogicalANDExpression": `LogicalANDExpression[In, Yield, Await] :
    BitwiseORExpression[?In, ?Yield, ?Await]
    LogicalANDExpression[?In, ?Yield, ?Await] && BitwiseORExpression[?In, ?Yield, ?Await]`,

  "LogicalORExpression": `LogicalORExpression[In, Yield, Await] :
    LogicalANDExpression[?In, ?Yield, ?Await]
    LogicalORExpression[?In, ?Yield, ?Await] || LogicalANDExpression[?In, ?Yield, ?Await]`,

  "CoalesceExpression": `CoalesceExpression[In, Yield, Await] :
    CoalesceExpressionHead[?In, ?Yield, ?Await] ?? BitwiseORExpression[?In, ?Yield, ?Await]`,

  "CoalesceExpressionHead": `CoalesceExpressionHead[In, Yield, Await] :
    CoalesceExpression[?In, ?Yield, ?Await]
    BitwiseORExpression[?In, ?Yield, ?Await]`,

  "ShortCircuitExpression": `ShortCircuitExpression[In, Yield, Await] :
    LogicalORExpression[?In, ?Yield, ?Await]
    CoalesceExpression[?In, ?Yield, ?Await]`,

  "ConditionalExpression": `ConditionalExpression[In, Yield, Await] :
    ShortCircuitExpression[?In, ?Yield, ?Await]
    ShortCircuitExpression[?In, ?Yield, ?Await] ? AssignmentExpression[+In, ?Yield, ?Await] : AssignmentExpression[?In, ?Yield, ?Await]`,

  "AssignmentExpression": `AssignmentExpression[In, Yield, Await] :
    ConditionalExpression[?In, ?Yield, ?Await]
    [+Yield] YieldExpression[?In, ?Await]
    ArrowFunction[?In, ?Yield, ?Await]
    AsyncArrowFunction[?In, ?Yield, ?Await]
    LeftHandSideExpression[?Yield, ?Await] = AssignmentExpression[?In, ?Yield, ?Await]
    LeftHandSideExpression[?Yield, ?Await] AssignmentOperator AssignmentExpression[?In, ?Yield, ?Await]
    LeftHandSideExpression[?Yield, ?Await] &&= AssignmentExpression[?In, ?Yield, ?Await]
    LeftHandSideExpression[?Yield, ?Await] ||= AssignmentExpression[?In, ?Yield, ?Await]
    LeftHandSideExpression[?Yield, ?Await] ??= AssignmentExpression[?In, ?Yield, ?Await]`,

  "AssignmentOperator": `AssignmentOperator : one of
    *= /= %= += -= <<= >>= >>>= &= ^= |= **=`,

  "AssignmentPattern": `AssignmentPattern[Yield, Await] :
    ObjectAssignmentPattern[?Yield, ?Await]
    ArrayAssignmentPattern[?Yield, ?Await]`,

  "ObjectAssignmentPattern": `ObjectAssignmentPattern[Yield, Await] :
    { }
    { AssignmentRestProperty[?Yield, ?Await] }
    { AssignmentPropertyList[?Yield, ?Await] }
    { AssignmentPropertyList[?Yield, ?Await] , AssignmentRestProperty[?Yield, ?Await]_opt }`,

  "ArrayAssignmentPattern": `ArrayAssignmentPattern[Yield, Await] :
    [ Elision_opt AssignmentRestElement[?Yield, ?Await]_opt ]
    [ AssignmentElementList[?Yield, ?Await] ]
    [ AssignmentElementList[?Yield, ?Await] , Elision_opt AssignmentRestElement[?Yield, ?Await]_opt ]`,

  "Expression": `Expression[In, Yield, Await] :
    AssignmentExpression[?In, ?Yield, ?Await]
    Expression[?In, ?Yield, ?Await] , AssignmentExpression[?In, ?Yield, ?Await]`,

  // ===== A.3 Statements =====

  "Statement": `Statement[Yield, Await, Return] :
    BlockStatement[?Yield, ?Await, ?Return]
    VariableStatement[?Yield, ?Await]
    EmptyStatement
    ExpressionStatement[?Yield, ?Await]
    IfStatement[?Yield, ?Await, ?Return]
    BreakableStatement[?Yield, ?Await, ?Return]
    ContinueStatement[?Yield, ?Await]
    BreakStatement[?Yield, ?Await]
    [+Return] ReturnStatement[?Yield, ?Await]
    WithStatement[?Yield, ?Await, ?Return]
    LabelledStatement[?Yield, ?Await, ?Return]
    ThrowStatement[?Yield, ?Await]
    TryStatement[?Yield, ?Await, ?Return]
    DebuggerStatement`,

  "Declaration": `Declaration[Yield, Await] :
    HoistableDeclaration[?Yield, ?Await, ~Default]
    ClassDeclaration[?Yield, ?Await, ~Default]
    LexicalDeclaration[+In, ?Yield, ?Await]`,

  "HoistableDeclaration": `HoistableDeclaration[Yield, Await, Default] :
    FunctionDeclaration[?Yield, ?Await, ?Default]
    GeneratorDeclaration[?Yield, ?Await, ?Default]
    AsyncFunctionDeclaration[?Yield, ?Await, ?Default]
    AsyncGeneratorDeclaration[?Yield, ?Await, ?Default]`,

  "BreakableStatement": `BreakableStatement[Yield, Await, Return] :
    IterationStatement[?Yield, ?Await, ?Return]
    SwitchStatement[?Yield, ?Await, ?Return]`,

  "BlockStatement": `BlockStatement[Yield, Await, Return] :
    Block[?Yield, ?Await, ?Return]`,

  "Block": `Block[Yield, Await, Return] :
    { StatementList[?Yield, ?Await, ?Return]_opt }`,

  "StatementList": `StatementList[Yield, Await, Return] :
    StatementListItem[?Yield, ?Await, ?Return]
    StatementList[?Yield, ?Await, ?Return] StatementListItem[?Yield, ?Await, ?Return]`,

  "StatementListItem": `StatementListItem[Yield, Await, Return] :
    Statement[?Yield, ?Await, ?Return]
    Declaration[?Yield, ?Await]`,

  "LexicalDeclaration": `LexicalDeclaration[In, Yield, Await] :
    LetOrConst BindingList[?In, ?Yield, ?Await] ;`,

  "LetOrConst": `LetOrConst :
    let
    const`,

  "BindingList": `BindingList[In, Yield, Await] :
    LexicalBinding[?In, ?Yield, ?Await]
    BindingList[?In, ?Yield, ?Await] , LexicalBinding[?In, ?Yield, ?Await]`,

  "LexicalBinding": `LexicalBinding[In, Yield, Await] :
    BindingIdentifier[?Yield, ?Await] Initializer[?In, ?Yield, ?Await]_opt
    BindingPattern[?Yield, ?Await] Initializer[?In, ?Yield, ?Await]`,

  "VariableStatement": `VariableStatement[Yield, Await] :
    var VariableDeclarationList[+In, ?Yield, ?Await] ;`,

  "VariableDeclarationList": `VariableDeclarationList[In, Yield, Await] :
    VariableDeclaration[?In, ?Yield, ?Await]
    VariableDeclarationList[?In, ?Yield, ?Await] , VariableDeclaration[?In, ?Yield, ?Await]`,

  "VariableDeclaration": `VariableDeclaration[In, Yield, Await] :
    BindingIdentifier[?Yield, ?Await] Initializer[?In, ?Yield, ?Await]_opt
    BindingPattern[?Yield, ?Await] Initializer[?In, ?Yield, ?Await]`,

  "BindingPattern": `BindingPattern[Yield, Await] :
    ObjectBindingPattern[?Yield, ?Await]
    ArrayBindingPattern[?Yield, ?Await]`,

  "ObjectBindingPattern": `ObjectBindingPattern[Yield, Await] :
    { }
    { BindingRestProperty[?Yield, ?Await] }
    { BindingPropertyList[?Yield, ?Await] }
    { BindingPropertyList[?Yield, ?Await] , BindingRestProperty[?Yield, ?Await]_opt }`,

  "ArrayBindingPattern": `ArrayBindingPattern[Yield, Await] :
    [ Elision_opt BindingRestElement[?Yield, ?Await]_opt ]
    [ BindingElementList[?Yield, ?Await] ]
    [ BindingElementList[?Yield, ?Await] , Elision_opt BindingRestElement[?Yield, ?Await]_opt ]`,

  "BindingRestProperty": `BindingRestProperty[Yield, Await] :
    ... BindingIdentifier[?Yield, ?Await]`,

  "BindingPropertyList": `BindingPropertyList[Yield, Await] :
    BindingProperty[?Yield, ?Await]
    BindingPropertyList[?Yield, ?Await] , BindingProperty[?Yield, ?Await]`,

  "BindingElementList": `BindingElementList[Yield, Await] :
    BindingElisionElement[?Yield, ?Await]
    BindingElementList[?Yield, ?Await] , BindingElisionElement[?Yield, ?Await]`,

  "BindingElisionElement": `BindingElisionElement[Yield, Await] :
    Elision_opt BindingElement[?Yield, ?Await]`,

  "BindingProperty": `BindingProperty[Yield, Await] :
    SingleNameBinding[?Yield, ?Await]
    PropertyName[?Yield, ?Await] : BindingElement[?Yield, ?Await]`,

  "BindingElement": `BindingElement[Yield, Await] :
    SingleNameBinding[?Yield, ?Await]
    BindingPattern[?Yield, ?Await] Initializer[+In, ?Yield, ?Await]_opt`,

  "SingleNameBinding": `SingleNameBinding[Yield, Await] :
    BindingIdentifier[?Yield, ?Await] Initializer[+In, ?Yield, ?Await]_opt`,

  "BindingRestElement": `BindingRestElement[Yield, Await] :
    ... BindingIdentifier[?Yield, ?Await]
    ... BindingPattern[?Yield, ?Await]`,

  "EmptyStatement": `EmptyStatement :
    ;`,

  "ExpressionStatement": `ExpressionStatement[Yield, Await] :
    [lookahead ∉ { {, function, async [no LineTerminator here] function, class, let [ }]
    Expression[+In, ?Yield, ?Await] ;`,

  "IfStatement": `IfStatement[Yield, Await, Return] :
    if ( Expression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return] else Statement[?Yield, ?Await, ?Return]
    if ( Expression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return] [lookahead ≠ else]`,

  "IterationStatement": `IterationStatement[Yield, Await, Return] :
    DoWhileStatement[?Yield, ?Await, ?Return]
    WhileStatement[?Yield, ?Await, ?Return]
    ForStatement[?Yield, ?Await, ?Return]
    ForInOfStatement[?Yield, ?Await, ?Return]`,

  "DoWhileStatement": `DoWhileStatement[Yield, Await, Return] :
    do Statement[?Yield, ?Await, ?Return] while ( Expression[+In, ?Yield, ?Await] ) ;`,

  "WhileStatement": `WhileStatement[Yield, Await, Return] :
    while ( Expression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]`,

  "ForStatement": `ForStatement[Yield, Await, Return] :
    for ( [lookahead ≠ let [] Expression[~In, ?Yield, ?Await]_opt ; Expression[+In, ?Yield, ?Await]_opt ; Expression[+In, ?Yield, ?Await]_opt ) Statement[?Yield, ?Await, ?Return]
    for ( var VariableDeclarationList[~In, ?Yield, ?Await] ; Expression[+In, ?Yield, ?Await]_opt ; Expression[+In, ?Yield, ?Await]_opt ) Statement[?Yield, ?Await, ?Return]
    for ( LexicalDeclaration[~In, ?Yield, ?Await] Expression[+In, ?Yield, ?Await]_opt ; Expression[+In, ?Yield, ?Await]_opt ) Statement[?Yield, ?Await, ?Return]`,

  "ForInOfStatement": `ForInOfStatement[Yield, Await, Return] :
    for ( [lookahead ≠ let [] LeftHandSideExpression[?Yield, ?Await] in Expression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    for ( var ForBinding[?Yield, ?Await] in Expression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    for ( ForDeclaration[?Yield, ?Await] in Expression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    for ( [lookahead ∉ { let, async of }] LeftHandSideExpression[?Yield, ?Await] of AssignmentExpression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    for ( var ForBinding[?Yield, ?Await] of AssignmentExpression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    for ( ForDeclaration[?Yield, ?Await] of AssignmentExpression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    [+Await] for await ( [lookahead ≠ let] LeftHandSideExpression[?Yield, ?Await] of AssignmentExpression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    [+Await] for await ( var ForBinding[?Yield, ?Await] of AssignmentExpression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]
    [+Await] for await ( ForDeclaration[?Yield, ?Await] of AssignmentExpression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]`,

  "ForDeclaration": `ForDeclaration[Yield, Await] :
    LetOrConst ForBinding[?Yield, ?Await]`,

  "ForBinding": `ForBinding[Yield, Await] :
    BindingIdentifier[?Yield, ?Await]
    BindingPattern[?Yield, ?Await]`,

  "ContinueStatement": `ContinueStatement[Yield, Await] :
    continue ;
    continue [no LineTerminator here] LabelIdentifier[?Yield, ?Await] ;`,

  "BreakStatement": `BreakStatement[Yield, Await] :
    break ;
    break [no LineTerminator here] LabelIdentifier[?Yield, ?Await] ;`,

  "ReturnStatement": `ReturnStatement[Yield, Await] :
    return ;
    return [no LineTerminator here] Expression[+In, ?Yield, ?Await] ;`,

  "WithStatement": `WithStatement[Yield, Await, Return] :
    with ( Expression[+In, ?Yield, ?Await] ) Statement[?Yield, ?Await, ?Return]`,

  "SwitchStatement": `SwitchStatement[Yield, Await, Return] :
    switch ( Expression[+In, ?Yield, ?Await] ) CaseBlock[?Yield, ?Await, ?Return]`,

  "CaseBlock": `CaseBlock[Yield, Await, Return] :
    { CaseClauses[?Yield, ?Await, ?Return]_opt }
    { CaseClauses[?Yield, ?Await, ?Return]_opt DefaultClause[?Yield, ?Await, ?Return] CaseClauses[?Yield, ?Await, ?Return]_opt }`,

  "CaseClauses": `CaseClauses[Yield, Await, Return] :
    CaseClause[?Yield, ?Await, ?Return]
    CaseClauses[?Yield, ?Await, ?Return] CaseClause[?Yield, ?Await, ?Return]`,

  "CaseClause": `CaseClause[Yield, Await, Return] :
    case Expression[+In, ?Yield, ?Await] : StatementList[?Yield, ?Await, ?Return]_opt`,

  "DefaultClause": `DefaultClause[Yield, Await, Return] :
    default : StatementList[?Yield, ?Await, ?Return]_opt`,

  "LabelledStatement": `LabelledStatement[Yield, Await, Return] :
    LabelIdentifier[?Yield, ?Await] : LabelledItem[?Yield, ?Await, ?Return]`,

  "LabelledItem": `LabelledItem[Yield, Await, Return] :
    Statement[?Yield, ?Await, ?Return]
    FunctionDeclaration[?Yield, ?Await, ~Default]`,

  "ThrowStatement": `ThrowStatement[Yield, Await] :
    throw [no LineTerminator here] Expression[+In, ?Yield, ?Await] ;`,

  "TryStatement": `TryStatement[Yield, Await, Return] :
    try Block[?Yield, ?Await, ?Return] Catch[?Yield, ?Await, ?Return]
    try Block[?Yield, ?Await, ?Return] Finally[?Yield, ?Await, ?Return]
    try Block[?Yield, ?Await, ?Return] Catch[?Yield, ?Await, ?Return] Finally[?Yield, ?Await, ?Return]`,

  "Catch": `Catch[Yield, Await, Return] :
    catch ( CatchParameter[?Yield, ?Await] ) Block[?Yield, ?Await, ?Return]
    catch Block[?Yield, ?Await, ?Return]`,

  "Finally": `Finally[Yield, Await, Return] :
    finally Block[?Yield, ?Await, ?Return]`,

  "CatchParameter": `CatchParameter[Yield, Await] :
    BindingIdentifier[?Yield, ?Await]
    BindingPattern[?Yield, ?Await]`,

  "DebuggerStatement": `DebuggerStatement :
    debugger ;`,

  // ===== A.4 Functions and Classes =====

  "UniqueFormalParameters": `UniqueFormalParameters[Yield, Await] :
    FormalParameters[?Yield, ?Await]`,

  "FormalParameters": `FormalParameters[Yield, Await] :
    [empty]
    FunctionRestParameter[?Yield, ?Await]
    FormalParameterList[?Yield, ?Await]
    FormalParameterList[?Yield, ?Await] ,
    FormalParameterList[?Yield, ?Await] , FunctionRestParameter[?Yield, ?Await]`,

  "FormalParameterList": `FormalParameterList[Yield, Await] :
    FormalParameter[?Yield, ?Await]
    FormalParameterList[?Yield, ?Await] , FormalParameter[?Yield, ?Await]`,

  "FunctionRestParameter": `FunctionRestParameter[Yield, Await] :
    BindingRestElement[?Yield, ?Await]`,

  "FormalParameter": `FormalParameter[Yield, Await] :
    BindingElement[?Yield, ?Await]`,

  "FunctionDeclaration": `FunctionDeclaration[Yield, Await, Default] :
    function BindingIdentifier[?Yield, ?Await] ( FormalParameters[~Yield, ~Await] ) { FunctionBody[~Yield, ~Await] }
    [+Default] function ( FormalParameters[~Yield, ~Await] ) { FunctionBody[~Yield, ~Await] }`,

  "FunctionExpression": `FunctionExpression :
    function BindingIdentifier[~Yield, ~Await]_opt ( FormalParameters[~Yield, ~Await] ) { FunctionBody[~Yield, ~Await] }`,

  "FunctionBody": `FunctionBody[Yield, Await] :
    FunctionStatementList[?Yield, ?Await]`,

  "FunctionStatementList": `FunctionStatementList[Yield, Await] :
    StatementList[?Yield, ?Await, +Return]_opt`,

  "ArrowFunction": `ArrowFunction[In, Yield, Await] :
    ArrowParameters[?Yield, ?Await] [no LineTerminator here] => ConciseBody[?In]`,

  "ArrowParameters": `ArrowParameters[Yield, Await] :
    BindingIdentifier[?Yield, ?Await]
    CoverParenthesizedExpressionAndArrowParameterList[?Yield, ?Await]`,

  "ConciseBody": `ConciseBody[In] :
    [lookahead ≠ {] ExpressionBody[?In, ~Await]
    { FunctionBody[~Yield, ~Await] }`,

  "ExpressionBody": `ExpressionBody[In, Await] :
    AssignmentExpression[?In, ~Yield, ?Await]`,

  "ArrowFormalParameters": `ArrowFormalParameters[Yield, Await] :
    ( UniqueFormalParameters[?Yield, ?Await] )`,

  "AsyncArrowFunction": `AsyncArrowFunction[In, Yield, Await] :
    async [no LineTerminator here] AsyncArrowBindingIdentifier[?Yield] [no LineTerminator here] => AsyncConciseBody[?In]
    CoverCallExpressionAndAsyncArrowHead[?Yield, ?Await] [no LineTerminator here] => AsyncConciseBody[?In]`,

  "AsyncConciseBody": `AsyncConciseBody[In] :
    [lookahead ≠ {] ExpressionBody[?In, +Await]
    { AsyncFunctionBody }`,

  "AsyncArrowBindingIdentifier": `AsyncArrowBindingIdentifier[Yield] :
    BindingIdentifier[?Yield, +Await]`,

  "CoverCallExpressionAndAsyncArrowHead": `CoverCallExpressionAndAsyncArrowHead[Yield, Await] :
    MemberExpression[?Yield, ?Await] Arguments[?Yield, ?Await]`,

  "AsyncArrowHead": `AsyncArrowHead :
    async [no LineTerminator here] ArrowFormalParameters[~Yield, +Await]`,

  "MethodDefinition": `MethodDefinition[Yield, Await] :
    ClassElementName[?Yield, ?Await] ( UniqueFormalParameters[~Yield, ~Await] ) { FunctionBody[~Yield, ~Await] }
    GeneratorMethod[?Yield, ?Await]
    AsyncMethod[?Yield, ?Await]
    AsyncGeneratorMethod[?Yield, ?Await]
    get ClassElementName[?Yield, ?Await] ( ) { FunctionBody[~Yield, ~Await] }
    set ClassElementName[?Yield, ?Await] ( PropertySetParameterList ) { FunctionBody[~Yield, ~Await] }`,

  "PropertySetParameterList": `PropertySetParameterList :
    FormalParameter[~Yield, ~Await]`,

  "GeneratorDeclaration": `GeneratorDeclaration[Yield, Await, Default] :
    function * BindingIdentifier[?Yield, ?Await] ( FormalParameters[+Yield, ~Await] ) { GeneratorBody }
    [+Default] function * ( FormalParameters[+Yield, ~Await] ) { GeneratorBody }`,

  "GeneratorExpression": `GeneratorExpression :
    function * BindingIdentifier[+Yield, ~Await]_opt ( FormalParameters[+Yield, ~Await] ) { GeneratorBody }`,

  "GeneratorMethod": `GeneratorMethod[Yield, Await] :
    * ClassElementName[?Yield, ?Await] ( UniqueFormalParameters[+Yield, ~Await] ) { GeneratorBody }`,

  "GeneratorBody": `GeneratorBody :
    FunctionBody[+Yield, ~Await]`,

  "YieldExpression": `YieldExpression[In, Await] :
    yield
    yield [no LineTerminator here] AssignmentExpression[?In, +Yield, ?Await]
    yield [no LineTerminator here] * AssignmentExpression[?In, +Yield, ?Await]`,

  "AsyncGeneratorDeclaration": `AsyncGeneratorDeclaration[Yield, Await, Default] :
    async [no LineTerminator here] function * BindingIdentifier[?Yield, ?Await] ( FormalParameters[+Yield, +Await] ) { AsyncGeneratorBody }
    [+Default] async [no LineTerminator here] function * ( FormalParameters[+Yield, +Await] ) { AsyncGeneratorBody }`,

  "AsyncGeneratorExpression": `AsyncGeneratorExpression :
    async [no LineTerminator here] function * BindingIdentifier[+Yield, +Await]_opt ( FormalParameters[+Yield, +Await] ) { AsyncGeneratorBody }`,

  "AsyncGeneratorMethod": `AsyncGeneratorMethod[Yield, Await] :
    async [no LineTerminator here] * ClassElementName[?Yield, ?Await] ( UniqueFormalParameters[+Yield, +Await] ) { AsyncGeneratorBody }`,

  "AsyncGeneratorBody": `AsyncGeneratorBody :
    FunctionBody[+Yield, +Await]`,

  "AsyncFunctionDeclaration": `AsyncFunctionDeclaration[Yield, Await, Default] :
    async [no LineTerminator here] function BindingIdentifier[?Yield, ?Await] ( FormalParameters[~Yield, +Await] ) { AsyncFunctionBody }
    [+Default] async [no LineTerminator here] function ( FormalParameters[~Yield, +Await] ) { AsyncFunctionBody }`,

  "AsyncFunctionExpression": `AsyncFunctionExpression :
    async [no LineTerminator here] function BindingIdentifier[~Yield, +Await]_opt ( FormalParameters[~Yield, +Await] ) { AsyncFunctionBody }`,

  "AsyncMethod": `AsyncMethod[Yield, Await] :
    async [no LineTerminator here] ClassElementName[?Yield, ?Await] ( UniqueFormalParameters[~Yield, +Await] ) { AsyncFunctionBody }`,

  "AsyncFunctionBody": `AsyncFunctionBody :
    FunctionBody[~Yield, +Await]`,

  "AwaitExpression": `AwaitExpression[Yield] :
    await UnaryExpression[?Yield, +Await]`,

  "ClassDeclaration": `ClassDeclaration[Yield, Await, Default] :
    class BindingIdentifier[?Yield, ?Await] ClassTail[?Yield, ?Await]
    [+Default] class ClassTail[?Yield, ?Await]`,

  "ClassExpression": `ClassExpression[Yield, Await] :
    class BindingIdentifier[?Yield, ?Await]_opt ClassTail[?Yield, ?Await]`,

  "ClassTail": `ClassTail[Yield, Await] :
    ClassHeritage[?Yield, ?Await]_opt { ClassBody[?Yield, ?Await]_opt }`,

  "ClassHeritage": `ClassHeritage[Yield, Await] :
    extends LeftHandSideExpression[?Yield, ?Await]`,

  "ClassBody": `ClassBody[Yield, Await] :
    ClassElementList[?Yield, ?Await]`,

  "ClassElementList": `ClassElementList[Yield, Await] :
    ClassElement[?Yield, ?Await]
    ClassElementList[?Yield, ?Await] ClassElement[?Yield, ?Await]`,

  "ClassElement": `ClassElement[Yield, Await] :
    MethodDefinition[?Yield, ?Await]
    static MethodDefinition[?Yield, ?Await]
    FieldDefinition[?Yield, ?Await] ;
    static FieldDefinition[?Yield, ?Await] ;
    ClassStaticBlock
    ;`,

  "FieldDefinition": `FieldDefinition[Yield, Await] :
    ClassElementName[?Yield, ?Await] Initializer[+In, ?Yield, ?Await]_opt`,

  "ClassElementName": `ClassElementName[Yield, Await] :
    PropertyName[?Yield, ?Await]
    PrivateIdentifier`,

  "ClassStaticBlock": `ClassStaticBlock :
    static { ClassStaticBlockBody }`,

  "ClassStaticBlockBody": `ClassStaticBlockBody :
    ClassStaticBlockStatementList`,

  "ClassStaticBlockStatementList": `ClassStaticBlockStatementList :
    StatementList[~Yield, +Await, ~Return]_opt`,

  // ===== A.5 Scripts and Modules =====

  "Script": `Script :
    ScriptBody_opt`,

  "ScriptBody": `ScriptBody :
    StatementList[~Yield, ~Await, ~Return]`,

  "Module": `Module :
    ModuleBody_opt`,

  "ModuleBody": `ModuleBody :
    ModuleItemList`,

  "ModuleItemList": `ModuleItemList :
    ModuleItem
    ModuleItemList ModuleItem`,

  "ModuleItem": `ModuleItem :
    ImportDeclaration
    ExportDeclaration
    StatementListItem[~Yield, +Await, ~Return]`,

  "ModuleExportName": `ModuleExportName :
    IdentifierName
    StringLiteral`,

  "ImportDeclaration": `ImportDeclaration :
    import ImportClause FromClause WithClause_opt ;
    import ModuleSpecifier WithClause_opt ;`,

  "ImportClause": `ImportClause :
    ImportedDefaultBinding
    NameSpaceImport
    NamedImports
    ImportedDefaultBinding , NameSpaceImport
    ImportedDefaultBinding , NamedImports`,

  "ImportedDefaultBinding": `ImportedDefaultBinding :
    ImportedBinding`,

  "NameSpaceImport": `NameSpaceImport :
    * as ImportedBinding`,

  "NamedImports": `NamedImports :
    { }
    { ImportsList }
    { ImportsList , }`,

  "FromClause": `FromClause :
    from ModuleSpecifier`,

  "ImportsList": `ImportsList :
    ImportSpecifier
    ImportsList , ImportSpecifier`,

  "ImportSpecifier": `ImportSpecifier :
    ImportedBinding
    ModuleExportName as ImportedBinding`,

  "ModuleSpecifier": `ModuleSpecifier :
    StringLiteral`,

  "ImportedBinding": `ImportedBinding :
    BindingIdentifier[~Yield, +Await]`,

  "WithClause": `WithClause :
    with { }
    with { WithEntries ,_opt }`,

  "WithEntries": `WithEntries :
    AttributeKey : StringLiteral
    AttributeKey : StringLiteral , WithEntries`,

  "AttributeKey": `AttributeKey :
    IdentifierName
    StringLiteral`,

  "ExportDeclaration": `ExportDeclaration :
    export ExportFromClause FromClause WithClause_opt ;
    export NamedExports ;
    export VariableStatement[~Yield, +Await]
    export Declaration[~Yield, +Await]
    export default HoistableDeclaration[~Yield, +Await, +Default]
    export default ClassDeclaration[~Yield, +Await, +Default]
    export default [lookahead ∉ { function, async [no LineTerminator here] function, class }] AssignmentExpression[+In, ~Yield, +Await] ;`,

  "ExportFromClause": `ExportFromClause :
    *
    * as ModuleExportName
    NamedExports`,

  "NamedExports": `NamedExports :
    { }
    { ExportsList }
    { ExportsList , }`,

  "ExportsList": `ExportsList :
    ExportSpecifier
    ExportsList , ExportSpecifier`,

  "ExportSpecifier": `ExportSpecifier :
    ModuleExportName
    ModuleExportName as ModuleExportName`,
};

/**
 * Gets the EBNF definition for a given rule name.
 * Returns undefined if not found.
 */
export function getEbnfDefinition(name: RuleName): string | undefined {
  return EBNF_DEFINITIONS[name];
}

/**
 * Get all EBNF rule names for grammar coverage checking.
 */
export function getEbnfRuleNames(): string[] {
  return Object.keys(EBNF_DEFINITIONS);
}
