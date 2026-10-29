# Electronics and Embedded Hardware

## Overview

Source-first study guides for electronic circuits, experimental learning and single-board computing. These documents are educational references; a described experiment is not evidence of a validated hardware design.

## Scope and boundaries

Electronic circuits, laboratory learning, and embedded hardware integration belong here. Firmware implementation guides belong in [Programming](../programming/README.md); mathematical methods belong in [Mathematics](../mathematics/README.md). This collection is intentionally flat.

## Directory map and documentation catalog

| Source | Purpose |
|---|---|
| [The Art of Electronics curriculum](the-art-of-electronics-curriculum.tex) | Theory and prerequisite-ordered study. |
| [X-Chapters laboratory course](the-art-of-electronics-x-chapters-lab-course.tex) | Hands-on reinforcement and measurement practice. |
| [Orange Pi Zero engineering guide](orange-pi-zero-engineering-guide.tex) | Single-board computing and systems integration. |

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
