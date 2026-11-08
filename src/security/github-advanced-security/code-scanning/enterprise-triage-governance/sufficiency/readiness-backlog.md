# Sufficiency Gates, Decision Review and Remediation Backlog

**Assessment scope:** document content from the cited `main` baseline; no production organization data, tokens, entitlement, approvals or scan results were reviewed. The current architecture is a **proposed reference / synthetic offline PoC**, not an authorized deployed capability.

## Readiness verdict

| Gate | What is required | Result for assessed baseline | Evidence / blocker |
|---|---|---|---|
| L1 — architecture/documentation | Controlled references, requirements traceability, consistent AD/viewpoint/ADRs, independent document review | **Provisional draft; not formally verified** | Canonical references exist; no named enterprise owner, accepted ADR or sign-off |
| L2 — pilot | Named owner/reviewer, authorized scope, read-only API verification, measured baseline, reviewed threat model, negative tests, pilot approval | **Not demonstrated** | Synthetic tests and unfilled workbooks only; no scoped pilot approval or tenant evidence |
| L3 — production | Edition/permissions verification, approved security policy, separation of duties, protected audit/retention, incident drill, change authorization, operational SLOs | **Not demonstrated / no authorization** | No privileged executor or independent go-live review; real behavior unverified |

Only an authorized human review and relevant source-of-truth evidence may change gate status. A GitHub CI success validates checks, not L1 sign-off or a live control.

## Existing ADR decision review

| ADR | Current state | What must be independently resolved |
|---|---|---|
| [APPSEC-001](../../../../../architecture/decisions/appsec-code-scanning/adr-appsec-001-read-only-discovery.tex) | PROPOSED, retain | Actual app/install scopes, collector denial tests and owner acceptance |
| [APPSEC-002](../../../../../architecture/decisions/appsec-code-scanning/adr-appsec-002-deterministic-policy.tex) | PROPOSED, retain | Policy ownership, canonical input/digest contract and risk tolerance |
| [APPSEC-003](../../../../../architecture/decisions/appsec-code-scanning/adr-appsec-003-delegated-review.tex) | PROPOSED, retain | Independent reviewer identity, executor design and production least privilege |

**New ADRs only if decisions become material and unresolved:** evidence store/residency and retention; durable outbox and privileged execution location; component identity/owner authority; GitHub App permissions. Never mark proposed choices `accepted` without recorded authorized action.

## Prioritized delivery backlog (proposed owner roles, not assigned people)

The user stories below extend, rather than replace, the existing [Agile backlog](../references/10-agile-backlog.tex). Story points are relative estimates subject to team calibration. A story is `done` only with working evidence, review and tests; drafting a form alone cannot satisfy it.

| Story / Epic | Priority / points | Responsible role | Depends on | Given / When / Then acceptance | Verification and DoD evidence |
|---|---|---|---|---|---|
| DOC-GOV-01 / Governance | P0 / 5 | Platform service owner | Enterprise sponsor | Given authorized charter scope, when ownership is baselined, then each domain and approval right has an accountable person | Scoped decision-rights record; conflict and unassigned-role test; approved form |
| DOC-GOV-02 / Governance | P0 / 5 | Architecture steward | DOC-GOV-01 | Given an organization/repo census, when components are correlated, then denominators, owners and ambiguous identities are explicit | Independent read-only sample, completeness report, unresolved queue |
| DOC-GOV-03 / Governance | P0 / 3 | AppSec control owner | DOC-GOV-01 | Given candidate rules, when approved, then policy digest, version and authorized reviewer are controlled | Review records; tamper and unauthorized update tests |
| DOC-INT-01 / Integration | P0 / 8 | Discovery engineer | DOC-GOV-02 | Given E1/E2/E3 records, when transformed, then every consumer receives schema, provenance, status and stable IDs | Contract fixtures, schema validation, missing/denied tests |
| DOC-INT-02 / Integration | P0 / 8 | Platform security engineer | DOC-GOV-03 | Given restricted app scope, when privileges are exercised in a pilot, then collector write fails and executor rights are isolated | Permission inventory; negative access and fork-PR trust tests |
| DOC-APP-01 / Security review | P0 / 5 | AppSec reviewer lead | DOC-GOV-03 | Given dismissal requests, when identity and evidence are checked, then self-approval and reason-only approvals are rejected | Reviewer authority evidence; negative fixtures; closed exceptions |
| DOC-APP-02 / Security review | P0 / 5 | GitHub platform engineer | DOC-GOV-02 | Given PR/head and effective ruleset, when diagnosed, then code scanning, checks, reviews and queues are independently classified | Sample read-only PRs and blocker adjudication |
| DOC-SEC-01 / Assurance | P0 / 8 | Security architect | DOC-INT-01/02 | Given validated trust boundaries, when threat tested, then fail-closed cases and detection/containment are evidenced | Threat model, negative matrix, independent security review |
| DOC-OPS-01 / Operations | P0 / 5 | Evidence/records custodian | DOC-GOV-01 | Given all evidence types, when classified, then retention, access, deletion and legal hold are approved | Records schedule and authorization; access/log tests |
| DOC-OPS-02 / Operations | P0 / 5 | Incident response lead | DOC-INT-02, DOC-SEC-01 | Given an incorrect dismissal scenario, when detected, then token isolation, rollback/reopen and cross-branch reconciliation are demonstrated | Timed drill, actor log, observed GitHub state |
| DOC-PILOT-01 / Pilot | P0 / 8 | Platform/AppSec service owners | All prior P0 | Given a read-only baseline and approved nonproduction scope, when shadow mode runs, then precision, missing data and latency measures are reported | Pilot readiness form, metric record, independent go/no-go |
| DOC-PROD-01 / Production | P0 / 8 | Change authority | DOC-PILOT-01 | Given successful pilot and security review, when authorized rollout is proposed, then scope, limits, rollback and audit checks are verifiable | Signed authorization, restrictions, runbook, post-change verification |
| DOC-OPS-03 / Service quality | P1 / 3 | Operations lead | DOC-PILOT-01 | Given trustworthy denominators, when reporting, then targets and error budgets are independently ratified | KPI scorecard and change-controlled SLA/SLO |
| DOC-OPS-04 / Training | P1 / 3 | Platform/AppSec trainers | DOC-OPS-02 | Given role-specific curriculum, when on-call staff are certified, then unknown data and incident cases are escalated correctly | Attendance, practical assessment, handover record |
| DOC-ARC-01 / Decision records | P1 / 3 | Architecture board | DOC-GOV-01 | Given open deployment or storage choices, when decided, then alternatives and reversibility are recorded with authority | Accepted ADR references, independent review, no phantom approvals |
| DOC-AUD-01 / Assurance | P1 / 5 | Audit/ISMS owner | DOC-OPS-01 | Given tailored control applicability, when assessed, then every control has evidence, exception and tested outcome | Evidence/controls crosswalk; no compliance assertion from a link |

