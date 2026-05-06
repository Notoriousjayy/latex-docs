# Views and Beyond

The Views and Beyond methodology for documenting software architecture
(Clements, Bachmann, Bass, Garlan, Ivers, Little, Merson, Nord, Stafford —
2nd ed.). This subtree is the spine of the architecture documentation.

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
make build-category-architecture
```

## Related

- `../README.md`
- `framework-mappings/mapping-to-iso42010.tex`
- Upstream: *Documenting Software Architectures: Views and Beyond* (2nd ed.).
