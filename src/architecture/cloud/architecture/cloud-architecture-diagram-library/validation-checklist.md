
# Cloud Architecture Diagram Library Validation Checklist

Use this checklist after migration and after diagram-library updates.

## Repository Safety

- [ ] No existing LaTeX documents were moved.
- [ ] No unrelated files were overwritten.
- [ ] `Makefile`, `latexmkrc`, and GitHub Actions workflow files were not changed unless separately reviewed.
- [ ] The imported library exists under `src/architecture/cloud/architecture/cloud-architecture-diagram-library/`.

## Source Integrity

- [ ] `advanced-cloud-architecture-plantuml/` exists.
- [ ] `cloud-arch-plantuml/` exists.
- [ ] `specialized_cloud_architectures_puml/` exists.
- [ ] All expected `.puml` files are present.
- [ ] `advanced-cloud-architecture-plantuml/manifest.csv` is preserved.
- [ ] `cloud-architecture-diagram-library-manifest.csv` was regenerated.

## Rendering

- [ ] PlantUML renders the imported `.puml` files without errors.
- [ ] SVG output exists under `cloud-architecture-diagram-library/svg/`.
- [ ] PNG output exists under `cloud-architecture-diagram-library/png/`.
- [ ] Generated image paths mirror the source collection layout.

## LaTeX Integration

- [ ] `src/architecture/cloud/architecture/cloud-architecture-diagram-library-index.tex` exists.
- [ ] The index document compiles with `pdflatex` or the repository's normal `latexmk` workflow.
- [ ] At least one LaTeX document can reference a rendered diagram using a relative `\includegraphics` path.
- [ ] Existing LaTeX builds still pass.

## Acceptance Criteria

- [ ] The original LaTeX repository structure is preserved.
- [ ] PlantUML diagrams render recursively under the architecture category.
- [ ] Rendered diagrams can be used from LaTeX without absolute paths.
- [ ] README/index documentation explains how to use and maintain the library.
- [ ] No unrelated files are renamed, moved, or deleted.
