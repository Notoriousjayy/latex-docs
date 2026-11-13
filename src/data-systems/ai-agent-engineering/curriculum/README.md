# AI Agent Engineering Curriculum

## Source document

- [AI Agent Engineering: Comprehensive Developer Curriculum](ai-agent-engineering-comprehensive-syllabus.tex) — 16-week, approximately 160-hour instructional syllabus covering agent frameworks, harness architecture, Model Context Protocol, enterprise guardrails, reliability, and GitHub AppSec governance.

## Content and structure

The syllabus contains the 23-section program design, technical module study guides, 16 weekly learning plans and labs, educational-resource catalogs, traceability matrices, assessment rubrics, and a read-only GitHub CodeQL agent capstone.

## Compilation

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error ai-agent-engineering-comprehensive-syllabus.tex
```

This standalone source uses pdfLaTeX-compatible Unicode declarations and contains a native LaTeX prerequisite diagram instead of referencing a separate PNG. Build from this directory or use the repository category build.

## Editorial and security boundaries

This syllabus is educational and does not imply that the proposed controls have been deployed, independently assessed, or authorized. Version-specific MCP behavior and training links must be revalidated before running production integrations. The GitHub capstone begins with read-only access; privileged changes require separately verified policy and approval gates.