For each story, implementation tasks are: enumerate exact in-scope identities; update appropriate canonical document or form; implement the independent positive and negative verification case; retain reviewer identity and immutable version in restricted records; revise impacted architecture diagrams/ADRs; report unresolved evidence. Maintain sprint ownership and status in the project's actual work tracker if provisioned; no Taiga project is created here.

## Story-level implementation tasks and explicit Definition of Done

Each story below uses the corresponding table row for owner role, priority, points, dependencies and Given/When/Then acceptance. The following activities and controls are **additional requirements**, not evidence that the story has been executed.

| Story | Implementation tasks | Story-specific DoD |
|---|---|---|
| DOC-GOV-01 | Obtain sponsor scope; identify control owners; map delegated authority; check conflicting decisions; approve charter | Charter and conflict review signed by authorized sponsor |
| DOC-GOV-02 | Query authorized read-only inventory; reconcile repo IDs and monorepo components; sample ownership with independent owner | Versioned census, gaps and owner attestations independently reviewed |
| DOC-GOV-03 | Draft deterministic policy ownership; bind version/digest; define protected update workflow; test unauthorized edits | Accepted rule bundle, change record and negative integrity test |
| DOC-INT-01 | Establish data schema; bind source version and status; validate E1/E2/E3; test missing/ambiguous links | Reviewed producer/consumer schema, contract tests and missing-state evidence |
| DOC-INT-02 | Inspect installation permission matrix; split collector/executor identities; test denied writes; verify fork PR trust | Security-approved installation record with negative privilege tests |
| DOC-APP-01 | Map delegated review APIs and roles; verify request/reviewer identity; test weak reason and self approval | Evidence-backed delegated review decision procedure and adversarial test |
| DOC-APP-02 | Sample blocked PRs; compare status checks, code scan merge rule, review and queue; adjudicate ambiguity | Blocker confusion matrix, sample evidence and approved routing |
| DOC-SEC-01 | Threat model untrusted data and policy changes; assess STRIDE threats; execute denial and replay cases | Independent threat-model findings, closure status and risk owner review |
| DOC-OPS-01 | Inventory evidence classes; select restricted retention store; set access/logging/legal hold rules; test retrieval | Approved records schedule and verified audit access test |
| DOC-OPS-02 | Simulate incorrect dismissal; suspend future executor; trace branches; rehearse authorized reopening and log reconciliation | Timed signed exercise with GitHub-observed correction and remaining gaps |
| DOC-PILOT-01 | Establish scope and cohort; collect before metrics; run shadow policy and reviewer comparison; approve exit gate | Signed pilot form with missed-data and incorrect-decision counts |
| DOC-PROD-01 | Verify L2 evidence; audit executor and token rights; test rollback and alarms; acquire change decision | Written production authorization and independently observed activation/reversal |
| DOC-OPS-03 | Select explicit latency/quality denominators; define SLO window and exclusions; review with owners | Approved baseline and targets with reproducible query definitions |
| DOC-OPS-04 | Build role training; run synthetic triage and incident practical; verify escalation route | Signed competency review and named trained backups |
| DOC-ARC-01 | Consolidate proposal alternatives; assess impact on schema/storage/executor; convene architecture review | Recorded accept/reject decision with reversibility and owner |
| DOC-AUD-01 | Obtain applicable standards baseline; map each chosen control to tested evidence; conduct gap review | Tailored control matrix with observed evidence, auditor/ISMS review and open findings |

No item is closed merely because its form, code snippet or synthetic fixture exists. Evidence must be stored in an authorized restricted system and referenced by opaque record ID in public documentation.

## Existing Template–Blank instruments reused

Discovery (four pairs): AD, viewpoint, implementation workbook, evidence and validation workbook. AppSec (twelve pairs): merge-blocker assessment, repository policy profile, automated decision record, false-positive validation, dismissal review, risk acceptance, privileged access review, threat model, control evidence crosswalk, pilot readiness, evidence validation, effectiveness scorecard. These sixteen pairs cover the requested operational forms at **design level**, so no new printable pairs are justified until a concrete missing record is identified and reviewed. Forms remain unfilled and never constitute sign-off.

## Open P0 facts that cannot be inferred from a public documentation repository

No authorized org and tenancy census; no application-owner attestation; no policy/risk approval; no actual GitHub App installation/permission proof; no independently confirmed delegated-review entitlement by edition; no measurable live PR/alert sample; no signed data retention and audit custody; no tested cross-branch recovery; no accepted ADR or go-live/change authorization. Each maps to a P0 story above and must be collected through appropriate private channels before the corresponding gate can pass.
