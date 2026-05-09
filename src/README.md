# src/

LaTeX document sources, organized by domain. Every top-level folder is a
domain; within a domain, content is grouped by subdomain or by document
type. The repository builds standalone roots (`.tex` files containing
`\documentclass`); the `Makefile` discovers them automatically.

## Domains

| Folder | Contents |
|---|---|
| `architecture/` | Software & enterprise architecture, Views and Beyond, TOGAF, governance. |
| `data-systems/` | AI/ML, streaming (Kafka), and other data-platform documentation. |
| `devops/` | CI/CD, GitHub Actions, GitOps, platform (k8s, nginx), secrets management. |
| `electronics/` | Self-study electronics (Art of Electronics curriculum). |
| `game-development/` | Game design documents, animation, asset pipelines, physics engines. |
| `mathematics/` | Algebra, calculus, geometry — typeset references and study plans. |
| `personal/` | Personal/finance/gardening reference material. |
| `programming/` | Language references (C/C++, Java, TypeScript) and web/frontend. |
| `security/` | AppSec, GHAS, OWASP, certifications, cloud security, CIS standards. |

## Conventions

- **Naming:** lowercase kebab-case for every folder and file. See
  `RESTRUCTURE-PROPOSAL.md` §6 for the full rules.
- **House style:** every root document loads
  `\usepackage{latex-docs-style}` (resolved via `TEXINPUTS` to
  `tooling/latex/latex-docs-style.sty`).
- **Diagrams:** PlantUML co-locates with the document that owns it.
  Cross-cutting PlantUML config lives in `tooling/plantuml/`.
- **Generated artifacts:** PDFs and LaTeX aux files are git-ignored;
  CI publishes built PDFs under `public/`.

## Building

```bash
make list-roots                       # show every buildable .tex
make build-all                        # serial build of every root
make build-parallel JOBS=8            # parallel build
make build-category-architecture      # one category
```

For a single document, see the parent `README.md` of its folder.

## Document-type taxonomy

Within a domain, when ≥ 2 documents share a type, group them under one of
the following folder names:

| Folder | Use for |
|---|---|
| `fundamentals/` | Introductory and foundational explainers. |
| `references/` | Cheatsheets, indexes, cataloged rules. |
| `runbooks/` | SOPs, triage workflows, playbooks. |
| `study-plans/` | Curricula, ordered user-story sequences. |
| `templates/` | Reusable starting points (not meant to compile alone). |

Singletons live at the domain or subdomain root. The taxonomy is a
convention, not a mandate.

## Related

- `../README.md` — repository top-level README.
- `../tooling/latex/latex-docs-style.sty` — house style.
- `../RESTRUCTURE-PROPOSAL.md` — restructuring rationale.



