# Optimized LaTeX Build System

This document describes the modularized GitHub Actions workflow architecture designed for high-performance builds of the latex-docs repository (~420 documents).

## Quick Start

### Local Development
```bash
# Build everything (parallel)
make publish-parallel

# Build single category
make build-category-security

# Build only changed files
make build-changed

# List all documents
make list-roots
```

### GitHub Actions
- **CI runs automatically** on pushes/PRs to `main` affecting `src/**/*.tex`
- **Manual trigger**: Go to Actions → "LaTeX CI" → "Run workflow"
- **Full rebuild**: Check "Build all documents" option

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Trigger Events                              │
│         (push, pull_request, release, workflow_dispatch)            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  latex-ci.yml │      │latex-pages.yml│      │latex-release  │
│   (PRs/Push)  │      │  (Deploy)     │      │   (Tags)      │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  _build-latex.yml   │  ◄── Reusable Workflow
                    │  (Core Build Logic) │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  setup-latex    │  │ render-plantuml │  │ build-documents │
│  (Composite)    │  │  (Composite)    │  │   (Composite)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Key Optimizations

### 1. Parallel Matrix Builds
Documents are grouped by category (architecture, devops, security, etc.) and built concurrently using GitHub Actions matrix strategy.

```yaml
strategy:
  fail-fast: false
  max-parallel: 6
  matrix:
    category: [architecture, devops, security, mathematics, ...]
```

**Impact**: ~4-8x faster for full rebuilds

### 2. Intelligent Change Detection
Only builds affected documents when specific files change:

| Change Type | Build Scope |
|-------------|-------------|
| Single `.tex` file | That document only |
| `.tex` in same directory | Documents using `\input` from there |
| `common/*.tex` or `tooling/*.tex` | All documents |
| Workflow changes | Full rebuild (verification) |

### 3. Multi-Layer Caching

| Cache Layer | Scope | Time Saved |
|-------------|-------|------------|
| TeX Live packages | Global | 3-5 min |
| LaTeX aux files | Per-category | 30-60 sec/doc |
| PlantUML outputs | Committed | 1-2 min |

### 4. Native Ubuntu Runners

| Approach | Setup Time | Image Size |
|----------|------------|------------|
| texlive-full container | 2-4 min | ~7 GB |
| Native + cached packages | <30 sec | ~1 GB |

## Workflow Files

### Primary Workflows

| File | Purpose | Trigger |
|------|---------|---------|
| `latex-ci.yml` | Validate builds | PRs, push to main |
| `latex-pages.yml` | Deploy to GitHub Pages | push to main |
| `latex-release.yml` | Attach PDFs to releases | tag publish |
| `render-plantuml.yml` | Auto-render diagrams | `.puml` changes |

### Reusable Workflow

| File | Purpose |
|------|---------|
| `_build-latex.yml` | Core build orchestration, called by all primary workflows |

### Composite Actions

| Action | Purpose |
|--------|---------|
| `.github/actions/setup-latex/` | Install and cache TeX Live |
| `.github/actions/render-plantuml/` | Render PlantUML diagrams |
| `.github/actions/build-documents/` | Build LaTeX with caching |

## Expected Build Times

### Before Optimization
| Scenario | Time |
|----------|------|
| Any change | 45-60 min |
| Full rebuild | 45-60 min |

### After Optimization
| Scenario | Time |
|----------|------|
| Single file (cached) | 2-4 min |
| Category rebuild | 5-12 min |
| Full rebuild (parallel) | 12-20 min |
| PlantUML only | 1-2 min |

## Directory Structure

```
latex-docs/
├── .github/
│   ├── actions/
│   │   ├── setup-latex/
│   │   │   └── action.yml
│   │   ├── build-documents/
│   │   │   └── action.yml
│   │   └── render-plantuml/
│   │       └── action.yml
│   └── workflows/
│       ├── _build-latex.yml      # Reusable
│       ├── latex-ci.yml          # CI
│       ├── latex-pages.yml       # Pages
│       ├── latex-release.yml     # Releases
│       └── render-plantuml.yml   # Diagrams
├── src/
│   ├── architecture/
│   ├── devops/
│   ├── security/
│   └── ... (other categories)
├── public/
│   ├── pdfs/       # Built PDFs (organized)
│   └── logs/       # Build logs
├── Makefile
├── latexmkrc
└── tooling/
    └── latex/
        └── common-preamble.tex
```

## GitHub Pages Output

The `latex-pages.yml` workflow produces:

```
https://<username>.github.io/<repo>/
├── index.html           # Auto-generated catalog
└── pdfs/
    ├── architecture/
    │   ├── documenting-software-architecture/
    │   │   ├── architecture-playbook.pdf
    │   │   └── ...
    │   └── views-and-beyond/
    │       └── ...
    ├── security/
    │   └── ...
    └── ...
```

## Local Development

### Prerequisites
```bash
# Ubuntu/Debian
sudo apt-get install \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-pictures \
  texlive-science \
  latexmk \
  python3-pygments

# macOS (with MacTeX)
brew install --cask mactex
pip3 install pygments
```

### Makefile Targets

```bash
make help                    # Show all targets
make list-categories         # Show categories with counts
make build-category-devops   # Build single category
make build-parallel JOBS=8   # Parallel build all
make publish                 # Build + organize for Pages
make clean                   # Remove aux files
make distclean               # Remove everything generated
```

## Troubleshooting

### "pygmentize not found"
The minted package requires Pygments:
```bash
pip3 install pygments
# Verify:
which pygmentize
```

### Cache not restoring
- Check Actions → job → "Cache LaTeX" step for hit/miss
- Cache key includes tex file hashes; any change invalidates
- Manually clear: Settings → Actions → Caches → Delete

### Parallel builds failing randomly
- Resource contention on shared files
- Solution: Ensure each document uses isolated `_minted-*` directories
- The composite action creates these automatically

### PlantUML not rendering
1. Check that `.puml` files are committed (not in `.gitignore`)
2. Run workflow manually: Actions → "Render PlantUML"
3. Verify outputs in `src/**/png/` and `src/**/svg/`

### Build succeeds but PDF missing from Pages
- Check the `stage` job in `latex-pages.yml`
- Verify artifact download succeeded
- Check `site/pdfs/` structure in job logs

## Contributing

When adding new documents:

1. Place in appropriate category under `src/`
2. Ensure `\documentclass` is the first non-comment line
3. Keep dependencies (images, `\input` files) in same directory
4. Test locally: `make build-category-<name>`
5. If using minted, test with `--shell-escape`

## Advanced: Custom Categories

To add a new top-level category:

1. Create `src/my-category/`
2. Add `.tex` files with `\documentclass`
3. The system auto-discovers categories from `src/*/`
4. No workflow changes needed

## Metrics

For a repository with ~420 documents across 15+ categories:

| Metric | Value |
|--------|-------|
| Full parallel build | ~15 min |
| Incremental (1 file) | ~3 min |
| Cache hit rate | ~90% |
| Parallel jobs | 6 concurrent |
| Artifact size | ~200 MB |
