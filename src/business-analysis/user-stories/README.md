# User Stories and Agile Requirements Engineering Documentation Suite

An original, book-grounded LaTeX learning and implementation library based on Mike Cohn's *User Stories Applied: For Agile Software Development* (2004). All chapters are covered by individually authored study guides. The suite combines reusable operating artifacts with a coherent Service Request Portal laboratory case, but it does not reproduce the book's copyrighted chapters.

## Contents

| Directory | Contents |
|---|---|
| `technical-reference/` | Story engineering reference, traceability governance, acceptance-test handbook |
| `study-guides/` | Separate study guides for all 21 chapters |
| `templates/` | Annotated reusable forms with examples and bracketed prompts |
| `blank-forms/` | Matched print-ready, unfilled forms (no example values or bracketed prompts) |
| `workbooks/templates/` | Four instructor/workshop workbooks with examples |
| `workbooks/blank/` | Four genuinely unfilled workbook counterparts |
| `scorecards/templates/` | INVEST, acceptance and backlog quality scorecards, annotated |
| `scorecards/blank/` | Unscored printable counterparts |
| `procedures/` | Five operating procedures with accountable decisions and exit criteria |
| `laboratories/` | Nine exercises including an integrated capstone |
| `curriculum/` | Prerequisite-based 12-module path and chapter-to-operations crosswalk |
| `references/` | Source attribution, historical-vs-new methodology boundary |
| `shared/` | Reusable LaTeX preamble for consistent professional typesetting |

## Quick start

Open `curriculum/prerequisite-based-learning-curriculum.tex` and its chapter crosswalk to choose a learning path. For practical adoption, start with `technical-reference/user-stories-engineering-reference.tex`, then copy any annotated template to learn how it should be completed. Print the matching file in `blank-forms/` or `workbooks/blank/` for an empty working sheet. Do not print an annotated template expecting it to be blank.

**Repository integration:** This collection is indexed in the root discovery catalog. Pair registrations live in `tooling/manifests/reusable-artifact-pairs.json`; the canonical document inventory excludes registered derivative blanks, which are governed separately.

## Build and validate

Use the repository-root build toolchain (not a nested Makefile):

```bash
make preflight
make build-category-business-analysis
python3 tooling/scripts/validate_artifact_pairs.py
```

The standalone LaTeX documents use a local shared preamble and the repository pdfLaTeX runner discovers every document root. Generated PDFs are build artifacts and are not committed as source.

## Naming and template/blank guarantee

Every item in `templates/` has a same-stem `-blank.tex` in `blank-forms/`; every workbook and scorecard has an analogous pair. `-template.tex` or `-workbook-template.tex` contains explanatory text and sample answers. `-blank.tex` or `-workbook-blank.tex` has only field labels, scoring/rating key when necessary, and empty writing areas. No placeholder words in square brackets are printed in blank files.

## Source integrity and limitations

* Core concepts are attributed to the 2004 book, with page locations in study-guide headers.
* Original Service Request Portal examples, Gherkin-style scenarios, traceability metadata, security-control illustrations, and modern workflow patterns are extensions, not represented as quotations or requirements of the book.
* Numbers used in worked forecasts, SLAs and laboratory cases are illustrative and not real-world benchmarks.
* Current Scrum Guide or formal standards conformity is **not** certified by this educational suite.
* The user-provided book PDF is intentionally **not** redistributed within this package.

## Learning deliverable

A successful capstone has a role-goal map, 12-story backlog, meaningful INVEST reviews, vertical slices, relative estimates, two risk-aware release scenarios, at least 12 acceptance examples, an evidence trace graph and a reasoned release acceptance decision. The strength of the evidence matters more than document length.
