# Architecture Documentation Suite v1.0

This compact operational companion to the [Views and Beyond Documentation Engineering Suite](../documentation-engineering-suite/README.md) integrates seven original standalone LaTeX documents informed by Clements et al., *Documenting Software Architectures: Views and Beyond*, 2nd ed. (2011). The books and generated PDFs are not committed.

## Document index

| ID | Document |
|---|---|
| 01 | [Views and Beyond technical study](01-views-and-beyond-study.tex) |
| 02 | [Software Architecture Document authoring template](02-software-architecture-document-template.tex) |
| 04 | [Integrated documentation framework](04-integrated-documentation-framework.tex) |
| 05 | [Architecture documentation review framework](05-architecture-review-framework.tex) |
| 06 | [Repository architecture analysis methodology](06-repository-architecture-analysis.tex) |
| 07 | [Proposed AI agent harness architecture documentation standard](07-agent-harness-architecture-standard.tex) |
| 08 | [48-hour architecture documentation curriculum](08-architecture-documentation-curriculum.tex) |

Deliverable 03 (the Agent Skills collection) is intentionally outside this LaTeX integration. The SAD document is an instructional authoring template; the existing larger suite supplies governed Template–Blank forms.

## Supporting models and validation

- [PlantUML sources](diagrams/): nine proposed agent harness diagrams, adapted to the repository's shared style modules with no legacy skinparam directives. Models are target-design illustrations, not observed production evidence.
- [Manifest schema](schemas/architecture-manifest.schema.json) and [example manifest](examples/example-manifest.json): representative proposed architecture records; not an exhaustive semantic model.
- [Review register](examples/review-register.csv): twelve gates, initially NOT-RUN.
- [Structural validator](scripts/validate.py) and [six tests](tests/test_validate.py): checks IDs, references, provenance fields and high-priority concern mappings, not architectural correctness.

## Build and verification

Run `make preflight` and `make build-category-architecture` from the repository root. These seven roots are automatically discovered by the source-first build and Pages publishing pipeline. The imported LaTeX is byte-for-byte identical to the original locally compiled v1.0 documents and intentionally retains its self-contained preamble; a future house-style migration should be separately reviewed. No generated PDFs are checked in.

From this directory, run:

```bash
python3 scripts/validate.py examples/example-manifest.json
python3 -m unittest discover -s tests -v
```

All seven original sources compiled locally; diagram styles were adapted during integration and have not been locally rendered. Repository CI and Pages status must be verified separately.

## Provenance

Views and Beyond structures, view packaging and documentation review are derived from the source book; the agent harness design, local gate thresholds, recovery workflow, schemas and 48-hour curriculum are original extensions. ISO/IEC/IEEE 42010:2022 treatment is conceptual alignment, not normative conformance or certification. Do not publish the source textbook or treat the proposed architecture as operational evidence.
