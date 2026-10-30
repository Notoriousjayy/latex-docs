# LaTeX Documentation Library

A source-controlled engineering documentation library covering software architecture, cybersecurity, DevOps, programming, mathematics, electronics, business operations, and structured learning. **LaTeX source is authoritative**; generated PDFs are build products, not the canonical editing format.

## Start here

| Goal | Entry point |
|---|---|
| Find a topic or project | [Source catalog](src/README.md) |
| Browse reusable templates, workbooks, scorecards or user stories | [Discovery catalog](catalog/README.md) and [Template–Blank pair catalog](catalog/template-blank-pairs.md) |
| Find secure coding standards by language | [Programming language guide](src/programming/languages/README.md) |
| Compare architecture documentation standards and tooling | [Architecture documentation technical reference](src/architecture/technical-documents/architecture-documentation-standards-frameworks-and-tooling.tex) |
| Review architectural choices | [ADR template library](src/architecture/decisions/readme.md) |
| Build enterprise-scale GitHub architecture discovery | [Discovery technical reference and working forms](src/architecture/github-actions-discovery-suite.md) |
| Understand architecture governance | [CCoE governance suite](src/architecture/governance/ccoe/readme.md) |
| Browse structured study notes | [Cornell Notes collections](src/cornell-notes/README.md) |
| Author diagrams consistently | [PlantUML style framework](tooling/plantuml/README.md) |
| Inspect the implementation of the build | [Build helper](tooling/scripts/latex_build.py) and [Makefile](Makefile) |

## Repository map

The [multidimensional discovery catalog](catalog/README.md) provides links by subject, domain and artifact type; it does not duplicate documents. The catalog manifest clearly distinguishes inspected content from provisional path-derived classifications.


`src/` organizes the documents by domain; `tooling/` contains style modules, scripts, and manifests; `tests/` checks build, styles, collections, and diagrams; `.github/workflows/` defines validation, publishing, and release automation. [Browse every domain](src/README.md), including business analysis, startups, and technical writing.

## Quick start

From the repository root, install Python 3, `latexmk`, a pdfLaTeX-capable TeX Live distribution with the packages used by the corpus, Pygments for `minted`, and Java/Graphviz for PlantUML rendering. The CI configuration is the practical reference for a compatible toolchain.

```bash
make help
make list-categories
make list-roots
make preflight
make build-category-architecture
make build-parallel JOBS=4
make render-plantuml
```

Root discovery is based on `.tex` files under `src/` that declare `\documentclass`. Not every `.tex` is a standalone root: included fragments and templates may depend on another document. A category build writes by default beside the source roots; **publishing** explicitly stages PDFs and logs under `public/pdfs/` and `public/logs/`.

### Build and publish commands

| Command | Effect |
|---|---|
| `make preflight` | Check the repository's pdfLaTeX-only policy before compiling. |
| `make build-all` | Compile every discovered root serially. |
| `make build-parallel JOBS=4` | Compile roots concurrently. |
| `make build-category-<domain>` | Build one top-level `src/` domain. |
| `make build-changed BASE_REF=<sha> HEAD_REF=<sha>` | Build roots affected by the specified Git comparison. |
| `make plan PLAN_MODE=changed` | Create a build plan for sharded CI work. |
| `make verify-corpus PLAN=<plan.json>` | Verify published PDF coverage against a plan. |
| `make publish` / `make publish-parallel JOBS=4` | Build and stage a complete PDF corpus under `public/pdfs/`. |
| `make clean` / `make distclean` | Remove build artifacts; `distclean` also removes generated PDFs. |

### Building a single document

The supported helper sets `TEXINPUTS` for both the core house style and the semantic modules, then invokes `latexmk` with `-pdf`, strict error flags and shell escape. Prefer a category/changed build. When invoking `latexmk` manually, provide the required style search paths and an appropriate working directory.

```bash
export TEXINPUTS="$(pwd)/tooling/latex//:$(pwd)/tooling/styles/latex//:${TEXINPUTS:-}"
cd src/architecture/decisions
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error adr-lifecycle-and-review-guide.tex
```

## Authoring standards

- **One semantic module per root.** Load an appropriate concrete package from [`tooling/styles/latex/`](tooling/styles/latex/) (for example, `technical-design-spec` or `cornell-notes`). These inherit the canonical house style in [`tooling/latex/style.sty`](tooling/latex/style.sty).

- **Metadata is explicit.** Use the document title, subtitle, version, status, owner and summary macros supported by the selected module; do not recreate shared title pages, callouts, typography or palette definitions locally.

- **Keep evidence distinct from templates.** Blank ADRs, governance forms and study material are reusable sources; they do not represent approved project decisions, operational evidence or independent certification.

- **Use predictable names and paths.** Prefer lowercase kebab-case for newly authored sources. Preserve intentional legacy paths rather than renaming files during a documentation-only revision.

- **Keep diagrams source-controlled.** Maintain `.puml` beside their owning material where practical. Reuse the [shared PlantUML framework](tooling/plantuml/README.md), validate syntax and review rendered output.

- **Protect provenance and privacy.** The repository is public. Review sensitive, personal, licensed and third-party material before publication; source documents are not automatically public-distribution clearances.

## CI, Pages and releases

| Workflow | Trigger | Purpose |
|---|---|---|
| [LaTeX CI](.github/workflows/latex-ci.yml) | Pull requests affecting sources/tooling; manual dispatch | Validate affected roots through the shared build workflow. |
| [GitHub Pages](.github/workflows/latex-pages.yml) | `main` changes, manual dispatch and weekly scheduled full verification | Build/verify the corpus, stage its PDF and raster artifacts, publish Pages. |
| [LaTeX release](.github/workflows/latex-release.yml) | Published releases; manual dispatch | Reuse a verified matching artifact where available, otherwise rebuild and package PDFs. |

These workflows delegate compilation to [the reusable build workflow](.github/workflows/_build-latex.yml). Only YAML files within `.github/workflows/` run as GitHub Actions workflows; the root-level `github-workflows-build-latex.yml` is not activated automatically. Build success must be confirmed from workflow runs, not inferred from the presence of source files.

## Contributing and quality checks

Before opening a pull request: check the source path, add or update the closest README, verify relative links, document prerequisites, avoid claiming untested builds, and run the relevant tests and checks. For broad source or style changes, run the full build and examine generated PDFs, diagram outputs and build summaries.

```bash
git diff --check
python3 -m unittest discover -s tests
make preflight
make build-category-security
```

**Repository navigation:** [Source index](src/README.md) · [Architecture](src/architecture/README.md) · [Security](src/security/README.md) · [Programming](src/programming/README.md) · [DevOps](src/devops/README.md)

## Agile requirements and user stories

Explore the [User Stories and Agile Requirements Engineering suite](src/business-analysis/user-stories/README.md), with matching template/blank pairs and a chapter-to-operations curriculum.
