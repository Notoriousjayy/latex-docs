# Integrated Architecture Documentation Suite

Original engineering guidance informed by *Documenting Software Architectures: Views and Beyond*, second edition, and ISO/IEC/IEEE 42010:2022. Licensed source PDFs are excluded. No formal conformance or deployment claim is made.

## Directory map and documentation catalog

| Source | PDF pages |
|---|---:|
| [Software Architecture Documentation with Views and Beyond and ISO/IEC/IEEE 42010:2022](software-architecture-docs-vb-iso-42010-2022.tex) | 9 |
| [Integrated SAD Template](integrated-sad-template.tex) | 8 |
| [Integrated SAD Blank](integrated-sad-blank.tex) | 6 |
| [Architecture Viewpoint Catalog](architecture-viewpoint-catalog-vb-42010.tex) | 13 |
| [Architecture Description Conformance Guide](architecture-conformance-guide-42010-2022.tex) | 6 |
| [Architecture Documentation Review Checklist](architecture-documentation-review-checklist.tex) | 6 |
| [Reference SAD: Repository Security Analysis](reference-sad-security-analysis.tex) | 9 |

## Working sequence

Read the methodology, select and adapt viewpoints, instantiate the guided SAD Template or printable Blank, and compare against the illustrative security-analysis architecture. Apply the review checklist and separately assess normative conformance.

## Template–Blank governance

The SAD Template and Blank form one logical artifact under `ARCH-AD-INTEGRATED-VB-42010`. The Blank is excluded from the canonical semantic inventory and independently compilable.

## Build and validate

From the repository root, use `make preflight` and `make build-category-architecture`. The seven standalone sources retain the locally validated formatting. Shared semantic style migration is a separate layout change. All seven compiled locally to 57 pages without final warnings, errors or overfull/underfull boxes. See [validation notes](VALIDATION.md).

## Related collections

- [Views and Beyond](../readme.md)
- [Documentation engineering suite](../documentation-engineering-suite/README.md)
- [Operational architecture documentation suite](../architecture-documentation-suite/README.md)
- [Architecture domain](../../README.md)
