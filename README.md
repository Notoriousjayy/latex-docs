# latex-docs

A categorized LaTeX document library organized under `src/` with kebab-case
directory naming. The repository is **source-first**: PDFs and LaTeX build
artifacts are generated locally/CI and are not committed.

All documents share a single canonical house style supplied by
`tooling/latex/latex-docs-style.sty` (loaded as `latex-docs-style`).

---

## Repository layout

- `src/` — all LaTeX sources, grouped by domain (`security/`,
  `architecture/`, `devops/`, `data-systems/`, `programming/`,
  `mathematics/`, `game-development/`, `electronics/`, `personal/`, …).
- `src/common/` — shared helpers (e.g., CI-safe macros).
- `tooling/latex/` — shared style and preamble:
  - `latex-docs-style.sty` — the canonical house style. Every root
    document loads it via `\usepackage{latex-docs-style}` immediately
    after `\documentclass`.
  - `common-preamble.tex` — legacy include retained for backwards
    compatibility.
- `tooling/scripts/` — utility scripts.
- `.github/workflows/` — CI / publishing workflows.

> GitHub Actions only executes workflows placed under
> `.github/workflows/`. A root-level file such as
> `github-workflows-build-latex.yml` is reference material; copy it under
> `.github/workflows/` to activate it.

---

## House style: `latex-docs-style.sty`

`tooling/latex/latex-docs-style.sty` is loaded once per document and owns
every shared concern: page geometry, fonts and microtypography, tables
and lists, the colour palette (Navy / Steel / Teal / Brick over neutral
backgrounds), tcolorbox callouts, hyperlinks, code rendering, and
document metadata. Documents should not redefine these — the
standardiser strips duplicate `\usepackage`, callout-box, and
helper-macro definitions during normalization.

### Public API

#### Metadata (value-emitter macros)

In any document preamble, after `\usepackage{latex-docs-style}`:

```latex
\renewcommand{\DocTitle}{Cloud Governance \& Control Framework}
\renewcommand{\DocSubtitle}{Views \& Beyond Documentation Package}
\renewcommand{\DocVersion}{v0.1}
\renewcommand{\DocStatus}{Draft}
\renewcommand{\DocOwner}{Cloud Platform \& Governance Team}
\renewcommand{\DocAuthor}{Jordan Suber}
\renewcommand{\DocDate}{\today}
\renewcommand{\DocSummary}{One-paragraph statement of purpose.}
```

There are also convenience setters: `\setDocTitle{...}`,
`\setDocVersion{...}`, etc. Either form works.

#### Title block / front matter

```latex
\begin{document}
\makedoctocpage   % renders title block + summary box + ToC + \clearpage
% --- body starts here ---
```

Or, if you only want pieces:

```latex
\makedoctitle      % centred title + subtitle + meta line
\makedocsummary    % "Purpose" box, suppressed when \DocSummary is empty
```

#### Named callouts

The five callout environments are pre-defined; the optional argument is
the title (matching the convention used throughout this repo):

```latex
\begin{notebox}[Discovery Indicators]      ... \end{notebox}
\begin{tipbox}[Key Discovery Point]        ... \end{tipbox}
\begin{warnbox}[Important]                 ... \end{warnbox}
\begin{infobox}[Architectural View Types]  ... \end{infobox}
\begin{viewbox} ... \end{viewbox}          % quiet, no title bar
```

Defaults are sensible: `\begin{notebox}` with no argument titles the box
"Note", and so on.

#### Helper macros

- `\safeincludegraphics[opts]{path}` — silently no-ops if the file is
  missing, so CI does not fail on a sketch in progress.
- `\cmark` / `\xmark` — checkmark / cross glyphs in palette colours.
- `\kbd{Ctrl+C}`, `\filename{config.yaml}`, `\cmd{git rebase}` —
  typeset their arguments in a small monospace face.

#### Code rendering (minted, with safe listings fallback)

