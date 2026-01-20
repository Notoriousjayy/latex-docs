# latex-docs

A categorized LaTeX document library organized under `src/` with kebab-case directory naming. The repository is intended to be **source-first**: PDFs and LaTeX build artifacts are generated locally/CI and are not committed.

## Repository layout

High-level structure (illustrative):

- `src/` — all LaTeX sources, grouped by domain (e.g., `security/`, `architecture/`, `devops/`, `data-systems/`, `programming/`, `mathematics/`, `game-development/`, `personal/`, etc.). See `MIGRATION_REPORT.md` for a fuller inventory and rationale.
- `src/common/` — shared helpers (e.g., CI-safe macros).
- `tooling/latex/` — shared preamble/helpers.
- `tooling/scripts/` — utility scripts.
- `.github/workflows/` — CI/publishing workflows:
  - `latex-ci.yml` (build + artifact upload)
  - `latex-pages.yml` (publish PDFs to GitHub Pages)
  - `latex-release.yml` (attach PDFs to tagged releases)

> Note: GitHub Actions only executes workflows placed under `.github/workflows/`. A root-level file like `github-workflows-build-latex.yml` is not active unless moved into `.github/workflows/`.

## Build model (“roots”)

This repo builds **standalone documents** (“roots”) by detecting any `src/**/*.tex` file that contains `\documentclass`. The Makefile automatically discovers these roots and builds them in place (PDFs sit alongside the corresponding `.tex` file under `src/`).

## Building locally

### Prerequisites

Recommended (especially if you use `minted`, extra fonts, or scientific packages):

- `latexmk`
- TeX Live packages commonly needed by the repo (examples used in CI): `texlive-latex-extra`, `texlive-fonts-extra`, `texlive-science`, `biber`, `python3-pygments`

On Ubuntu/Debian, the CI toolchain is a good reference set:
- `latexmk`, `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-fonts-extra`, `texlive-pictures`, `texlive-science`, `texlive-bibtex-extra`, `biber`, `python3-pygments`.

### Common commands

List detected build roots:

```bash
make list-roots
````

Build all detected roots:

```bash
make build-all
```

Clean aux files for all roots (keeps PDFs):

```bash
make clean
```

Remove aux files and PDFs for all roots:

```bash
make distclean
```

### Build one document

From the directory containing a root `.tex` file (the one with `\documentclass`), run:

```bash
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error <root>.tex
```

## CI / publishing

### CI build (artifacts)

Workflow: `.github/workflows/latex-ci.yml`

* Installs a TeX toolchain (incl. fonts/science/biber/pygments).
* Runs `make build-all`.
* Collects PDFs found under `src/` and uploads them as a workflow artifact, preserving the `src/` folder structure.

### GitHub Pages (browse PDFs)

Workflow: `.github/workflows/latex-pages.yml`

* Builds roots and stages PDFs into a `site/` directory.
* Generates a simple HTML index listing PDFs.
* Deploys to GitHub Pages.

### Releases (zip of PDFs)

Workflow: `.github/workflows/latex-release.yml`

* Trigger: push tags matching `v*`
* Builds all roots and packages collected PDFs into `release/latex-pdfs.zip`
* Publishes a GitHub Release and uploads the zip asset.

## Conventions

* Kebab-case directories and filenames (lowercase + hyphens, no spaces).
* Keep document assets (images, etc.) near the document that uses them.
* PDFs and LaTeX build artifacts are intentionally ignored by git (see repo `.gitignore` and related ignore patterns).

## Finding content

If you’re browsing by domain, start under `src/`. If you’re looking for “buildable” documents specifically, prefer:

```bash
make list-roots
```

That list is the authoritative set of standalone PDFs the automation expects to build.