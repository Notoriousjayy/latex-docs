# Startup and Small Business Operations

Reusable source material for startup planning, finance, operational design, security, product opportunities and business support. These files are planning aids and examples, not a registered business's completed records.

## Explore the collection

| Area | What it contains | Sources |
|---|---|---:|
| [`cleaning-services/`](cleaning-services/) | Service-business planning and operating artifacts. | 4 |
| [`curricula/`](curricula/) | Learning and training plans for entrepreneurship. | 1 |
| [`finance/`](finance/) | Financial models and small-business planning guidance. | 2 |
| [`game-development/`](game-development/) | Game-industry startup and product work. | 2 |
| [`iot/`](iot/) | IoT business and implementation concepts. | 1 |
| [`media/`](media/) | Media business planning and production operations. | 3 |
| [`security/`](security/) | Security controls and startup governance. | 2 |
| [`support/`](support/) | Operational support and service documentation. | 1 |
| [`templates/`](templates/) | Reusable startup and small-business document templates. | 2 |

## Build and validate

```bash
make preflight
make build-category-startups
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Using this collection

- Choose the business model first, then assemble the relevant planning, operating and security material.

- Pair business requirements with [business analysis](../business-analysis/readme.md) and architectural controls with the [enterprise business operations collection](../architecture/enterprise/business-operations/readme.md).

## Maintenance and scope

- Do not present examples or templates as legal, accounting or regulatory approval.

- Remove sample identities and sensitive financial information before public publication.

## Related

- [Source catalog](../readme.md)
