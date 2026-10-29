# Personal Reference Materials

## Overview

Personal study and reference sources covering career planning, e-books, finance, fitness and gardening. **This repository is public.** Do not assume these files or generated PDFs are private.

## Scope and boundaries

Personal educational/reference sources belong here; this public repository is not suitable for private records. Business formation sources belong in [Startups](../startups/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Technical documents](technical-documents/README.md) | Design guides, engineering references and explanatory technical material | 1 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [career](career/README.md) | Meeting preparation and career-related handouts. | 3 |
| [finance](finance/) | CD strategies, investment analysis and valuation guides. | 16 |
| [fitness](fitness/README.md) | Exercise and equipment references. | 2 |
| [gardening](gardening/README.md) | Aquaponics, sunlight and growing guides. | 2 |


## Recommended navigation

Start with the directory map above, then open the source matching your task. For an established documentation suite, follow its original chapter or artifact sequence rather than browsing alphabetically.

## Build and validate

```bash
make preflight
make build-category-personal
```

The repository build and publishing machinery discovers roots under this domain. **There is no documentation-level privacy exclusion**: review source files and generated artifacts before publication. Use `make publish` only when the complete corpus is appropriate for distribution.

## Publication and safety

- Remove personal identifiers, private health or financial information and credentials before committing.
- Treat finance and fitness content as educational material rather than professional recommendations.
- Preserve authorship, licensing, attribution and the context of dated assumptions.

## Maintenance conventions

Keep one authoritative source per artifact, prefer shallow subject-based directories, and add a directory index only when a collection merits one. Preserve LaTeX dependencies, attribution, and existing source provenance when moving files.

## Related domains

[Source catalog](../README.md) · [Repository overview](../../README.md)
