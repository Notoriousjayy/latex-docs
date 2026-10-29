# Source Catalog

## Overview

All authored documents live under `src/`, grouped by subject and then by project or artifact type. The folders are **source collections**, not necessarily standalone applications or deployable products. Use the closest domain README for scope and navigation.

## Scope and boundaries

This catalog describes authored technical sources, not independent products or deployed systems. Choose the **authoritative technical domain** for a source; use cross-links for related readers rather than duplicate files. All immediate domains have a canonical `README.md`.

## Directory map and documentation catalog

| Domain | Focus |

|---|---|

| [`architecture/`](architecture/README.md) | Architecture descriptions, patterns, cloud, governance, ADRs and TOGAF. |

| [`business-analysis/`](business-analysis/README.md) | BABOK-aligned business analysis and implementation artifacts. |

| [`cornell-notes/`](cornell-notes/README.md) | Chapter-oriented Cornell Notes across technical disciplines. |

| [`data-systems/`](data-systems/README.md) | AI/ML, networking and event-streaming systems. |

| [`devops/`](devops/README.md) | Delivery engineering, platform operations, build systems and secrets management. |

| [`documentation/`](documentation/README.md) | Letterhead and technical-writing templates/guides. |

| [`electronics/`](electronics/README.md) | Electronic circuits and single-board-computer studies. |

| [`game-development/`](game-development/README.md) | Game-engine concepts, pipelines, physics and design. |

| [`mathematics/`](mathematics/README.md) | Algebra, calculus, differential equations, geometry and proofs. |

| [`personal/`](personal/README.md) | Personal reference sources; review sensitivity before publishing. |

| [`programming/`](programming/README.md) | Algorithms, compilers, programming languages and systems programming. |

| [`security/`](security/README.md) | AppSec, cloud security, GHAS, GRC and security standards. |

| [`startups/`](startups/README.md) | Startup operating plans, security, finance and reusable templates. |

| [`templates/`](architecture/templates/) | Shared source templates for architecture artifacts. |

## Recommended navigation

Use `make list-roots` to enumerate compilable root documents and `make list-categories` to inspect supported domain names. Root discovery checks for `\documentclass`; helper files without it are not built independently.

```bash
make list-roots
make list-categories
make preflight
make build-category-programming
make publish
```

Ordinary builds default to source-adjacent output; `make publish` stages a complete PDF corpus in `public/pdfs/`. See the [repository README](../README.md) for dependencies, outputs and CI behavior.

## Maintenance conventions

- Put the document in the most specific existing domain and project directory; avoid creating parallel copies of a topic.

- Prefer source-first LaTeX files with lowercase kebab-case names. Use the appropriate shared semantic module rather than a bespoke visual system.

- Add a project README when a new subtree has multiple deliverables, a non-obvious reading sequence, external dependencies or special validation steps.

- Treat `fundamentals/`, `references/`, `runbooks/`, `study-plans/`, and `templates/` as useful conventions, not mandatory or exhaustive folders.

- Keep diagrams, examples, provenance and related evidence close to the material that owns them. Distinguish project-specific decisions from reusable templates.

## Build and validate

From the repository root, use `make preflight`, `make list-roots`, and the appropriate `make build-category-<domain>` target. The source catalog does not itself certify that the complete PDF corpus passed compilation.

## Related domains

- [Repository overview](../README.md)

- [Architecture Decision Records](architecture/decisions/readme.md)

- [Shared PlantUML system](../tooling/plantuml/README.md)
