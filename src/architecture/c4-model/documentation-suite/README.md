# C4 Model and Software Architecture Visualization Documentation Suite

## Scope and provenance

Book-aligned technical education for Simon Brown, *The C4 Model: Visualizing Software Architecture* (O'Reilly, 2026), plus an original enterprise documentation operating model. Chapter titles and reading maps follow the user-supplied 2026 text. Original synthesis, exercises, fictional application models, viewpoint specifications, scoring weights, CI practices, security exercises and standards crosswalks are **supplementary engineering practice** and are not attributed to the book.

The accompanying textbook is **not** included. None of these materials claim conformance with ISO/IEC/IEEE 42010:2022, OMG UML 2.5.1, or an organization-specific security certification.

## Why this location

`src/architecture/c4-model/documentation-suite/` follows the repository's domain-first `src/architecture` taxonomy and keeps a coherent teaching suite together. It references existing architecture-description, ADR and viewpoint catalogs rather than redefining them. See `src/architecture/architecture-description-index.md`, `src/architecture/templates/`, `src/architecture/decisions/`, and `src/architecture/views-and-beyond/`.

## Study and implementation order

1. `reference/c4-architecture-visualization-engineering-manual.tex`, `reference/c4-foundations-reference.tex` and `curriculum/prerequisite-curriculum.tex`.
2. `study-guides/chapter-01-...tex` through `chapter-12-...tex`, in book order.
3. `reference/diagram-specification-catalog.tex` and `viewpoints/` selection for stakeholder concerns.
4. `labs/` in numbered order, with original PlantUML examples in `examples/`.
5. `workbooks/` for concern-view-evidence paths and cross-view correspondence.
6. `scorecards/` and `templates/` or `blanks/` for review and acceptance records.

## Model and document type distinctions

- **C4 viewpoint specification** is reusable modeling guidance; a **C4 diagram/view** is system-specific.
- **Architecture description (AD)** is the overall documented architecture evidence package; an **ADR** is one decision rationale. Do not name either interchangeably with a diagram.
- **ISO/IEC/IEEE 42010:2022** governs architecture-description concepts and conformance, not the box palette or a mandatory set of C4 diagrams. Verify normative compliance with the purchased official standard.
- **Views and Beyond** provides module, component-and-connector and allocation viewtype thinking. A C4 diagram can complement these views; equivalence is not automatic.
- **UML** supplies notation/semantics for selected detailed diagrams; PlantUML is a renderer. A valid image is not a validated semantic model.

## Template–Blank contract

Every reusable authoring template under `templates/`, every workbook under `workbooks/`, and every scorecard under `scorecards/` has a same-stem `-template.tex` and `-blank.tex` pair. Printable Blank PDFs omit cover sheets, contain empty bordered writing space and no placeholder tokens such as `[To complete]`, and should never be filled with example data. Templates contain bracketed authoring help.

## Build and validation

From this suite directory:

```bash
python3 validate_suite.py
python3 validate_suite.py --compile
```

The compiler runs each LaTeX root in an isolated scratch directory and retains the generated PDF samples under `build/`. To build a single document:

```bash
cd study-guides
pdflatex -halt-on-error -interaction=nonstopmode chapter-01-a-failure-to-communicate.tex
```

For PlantUML, use the repository **existing pinned renderer and house style**: `make render-plantuml` and `python3 tooling/scripts/plantuml_lint.py` at repository root. The standalone zip does not bundle the private/pinned renderer or the house style files; it is meant for integration into the repository. The `.puml` examples require the existing style system.

## Reference register

- Simon Brown (2026), *The C4 Model: Visualizing Software Architecture*, O'Reilly. Primary attached reading.
- Official C4 definitions and checklist: https://c4model.com/ and https://c4model.com/diagrams/checklist.
- ISO/IEC/IEEE 42010:2022 catalogue: https://www.iso.org/standard/74393.html.
- OMG UML 2.5.1: https://www.omg.org/spec/UML/2.5.1.
- Clements et al., *Documenting Software Architectures: Views and Beyond*, Second Edition (2010/2011).
- C4-PlantUML: https://plantuml-stdlib.github.io/C4-PlantUML/.
- Local repository architecture style: `tooling/plantuml/README.md` and `tooling/styles/plantuml/c4/`.

## Repository integration checklist

Add this directory tree under the existing `src/architecture/` root. Add a link in `src/architecture/README.md` and update `catalog/templates.md`, `catalog/workbooks.md` and `catalog/scorecards.md` via the repository's established catalog generation process. Run `make preflight`, `make build-category-architecture`, canonical PlantUML checks and the new suite validator. Review naming conflicts or duplications before publishing. This suite is maintained in `src/architecture/c4-model/documentation-suite/`; source navigation and catalog generation follow the repository's conventions.
