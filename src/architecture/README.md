# Architecture

## Overview

Architecture descriptions, cloud reference architectures, architectural decisions, governance artifacts, diagrams, and learning material. The library contains reusable models and templates; it does not designate any template as an approved production architecture.

## Scope and boundaries

Architecture descriptions, ADRs, viewpoints, patterns, and governance belong here. Security operations belong in [Security](../security/README.md); implementation pipelines belong in [DevOps](../devops/README.md). Templates for architecture descriptions are distinct from ADR templates.

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Technical documents](technical-documents/README.md) | Design guides, engineering references and explanatory technical material | 6 |
| [Templates](templates/README.md) | Reusable structured starting points and document forms | 8 |
| [Workbooks and exercises](workbooks/README.md) | Practice, exercises, checklists and worked activities | 5 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [cloud](cloud/) | Cloud concepts, architecture/diagram sets and an engineering suite. | 27 |
| [decisions](decisions/) | Generic and specialized ADR templates with review governance. | 11 |
| [diagrams](diagrams/) | Cross-cutting diagrams and architectural model assets. | 0 |
| [enterprise](enterprise/) | Enterprise architecture, business operations, and IT service management. | 15 |
| [examples](examples/README.md) | Worked architecture examples. | 1 |
| [governance](governance/) | Cloud Center of Excellence artifacts and governance. | 62 |
| [patterns](patterns/README.md) | Reusable architecture patterns. | 5 |
| [standards](standards/) | ISO/IEC/IEEE 42010 architecture-description guidance. | 7 |
| [style system](style-system/) | Architecture styling and documentation standards. | 12 |
| [systems engineering](systems-engineering/README.md) | Systems engineering perspectives. | 1 |
| [togaf](togaf/README.md) | TOGAF material and guidance. | 5 |
| [uml](uml/) | UML notation material and reference diagrams. | 1 |
| [views and beyond](views-and-beyond/) | Viewpoint methodology, style catalogs and view packets. | 37 |


## Build and validate

```bash
make preflight
make build-category-architecture
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Enterprise GitHub Actions architecture discovery

See the [enterprise architecture discovery suite](github-actions-discovery-suite.md) for the uploaded technical reference and its four project-specific Template–Blank pairs: Architecture Description, evidence viewpoint, implementation workbook, and evidence/validation workbook. The Blank copies are printable and contain empty writing lines rather than bracketed prompts. Use separate ADRs for consequential design decisions.

## Recommended navigation

- Begin with the [architecture-description index](architecture-description-index.md) to understand diagram provenance and view/concern traceability.

- Use [ADRs](decisions/readme.md) for trade-offs and decision rationale; use [architecture descriptions](templates/README.md) to express the architecture of an entity of interest; and use [architecture viewpoint specifications](templates/README.md) for reusable conventions that govern views.

- Read the [ADR vs. AD vs. Viewpoint technical handout](technical-documents/adr-ad-viewpoint-governance-handout.tex) for authoritative terminology, lifecycle rules, traceability examples, and a semantic classification of unresolved architecture forms.

- Consult the [CCoE suite](governance/ccoe/readme.md) for governance templates and project-control records.

## Maintenance conventions

- An ADR template is not an accepted decision; sign-off must occur in an adopting project.

- ADRs, ADs and viewpoint specifications are separate artifact families. Reusable forms need a Template and a printable Blank; authoring guides, completed examples and non-standalone source fragments do not receive artificial Blank duplicates.

- Do not confuse a rendered PlantUML diagram with validated UML semantics or standards conformance.

- Keep individual diagrams with their source documents unless they are explicitly shared across projects.

## Related domains

- [Views and Beyond](views-and-beyond/readme.md)

- [Repository source catalog](../README.md)
