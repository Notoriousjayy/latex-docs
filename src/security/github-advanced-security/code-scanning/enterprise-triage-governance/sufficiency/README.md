# Enterprise GitHub Discovery and AppSec Governance — documentation sufficiency

**Baseline:** `Notoriousjayy/latex-docs` `main` at `964a52ef0ccaaddb089b3649525d3bc8863adda0` (2026-11-08). **Assessment type:** repository-source and controlled-document review, not an inspection of a real GitHub enterprise or an authorization to deploy. The file set in this folder is a controlled **planning and traceability overlay**, not a replacement for the existing canonical LaTeX reference documents.

## Read first

| Resource | Purpose |
|---|---|
| [Requirements and sufficiency matrix](requirements-matrix.csv) | One row per operational requirement; P0/P1/P2, coverage and environment-evidence gaps |
| [Canonical document register](document-register.csv) | Source-of-truth paths, purpose, governance owner **roles**, readiness and review cadence |
| [Architecture and control crosswalk](architecture-and-controls.md) | Integrated data contracts, security boundary, correspondence, authority and traceability |
| [Governance and operations](governance-operations.md) | Capability charter, decision rights, security/operations procedures and handover |
| [Readiness, ADR assessment and remediation backlog](readiness-backlog.md) | L1/L2/L3 evidence gates, unresolved P0s and implementation-ready delivery stories |
| [Verification and evidence protocol](verification.md) | Deterministic scope of static checks and separate live-environment verification protocol |

The original authoritative source documents remain in the [Discovery suite](../../../../../architecture/github-actions-discovery-suite.md) and [AppSec companion](../README.md). Existing guided/printable [AppSec forms](../forms/README.md), four Discovery forms, ten security reference documents, architecture AD/AVS, and three PROPOSED ADRs are **reused**, not forked. The [legacy dismissal review field guide](../../../administration/automating-review-github-advanced-sec-alert.tex) contains unsafe comment-length/reason-based examples and is **non-authoritative for production approval**.

## Audit decision and scope

- **Design references:** broad coverage exists; additional specificity is needed for evidence exchange, decision rights, retention, failure recovery and proof of adoption.
- **Enterprise operating data:** actual organization inventory, accountable persons, current ruleset/API behavior, review rights, security policy, telemetry and authorization records were **not made available or verified**.
- **Document completeness:** the proposed design has an accountable traceability structure, but final L1 approval is **not evidenced**; all P0 items with external prerequisites remain blocked.
- **Pilot readiness:** **not evidenced**. Simulation of policy decisions in Python does not establish a pilot.
- **Production readiness:** **not evidenced / unauthorized**. Nothing in this repository deploys a privileged dismissal executor.
- **Published repository:** public documentation must not contain real repository vulnerability descriptions, private deployment identifiers, credentials, or personal details.

## Controlled vocabulary

`coverage` in the matrix means documentation content coverage (`covered`, `partial`, `missing`); it does **not** mean live implementation. `operational_evidence` separately reports `unverified`, `not_applicable` or `offline_test_only`. `necessary`, `conditional`, `supporting` and `optional` describe document necessity; a conditional requirement becomes mandatory once the corresponding feature is selected. `owner_role` is a **proposed role**, not a named assignee or proof of acceptance. No `verified` field is implied from a document's mere existence.

## Change governance

Source document or policy change -> update impacted matrix rows -> assess architecture/ADR impacts -> update the canonical source -> update test/evidence crosswalk -> submit PR -> obtain the proper reviews -> collect post-merge environment evidence separately. Never write `passed` for an unexecuted acceptance criterion. See [verification](verification.md) for the automated cross-checks.

There are no signed authorizations or actual enterprise configuration exports in this package. All readiness claims are intentionally conservative.
