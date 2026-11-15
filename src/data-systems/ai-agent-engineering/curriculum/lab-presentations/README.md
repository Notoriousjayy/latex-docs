# AI Agent Engineering -- Laboratory Beamer Slide Decks

16 independent 16:9 pdfLaTeX presentations aligned to the syllabus Section 13 (pp. 25-40).
Source commit: `3b62f5ad71796489c5f6813ad9e53e41a54211cd`.
L01-L02 have implemented offline references; L03-L16 are scaffolds and are not production-ready.

| Lab | Week | Module | Presentation | Status |
|---|---:|---|---|---|
| L01 | 1 | M01 | [Agent system boundaries and LLM tool semantics](l01-agent-system-boundaries.tex) | Offline reference |
| L02 | 2 | M01 | [Minimal framework-free agent execution](l02-framework-free-agent.tex) | Offline reference |
| L03 | 3 | M02 | [Framework orchestration: LangGraph and SDK alternatives](l03-framework-orchestration.tex) | Scaffold |
| L04 | 4 | M02 | [Durable state, checkpoint recovery and human interrupts](l04-durable-state.tex) | Scaffold |
| L05 | 5 | M03 | [Agent harness control plane, context and environment](l05-agent-harness.tex) | Scaffold |
| L06 | 6 | M04 | [MCP host/client/server fundamentals and protocol revisions](l06-mcp-fundamentals.tex) | Scaffold |
| L07 | 7 | M05 | [Authenticated GitHub MCP and REST integration](l07-github-mcp-integration.tex) | Scaffold |
| L08 | 8 | M06 | [Context engineering, retrieval and midterm demonstration](l08-context-retrieval.tex) | Scaffold |
| L09 | 9 | M07 | [Agent threat modeling and adversarial boundaries](l09-agent-threat-modeling.tex) | Scaffold |
| L10 | 10 | M07 | [Policy-as-code, human approval and safe actions](l10-policy-and-approvals.tex) | Scaffold |
| L11 | 11 | M08 | [Multi-agent delegation and distributed execution](l11-multi-agent-delegation.tex) | Scaffold |
| L12 | 12 | M09 | [Evaluation-driven agent quality engineering](l12-agent-evaluation.tex) | Scaffold |
| L13 | 13 | M10 | [Observability, SLOs and operational fault recovery](l13-agent-observability.tex) | Scaffold |
| L14 | 14 | M11 | [Containerized deployment, CI/CD and workload isolation](l14-deployment-and-ci.tex) | Scaffold |
| L15 | 15 | M12 | [Capstone integration: GitHub AppSec agent (read-only)](l15-appsec-capstone.tex) | Scaffold |
| L16 | 16 | M12 | [Capstone hardening, independent review and operational handoff](l16-capstone-hardening.tex) | Scaffold |

Compiling: use the existing repository `make preflight` and `make build-category-data-systems`. Beamer sources are canonical; PDFs are generated products.

No live GitHub CodeQL dismissals, protected-branch bypasses, repository write tools or AWS infrastructure are authorized by these learning materials.
