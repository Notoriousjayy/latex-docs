# Views and Beyond Architecture Documentation

The Views and Beyond methodology for documenting software architecture
(Clements, Bachmann, Bass, Garlan, Ivers, Little, Merson, Nord, Stafford —
2nd ed.). This collection provides a foundation for viewpoint selection, model documentation and cross-view reasoning; it is not by itself a claim of standards conformance.

## Scope

**Belongs here:**
- Foundational explanations of the methodology (`fundamentals/`).
- Advanced topics (`advanced-concepts/`): variation points, spectrum of style specializations, viewpoint templates.
- Framework mappings: how Views and Beyond aligns with DoDAF, ISO 42010, RUP, Rozanski & Woods.
- Style catalogs: per-style documentation with co-located PUML diagrams.

**Does not belong here:**
- Application-domain examples — those go in their owning domain folder (`../../security/`, etc.).
- Tools and CI — see `../../../tooling/` and `../../../.github/`.

## Contents

| Child | Purpose |
|---|---|
| `fundamentals/` | Stakeholder needs, effective diagrams, review across phases, beyond-views. |
| `advanced-concepts/` | Variation points, style specializations, viewpoint template. |
| `framework-mappings/` | Mappings to DoDAF, ISO 42010, RUP, Rozanski & Woods. |
| `style-catalogs/` | Style catalog grouped by viewpoint family (allocation, component-and-connector, module). |
| `view-packets/` | Structured documentation packets and worked view examples. |

## Working sequence

1. Identify stakeholders, system boundaries and architectural concerns.
2. Choose a viewpoint with a corresponding model kind and notation.
3. Document elements, relationships, rationale, assumptions and cross-view correspondences.
4. Connect significant trade-offs to the [ADR template library](../decisions/readme.md) and check the [architecture-description index](../architecture-description-index.md).

## Style-catalog organization

```
style-catalogs/
├── allocation/                       # how software allocates to environment
│   ├── deployment-style/
│   ├── install-style/
│   └── work-assignment-style/
├── component-and-connector/          # runtime component/connector views
│   ├── client-server-style/
│   ├── component-and-connector-views/
│   ├── peer-to-peer-style/
│   ├── pipe-and-filter-style/
│   ├── publish-subscribe-style/
│   ├── service-oriented-architecture-style/
│   └── shared-data-style/
└── module/                           # static decomposition of code units
    ├── aspects-style/
    ├── data-model-style/
    ├── decomposition-style/
    ├── generalization-style/
    ├── layered-style/
    ├── module-views/
    └── uses-style/
```

Each `*-style/` folder contains numbered PUML diagrams and (typically)
one `.tex` document explaining the style.

## Conventions

- PUML files in a numbered series use 2-digit prefixes: `01-…`, `02-…`.
- Each style's `.tex` shares the folder slug: `decomposition-style/decomposition-style.tex`.
- `viewpoint-template.tex` (under `advanced-concepts/`) is the canonical
  starting point for a new style write-up.

## Building

```bash
make preflight
make build-category-architecture
make render-plantuml
```

Compiling a diagram does not verify semantic UML correctness. Review notation and rendered outputs in addition to LaTeX build status.

## Related

- `../readme.md`
- `framework-mappings/mapping-to-iso42010.tex`
- Upstream: *Documenting Software Architectures: Views and Beyond* (2nd ed.).



