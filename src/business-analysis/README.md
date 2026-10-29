# Business Analysis

## Overview

BABOK-oriented business-analysis source material and templates. The current collection is organized under `babok/` and emphasizes traceable requirements, analysis activities and stakeholder outcomes.

## Scope and boundaries

Use this domain for requirements elicitation, stakeholder analysis, business processes, and BABOK-oriented artifacts. Architecture decisions belong in [Architecture](../architecture/README.md); operating-business plans belong in [Startups](../startups/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Templates](templates/README.md) | Reusable structured starting points and document forms | 1 |
| [Workbooks and exercises](workbooks/README.md) | Practice, exercises, checklists and worked activities | 1 |
| [Study notes](study-notes/README.md) | Learning notes and subject summaries | 1 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [babok](babok/README.md) | BABOK-related engineering and analysis references. | 5 |


## Build and validate

```bash
make preflight
make build-category-business-analysis
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Recommended navigation

- Begin with the BABOK-oriented reference that matches the analysis activity; connect requirements to architecture decisions, delivery backlog and verification evidence.

- Use the source files as adaptable guidance, not as an assertion that a project has completed the BABOK process.

## Maintenance conventions

- Differentiate stakeholder needs, solution requirements, traceability and acceptance criteria.

- Preserve the source edition and do not misrepresent local interpretations as official certification guidance.

## Related domains

- [Architecture collection](../architecture/README.md)

- [Source catalog](../README.md)
