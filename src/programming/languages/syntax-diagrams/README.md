# Native Language Grammar and Railroad Diagrams

This suite consolidates grammar content from five upstream language syntax-diagram repositories into the source-first LaTeX documentation library. **No React application, npm dependency, or independent web deployment is imported.** The existing pdfLaTeX and pinned PlantUML pipelines remain authoritative.

## Imported language coverage

| Language | Text productions | Original diagram factories | PDF reference |
|---|---:|---:|---|
| ECMAScript 2025 | 261 | 261 | [ECMAScript](ecmascript-2025-syntax-reference.tex) |
| C++23 | 351 | 351 | [C++](cpp23-syntax-reference.tex) |
| C23 | 96 | 94 | [C](c23-syntax-reference.tex) |
| Java 25 | 253 | 253 | [Java](java-25-syntax-reference.tex) |
| Python 3.14 | 205 | 205 | [Python](python-314-syntax-reference.tex) |
| Total | 1,166 | 1,164 | Five printable references |

Two C23 productions (argument-expression-list and compound-literal) have source text but no upstream diagram factory. The difference is preserved and reported, not silently disguised.

The sixth [Grammar Notation Guide](grammar-notation-guide.tex) discusses BNF, EBNF, PEG and visualization limitations.

## Repository-owned assets

- data: pinned grammar text, exact source revision, rule names, section order and original template literals in JSON.
- data/upstream: original TypeScript grammar factory files archived as inert text for provenance only.
- generated: deterministic LaTeX listing fragments generated from the JSON.
- railroad-samples: illustrative PlantUML EBNF sources. The canonical renderer emits PNG and SVG, but both the **web gallery and PDF documents display PNG**.
- The six standalone LaTeX documents are compiled by the existing PDF build.

The existing GitHub Pages publication includes a static PNG gallery at the relative site path /syntax-diagrams/. The gallery is authored as plain HTML by the repository-owned Python staging helper, not by React, Webpack or a second Pages deployment.

## Verification

Run from the repository root:

    python3 tooling/scripts/generate_syntax_references.py --check
    python3 -m unittest -v tests.test_syntax_diagram_collection tests.test_native_syntax_gallery
    make preflight
    make build-category-programming

Regenerate the print fragments after intentional and reviewed changes to source grammar JSON:

    python3 tooling/scripts/generate_syntax_references.py

Render native syntax diagrams through the existing pinned PlantUML engine:

    make render-plantuml

The existing render workflow can publish the resulting PNG files for PDF embedding and for the static GitHub Pages gallery. If any of the five required PNG files is absent or invalid, the gallery staging job fails rather than publishing broken images.

**Visual parity is not yet complete:** all 1,166 grammar texts and 1,164 original factory source registrations are preserved for reference, but the published PNG gallery currently contains five curated native EBNF diagrams, not a picture for every production. Extending this to validated per-production railroad diagrams is further work.

See [source provenance](migration-provenance.md) and [rendering architecture decision](adr-native-grammar-rendering.md).
