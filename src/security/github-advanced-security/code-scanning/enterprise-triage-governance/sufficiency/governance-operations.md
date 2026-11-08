# Governance Operating Model, Security Operations and Handover

**Policy status:** proposed operating model, not approved enterprise policy. The roles below are **roles to assign**, not identified people. Names, organization tenancy, feature entitlement and delegated dismissal permissions have not been evidenced.

## 1. Charter and non-goals

**Mission:** deliver reliable read-only architecture discovery and evidence-based AppSec triage while maintaining independent security acceptance, accountable merge controls and defensible change history. **Service boundary:** GitHub organization/repository observation, architecture mapping, alert enrichment, exception review routing and future separately authorized enforcement. Non-goals: replacing GitHub merge policy, automatic risk acceptance based on an inferred dependency, bypassing missing scans, collecting secrets or broad production token provision.

**Service ownership to establish:** Platform Engineering service owner, AppSec control owner, Architecture Governance steward, repository/application owner registry, designated approvers, on-call escalation and privacy/records authority. Record the identities and acceptance in a restricted enterprise system, linked by non-sensitive record ID; do not publish identifying privileged access here.

## 2. Decision rights and RACI (proposed)

| Decision / responsibility | Accountable | Responsible | Consulted / independent check | Authorization requirement |
|---|---|---|---|---|
| Enterprise inventory and scope | Platform owner | Discovery operations | Architecture steward, repository owner | Authorized installation and repo scope |
| Application identity and E3 promotion | Architecture steward | Catalog maintainer | Business/service owner | Independently verified record |
| Security policy bundle, review SLA and thresholds | AppSec control owner | AppSec policy engineer | Risk owner, platform security | Independent security change approval |
| Risk acceptance of genuine finding | Designated risk owner | AppSec analyst | Repository owner and compliance when applicable | Defined risk-acceptance delegation; no self approval |
| False-positive dismissal decision | Authorized AppSec reviewer | Assigned analyst | Technical subject-matter expert | Review evidence and separation of duties |
| App installation, permissions and credential rotation | Platform security owner | Platform operations | AppSec and audit | Least privilege and change ticket |
| Privileged executor enabling, rollback and reenablement | Security change authority | Platform operator | AppSec and incident response | Signed go-live / rollback authority |
| Audit and evidence retention | Records/privacy owner | Evidence custodian | AppSec, legal/ISMS | Written retention/classification policy |
| SLO, quality scorecards and operational review | Joint Platform/AppSec service owner | Operations analysts | Architecture, business owner | Reviewed baselines and denominators |

**Segregation:** the requester cannot approve their own dismissal; the person/system issuing a decision is not automatically eligible to act on it; a CI bot cannot grant its own production privilege. If organizational staffing cannot support separate individuals, require an approved compensating control and independent audit with a documented risk decision. A role named here is not an actual authorization.

## 3. Standard operating sequence

1. **Scope intake:** get authorized org/repo inventory, collection permission and classification. Capture deny/unsupported counts and version.
2. **Discovery collection:** record E1 sources and revision; use versioned inference for E2; E3 requires independent corroboration. Failed/partial collection must appear in coverage.
3. **Identity reconciliation:** resolve monorepo component/repository/application/owner disagreements with stewardship. Maintain changes rather than overwrite historical evidence.
4. **Alert triage:** confirm actual code scanning analysis, head/base revisions, rule, path and impact. Use the existing [CodeQL triage SOP](../../how-to-use-this-sop.tex).
5. **Merge diagnosis:** separately examine ruleset code-scanning merge protection, status checks, required reviews and queue. Do not claim that dismissal fixes them.
6. **Exception request:** gather verified technical evidence, explicit scope, requester and expiry; record in existing [dismissal form](../forms/dismissal-request-review-template.tex) or [risk acceptance register](../forms/risk-acceptance-register-template.tex).
7. **Independent review:** validate authority, no self approval, current revision, security consequence and policy; reject unsupported reasons; explicitly approve/deny/return.
8. **Execution (not currently enabled):** require distinct executor identity, current-state preconditions and durable audit/outbox, then confirm GitHub's resulting state. Record any discrepancy as an incident.
9. **Reconciliation:** scheduled exception expiry, reopened findings, ownership drift and ruleset changes; review stale queue items.
10. **Management review:** publish aggregate metrics with denominators and missing-data rates; update risk/ADR/backlog and training.

