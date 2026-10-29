# Data Systems

## Overview

Technical references and study material for data-centric platforms and infrastructure, including AI/ML, streaming and networked data systems. Scope reflects the current files; it is not a claim of an operational data platform.

## Scope and boundaries

This domain covers data platforms, streaming and AI/ML systems. Place domain-independent program code in [Programming](../programming/README.md), and infrastructure automation in [DevOps](../devops/README.md).

## Directory map and documentation catalog

| Area | What it contains | Sources |
|---|---|---:|
| [`ai-ml/`](ai-ml/) | LLM and machine-learning adoption guidance. | 3 |
| [`networking/`](networking/) | Data-network concepts and networking-related references. | 1 |
| [`streaming/`](streaming/) | Event streaming and Kafka architecture. | 1 |

## Build and validate

```bash
make preflight
make build-category-data-systems
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Recommended navigation

- Identify the target platform, assumptions and data flow before adopting an example.

- Relate persistence and integration choices to the [architecture ADR collection](../architecture/decisions/readme.md).

## Maintenance conventions

- Capture data sensitivity, ownership, consistency, lineage and retention as explicit design considerations.

- Keep speculative future platform areas out of the inventory until source documents exist.

## Related domains

- [Source catalog](../README.md)
