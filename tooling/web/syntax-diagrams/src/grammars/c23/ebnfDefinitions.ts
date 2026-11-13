/**
 * EBNF definitions for C23 grammar rules.
 * Each entry maps a rule name to its EBNF syntax as specified in
 * ISO/IEC 9899:2024 (C23) Annex A.
 *
 * Notation:
 *   opt     = optional (subscript in standard, shown as superscript here)
 *   |       = alternative
 *   ...     = ellipsis token (not repetition)
 */

export type RuleName = string;

export const EBNF_DEFINITIONS: Record<RuleName, string> = {
  // ===== A.2 Lexical grammar =====

  "token": `token:
    keyword
    identifier
    constant
    string-literal
    punctuator`,

  "preprocessing-token": `preprocessing-token:
    header-name
    identifier
    pp-number
    character-constant
    string-literal
    punctuator
    each universal-character-name that cannot be one of the above
    each non-white-space-character that cannot be one of the above`,

  "identifier": `identifier:
    identifier-start
    identifier identifier-continue`,

  "universal-character-name": `universal-character-name:
    \\u hex-quad
    \\U hex-quad hex-quad`,

  "constant": `constant:
    integer-constant
    floating-constant
    enumeration-constant
    character-constant
    predefined-constant`,

  // ===== A.3.1 Expressions =====

  "primary-expression": `primary-expression:
    identifier
    constant
    string-literal
    ( expression )
    generic-selection`,

  "generic-selection": `generic-selection:
    _Generic ( assignment-expression , generic-assoc-list )`,

  "generic-assoc-list": `generic-assoc-list:
    generic-association
    generic-assoc-list , generic-association`,

  "generic-association": `generic-association:
    type-name : assignment-expression
    default : assignment-expression`,

  "argument-expression-list": `argument-expression-list:
    assignment-expression
    argument-expression-list , assignment-expression`,

  "compound-literal": `compound-literal:
    ( storage-class-specifiers_opt type-name ) braced-initializer`,

  "postfix-expression": `postfix-expression:
    primary-expression
    postfix-expression [ expression ]
    postfix-expression ( argument-expression-list_opt )
    postfix-expression . identifier
    postfix-expression -> identifier
    postfix-expression ++
    postfix-expression --
    compound-literal`,

  "unary-operator": `unary-operator: one of
    & * + - ~ !`,

  "unary-expression": `unary-expression:
    postfix-expression
    ++ unary-expression
    -- unary-expression
    unary-operator cast-expression
    sizeof unary-expression
    sizeof ( type-name )
    alignof ( type-name )`,

  "cast-expression": `cast-expression:
    unary-expression
    ( type-name ) cast-expression`,

  "multiplicative-expression": `multiplicative-expression:
    cast-expression
    multiplicative-expression * cast-expression
    multiplicative-expression / cast-expression
    multiplicative-expression % cast-expression`,

  "additive-expression": `additive-expression:
    multiplicative-expression
    additive-expression + multiplicative-expression
    additive-expression - multiplicative-expression`,

  "shift-expression": `shift-expression:
    additive-expression
    shift-expression << additive-expression
    shift-expression >> additive-expression`,

  "relational-expression": `relational-expression:
    shift-expression
    relational-expression < shift-expression
    relational-expression > shift-expression
    relational-expression <= shift-expression
    relational-expression >= shift-expression`,

  "equality-expression": `equality-expression:
    relational-expression
    equality-expression == relational-expression
    equality-expression != relational-expression`,

  "AND-expression": `AND-expression:
    equality-expression
    AND-expression & equality-expression`,

  "exclusive-OR-expression": `exclusive-OR-expression:
    AND-expression
    exclusive-OR-expression ^ AND-expression`,

  "inclusive-OR-expression": `inclusive-OR-expression:
    exclusive-OR-expression
    inclusive-OR-expression | exclusive-OR-expression`,

  "logical-AND-expression": `logical-AND-expression:
    inclusive-OR-expression
    logical-AND-expression && inclusive-OR-expression`,

  "logical-OR-expression": `logical-OR-expression:
    logical-AND-expression
    logical-OR-expression || logical-AND-expression`,

  "conditional-expression": `conditional-expression:
    logical-OR-expression
    logical-OR-expression ? expression : conditional-expression`,

  "assignment-operator": `assignment-operator: one of
    = *= /= %= += -= <<= >>= &= ^= |=`,

  "assignment-expression": `assignment-expression:
    conditional-expression
    unary-expression assignment-operator assignment-expression`,

  "expression": `expression:
    assignment-expression
    expression , assignment-expression`,

  "constant-expression": `constant-expression:
    conditional-expression`,

  // ===== A.3.2 Declarations =====

  "declaration": `declaration:
    declaration-specifiers init-declarator-list_opt ;
    attribute-specifier-sequence declaration-specifiers init-declarator-list ;
    static_assert-declaration
    attribute-declaration`,

  "declaration-specifiers": `declaration-specifiers:
    declaration-specifier attribute-specifier-sequence_opt
    declaration-specifier declaration-specifiers`,

  "declaration-specifier": `declaration-specifier:
    storage-class-specifier
    type-specifier-qualifier
    function-specifier`,

  "init-declarator-list": `init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator`,

  "init-declarator": `init-declarator:
    declarator
    declarator = initializer`,

  "storage-class-specifiers": `storage-class-specifiers:
    storage-class-specifier
    storage-class-specifiers storage-class-specifier`,

  "storage-class-specifier": `storage-class-specifier:
    auto
    constexpr
    extern
    register
    static
    thread_local
    typedef`,

  "type-specifier-qualifier": `type-specifier-qualifier:
    type-specifier
    type-qualifier
    alignment-specifier`,

  "type-specifier": `type-specifier:
    void
    char
    short
    int
    long
    float
    double
    signed
    unsigned
    _BitInt ( constant-expression )
    bool
    _Complex
    _Decimal32
    _Decimal64
    _Decimal128
    atomic-type-specifier
    struct-or-union-specifier
    enum-specifier
    typedef-name
    typeof-specifier`,

  "struct-or-union-specifier": `struct-or-union-specifier:
    struct-or-union attribute-specifier-sequence_opt identifier_opt { member-declaration-list }
    struct-or-union attribute-specifier-sequence_opt identifier`,

  "member-declaration-list": `member-declaration-list:
    member-declaration
    member-declaration-list member-declaration`,

  "member-declaration": `member-declaration:
    attribute-specifier-sequence_opt specifier-qualifier-list member-declarator-list_opt ;
    static_assert-declaration`,

  "specifier-qualifier-list": `specifier-qualifier-list:
    type-specifier-qualifier attribute-specifier-sequence_opt
    type-specifier-qualifier specifier-qualifier-list`,

  "enum-specifier": `enum-specifier:
    enum attribute-specifier-sequence_opt identifier_opt enum-type-specifier_opt { enumerator-list }
    enum attribute-specifier-sequence_opt identifier_opt enum-type-specifier_opt { enumerator-list , }
    enum identifier enum-type-specifier_opt`,

  "enumerator-list": `enumerator-list:
    enumerator
    enumerator-list , enumerator`,

  "enumerator": `enumerator:
    enumeration-constant attribute-specifier-sequence_opt
    enumeration-constant attribute-specifier-sequence_opt = constant-expression`,

  "atomic-type-specifier": `atomic-type-specifier:
    _Atomic ( type-name )`,

  "typeof-specifier": `typeof-specifier:
    typeof ( typeof-specifier-argument )
    typeof_unqual ( typeof-specifier-argument )`,

  "type-qualifier": `type-qualifier:
    const
    restrict
    volatile
    _Atomic`,

  "type-qualifier-list": `type-qualifier-list:
    type-qualifier
    type-qualifier-list type-qualifier`,

  "function-specifier": `function-specifier:
    inline
    _Noreturn`,

  "alignment-specifier": `alignment-specifier:
    alignas ( type-name )
    alignas ( constant-expression )`,

  "declarator": `declarator:
    pointer_opt direct-declarator`,

  "pointer": `pointer:
    * attribute-specifier-sequence_opt type-qualifier-list_opt
    * attribute-specifier-sequence_opt type-qualifier-list_opt pointer`,

  "direct-declarator": `direct-declarator:
    identifier attribute-specifier-sequence_opt
    ( declarator )
    array-declarator attribute-specifier-sequence_opt
    function-declarator attribute-specifier-sequence_opt`,

  "parameter-type-list": `parameter-type-list:
    parameter-list
    parameter-list , ...
    ...`,

  "parameter-list": `parameter-list:
    parameter-declaration
    parameter-list , parameter-declaration`,

  "parameter-declaration": `parameter-declaration:
    attribute-specifier-sequence_opt declaration-specifiers declarator
    attribute-specifier-sequence_opt declaration-specifiers abstract-declarator_opt`,

  "type-name": `type-name:
    specifier-qualifier-list abstract-declarator_opt`,

  "abstract-declarator": `abstract-declarator:
    pointer
    pointer_opt direct-abstract-declarator`,

  "direct-abstract-declarator": `direct-abstract-declarator:
    ( abstract-declarator )
    array-abstract-declarator attribute-specifier-sequence_opt
    function-abstract-declarator attribute-specifier-sequence_opt`,

  "braced-initializer": `braced-initializer:
    { }
    { initializer-list }
    { initializer-list , }`,

  "initializer": `initializer:
    assignment-expression
    braced-initializer`,

  "initializer-list": `initializer-list:
    designation_opt initializer
    initializer-list , designation_opt initializer`,

  "designation": `designation:
    designator-list =`,

  "designator-list": `designator-list:
    designator
    designator-list designator`,

  "designator": `designator:
    [ constant-expression ]
    . identifier`,

  // ===== A.3.3 Statements =====

  "statement": `statement:
    labeled-statement
    unlabeled-statement`,

  "label": `label:
    attribute-specifier-sequence_opt identifier :
    attribute-specifier-sequence_opt case constant-expression :
    attribute-specifier-sequence_opt default :`,

  "labeled-statement": `labeled-statement:
    label statement`,

  "unlabeled-statement": `unlabeled-statement:
    expression-statement
    attribute-specifier-sequence_opt primary-block
    attribute-specifier-sequence_opt jump-statement`,

  "compound-statement": `compound-statement:
    { block-item-list_opt }`,

  "block-item-list": `block-item-list:
    block-item
    block-item-list block-item`,

  "block-item": `block-item:
    declaration
    unlabeled-statement
    label`,

  "expression-statement": `expression-statement:
    expression_opt ;
    attribute-specifier-sequence expression ;`,

  "selection-statement": `selection-statement:
    if ( expression ) secondary-block
    if ( expression ) secondary-block else secondary-block
    switch ( expression ) secondary-block`,

  "iteration-statement": `iteration-statement:
    while ( expression ) secondary-block
    do secondary-block while ( expression ) ;
    for ( expression_opt ; expression_opt ; expression_opt ) secondary-block
    for ( declaration expression_opt ; expression_opt ) secondary-block`,

  "jump-statement": `jump-statement:
    goto identifier ;
    continue ;
    break ;
    return expression_opt ;`,

  // ===== A.3.4 External definitions =====

  "translation-unit": `translation-unit:
    external-declaration
    translation-unit external-declaration`,

  "external-declaration": `external-declaration:
    function-definition
    declaration`,

  "function-definition": `function-definition:
    attribute-specifier-sequence_opt declaration-specifiers declarator function-body`,

  "function-body": `function-body:
    compound-statement`,

  // ===== A.4 Preprocessing directives =====

  "preprocessing-file": `preprocessing-file:
    group_opt`,

  "group": `group:
    group-part
    group group-part`,

  "group-part": `group-part:
    if-section
    control-line
    text-line
    # non-directive`,

  "if-section": `if-section:
    if-group elif-groups_opt else-group_opt endif-line`,

  "if-group": `if-group:
    # if constant-expression new-line group_opt
    # ifdef identifier new-line group_opt
    # ifndef identifier new-line group_opt`,

  "elif-groups": `elif-groups:
    elif-group
    elif-groups elif-group`,

  "elif-group": `elif-group:
    # elif constant-expression new-line group_opt
    # elifdef identifier new-line group_opt
    # elifndef identifier new-line group_opt`,

  "else-group": `else-group:
    # else new-line group_opt`,

  "endif-line": `endif-line:
    # endif new-line`,

  "control-line": `control-line:
    # include pp-tokens new-line
    # embed pp-tokens new-line
    # define identifier replacement-list new-line
    # define identifier lparen identifier-list_opt ) replacement-list new-line
    # define identifier lparen ... ) replacement-list new-line
    # define identifier lparen identifier-list , ... ) replacement-list new-line
    # undef identifier new-line
    # line pp-tokens new-line
    # error pp-tokens_opt new-line
    # warning pp-tokens_opt new-line
    # pragma pp-tokens_opt new-line
    # new-line`,

  "text-line": `text-line:
    pp-tokens_opt new-line`,

  "non-directive": `non-directive:
    pp-tokens new-line`,

  "pp-tokens": `pp-tokens:
    preprocessing-token
    pp-tokens preprocessing-token`,

  "replacement-list": `replacement-list:
    pp-tokens_opt`,
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
