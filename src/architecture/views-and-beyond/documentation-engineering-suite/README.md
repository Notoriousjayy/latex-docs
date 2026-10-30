# Software Architecture Documentation and Engineering Suite

A complete, repository-ready collection of original LaTeX engineering materials derived from the concepts and chapter organization of **Paul Clements et al., _Documenting Software Architectures: Views and Beyond_, 2nd edition (2011)**.

## Governance and source provenance

The core categories of module, component-and-connector, and allocation views; view packaging; information beyond views; and documentation review are source-derived. All exercises, worked examples, form designs, scoring rubrics, and cloud / Terraform / CI/CD applications are **original suite extensions**, not quotations or book-prescribed techniques. This suite does **not** claim certification or conformance with an edition of ISO/IEC/IEEE 42010.

## Repository placement

`src/architecture/views-and-beyond/documentation-engineering-suite/<document-type>/<subject>.tex` preserves the domain -> document type convention and avoids needless subject nesting. Each leaf directory contains a README. `viewpoints/` contains viewpoint specifications, which are distinct from the architecture view, ADR, and complete architecture-description form families.

## Artifacts

- `reference/`: comprehensive engineering reference.
- `study-guides/`: Prologue, Chapters 1--11, Epilogue, and modeling appendices.
- `curriculum/`: 12-week prerequisite-based path.
- `viewpoints/`: 6 reusable viewpoint specifications.
- `templates/` and `blanks/`: 9 matching template/printable-blank pairs.
- `workbooks/`: 5 template/blank traceability and decision-analysis pairs.
- `labs/`: 8 hands-on engineering laboratories.
- `scorecards/`: 4 weighted assessment template/blank pairs.
- `shared/`: independent LaTeX style library.

## Build and validation

Requirements: `pdflatex` from a standard TeX Live distribution and Python 3. `latexmk` is optional for individual-document iterative editing.

```bash
make validate
make pdfs
```

`make pdfs` runs isolated parallel builds and writes compiled outputs to `build/` without modifying the source tree. For a quick single-document build:

```bash
cd src/software-architecture/reference
latexmk -pdf -halt-on-error -interaction=nonstopmode -outdir=../../../build Architecture_Documentation_Engineering_Reference.tex
```

The suite validator checks paired document presence, print-blank placeholder rules, and document wrappers. Never remove blank counterparts when renaming or adding a template/workbook/scorecard.

## Intended workflow

1. Read the engineering reference and identify stakeholder concerns.
2. Select the proper viewpoint specifications and views.
3. Create a full architecture description, view records, interface records, and ADRs using templates or blanks.
4. Maintain concern-to-view-to-evidence and cross-view correspondence in the workbooks.
5. Run role-specific reviews and scorecards, then version and publish evidence.

## Avoiding duplication

Record shared context, glossary, rationale, and cross-view associations once in the architecture description. A view refers to these elements by stable IDs. Treat diagrams as primary presentations with required supporting evidence, not as self-sufficient architecture documentation.

## Rights

The source textbook was user supplied for study. This suite contains original commentary, teaching exercises, examples, form layouts and adapted frameworks, not chapters of the book or long excerpts. Do not redistribute the uploaded textbook as part of this suite.

## Integration with latex-docs

This suite extends the established Views and Beyond architecture collection. From the repository root: `make preflight` and `make build-category-architecture`; from this suite directory: `make validate` and `make pdfs`.
