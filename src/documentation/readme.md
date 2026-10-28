# Documentation and Technical Writing

Reusable document design and professional communication sources, including letterhead variants and technical-writing guidance. Use these for presentation structure and editorial practice alongside the repository's semantic LaTeX modules.

## Explore the collection

| Area | What it contains | Sources |
|---|---|---:|
| [`letterhead/`](letterhead/) | Reusable letterhead and branded document examples. | 4 |
| [`technical-writing/`](technical-writing/) | Technical-writing methodology and guidance. | 1 |

## Build and validate

```bash
make preflight
make build-category-documentation
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Using this collection

- Choose a document type and appropriate semantic module before styling an artifact.

- Use examples as templates; replace placeholder details and validate accessibility, metadata and export.

## Maintenance and scope

- Do not copy personal or organization details from examples into unrelated deliverables.

- Honor the canonical style system unless an explicitly approved document family requires a variant.

## Related

- [House style](../../tooling/latex/style.sty)

- [Source catalog](../readme.md)
