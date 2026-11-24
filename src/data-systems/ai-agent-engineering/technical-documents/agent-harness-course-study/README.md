# Agent Harness Course Study

Six standalone pdfLaTeX technical documents based on the supplied course snapshot (8a5edab282632443). Original analysis, proposed controls, and curriculum exercises are distinguished from observed implementation. No upstream source dump, private data, credentials or generated PDFs are included.

- [Comprehensive Architecture Analysis](01-comprehensive-architecture-analysis.tex) — Components, control flows, memory and advanced execution patterns.
- [Harness Engineering Technical Guide](02-harness-engineering-technical-guide.tex) — Practical operating reference, diagrams and verification.
- [Security Architecture Assessment](03-security-architecture-assessment.tex) — Trust boundaries, injection, authorization, approval and isolation.
- [Vendor-Neutral Python Reference Architecture](04-vendor-neutral-python-reference-architecture.tex) — Ports and adapters, persistence, deployment and evaluation.
- [Agent Engineering Curriculum Integration](05-curriculum-integration.tex) — Source-to-lab crosswalk and proposed adoption plan.
- [Hands-On Agent Harness Learning Roadmap](06-hands-on-learning-roadmap.tex) — Sixteen progressive implementation labs and acceptance criteria.

- [Formal Architecture Description — C4, UML and ISO/IEC/IEEE 42010:2022](architecture-description/README.md) — draft source-based AD, 27 editable PlantUML models, architecture catalogs, evidence, security risks, retrospective ADRs and partial conformance assessment.

- [Three independent architecture descriptions](architecture-descriptions/README.md) — ERPA, governed PPA, learning-enabled PPA; source-linked C4/UML and provisional ISO assessments.

## Build

From the repository root run `make build-category-data-systems`, or run `latexmk -pdf -interaction=nonstopmode -halt-on-error <document>.tex` from this directory. All diagrams are native TikZ; each document is a separately discoverable root. The suite retains the self-contained style of the original integrated study and neighboring agent-engineering guides.

The curriculum crosswalk and labs are proposals, not completed curriculum implementation. Live writes, alert dismissal and AWS deployment remain excluded.
