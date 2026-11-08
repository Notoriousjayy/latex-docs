# Technical reference document sources

These LaTeX roots describe an engineering proposal and the implementation approach; they are not deployed controls or completed assessment forms. Source-specific review against current official GitHub APIs and enterprise permissions is required before production use.

- [01-enterprise-architecture-reference.tex](01-enterprise-architecture-reference.tex) — Enterprise architecture and authority boundaries
- [02-merge-blocker-governance.tex](02-merge-blocker-governance.tex) — Distinct GitHub merge blockers and diagnostic workflow
- [03-policy-as-code.tex](03-policy-as-code.tex) — Deterministic decisions and fail-closed inputs
- [04-delegated-dismissal-exception.tex](04-delegated-dismissal-exception.tex) — Delegated review and exception lifecycle
- [05-github-integration.tex](05-github-integration.tex) — GitHub App, API and Actions trust boundaries
- [06-threat-model-control-matrix.tex](06-threat-model-control-matrix.tex) — STRIDE risk/control model
- [07-observability-and-kpis.tex](07-observability-and-kpis.tex) — Metrics and experimental design
- [08-adoption-roadmap.tex](08-adoption-roadmap.tex) — Deployment readiness gates
- [09-operations-playbook.tex](09-operations-playbook.tex) — Developer/AppSec operating procedures
- [10-agile-backlog.tex](10-agile-backlog.tex) — Story-pointed delivery backlog

Build with `make build-category-security`; see [suite landing page](../README.md) and [guided/printable forms](../forms/README.md).
