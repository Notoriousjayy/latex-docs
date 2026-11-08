# Enterprise Code Scanning Triage, Dismissal Automation and Merge Governance

**Status:** engineering reference / offline proof of concept; **not deployed**. The suite complements [GitHub Actions Architecture Discovery](../../../../architecture/github-actions-discovery-suite.md). It reuses E1 observed, E2 inferred and E3 externally verified evidence semantics, but discovery remains a read-only provider. It does **not** approve production dismissals, modify rulesets, or bypass AppSec review.

## Operating boundaries

Code scanning **ruleset merge protection**, required **status checks**, required **PR reviews** and **delegated dismissal requests** are different blockers. A dismissed alert does not satisfy every merge requirement. GitHub documents that code scanning alert dismissal is cross-branch. An inferred dependency or a requester comment is not proof of a false positive. All unknown, denied, incomplete and stale states produce an abstention.

## Technical references

- [Enterprise Code Scanning Automation Architecture](references/01-enterprise-architecture-reference.tex)
- [Merge-Blocker Governance and Root-Cause Analysis](references/02-merge-blocker-governance.tex)
- [Deterministic Policy-as-Code and Decision Specification](references/03-policy-as-code.tex)
- [Delegated Dismissal and Exception Lifecycle](references/04-delegated-dismissal-exception.tex)
- [GitHub App and Actions Integration Guide](references/05-github-integration.tex)
- [Threat Model and Security Control Matrix](references/06-threat-model-control-matrix.tex)
- [AppSec Observability, KPIs and Causal Evaluation](references/07-observability-and-kpis.tex)
- [Implementation and Adoption Roadmap](references/08-adoption-roadmap.tex)
- [Application Security and Developer Operating Procedures](references/09-operations-playbook.tex)
- [Delivery Backlog and Engineering Acceptance Criteria](references/10-agile-backlog.tex)
- [Architecture Description](../../../../architecture/technical-documents/enterprise-appsec-code-scanning-architecture-description.tex)
- [Viewpoint Specification](../../../../architecture/technical-documents/enterprise-appsec-code-scanning-viewpoint-specification.tex)
- [Existing delegated alert review guide](../../administration/automating-review-github-advanced-sec-alert.tex) — assess and strengthen before adopting; its example comment-length/reason tests are insufficient to authorize dismissal.

## Validation and implementation

See [Lab README](labs/README.md), [Template–Blank workbook catalog](forms/README.md), [diagram sources](diagrams/README.md) and [GitHub API source register](references/05-github-integration.tex).
Run `python3 tooling/scripts/validate_artifact_pairs.py`, `python3 -m unittest discover -s tests -p 'test_enterprise_discovery_suite.py'`, targeted companion tests, `make preflight`, `make build-category-architecture` and `make build-category-security`.

## Production authorization limitations

Any future delegated dismissal execution needs separately reviewed GitHub App roles, approved security policy, separation of duties, protected audit trail, shadow mode, nonproduction pilot and rollback. The examples are not enabled GitHub Actions workflows. No real alerts or settings are modified by these documents.

## Original sources

- [GitHub code scanning merge protection](https://docs.github.com/en/code-security/concepts/code-scanning/merge-protection)
- [GitHub delegated alert dismissal](https://docs.github.com/en/code-security/concepts/security-at-scale/delegated-alert-dismissal)
- [GitHub code scanning REST API](https://docs.github.com/en/rest/code-scanning/code-scanning)
- [GitHub dismissal request API](https://docs.github.com/en/rest/code-scanning/alert-dismissal-requests)
