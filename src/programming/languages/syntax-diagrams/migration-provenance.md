# Grammar Migration Provenance and Known Limitations

## Pinned inputs

| Original repository | Language | Selected main commit | Text entries | Factories |
|---|---|---|---:|---:|
| [JavaScript-Syntax-diagrams](https://github.com/Notoriousjayy/JavaScript-Syntax-diagrams) | ECMAScript 2025 | 29725abeb6010e9b2bf7669010a0addcd07b32e7 | 261 | 261 |
| [Cpp23-Syntax-diagrams](https://github.com/Notoriousjayy/Cpp23-Syntax-diagrams) | C++23 | b546b5b0c79cbcf304e2232a4e61b871b825b599 | 351 | 351 |
| [c23-syntax-diagrams](https://github.com/Notoriousjayy/c23-syntax-diagrams) | C23 | 11e9a6995e30f3327225d8241c28c5f5d06e7830 | 96 | 94 |
| [java21-syntax-diagrams](https://github.com/Notoriousjayy/java21-syntax-diagrams) | Java 25 | 177088bf881aaca4f0406d90f88d5b04d3ad7c84 | 253 | 253 |
| [Python-syntax-diagrams](https://github.com/Notoriousjayy/Python-syntax-diagrams) | Python 3.14 | d42d1ead4e1cf94149943a4cf8ea79f0dd96eaef | 205 | 205 |

The C++ repository's default branch appeared to be a Dependabot branch. This migration deliberately pinned its main branch instead.

The Java repository's historical name contains java21, but its implementation targets Java 25.

## Source-to-destination map

| Original source | Destination | Status |
|---|---|---|
| Grammar diagram factory module | data/upstream in inert .txt form | Preserved verbatim, non-executable |
| EBNF definitions module | data/*.json | Preserved as literal and decoded text |
| Section registration | data/*.json | Preserved |
| Printable grammar listings | generated/*-rules.tex | Deterministically generated |
| React application and Webpack rendering | None | Explicitly excluded by request |
| Representative native railroad diagram | railroad-samples/*.puml | Five authored native examples |
| Published diagram rendering | Existing PNG pipeline and Pages staging | Uses same existing workflow |
| Language PDF references | Five standalone LaTeX documents | Written for pdfLaTeX |
| Notation guide | grammar-notation-guide.tex | Written for pdfLaTeX |

## Semantics and remaining work

The source modules contain 1,164 registered railroad-diagram factories. **There is no claim that all have been translated into PlantUML diagram sources or rendered PNGs.** The initial migration contains five curated PNG examples. A follow-up effort should author or validate additional native diagrams and verify semantic correspondence before publishing one for every grammar production.

The two C23 text-only rules lacking diagram factories in the source are argument-expression-list and compound-literal. Both remain in the text corpus.

The C23 application itself called its grammar a practical subset. Python's grammar uses PEG ordered choice and semantic operators, which should not be flattened into nominally equivalent EBNF. ECMAScript, C and C++ have contextual and semantic restrictions beyond a syntax diagram.

The imported sources describe MIT licensing in their READMEs; reviewers should independently confirm license notices and correct attribution before redistributing any derivative.

The original repositories are unchanged.
