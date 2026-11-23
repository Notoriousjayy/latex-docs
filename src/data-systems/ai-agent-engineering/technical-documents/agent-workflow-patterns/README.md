# AI Agent Workflow and Orchestration Patterns — Source Chapters

These seven LaTeX files are **included fragments**, not independently compilable roots. The canonical standalone document is [AI Agent Workflow and Orchestration Patterns](../ai-agent-workflow-orchestration-patterns-guide.tex), which loads the repository's `technical-design-spec` module.

## Chapter map

| Source | Purpose |
|---|---|
| [01-foundations.tex](01-foundations.tex) | Architectural layers, terminology, control authority |
| [02-fixed-workflows.tex](02-fixed-workflows.tex) | Chaining, parallelization, routing, deterministic control |
| [03-dynamic-agents.tex](03-dynamic-agents.tex) | ReAct, planning, supervisor-workers, collaborative agents |
| [04-governance-and-protocols.tex](04-governance-and-protocols.tex) | Reflection, approval, MCP/A2A, security threat model |
| [05-selection-and-case-study.tex](05-selection-and-case-study.tex) | Comparative matrix, trade-offs, secure-code-review case |
| [06-python-and-verification.tex](06-python-and-verification.tex) | Python reference, tests, evaluation, acceptance criteria |
| [07-references.tex](07-references.tex) | Diagram inventory and source references |

Twelve editable TikZ diagrams are embedded in the chapter sources and rendered by the parent document. Build from the repository root with `make preflight` and `make build-category-data-systems`. Generated PDFs are build artifacts rather than source-of-truth files.

This is an original engineering guide; quantitative trade-offs are design approximations and not benchmark claims.
