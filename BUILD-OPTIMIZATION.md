# Optimized LaTeX Build System

This document describes the modularized GitHub Actions workflow architecture designed to significantly reduce build times for the latex-docs repository.

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

### 1. Change Detection
Instead of building all ~200 documents on every commit, the system detects which files changed and only builds affected documents.

```yaml
# Before: Always builds everything
make build-all  # 45+ minutes

# After: Only builds what changed
if: steps.changes.outputs.has-changes == 'true'
# Plus selective file filtering
```

### 2. Parallel Matrix Builds
Documents are organized by category and built in parallel using GitHub Actions matrix strategy.

```yaml
strategy:
  fail-fast: false
  matrix:
    category: [architecture, devops, security, mathematics, ...]
```

**Estimated speedup:** 4-8x (depending on document distribution)

### 3. Aggressive Caching

| Cache Target | Hit Rate | Time Saved |
|--------------|----------|------------|
| TeX Live packages | ~95% | 3-5 min |
| LaTeX auxiliary files | ~80% | 1-2 min per doc |
| PlantUML diagrams | 100%* | 30-60 sec |

*PlantUML outputs are committed to repo, eliminating re-renders.

### 4. Reusable Components
Common logic is extracted into composite actions, eliminating ~300 lines of duplicated code.

| Component | Lines Saved | Workflows Using |
|-----------|-------------|-----------------|
| setup-latex | ~30 lines | 4 |
| render-plantuml | ~80 lines | 3 |
| build-documents | ~60 lines | 3 |

### 5. Native Ubuntu Runners
Replaced the heavy `texlive-full` Docker container (~7GB) with native Ubuntu + cached TeX Live installation.

| Approach | Image Size | Pull Time |
|----------|------------|-----------|
| texlive-full container | ~7 GB | 2-4 min |
| Native + cached | ~1 GB | <30 sec |

## Workflow Files

### Primary Workflows
| File | Purpose | Trigger |
|------|---------|---------|
| `latex-ci.yml` | Build validation | PRs, push to main |
| `latex-pages.yml` | GitHub Pages deploy | push to main |
| `latex-release.yml` | Release artifacts | tag publish |
| `render-plantuml.yml` | Diagram rendering | .puml changes |

### Reusable Workflow
| File | Purpose |
|------|---------|
| `_build-latex.yml` | Core build logic, called by all primary workflows |

### Composite Actions
| Directory | Purpose |
|-----------|---------|
| `.github/actions/setup-latex/` | Install and cache TeX Live |
| `.github/actions/render-plantuml/` | Render PlantUML diagrams |
| `.github/actions/build-documents/` | Build LaTeX documents with caching |

## Expected Build Times

### Before Optimization
| Scenario | Time |
|----------|------|
| Single file change | 45-60 min |
| Full rebuild | 45-60 min |
| PlantUML only | 5-10 min |

### After Optimization
| Scenario | Time |
|----------|------|
| Single file change (cached) | 2-5 min |
| Category rebuild (parallel) | 5-15 min |
| Full rebuild (parallel) | 15-25 min |
| PlantUML only | 1-2 min |

## Local Development

### Quick Commands
```bash
# List all buildable documents
make list-roots

# List categories with document counts
make list-categories

# Build single category
make build-category-security

# Parallel build all
make build-parallel JOBS=8

# Build only changed files (since last commit)
make build-changed
```

### Prerequisites
Ensure you have:
- TeX Live (texlive-latex-extra, texlive-fonts-extra, etc.)
- latexmk
- LuaLaTeX (for Unicode support)
- Python + Pygments (for minted package)

## Migration Guide

### Step 1: Replace Workflow Files
Copy the new workflow files to `.github/workflows/`:
- `_build-latex.yml`
- `latex-ci.yml`
- `latex-pages.yml`
- `latex-release.yml`
- `render-plantuml.yml`

### Step 2: Add Composite Actions
Copy the actions to `.github/actions/`:
- `setup-latex/action.yml`
- `render-plantuml/action.yml`
- `build-documents/action.yml`

### Step 3: Update Makefile
Replace the existing Makefile with the optimized version.

### Step 4: Test
1. Push a single `.tex` file change
2. Verify only that file builds
3. Test parallel builds with `workflow_dispatch`

## Troubleshooting

### Cache Not Working
- Check cache key patterns
- Verify `actions/cache@v4` is used
- Cache size limit is 10GB per repo

### Parallel Builds Failing
- Check matrix output in `prepare` job
- Verify category directories exist
- Check for race conditions in shared resources

### PlantUML Not Rendering
- Ensure `.puml` files are committed (not gitignored)
- Check the `render-plantuml.yml` workflow ran
- Verify SVG/PNG directories exist

## Contributing
When adding new documents:
1. Place in appropriate category under `src/`
2. Use `\documentclass` as first non-comment line
3. Keep dependencies (images, inputs) in same directory
4. Test with `make build-category-<name>` before pushing
