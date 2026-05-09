# Architecture

Software and enterprise architecture documentation: viewpoint
frameworks, governance, patterns, systems engineering, and TOGAF
adoption material.

## Scope

**Belongs here:**
- Architectural-viewpoint documentation (Views and Beyond, ISO/IEC/IEEE 42010, RUP, DoDAF).
- Enterprise framework material (TOGAF ADM, viewpoint mappings).
- Governance frameworks at the architectural layer (cloud governance, control frameworks).
- Architectural patterns (build-system facades, etc.).

**Does not belong here:**
- AppSec process flows — see `../security/application-security/processes/`.
- CI/CD pipeline details — see `../devops/ci-cd/`.
- Code-level patterns and language idioms — see `../programming/`.

## Contents

| Child | Purpose |
|---|---|
| `governance/` | Cloud governance and control frameworks; Confluence space rationale. |
| `patterns/` | Architectural patterns (build-system facade, etc.). |
| `systems-engineering/` | Systems-engineering perspective on software architecture. |
| `togaf/` | TOGAF ADM user stories and overviews. |
| `views-and-beyond/` | The largest subtree — Views and Beyond methodology, style catalogs, framework mappings. See child README. |
| `diagrams/` | Cross-cutting architecture diagrams not owned by any single document. |

## Conventions

- Diagrams co-locate with the document that owns them, except in
  `diagrams/` (cross-cutting only).
- Style catalogs sit under `views-and-beyond/style-catalogs/<aspect>/<style>-style/`.
- Framework mappings are named `mapping-to-<framework>.tex`.

## Building

```bash
make build-category-architecture
```

## Related

- `../README.md`
- `views-and-beyond/README.md`
- Upstream: *Documenting Software Architectures: Views and Beyond* (Clements et al., 2nd ed.).



