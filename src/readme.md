# Source Catalog

All authored documents live under `src/`, grouped by subject and then by project or artifact type. The folders are **source collections**, not necessarily standalone applications or deployable products. Use the closest domain README for scope and navigation.

## Domains

| Domain | Focus |

|---|---|

| [`architecture/`](architecture/readme.md) | Architecture descriptions, patterns, cloud, governance, ADRs and TOGAF. |

| [`business-analysis/`](business-analysis/readme.md) | BABOK-aligned business analysis and implementation artifacts. |

| [`cornell-notes/`](cornell-notes/README.md) | Chapter-oriented Cornell Notes across technical disciplines. |

| [`data-systems/`](data-systems/readme.md) | AI/ML, networking and event-streaming systems. |

| [`devops/`](devops/readme.md) | Delivery engineering, platform operations, build systems and secrets management. |

| [`documentation/`](documentation/readme.md) | Letterhead and technical-writing templates/guides. |

| [`electronics/`](electronics/readme.md) | Electronic circuits and single-board-computer studies. |

| [`game-development/`](game-development/readme.md) | Game-engine concepts, pipelines, physics and design. |

| [`mathematics/`](mathematics/readme.md) | Algebra, calculus, differential equations, geometry and proofs. |

| [`personal/`](personal/readme.md) | Personal reference sources; review sensitivity before publishing. |

| [`programming/`](programming/readme.md) | Algorithms, compilers, programming languages and systems programming. |

| [`security/`](security/readme.md) | AppSec, cloud security, GHAS, GRC and security standards. |

| [`startups/`](startups/readme.md) | Startup operating plans, security, finance and reusable templates. |

| [`templates/`](templates/) | Shared source templates for architecture artifacts. |

## Find or build a document

Use `make list-roots` to enumerate compilable root documents and `make list-categories` to inspect supported domain names. Root discovery checks for `\documentclass`; helper files without it are not built independently.

```bash
make list-roots
make list-categories
make preflight
make build-category-programming
make publish
```

Ordinary builds default to source-adjacent output; `make publish` stages a complete PDF corpus in `public/pdfs/`. See the [repository README](../README.md) for dependencies, outputs and CI behavior.

## Organizing new material

- Put the document in the most specific existing domain and project directory; avoid creating parallel copies of a topic.

- Prefer source-first LaTeX files with lowercase kebab-case names. Use the appropriate shared semantic module rather than a bespoke visual system.

- Add a project README when a new subtree has multiple deliverables, a non-obvious reading sequence, external dependencies or special validation steps.

- Treat `fundamentals/`, `references/`, `runbooks/`, `study-plans/`, and `templates/` as useful conventions, not mandatory or exhaustive folders.

- Keep diagrams, examples, provenance and related evidence close to the material that owns them. Distinguish project-specific decisions from reusable templates.

## Related

- [Repository overview](../README.md)

- [Architecture Decision Records](architecture/decisions/readme.md)

- [Shared PlantUML system](../tooling/plantuml/README.md)
