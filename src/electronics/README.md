# Electronics and Embedded Hardware

## Overview

Source-first study guides for electronic circuits, experimental learning and single-board computing. These documents are educational references; a described experiment is not evidence of a validated hardware design.

## Scope and boundaries

Electronic circuits, laboratory learning, and embedded hardware integration belong here. Firmware implementation guides belong in [Programming](../programming/README.md); mathematical methods belong in [Mathematics](../mathematics/README.md). This collection is intentionally flat.

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Technical documents](technical-documents/README.md) | Design guides, engineering references and explanatory technical material | 1 |
| [Workbooks and exercises](workbooks/README.md) | Practice, exercises, checklists and worked activities | 1 |
| [Study guides](study-guides/README.md) | Study plans, curricula and guided reading | 1 |


## Recommended navigation

1. Establish a theory baseline with the curriculum.
2. Use the laboratory companion for experimentation; confirm limits and procedures against current device datasheets.
3. Apply circuit and systems concepts to the Orange Pi guide, distinguishing hardware claims from software examples.

## Build and validate

```bash
make preflight
make build-category-electronics
```

Run from the repository root. To collect PDFs under `public/pdfs/`, run `make publish`. A successful LaTeX build does not verify electrical safety or hardware behavior.

## Maintenance conventions

- State voltage, current, grounding, isolation and measurement assumptions for experiments.
- Cite source editions and component datasheets.
- Keep source files in the canonical LaTeX style; avoid duplicating unrelated designs.

## Related domains

[Programming](../programming/README.md) · [Source catalog](../README.md)