The .sty detects `-shell-escape` at runtime.

- **With shell-escape on**, it loads `minted` and Pygments-driven syntax
  highlighting works as usual.
- **Without shell-escape**, it pre-loads `listings` and shims the
  minted API (`\begin{minted}{lang}`, `\mintinline`, `\inputminted`,
  `\setminted`) onto listings so existing source still typesets — just
  without colourised highlighting.

Either way, the document compiles.

---

## Build model

The repository builds **standalone documents** ("roots") — every
`src/**/*.tex` file containing `\documentclass`. The `Makefile`
auto-discovers these and builds each in its own leaf directory (PDFs and
caches sit alongside their source under `src/`).

### TEXINPUTS resolution

Because the Makefile `cd`s into each leaf directory before invoking
`latexmk`, the repo-root `latexmkrc` is **not** auto-loaded. The
Makefile instead exports

```make
TEXINPUTS := $(abspath tooling/latex)//:$(TEXINPUTS)
```

so the shared `latex-docs-style.sty` is found via `kpsewhich`. If you
invoke `latexmk` directly from the repo root, prepend the same path
manually:

```bash
export TEXINPUTS="$(pwd)/tooling/latex//:$TEXINPUTS"
latexmk -pdf -shell-escape -interaction=nonstopmode src/some/path/foo.tex
```

---

## Building locally

### Prerequisites

- `latexmk`
- TeX Live: `texlive-latex-recommended texlive-latex-extra
  texlive-fonts-recommended texlive-fonts-extra texlive-pictures
  texlive-science texlive-bibtex-extra biber python3-pygments`

### Common commands

```bash
make list-roots                       # show every buildable .tex
make list-categories                  # categories with document counts
make build-all                        # serial build of every root
make build-parallel JOBS=8            # parallel build
make build-category-architecture      # one category
make clean                            # drop aux files, keep PDFs
make distclean                        # drop aux files and PDFs
```

### Build one document

```bash
cd src/architecture/governance
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error \
        -file-line-error cloud-governance-control-framework.tex
```

`TEXINPUTS` from the Makefile is inherited if you invoke through `make`;
otherwise export it as shown above.

---

## CI / publishing

### CI build (artifacts) — `.github/workflows/latex-ci.yml`

Installs the TeX toolchain (with fonts/science/biber/pygments), runs
`make build-all`, collects PDFs under `src/`, uploads as a workflow
artifact preserving the `src/` folder structure.

### GitHub Pages — `.github/workflows/latex-pages.yml`

Builds roots, stages PDFs into a `site/` directory, generates an HTML
index, deploys to Pages.

### Releases — `.github/workflows/latex-release.yml`

Trigger: tags matching `v*`. Builds all roots, packages collected PDFs
into `release/latex-pdfs.zip`, publishes a GitHub Release with the zip
attached.

---

## Conventions

- Kebab-case directories and filenames (lowercase + hyphens, no spaces).
- Document assets (images, etc.) live next to the document that uses
  them.
- Every root opens with a standardized banner comment naming the file's
  repo-relative path and the house-style version.
- PDFs and LaTeX build artifacts are git-ignored.

---

## Maintaining the house style

Changes to `tooling/latex/latex-docs-style.sty` must keep ALL existing
documents compiling cleanly under `latexmk -pdf -shell-escape` with no
new warnings. The style file uses `\providecommand`, `\providecolor`,
`\PassOptionsToPackage`, and `\@ifundefined` guards throughout so it is
safe to load atop legacy preambles.

Public macro names (`\DocTitle`, `\makedoctocpage`, `\notebox`, `\kbd`,
`\safeincludegraphics`, `\cmark`, …) are part of the contract — they
must stay backwards-compatible. Add new names; do not rename existing
ones.

---

## Finding content

For browsing by domain, start under `src/`. For "buildable" documents
specifically:

```bash
make list-roots
```

That list is the authoritative set of standalone PDFs the automation
expects to build.



