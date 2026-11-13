/**
 * EBNF definitions for C++23 grammar rules.
 * 
 * These definitions are displayed below each railroad diagram to provide
 * the textual grammar specification alongside the visual representation.
 * 
 * Based on the C++ Standard Grammar Summary (Annex A).
 * Reference: https://eel.is/c++draft/gram
 */

import type { RuleName } from "./cppGrammar";

/**
 * EBNF definitions keyed by rule name.
 * Each value is a multi-line string showing the grammar production.
 */
export const EBNF_DEFINITIONS: Record<RuleName, string> = {
  // ===== A.2 Keywords [gram.key] =====
  
  "typedef-name": `typedef-name:
    identifier
    simple-template-id`,

  "namespace-name": `namespace-name:
    identifier
    namespace-alias`,

  "namespace-alias": `namespace-alias:
    identifier`,

  "class-name": `class-name:
    identifier
    simple-template-id`,

  "enum-name": `enum-name:
    identifier`,

  "template-name": `template-name:
    identifier`,

  // ===== A.3 Lexical conventions [gram.lex] =====

  "n-char": `n-char:
    any member of the translation character set except } or new-line`,

  "n-char-sequence": `n-char-sequence:
    n-char
    n-char-sequence n-char`,

  "named-universal-character": `named-universal-character:
    \\N{ n-char-sequence }`,

  "hex-quad": `hex-quad:
    hexadecimal-digit hexadecimal-digit hexadecimal-digit hexadecimal-digit`,

  "simple-hexadecimal-digit-sequence": `simple-hexadecimal-digit-sequence:
    hexadecimal-digit
    simple-hexadecimal-digit-sequence hexadecimal-digit`,

  "universal-character-name": `universal-character-name:
    \\u hex-quad
    \\U hex-quad hex-quad
    \\u{ simple-hexadecimal-digit-sequence }
    named-universal-character`,

  "preprocessing-token": `preprocessing-token:
    header-name
    import-keyword
    module-keyword
    export-keyword
    identifier
    pp-number
    character-literal
    user-defined-character-literal
    string-literal
    user-defined-string-literal
    preprocessing-op-or-punc
    each non-whitespace character that cannot be one of the above`,

  "token": `token:
    identifier
    keyword
    literal
    operator-or-punctuator`,

  "header-name": `header-name:
    < h-char-sequence >
    " q-char-sequence "`,

  "h-char-sequence": `h-char-sequence:
    h-char
    h-char-sequence h-char`,

  "h-char": `h-char:
    any member of the translation character set except new-line and >`,

  "q-char-sequence": `q-char-sequence:
    q-char
    q-char-sequence q-char`,

  "q-char": `q-char:
    any member of the translation character set except new-line and "`,

  "pp-number": `pp-number:
    digit
    . digit
    pp-number identifier-continue
    pp-number ' digit
    pp-number ' nondigit
    pp-number e sign
    pp-number E sign
    pp-number p sign
    pp-number P sign
    pp-number .`,

  "identifier": `identifier:
    identifier-start
    identifier identifier-continue`,

  "identifier-start": `identifier-start:
    nondigit
    an element of the translation character set with the Unicode property XID_Start`,

  "identifier-continue": `identifier-continue:
    digit
    nondigit
    an element of the translation character set with the Unicode property XID_Continue`,

  "nondigit": `nondigit: one of
    a b c d e f g h i j k l m
    n o p q r s t u v w x y z
    A B C D E F G H I J K L M
    N O P Q R S T U V W X Y Z _`,

  "digit": `digit: one of
    0 1 2 3 4 5 6 7 8 9`,

  "keyword": `keyword:
    any identifier listed in Table 5
    import-keyword
    module-keyword
    export-keyword`,

  "preprocessing-op-or-punc": `preprocessing-op-or-punc:
    preprocessing-operator
    operator-or-punctuator`,

  "preprocessing-operator": `preprocessing-operator: one of
    # ## %: %:%:`,

  "operator-or-punctuator": `operator-or-punctuator: one of
    { } [ ] ( )
    <: :> <% %> ; : ...
    ? :: . .* -> ->* ~
    ! + - * / % ^ & |
    = += -= *= /= %= ^= &= |=
    == != < > <= >= <=> && ||
    << >> <<= >>= ++ -- ,
    and or xor not bitand bitor compl
    and_eq or_eq xor_eq not_eq`,

  // ===== A.3 Literals =====

  "literal": `literal:
    integer-literal
    character-literal
    floating-point-literal
    string-literal
    boolean-literal
    pointer-literal
    user-defined-literal`,

  "integer-literal": `integer-literal:
    binary-literal integer-suffix_opt
    octal-literal integer-suffix_opt
    decimal-literal integer-suffix_opt
    hexadecimal-literal integer-suffix_opt`,

  "binary-literal": `binary-literal:
    0b binary-digit
    0B binary-digit
    binary-literal '_opt binary-digit`,

  "octal-literal": `octal-literal:
    0
    octal-literal '_opt octal-digit`,

  "decimal-literal": `decimal-literal:
    nonzero-digit
    decimal-literal '_opt digit`,

  "hexadecimal-literal": `hexadecimal-literal:
    hexadecimal-prefix hexadecimal-digit-sequence`,

  "binary-digit": `binary-digit: one of
    0 1`,

  "octal-digit": `octal-digit: one of
    0 1 2 3 4 5 6 7`,

  "nonzero-digit": `nonzero-digit: one of
    1 2 3 4 5 6 7 8 9`,

  "hexadecimal-prefix": `hexadecimal-prefix: one of
    0x 0X`,

  "hexadecimal-digit-sequence": `hexadecimal-digit-sequence:
    hexadecimal-digit
    hexadecimal-digit-sequence '_opt hexadecimal-digit`,

  "hexadecimal-digit": `hexadecimal-digit: one of
    0 1 2 3 4 5 6 7 8 9
    a b c d e f
    A B C D E F`,

  "integer-suffix": `integer-suffix:
    unsigned-suffix long-suffix_opt
    unsigned-suffix long-long-suffix_opt
    unsigned-suffix size-suffix_opt
    long-suffix unsigned-suffix_opt
    long-long-suffix unsigned-suffix_opt
    size-suffix unsigned-suffix_opt`,

  "unsigned-suffix": `unsigned-suffix: one of
    u U`,

  "long-suffix": `long-suffix: one of
    l L`,

  "long-long-suffix": `long-long-suffix: one of
    ll LL`,

  "size-suffix": `size-suffix: one of
    z Z`,

  "character-literal": `character-literal:
    encoding-prefix_opt ' c-char-sequence '`,

  "encoding-prefix": `encoding-prefix: one of
    u8 u U L`,

  "c-char-sequence": `c-char-sequence:
    c-char
    c-char-sequence c-char`,

  "c-char": `c-char:
    basic-c-char
    escape-sequence
    universal-character-name`,

  "basic-c-char": `basic-c-char:
    any member of the translation character set except ', \\, or new-line`,

  "escape-sequence": `escape-sequence:
    simple-escape-sequence
    numeric-escape-sequence
    conditional-escape-sequence`,

  "simple-escape-sequence": `simple-escape-sequence:
    \\ simple-escape-sequence-char`,

  "simple-escape-sequence-char": `simple-escape-sequence-char: one of
    ' " ? \\ a b f n r t v`,

  "numeric-escape-sequence": `numeric-escape-sequence:
    octal-escape-sequence
    hexadecimal-escape-sequence`,

  "simple-octal-digit-sequence": `simple-octal-digit-sequence:
    octal-digit
    simple-octal-digit-sequence octal-digit`,

  "octal-escape-sequence": `octal-escape-sequence:
    \\ octal-digit
    \\ octal-digit octal-digit
    \\ octal-digit octal-digit octal-digit
    \\o{ simple-octal-digit-sequence }`,

  "hexadecimal-escape-sequence": `hexadecimal-escape-sequence:
    \\x simple-hexadecimal-digit-sequence
    \\x{ simple-hexadecimal-digit-sequence }`,

  "conditional-escape-sequence": `conditional-escape-sequence:
    \\ conditional-escape-sequence-char`,

  "conditional-escape-sequence-char": `conditional-escape-sequence-char:
    any member of the basic character set that is not an octal-digit,
    a simple-escape-sequence-char, or the characters N, o, u, U, or x`,

  "floating-point-literal": `floating-point-literal:
    decimal-floating-point-literal
    hexadecimal-floating-point-literal`,

  "decimal-floating-point-literal": `decimal-floating-point-literal:
    fractional-constant exponent-part_opt floating-point-suffix_opt
    digit-sequence exponent-part floating-point-suffix_opt`,

  "hexadecimal-floating-point-literal": `hexadecimal-floating-point-literal:
    hexadecimal-prefix hexadecimal-fractional-constant binary-exponent-part floating-point-suffix_opt
    hexadecimal-prefix hexadecimal-digit-sequence binary-exponent-part floating-point-suffix_opt`,

  "fractional-constant": `fractional-constant:
    digit-sequence_opt . digit-sequence
    digit-sequence .`,

  "hexadecimal-fractional-constant": `hexadecimal-fractional-constant:
    hexadecimal-digit-sequence_opt . hexadecimal-digit-sequence
    hexadecimal-digit-sequence .`,

  "exponent-part": `exponent-part:
    e sign_opt digit-sequence
    E sign_opt digit-sequence`,

  "binary-exponent-part": `binary-exponent-part:
    p sign_opt digit-sequence
    P sign_opt digit-sequence`,

  "sign": `sign: one of
    + -`,

  "digit-sequence": `digit-sequence:
    digit
    digit-sequence '_opt digit`,

  "floating-point-suffix": `floating-point-suffix: one of
    f l f16 f32 f64 f128 bf16 F L F16 F32 F64 F128 BF16`,

  "string-literal": `string-literal:
    encoding-prefix_opt " s-char-sequence_opt "
    encoding-prefix_opt R raw-string`,

  "s-char-sequence": `s-char-sequence:
    s-char
    s-char-sequence s-char`,

  "s-char": `s-char:
    basic-s-char
    escape-sequence
    universal-character-name`,

  "basic-s-char": `basic-s-char:
    any member of the translation character set except ", \\, or new-line`,

  "raw-string": `raw-string:
    " d-char-sequence_opt ( r-char-sequence_opt ) d-char-sequence_opt "`,

  "r-char-sequence": `r-char-sequence:
    r-char
    r-char-sequence r-char`,

  "r-char": `r-char:
    any member of the translation character set, except ) followed by
    the initial d-char-sequence followed by "`,

  "d-char-sequence": `d-char-sequence:
    d-char
    d-char-sequence d-char`,

  "d-char": `d-char:
    any member of the basic character set except:
    space, (, ), \\, horizontal tab, vertical tab, form feed, and new-line`,

  "boolean-literal": `boolean-literal:
    false
    true`,

  "pointer-literal": `pointer-literal:
    nullptr`,

  "user-defined-literal": `user-defined-literal:
    user-defined-integer-literal
    user-defined-floating-point-literal
    user-defined-string-literal
    user-defined-character-literal`,

  "user-defined-integer-literal": `user-defined-integer-literal:
    decimal-literal ud-suffix
    octal-literal ud-suffix
    hexadecimal-literal ud-suffix
    binary-literal ud-suffix`,

  "user-defined-floating-point-literal": `user-defined-floating-point-literal:
    fractional-constant exponent-part_opt ud-suffix
    digit-sequence exponent-part ud-suffix
    hexadecimal-prefix hexadecimal-fractional-constant binary-exponent-part ud-suffix
    hexadecimal-prefix hexadecimal-digit-sequence binary-exponent-part ud-suffix`,

  "user-defined-string-literal": `user-defined-string-literal:
    string-literal ud-suffix`,

  "user-defined-character-literal": `user-defined-character-literal:
    character-literal ud-suffix`,

  "ud-suffix": `ud-suffix:
    identifier`,

  // ===== A.4 Basics [gram.basic] =====

  "translation-unit": `translation-unit:
    declaration-seq_opt
    global-module-fragment_opt module-declaration declaration-seq_opt private-module-fragment_opt`,

  // ===== A.5 Expressions [gram.expr] =====

  "primary-expression": `primary-expression:
    literal
    this
    ( expression )
    id-expression
    lambda-expression
    fold-expression
    requires-expression`,

  "id-expression": `id-expression:
    unqualified-id
    qualified-id`,

  "unqualified-id": `unqualified-id:
    identifier
    operator-function-id
    conversion-function-id
    literal-operator-id
    ~ type-name
    ~ decltype-specifier
    template-id`,

  "qualified-id": `qualified-id:
    nested-name-specifier template_opt unqualified-id`,

  "nested-name-specifier": `nested-name-specifier:
    ::
    type-name ::
    namespace-name ::
    decltype-specifier ::
    nested-name-specifier identifier ::
    nested-name-specifier template_opt simple-template-id ::`,

  "lambda-expression": `lambda-expression:
    lambda-introducer attribute-specifier-seq_opt lambda-declarator compound-statement
    lambda-introducer < template-parameter-list > requires-clause_opt attribute-specifier-seq_opt
        lambda-declarator compound-statement`,

  "lambda-introducer": `lambda-introducer:
    [ lambda-capture_opt ]`,

  "lambda-declarator": `lambda-declarator:
    lambda-specifier-seq noexcept-specifier_opt attribute-specifier-seq_opt trailing-return-type_opt
    noexcept-specifier attribute-specifier-seq_opt trailing-return-type_opt
    trailing-return-type_opt
    ( parameter-declaration-clause ) lambda-specifier-seq_opt noexcept-specifier_opt
        attribute-specifier-seq_opt trailing-return-type_opt requires-clause_opt`,

  "lambda-specifier": `lambda-specifier:
    consteval
    constexpr
    mutable
    static`,

  "lambda-specifier-seq": `lambda-specifier-seq:
    lambda-specifier
    lambda-specifier lambda-specifier-seq`,

  "lambda-capture": `lambda-capture:
    capture-default
    capture-list
    capture-default , capture-list`,

  "capture-default": `capture-default:
    &
    =`,

  "capture-list": `capture-list:
    capture
    capture-list , capture`,

  "capture": `capture:
    simple-capture
    init-capture`,

  "simple-capture": `simple-capture:
    identifier ..._opt
    & identifier ..._opt
    this
    * this`,

  "init-capture": `init-capture:
    ..._opt identifier initializer
    & ..._opt identifier initializer`,

  "fold-expression": `fold-expression:
    ( cast-expression fold-operator ... )
    ( ... fold-operator cast-expression )
    ( cast-expression fold-operator ... fold-operator cast-expression )`,

  "fold-operator": `fold-operator: one of
    + - * / % ^ & | << >>
    += -= *= /= %= ^= &= |= <<= >>= =
    == != < > <= >= && || , .* ->*`,

  "requires-expression": `requires-expression:
    requires requirement-parameter-list_opt requirement-body`,

  "requirement-parameter-list": `requirement-parameter-list:
    ( parameter-declaration-clause )`,

  "requirement-body": `requirement-body:
    { requirement-seq }`,

  "requirement-seq": `requirement-seq:
    requirement
    requirement requirement-seq`,

  "requirement": `requirement:
    simple-requirement
    type-requirement
    compound-requirement
    nested-requirement`,

  "simple-requirement": `simple-requirement:
    expression ;`,

  "type-requirement": `type-requirement:
    typename nested-name-specifier_opt type-name ;`,

  "compound-requirement": `compound-requirement:
    { expression } noexcept_opt return-type-requirement_opt ;`,

  "return-type-requirement": `return-type-requirement:
    -> type-constraint`,

  "nested-requirement": `nested-requirement:
    requires constraint-expression ;`,

  "postfix-expression": `postfix-expression:
    primary-expression
    postfix-expression [ expression-list_opt ]
    postfix-expression ( expression-list_opt )
    simple-type-specifier ( expression-list_opt )
    typename-specifier ( expression-list_opt )
    simple-type-specifier braced-init-list
    typename-specifier braced-init-list
    postfix-expression . template_opt id-expression
    postfix-expression -> template_opt id-expression
    postfix-expression ++
    postfix-expression --
    dynamic_cast < type-id > ( expression )
    static_cast < type-id > ( expression )
    reinterpret_cast < type-id > ( expression )
    const_cast < type-id > ( expression )
    typeid ( expression )
    typeid ( type-id )`,

  "expression-list": `expression-list:
    initializer-list`,

  "unary-expression": `unary-expression:
    postfix-expression
    unary-operator cast-expression
    ++ cast-expression
    -- cast-expression
    await-expression
    sizeof unary-expression
    sizeof ( type-id )
    sizeof ... ( identifier )
    alignof ( type-id )
    noexcept-expression
    new-expression
    delete-expression`,

  "unary-operator": `unary-operator: one of
    * & + - ! ~`,

  "await-expression": `await-expression:
    co_await cast-expression`,

  "noexcept-expression": `noexcept-expression:
    noexcept ( expression )`,

  "new-expression": `new-expression:
    ::_opt new new-placement_opt new-type-id new-initializer_opt
    ::_opt new new-placement_opt ( type-id ) new-initializer_opt`,

  "new-placement": `new-placement:
    ( expression-list )`,

  "new-type-id": `new-type-id:
    type-specifier-seq new-declarator_opt`,

  "new-declarator": `new-declarator:
    ptr-operator new-declarator_opt
    noptr-new-declarator`,

  "noptr-new-declarator": `noptr-new-declarator:
    [ expression_opt ] attribute-specifier-seq_opt
    noptr-new-declarator [ constant-expression ] attribute-specifier-seq_opt`,

  "new-initializer": `new-initializer:
    ( expression-list_opt )
    braced-init-list`,

  "delete-expression": `delete-expression:
    ::_opt delete cast-expression
    ::_opt delete [ ] cast-expression`,

  "cast-expression": `cast-expression:
    unary-expression
    ( type-id ) cast-expression`,

  "pm-expression": `pm-expression:
    cast-expression
    pm-expression .* cast-expression
    pm-expression ->* cast-expression`,

  "multiplicative-expression": `multiplicative-expression:
    pm-expression
    multiplicative-expression * pm-expression
    multiplicative-expression / pm-expression
    multiplicative-expression % pm-expression`,

  "additive-expression": `additive-expression:
    multiplicative-expression
    additive-expression + multiplicative-expression
    additive-expression - multiplicative-expression`,

  "shift-expression": `shift-expression:
    additive-expression
    shift-expression << additive-expression
    shift-expression >> additive-expression`,

  "compare-expression": `compare-expression:
    shift-expression
    compare-expression <=> shift-expression`,

  "relational-expression": `relational-expression:
    compare-expression
    relational-expression < compare-expression
    relational-expression > compare-expression
    relational-expression <= compare-expression
    relational-expression >= compare-expression`,

  "equality-expression": `equality-expression:
    relational-expression
    equality-expression == relational-expression
    equality-expression != relational-expression`,

  "and-expression": `and-expression:
    equality-expression
    and-expression & equality-expression`,

  "exclusive-or-expression": `exclusive-or-expression:
    and-expression
    exclusive-or-expression ^ and-expression`,

  "inclusive-or-expression": `inclusive-or-expression:
    exclusive-or-expression
    inclusive-or-expression | exclusive-or-expression`,

  "logical-and-expression": `logical-and-expression:
    inclusive-or-expression
    logical-and-expression && inclusive-or-expression`,

  "logical-or-expression": `logical-or-expression:
    logical-and-expression
    logical-or-expression || logical-and-expression`,

  "conditional-expression": `conditional-expression:
    logical-or-expression
    logical-or-expression ? expression : assignment-expression`,

  "yield-expression": `yield-expression:
    co_yield assignment-expression
    co_yield braced-init-list`,

  "throw-expression": `throw-expression:
    throw assignment-expression_opt`,

  "assignment-expression": `assignment-expression:
    conditional-expression
    yield-expression
    throw-expression
    logical-or-expression assignment-operator initializer-clause`,

  "assignment-operator": `assignment-operator: one of
    = *= /= %= += -= >>= <<= &= ^= |=`,

  "expression": `expression:
    assignment-expression
    expression , assignment-expression`,

  "constant-expression": `constant-expression:
    conditional-expression`,

  // ===== A.6 Statements [gram.stmt] =====

  "statement": `statement:
    labeled-statement
    attribute-specifier-seq_opt expression-statement
    attribute-specifier-seq_opt compound-statement
    attribute-specifier-seq_opt selection-statement
    attribute-specifier-seq_opt iteration-statement
    attribute-specifier-seq_opt jump-statement
    declaration-statement
    attribute-specifier-seq_opt try-block`,

  "init-statement": `init-statement:
    expression-statement
    simple-declaration
    alias-declaration`,

  "condition": `condition:
    expression
    attribute-specifier-seq_opt decl-specifier-seq declarator brace-or-equal-initializer`,

  "label": `label:
    attribute-specifier-seq_opt identifier :
    attribute-specifier-seq_opt case constant-expression :
    attribute-specifier-seq_opt default :`,

  "labeled-statement": `labeled-statement:
    label statement`,

  "expression-statement": `expression-statement:
    expression_opt ;`,

  "compound-statement": `compound-statement:
    { statement-seq_opt label-seq_opt }`,

  "statement-seq": `statement-seq:
    statement
    statement-seq statement`,

  "label-seq": `label-seq:
    label
    label-seq label`,

  "selection-statement": `selection-statement:
    if constexpr_opt ( init-statement_opt condition ) statement
    if constexpr_opt ( init-statement_opt condition ) statement else statement
    if !_opt consteval compound-statement
    if !_opt consteval compound-statement else statement
    switch ( init-statement_opt condition ) statement`,

  "iteration-statement": `iteration-statement:
    while ( condition ) statement
    do statement while ( expression ) ;
    for ( init-statement condition_opt ; expression_opt ) statement
    for ( init-statement_opt for-range-declaration : for-range-initializer ) statement`,

  "for-range-declaration": `for-range-declaration:
    attribute-specifier-seq_opt decl-specifier-seq declarator
    attribute-specifier-seq_opt decl-specifier-seq ref-qualifier_opt [ identifier-list ]`,

  "for-range-initializer": `for-range-initializer:
    expr-or-braced-init-list`,

  "jump-statement": `jump-statement:
    break ;
    continue ;
    return expr-or-braced-init-list_opt ;
    coroutine-return-statement
    goto identifier ;`,

  "coroutine-return-statement": `coroutine-return-statement:
    co_return expr-or-braced-init-list_opt ;`,

  "declaration-statement": `declaration-statement:
    block-declaration`,

  // ===== A.7 Declarations [gram.dcl] =====

  "declaration-seq": `declaration-seq:
    declaration
    declaration-seq declaration`,

  "declaration": `declaration:
    name-declaration
    special-declaration`,

  "name-declaration": `name-declaration:
    block-declaration
    nodeclspec-function-declaration
    function-definition
    template-declaration
    deduction-guide
    linkage-specification
    namespace-definition
    empty-declaration
    attribute-declaration
    module-import-declaration`,

  "special-declaration": `special-declaration:
    explicit-instantiation
    explicit-specialization
    export-declaration`,

  "block-declaration": `block-declaration:
    simple-declaration
    asm-declaration
    namespace-alias-definition
    using-declaration
    using-enum-declaration
    using-directive
    static_assert-declaration
    alias-declaration
    opaque-enum-declaration`,

  "nodeclspec-function-declaration": `nodeclspec-function-declaration:
    attribute-specifier-seq_opt declarator ;`,

  "alias-declaration": `alias-declaration:
    using identifier attribute-specifier-seq_opt = defining-type-id ;`,

  "simple-declaration": `simple-declaration:
    decl-specifier-seq init-declarator-list_opt ;
    attribute-specifier-seq decl-specifier-seq init-declarator-list ;
    attribute-specifier-seq_opt decl-specifier-seq ref-qualifier_opt [ identifier-list ] initializer ;`,

  "static_assert-declaration": `static_assert-declaration:
    static_assert ( constant-expression ) ;
    static_assert ( constant-expression , string-literal ) ;`,

  "empty-declaration": `empty-declaration:
    ;`,

  "attribute-declaration": `attribute-declaration:
    attribute-specifier-seq ;`,

  "decl-specifier": `decl-specifier:
    storage-class-specifier
    defining-type-specifier
    function-specifier
    friend
    typedef
    constexpr
    consteval
    constinit
    inline`,

  "decl-specifier-seq": `decl-specifier-seq:
    decl-specifier attribute-specifier-seq_opt
    decl-specifier decl-specifier-seq`,

  "storage-class-specifier": `storage-class-specifier:
    static
    thread_local
    extern
    mutable`,

  "function-specifier": `function-specifier:
    virtual
    explicit-specifier`,

  "explicit-specifier": `explicit-specifier:
    explicit ( constant-expression )
    explicit`,

  "type-specifier": `type-specifier:
    simple-type-specifier
    elaborated-type-specifier
    typename-specifier
    cv-qualifier`,

  "type-specifier-seq": `type-specifier-seq:
    type-specifier attribute-specifier-seq_opt
    type-specifier type-specifier-seq`,

  "defining-type-specifier": `defining-type-specifier:
    type-specifier
    class-specifier
    enum-specifier`,

  "defining-type-specifier-seq": `defining-type-specifier-seq:
    defining-type-specifier attribute-specifier-seq_opt
    defining-type-specifier defining-type-specifier-seq`,

  "simple-type-specifier": `simple-type-specifier:
    nested-name-specifier_opt type-name
    nested-name-specifier template simple-template-id
    decltype-specifier
    placeholder-type-specifier
    nested-name-specifier_opt template-name
    char
    char8_t
    char16_t
    char32_t
    wchar_t
    bool
    short
    int
    long
    signed
    unsigned
    float
    double
    void`,

  "type-name": `type-name:
    class-name
    enum-name
    typedef-name`,

  "elaborated-type-specifier": `elaborated-type-specifier:
    class-key attribute-specifier-seq_opt nested-name-specifier_opt identifier
    class-key simple-template-id
    class-key nested-name-specifier template_opt simple-template-id
    enum nested-name-specifier_opt identifier`,

  "decltype-specifier": `decltype-specifier:
    decltype ( expression )`,

  "placeholder-type-specifier": `placeholder-type-specifier:
    type-constraint_opt auto
    type-constraint_opt decltype ( auto )`,

  "init-declarator-list": `init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator`,

  "init-declarator": `init-declarator:
    declarator initializer_opt
    declarator requires-clause`,

  "declarator": `declarator:
    ptr-declarator
    noptr-declarator parameters-and-qualifiers trailing-return-type`,

  "ptr-declarator": `ptr-declarator:
    noptr-declarator
    ptr-operator ptr-declarator`,

  "noptr-declarator": `noptr-declarator:
    declarator-id attribute-specifier-seq_opt
    noptr-declarator parameters-and-qualifiers
    noptr-declarator [ constant-expression_opt ] attribute-specifier-seq_opt
    ( ptr-declarator )`,

  "parameters-and-qualifiers": `parameters-and-qualifiers:
    ( parameter-declaration-clause ) cv-qualifier-seq_opt
        ref-qualifier_opt noexcept-specifier_opt attribute-specifier-seq_opt`,

  "trailing-return-type": `trailing-return-type:
    -> type-id`,

  "ptr-operator": `ptr-operator:
    * attribute-specifier-seq_opt cv-qualifier-seq_opt
    & attribute-specifier-seq_opt
    && attribute-specifier-seq_opt
    nested-name-specifier * attribute-specifier-seq_opt cv-qualifier-seq_opt`,

  "cv-qualifier-seq": `cv-qualifier-seq:
    cv-qualifier cv-qualifier-seq_opt`,

  "cv-qualifier": `cv-qualifier:
    const
    volatile`,

  "ref-qualifier": `ref-qualifier:
    &
    &&`,

  "declarator-id": `declarator-id:
    ..._opt id-expression`,

  "type-id": `type-id:
    type-specifier-seq abstract-declarator_opt`,

  "defining-type-id": `defining-type-id:
    defining-type-specifier-seq abstract-declarator_opt`,

  "abstract-declarator": `abstract-declarator:
    ptr-abstract-declarator
    noptr-abstract-declarator_opt parameters-and-qualifiers trailing-return-type
    abstract-pack-declarator`,

  "ptr-abstract-declarator": `ptr-abstract-declarator:
    noptr-abstract-declarator
    ptr-operator ptr-abstract-declarator_opt`,

  "noptr-abstract-declarator": `noptr-abstract-declarator:
    noptr-abstract-declarator_opt parameters-and-qualifiers
    noptr-abstract-declarator_opt [ constant-expression_opt ] attribute-specifier-seq_opt
    ( ptr-abstract-declarator )`,

  "abstract-pack-declarator": `abstract-pack-declarator:
    noptr-abstract-pack-declarator
    ptr-operator abstract-pack-declarator`,

  "noptr-abstract-pack-declarator": `noptr-abstract-pack-declarator:
    noptr-abstract-pack-declarator parameters-and-qualifiers
    noptr-abstract-pack-declarator [ constant-expression_opt ] attribute-specifier-seq_opt
    ...`,

  "parameter-declaration-clause": `parameter-declaration-clause:
    parameter-declaration-list_opt ..._opt
    parameter-declaration-list , ...`,

  "parameter-declaration-list": `parameter-declaration-list:
    parameter-declaration
    parameter-declaration-list , parameter-declaration`,

  "parameter-declaration": `parameter-declaration:
    attribute-specifier-seq_opt this_opt decl-specifier-seq declarator
    attribute-specifier-seq_opt decl-specifier-seq declarator = initializer-clause
    attribute-specifier-seq_opt this_opt decl-specifier-seq abstract-declarator_opt
    attribute-specifier-seq_opt decl-specifier-seq abstract-declarator_opt = initializer-clause`,

  "initializer": `initializer:
    brace-or-equal-initializer
    ( expression-list )`,

  "brace-or-equal-initializer": `brace-or-equal-initializer:
    = initializer-clause
    braced-init-list`,

  "initializer-clause": `initializer-clause:
    assignment-expression
    braced-init-list`,

  "braced-init-list": `braced-init-list:
    { initializer-list ,_opt }
    { designated-initializer-list ,_opt }
    { }`,

  "initializer-list": `initializer-list:
    initializer-clause ..._opt
    initializer-list , initializer-clause ..._opt`,

  "designated-initializer-list": `designated-initializer-list:
    designated-initializer-clause
    designated-initializer-list , designated-initializer-clause`,

  "designated-initializer-clause": `designated-initializer-clause:
    designator brace-or-equal-initializer`,

  "designator": `designator:
    . identifier`,

  "expr-or-braced-init-list": `expr-or-braced-init-list:
    expression
    braced-init-list`,

  "function-definition": `function-definition:
    attribute-specifier-seq_opt decl-specifier-seq_opt declarator virt-specifier-seq_opt function-body
    attribute-specifier-seq_opt decl-specifier-seq_opt declarator requires-clause function-body`,

  "function-body": `function-body:
    ctor-initializer_opt compound-statement
    function-try-block
    = default ;
    = delete ;`,

  "enum-specifier": `enum-specifier:
    enum-head { enumerator-list_opt }
    enum-head { enumerator-list , }`,

  "enum-head": `enum-head:
    enum-key attribute-specifier-seq_opt enum-head-name_opt enum-base_opt`,

  "enum-head-name": `enum-head-name:
    nested-name-specifier_opt identifier`,

  "opaque-enum-declaration": `opaque-enum-declaration:
    enum-key attribute-specifier-seq_opt enum-head-name enum-base_opt ;`,

  "enum-key": `enum-key:
    enum
    enum class
    enum struct`,

  "enum-base": `enum-base:
    : type-specifier-seq`,

  "enumerator-list": `enumerator-list:
    enumerator-definition
    enumerator-list , enumerator-definition`,

  "enumerator-definition": `enumerator-definition:
    enumerator
    enumerator = constant-expression`,

  "enumerator": `enumerator:
    identifier attribute-specifier-seq_opt`,

  "using-enum-declaration": `using-enum-declaration:
    using enum using-enum-declarator ;`,

  "using-enum-declarator": `using-enum-declarator:
    nested-name-specifier_opt identifier
    nested-name-specifier_opt simple-template-id`,

  "namespace-definition": `namespace-definition:
    named-namespace-definition
    unnamed-namespace-definition
    nested-namespace-definition`,

  "named-namespace-definition": `named-namespace-definition:
    inline_opt namespace attribute-specifier-seq_opt identifier { namespace-body }`,

  "unnamed-namespace-definition": `unnamed-namespace-definition:
    inline_opt namespace attribute-specifier-seq_opt { namespace-body }`,

  "nested-namespace-definition": `nested-namespace-definition:
    namespace enclosing-namespace-specifier :: inline_opt identifier { namespace-body }`,

  "enclosing-namespace-specifier": `enclosing-namespace-specifier:
    identifier
    enclosing-namespace-specifier :: inline_opt identifier`,

  "namespace-body": `namespace-body:
    declaration-seq_opt`,

  "namespace-alias-definition": `namespace-alias-definition:
    namespace identifier = qualified-namespace-specifier ;`,

  "qualified-namespace-specifier": `qualified-namespace-specifier:
    nested-name-specifier_opt namespace-name`,

  "using-directive": `using-directive:
    attribute-specifier-seq_opt using namespace nested-name-specifier_opt namespace-name ;`,

  "using-declaration": `using-declaration:
    using using-declarator-list ;`,

  "using-declarator-list": `using-declarator-list:
    using-declarator ..._opt
    using-declarator-list , using-declarator ..._opt`,

  "using-declarator": `using-declarator:
    typename_opt nested-name-specifier unqualified-id`,

  "asm-declaration": `asm-declaration:
    attribute-specifier-seq_opt asm ( string-literal ) ;`,

  "linkage-specification": `linkage-specification:
    extern string-literal { declaration-seq_opt }
    extern string-literal name-declaration`,

  "attribute-specifier-seq": `attribute-specifier-seq:
    attribute-specifier-seq_opt attribute-specifier`,

  "attribute-specifier": `attribute-specifier:
    [ [ attribute-using-prefix_opt attribute-list ] ]
    alignment-specifier`,

  "alignment-specifier": `alignment-specifier:
    alignas ( type-id ..._opt )
    alignas ( constant-expression ..._opt )`,

  "attribute-using-prefix": `attribute-using-prefix:
    using attribute-namespace :`,

  "attribute-list": `attribute-list:
    attribute_opt
    attribute-list , attribute_opt
    attribute ...
    attribute-list , attribute ...`,

  "attribute": `attribute:
    attribute-token attribute-argument-clause_opt`,

  "attribute-token": `attribute-token:
    identifier
    attribute-scoped-token`,

  "attribute-scoped-token": `attribute-scoped-token:
    attribute-namespace :: identifier`,

  "attribute-namespace": `attribute-namespace:
    identifier`,

  "attribute-argument-clause": `attribute-argument-clause:
    ( balanced-token-seq_opt )`,

  "balanced-token-seq": `balanced-token-seq:
    balanced-token
    balanced-token-seq balanced-token`,

  "balanced-token": `balanced-token:
    ( balanced-token-seq_opt )
    [ balanced-token-seq_opt ]
    { balanced-token-seq_opt }
    any token other than a parenthesis, a bracket, or a brace`,

  // ===== A.8 Modules [gram.module] =====

  "module-declaration": `module-declaration:
    export-keyword_opt module-keyword module-name module-partition_opt attribute-specifier-seq_opt ;`,

  "module-name": `module-name:
    module-name-qualifier_opt identifier`,

  "module-partition": `module-partition:
    : module-name-qualifier_opt identifier`,

  "module-name-qualifier": `module-name-qualifier:
    identifier .
    module-name-qualifier identifier .`,

  "export-declaration": `export-declaration:
    export name-declaration
    export { declaration-seq_opt }
    export-keyword module-import-declaration`,

  "module-import-declaration": `module-import-declaration:
    import-keyword module-name attribute-specifier-seq_opt ;
    import-keyword module-partition attribute-specifier-seq_opt ;
    import-keyword header-name attribute-specifier-seq_opt ;`,

  "global-module-fragment": `global-module-fragment:
    module-keyword ; declaration-seq_opt`,

  "private-module-fragment": `private-module-fragment:
    module-keyword : private ; declaration-seq_opt`,

  // ===== A.9 Classes [gram.class] =====

  "class-specifier": `class-specifier:
    class-head { member-specification_opt }`,

  "class-head": `class-head:
    class-key attribute-specifier-seq_opt class-head-name class-virt-specifier_opt base-clause_opt
    class-key attribute-specifier-seq_opt base-clause_opt`,

  "class-head-name": `class-head-name:
    nested-name-specifier_opt class-name`,

  "class-virt-specifier": `class-virt-specifier:
    final`,

  "class-key": `class-key:
    class
    struct
    union`,

  "member-specification": `member-specification:
    member-declaration member-specification_opt
    access-specifier : member-specification_opt`,

  "member-declaration": `member-declaration:
    attribute-specifier-seq_opt decl-specifier-seq_opt member-declarator-list_opt ;
    function-definition
    using-declaration
    using-enum-declaration
    static_assert-declaration
    template-declaration
    explicit-specialization
    deduction-guide
    alias-declaration
    opaque-enum-declaration
    empty-declaration`,

  "member-declarator-list": `member-declarator-list:
    member-declarator
    member-declarator-list , member-declarator`,

  "member-declarator": `member-declarator:
    declarator virt-specifier-seq_opt pure-specifier_opt
    declarator requires-clause
    declarator brace-or-equal-initializer_opt
    identifier_opt attribute-specifier-seq_opt : constant-expression brace-or-equal-initializer_opt`,

  "virt-specifier-seq": `virt-specifier-seq:
    virt-specifier
    virt-specifier-seq virt-specifier`,

  "virt-specifier": `virt-specifier:
    override
    final`,

  "pure-specifier": `pure-specifier:
    = 0`,

  "conversion-function-id": `conversion-function-id:
    operator conversion-type-id`,

  "conversion-type-id": `conversion-type-id:
    type-specifier-seq conversion-declarator_opt`,

  "conversion-declarator": `conversion-declarator:
    ptr-operator conversion-declarator_opt`,

  "base-clause": `base-clause:
    : base-specifier-list`,

  "base-specifier-list": `base-specifier-list:
    base-specifier ..._opt
    base-specifier-list , base-specifier ..._opt`,

  "base-specifier": `base-specifier:
    attribute-specifier-seq_opt class-or-decltype
    attribute-specifier-seq_opt virtual access-specifier_opt class-or-decltype
    attribute-specifier-seq_opt access-specifier virtual_opt class-or-decltype`,

  "class-or-decltype": `class-or-decltype:
    nested-name-specifier_opt type-name
    nested-name-specifier template simple-template-id
    decltype-specifier`,

  "access-specifier": `access-specifier:
    private
    protected
    public`,

  "ctor-initializer": `ctor-initializer:
    : mem-initializer-list`,

  "mem-initializer-list": `mem-initializer-list:
    mem-initializer ..._opt
    mem-initializer-list , mem-initializer ..._opt`,

  "mem-initializer": `mem-initializer:
    mem-initializer-id ( expression-list_opt )
    mem-initializer-id braced-init-list`,

  "mem-initializer-id": `mem-initializer-id:
    class-or-decltype
    identifier`,

  // ===== A.10 Overloading [gram.over] =====

  "operator-function-id": `operator-function-id:
    operator operator`,

  "operator": `operator: one of
    new delete new[] delete[] co_await ( ) [ ] -> ->*
    ~ ! + - * / % ^ &
    | = += -= *= /= %= ^= &=
    |= == != < > <= >= <=> &&
    || << >> <<= >>= ++ -- ,`,

  "literal-operator-id": `literal-operator-id:
    operator string-literal identifier
    operator user-defined-string-literal`,

  // ===== A.11 Templates [gram.temp] =====

  "template-declaration": `template-declaration:
    template-head declaration
    template-head concept-definition`,

  "template-head": `template-head:
    template < template-parameter-list > requires-clause_opt`,

  "template-parameter-list": `template-parameter-list:
    template-parameter
    template-parameter-list , template-parameter`,

  "requires-clause": `requires-clause:
    requires constraint-logical-or-expression`,

  "constraint-logical-or-expression": `constraint-logical-or-expression:
    constraint-logical-and-expression
    constraint-logical-or-expression || constraint-logical-and-expression`,

  "constraint-logical-and-expression": `constraint-logical-and-expression:
    primary-expression
    constraint-logical-and-expression && primary-expression`,

  "template-parameter": `template-parameter:
    type-parameter
    parameter-declaration`,

  "type-parameter": `type-parameter:
    type-parameter-key ..._opt identifier_opt
    type-parameter-key identifier_opt = type-id
    type-constraint ..._opt identifier_opt
    type-constraint identifier_opt = type-id
    template-head type-parameter-key ..._opt identifier_opt
    template-head type-parameter-key identifier_opt = id-expression`,

  "type-parameter-key": `type-parameter-key:
    class
    typename`,

  "type-constraint": `type-constraint:
    nested-name-specifier_opt concept-name
    nested-name-specifier_opt concept-name < template-argument-list_opt >`,

  "simple-template-id": `simple-template-id:
    template-name < template-argument-list_opt >`,

  "template-id": `template-id:
    simple-template-id
    operator-function-id < template-argument-list_opt >
    literal-operator-id < template-argument-list_opt >`,

  "template-argument-list": `template-argument-list:
    template-argument ..._opt
    template-argument-list , template-argument ..._opt`,

  "template-argument": `template-argument:
    constant-expression
    type-id
    id-expression`,

  "constraint-expression": `constraint-expression:
    logical-or-expression`,

  "deduction-guide": `deduction-guide:
    explicit-specifier_opt template-name ( parameter-declaration-clause ) -> simple-template-id ;`,

  "concept-definition": `concept-definition:
    concept concept-name attribute-specifier-seq_opt = constraint-expression ;`,

  "concept-name": `concept-name:
    identifier`,

  "typename-specifier": `typename-specifier:
    typename nested-name-specifier identifier
    typename nested-name-specifier template_opt simple-template-id`,

  "explicit-instantiation": `explicit-instantiation:
    extern_opt template declaration`,

  "explicit-specialization": `explicit-specialization:
    template < > declaration`,

  // ===== A.12 Exception handling [gram.except] =====

  "try-block": `try-block:
    try compound-statement handler-seq`,

  "function-try-block": `function-try-block:
    try ctor-initializer_opt compound-statement handler-seq`,

  "handler-seq": `handler-seq:
    handler handler-seq_opt`,

  "handler": `handler:
    catch ( exception-declaration ) compound-statement`,

  "exception-declaration": `exception-declaration:
    attribute-specifier-seq_opt type-specifier-seq declarator
    attribute-specifier-seq_opt type-specifier-seq abstract-declarator_opt
    ...`,

  "noexcept-specifier": `noexcept-specifier:
    noexcept ( constant-expression )
    noexcept`,

  // ===== A.13 Preprocessing directives [gram.cpp] =====

  "preprocessing-file": `preprocessing-file:
    group_opt
    module-file`,

  "module-file": `module-file:
    pp-global-module-fragment_opt pp-module group_opt pp-private-module-fragment_opt`,

  "pp-global-module-fragment": `pp-global-module-fragment:
    module ; new-line group_opt`,

  "pp-private-module-fragment": `pp-private-module-fragment:
    module : private ; new-line group_opt`,

  "group": `group:
    group-part
    group group-part`,

  "group-part": `group-part:
    control-line
    if-section
    text-line
    # conditionally-supported-directive`,

  "control-line": `control-line:
    # include pp-tokens new-line
    pp-import
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

  "text-line": `text-line:
    pp-tokens_opt new-line`,

  "conditionally-supported-directive": `conditionally-supported-directive:
    pp-tokens new-line`,

  "lparen": `lparen:
    a ( character not immediately preceded by whitespace`,

  "identifier-list": `identifier-list:
    identifier
    identifier-list , identifier`,

  "replacement-list": `replacement-list:
    pp-tokens_opt`,

  "pp-tokens": `pp-tokens:
    preprocessing-token
    pp-tokens preprocessing-token`,

  "new-line": `new-line:
    the new-line character`,

  "defined-macro-expression": `defined-macro-expression:
    defined identifier
    defined ( identifier )`,

  "h-preprocessing-token": `h-preprocessing-token:
    any preprocessing-token other than >`,

  "h-pp-tokens": `h-pp-tokens:
    h-preprocessing-token
    h-pp-tokens h-preprocessing-token`,

  "header-name-tokens": `header-name-tokens:
    string-literal
    < h-pp-tokens >`,

  "has-include-expression": `has-include-expression:
    __has_include ( header-name )
    __has_include ( header-name-tokens )`,

  "has-attribute-expression": `has-attribute-expression:
    __has_cpp_attribute ( pp-tokens )`,

  "pp-module": `pp-module:
    export_opt module pp-tokens_opt ; new-line`,

  "pp-import": `pp-import:
    export_opt import header-name pp-tokens_opt ; new-line
    export_opt import header-name-tokens pp-tokens_opt ; new-line
    export_opt import pp-tokens ; new-line`,

  "va-opt-replacement": `va-opt-replacement:
    __VA_OPT__ ( pp-tokens_opt )`,
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
