# AI Agent Harness Course — Architecture Description

AD-AHC-001 / 0.1 / draft. Companion to the six-document study. Based on supplied snapshot label 8a5edab282632443; full SHA and runtime not verified. No certification or full conformance claim.

- [LaTeX document](main.tex)
- [Canonical architecture model](models/architecture.json)
- [Diagram catalog](diagrams/catalog.csv) (27 editable PlantUML sources)
- [Source evidence](evidence/repository-evidence.csv), [coverage](evidence/analysis-coverage.csv), [security risks](evidence/security-risks.csv)
- [Retrospective ADRs](decisions/README.md)
- [Requirement-level conformance matrix](conformance/iso-42010-matrix.csv)

## Build

From repository root use `python3 tooling/scripts/plantuml_lint.py`, `make render-plantuml`, and `make build-category-data-systems`. The existing repository renderer pins PlantUML and bundled C4. It emits PNG/SVG/JPG beside the diagrams in managed directories. The document embeds PNGs when present and prints a source reference otherwise. The root is discoverable by the existing pdfLaTeX build. No generated binaries are committed. To validate model references, run `python3 src/data-systems/ai-agent-engineering/technical-documents/agent-harness-course-study/architecture-description/validate.py`.

## Verification limitations

Static review only. PlantUML engine unavailable in the authoring environment; diagram rendering and visual review are not executed. LaTeX repository house-style compilation and validator execution are not verified here. Full code review of every implementation, exact deployment mapping, restart and security tests, and complete ISO conformance remain open. Some container grouping and dependency directions are explicitly inferred. Earlier study and licensed sources are referenced, not copied. See the coverage CSV for omitted/partial scenarios. No upstream application modified.