## 4. Failure, incident and recovery paths

| Trigger | Immediate operator response | Escalation / required evidence |
|---|---|---|
| Discovery access denied/partial/stale | Mark unknown, pause enrichment claims, re-run within authorized limits | Platform on-call; source ref, API status, missing denominator |
| Code scanning not completed | Hold any disposition; fix failing scan/required check | Repository owner/CI operator; check identity and run |
| Suspected incorrect dismissal / approval | Disable privileged executor (if deployed), suspend related automation, preserve decision record | AppSec incident lead + platform security; affected branches/alerts, actor, policy and event IDs |
| Credential leakage or privilege misuse | Revoke/rotate affected installations, isolate workflow, invoke organization IR | Security incident response; avoid leaking evidence in docs/CI |
| Lost audit trail or integrity mismatch | Stop mutation, quarantine evidence, reconcile from authoritative GitHub logs | Records custodian/incident response; input/output digests |
| Exception expired or subject changed | Route for fresh review, do not automatically renew | AppSec reviewer and risk owner; scope and version comparison |
| GitHub rate limit/outage | Back off, checkpoint, show reduced coverage, queue bounded retries | Platform owner; retry and data-freshness telemetry |

Corrective reopen is subject to current GitHub capabilities/permissions and explicit review. A blanket rollback of alert dismissals may be impossible; record affected branches and manual remedies. No automatic exception extension.

## 5. Service management measures — definitions, not invented targets

Define per-review reporting window and system-of-record timestamp: (a) collector coverage = successfully observed in-scope repositories / authorized known repositories; (b) evidence completeness = records with required fields / evaluated records; (c) E3 validation rate = corroborated edges / candidates submitted to E3 review; (d) alert review P50/P95 elapsed time = review decision minus complete request received time; (e) false-positive reversal rate = independently confirmed incorrect dismissals / reviewed dismissals; (f) merge-blocker precision = correctly assigned root causes / adjudicated sampled blockers; (g) exception expiry compliance = on-time revalidations / exceptions due; (h) unverified decision rate = abstentions / evaluated requests. Collect sampling method, denominator, missing values and latency clock exclusions. **No SLA/SLO numeric threshold is approved**; owners must select targets after read-only baselining and risk review.

## 6. Retention, privacy, access review and document lifecycle

Source code paths, analyst notes, applicant identity and vulnerability traces may be sensitive even if a repo is public. Establish data classification, legitimate access need, encrypt in transit/at rest, minimum access, audit read/write, jurisdiction and legal hold before storing a production record. **Retention periods are not specified here**; records authority must assign per evidence type and deletion/hold protocol. The public LaTeX repo carries non-sensitive schema and redacted evidence IDs only.

Onboarding: read the two authoritative suite indexes and appropriate AD/AVS; complete a synthetic case in the offline lab; inspect a real read-only sample only after authorization; demonstrate escalation of an unknown state; acknowledge that E2 is never approval proof. Record capability sign-off using the existing implementation and evidence workbooks. Schedule policy, access and documentation reviews under an approved cadence; initial proposed review is at every material policy, API, ownership, or threat-boundary change, plus a periodic review cadence selected by service owners. Train incident responders separately before privileged execution.

## 7. Handover and change management

An accepted change must include: stable requirement ID, modified document source, policy/ADR implications, affected controls, regression tests, evidence identifiers, owner and reviewer decision, and operational communications. Assign incident escalation and rotation coverage, inventory all installed GitHub App permissions and deployed workflows, link restricted runbooks, and demonstrate a rollback exercise. At handover, unresolved P0 external-authority items remain blockers rather than implicitly accepted risks.
