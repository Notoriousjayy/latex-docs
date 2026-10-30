# Startup and Small Business Operations

## Overview

Reusable source material for startup planning, finance, operational design, security, product opportunities and business support. These files are planning aids and examples, not a registered business's completed records.

## Scope and boundaries

Business formation, operating models, venture planning, and company-specific engineering/business artifacts belong here. General BABOK methods belong in [Business Analysis](../business-analysis/README.md); reusable architecture patterns belong in [Architecture](../architecture/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Technical documents](technical-documents/README.md) | Design guides, engineering references and explanatory technical material | 1 |
| [Templates](templates/README.md) | Reusable structured starting points and document forms | 2 |
| [Workbooks and exercises](workbooks/README.md) | Practice, exercises, checklists and worked activities | 1 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [cleaning services](cleaning-services/README.md) | Service-business planning and operating artifacts. | 4 |
| [finance](finance/README.md) | Financial models and small-business planning guidance. | 2 |
| [game development](game-development/README.md) | Game-industry startup and product work. | 2 |
| [iot](iot/) | IoT business and implementation concepts. | 1 |
| [media](media/) | Media business planning and production operations. | 3 |
| [security](security/) | Security controls and startup governance. | 2 |
| [small business management](small-business-management/README.md) | 23-chapter entrepreneurship curriculum; finance laboratories, operations procedures, business cases, forms and assessment scorecards. | 111 |


## Build and validate

```bash
make preflight
make build-category-startups
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Recommended navigation

- Choose the business model first, then assemble the relevant planning, operating and security material.

- Pair business requirements with [business analysis](../business-analysis/README.md) and architectural controls with the [enterprise business operations collection](../architecture/enterprise/business-operations/readme.md).

## Maintenance conventions

- Do not present examples or templates as legal, accounting or regulatory approval.

- Remove sample identities and sensitive financial information before public publication.

## Related domains

- [Source catalog](../README.md)
