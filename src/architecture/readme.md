# Architecture

Architecture descriptions, cloud reference architectures, architectural decisions, governance artifacts, diagrams, and learning material. The library contains reusable models and templates; it does not designate any template as an approved production architecture.

## Explore the collection

| Area | What it contains | Sources |
|---|---|---:|
| [`cloud/`](cloud/) | Cloud concepts, architecture/diagram sets and an engineering suite. | 27 |
| [`decisions/`](decisions/) | Generic and specialized ADR templates with review governance. | 11 |
| [`diagramming/`](diagramming/) | Guides and conventions for architecture diagramming. | 1 |
| [`diagrams/`](diagrams/) | Cross-cutting diagrams and architectural model assets. | 0 |
| [`enterprise/`](enterprise/) | Enterprise architecture, business operations, and IT service management. | 15 |
| [`examples/`](examples/) | Worked architecture examples. | 1 |
| [`governance/`](governance/) | Cloud Center of Excellence artifacts and governance. | 62 |
| [`learning/`](learning/) | Architecture study material and learning roadmaps. | 1 |
| [`patterns/`](patterns/) | Reusable architecture patterns. | 5 |
| [`standards/`](standards/) | ISO/IEC/IEEE 42010 architecture-description guidance. | 7 |
| [`style-system/`](style-system/) | Architecture styling and documentation standards. | 12 |
| [`systems-engineering/`](systems-engineering/) | Systems engineering perspectives. | 1 |
| [`togaf/`](togaf/) | TOGAF material and guidance. | 5 |
| [`uml/`](uml/) | UML notation material and reference diagrams. | 1 |
| [`views-and-beyond/`](views-and-beyond/) | Viewpoint methodology, style catalogs and view packets. | 37 |

## Build and validate

```bash
make preflight
make build-category-architecture
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Using this collection

- Begin with the [architecture-description index](architecture-description-index.md) to understand diagram provenance and view/concern traceability.

- Use [ADRs](decisions/readme.md) for trade-offs and design rationale; use [architecture descriptions](standards/iso-iec-ieee-42010/) for stakeholder concerns, views and correspondences.

- Consult the [CCoE suite](governance/ccoe/readme.md) for governance templates and project-control records.

## Maintenance and scope

- An ADR template is not an accepted decision; sign-off must occur in an adopting project.

- Do not confuse a rendered PlantUML diagram with validated UML semantics or standards conformance.

- Keep individual diagrams with their source documents unless they are explicitly shared across projects.

## Related

- [Views and Beyond](views-and-beyond/readme.md)

- [Repository source catalog](../readme.md)
