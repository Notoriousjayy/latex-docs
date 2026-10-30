# DevOps

## Overview

Guides and reference material for build engineering, CI/CD, GitHub Actions, GitOps, delivery pipelines, operations, platforms and secrets management.

## Scope and boundaries

Use this domain for build/release automation, platform operations, GitOps, and secrets-management operations. Secure-design controls belong in [Security](../security/README.md), while overarching architecture decisions belong in [Architecture](../architecture/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Technical documents](technical-documents/README.md) | Design guides, engineering references and explanatory technical material | 1 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [build systems](build-systems/) | Build systems, CMake and related tooling. | 19 |
| [ci cd](ci-cd/) | Pipeline architecture and delivery practice. | 5 |
| [foundations](foundations/) | Version control, SDLC fundamentals and Git usage. | 5 |
| [github actions](github-actions/README.md) | Workflow design, actions and GitHub automation. | 12 |
| [platform](platform/) | Kubernetes, Nginx, platform and repository operations. | 20 |
| [secrets management](secrets-management/) | Secret lifecycle, vaults and operational processes. | 5 |



## Continuous Integration and CI/CD Engineering Suite

The [Continuous Integration and CI/CD Engineering suite](ci-cd/continuous-integration-engineering/README.md) provides the nine-chapter Duvall/Matyas/Glover study sequence, a 12-module prerequisite curriculum, Python/Java/C++ labs, GitHub Actions teaching workflows, DevSecOps practices, pipeline architecture specifications, benchmarking, CI/CD maturity reviews, and eight governed printable Template–Blank pairs. The workflows are inactive teaching assets, not workflows for this documentation repository.

## Build and validate

```bash
make preflight
make build-category-devops
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## AWS deployment architecture cross-reference

Use the [Secure AWS Terraform architecture standard](../architecture/cloud/secure-aws-terraform-repository-deployment/README.md) for OIDC-based Terraform deployments, state isolation, and platform security controls. Example workflows are documentation assets, not active CI for this repository.

## Continuous Delivery engineering suite\n\nThe [Continuous Delivery, CI/CD and Release Engineering Documentation Suite](ci-cd/continuous-delivery-release-engineering/README.md) adds 15 chapter guides based on Humble and Farley, AWS/Terraform laboratories, automated quality gates, progressive-delivery and rollback practices, and governed printable workbooks, templates, and scorecards. The companion [Continuous Integration suite](ci-cd/continuous-integration-engineering/README.md) covers the earlier CI foundation.\n\n## Recommended navigation

- Start with `foundations/` for concepts, `ci-cd/` for delivery architecture, and `github-actions/` for platform-specific workflow syntax.

- Use repository-owned [Make targets](../../Makefile) as the operational entry point for building these LaTeX documents.

- Cross-reference [security workflows](../security/README.md) when discussing code scanning, dependency findings and secret scanning.

## Maintenance conventions

- An illustrative CI/CD pipeline is not a deployed pipeline; identify integrations and secrets before adapting it.

- Never commit credentials, tokens, kubeconfigs or real environment data.

- Use principle-of-least-privilege examples and document deployment prerequisites and rollback boundaries.

## Related domains

- [Source catalog](../README.md)
