# Integrated Architecture and Control Traceability

**Status: proposed design / not deployed.** This crosswalk refines, but does not replace, the [Architecture Discovery guide](../../../../../architecture/technical-documents/github-actions-architecture-discovery-enterprise-scale.tex), [AppSec Architecture Description](../../../../../architecture/technical-documents/enterprise-appsec-code-scanning-architecture-description.tex), [AppSec viewpoint](../../../../../architecture/technical-documents/enterprise-appsec-code-scanning-viewpoint-specification.tex), [policy design](../references/03-policy-as-code.tex), or [GitHub integration guide](../references/05-github-integration.tex).

## 1. Processing and authority boundaries

```text
Authorized organization/repository scope
    | read-only, scope-filtered API collection (E1)
    v
Architecture Discovery inventory and evidence ledger
    | immutable revision and collection provenance; E2 marked inferred
    v
Versioned discovery-to-AppSec envelope -> coverage/status normalization
    | no write token, no approval grants
    v
Alert / PR / effective ruleset enrichment (untrusted until verified)
    |
    v
Deterministic policy evaluator (advisory decision + abstain)
    | no mutation; policy digest, input digest, decision reason
    v
Human independent review and independently verified exception authority
    |
    v
Separately provisioned privileged executor (DESIGN ONLY, not implemented)
    | fresh GitHub preconditions + explicit authorization + audit outbox
    v
GitHub API as source of truth -> read-after-write reconciliation
    |
    v
Immutable evidence/metrics/drift monitoring and incident escalation
```

Collector and evaluator permissions must be read-only. A contributor-controlled branch, event payload, generated summary, check output, E2 inference or an AI classification is **never** a signing authority. Write-capable integration must be separately approved, isolated and tested. GitHub (its effective rulesets, reviews, checks, queue, and code scanning merge protection) alone determines merge eligibility.

## 2. Proposed versioned data contract (do not treat as implemented API)

`discovery_envelope_v1` MUST encode:
- `schema_version`, `collection_id`, `collected_at_utc`, `collector_version`, `source_uri`, `source_commit_sha`, `source_ref`, `repo_node_id`, `repo_full_name_at_collection`.
- `organization_node_id`, `workflow_path`, `workflow_revision`, `component_id`, `application_id` (nullable), `declared_owner_id` (nullable); declare the identifier authority and collision/reassignment behavior for every field.
- `relation_id`, `relation_kind`, `evidence_class` (E1 observed, E2 inferred, E3 externally verified), `extraction_rule_version`, `confidence` (for E2 only), `source_digest`, `evidence_uri`, `corroboration_uri` (for E3), `verification_actor_or_system` (when verified).
- `collection_status` = complete | partial | denied | missing | truncated | stale | parse_error | unsupported; `access_scope` and `completeness_denominator`. **Never interpret an unavailable record as an absent record.**

`appsec_decision_envelope_v1` MUST additionally bind:
- Repository stable ID, PR ID/number, `base_sha`, `head_sha`, alert identity and analysis key, tool/pack version, rule and fingerprint, observed alert state and `observed_at_utc`.
- Scan completion per required tool and ref; independent categories for required reviews, checks, effective branch/ruleset merge protection, merge queue, and delegated dismissal request.
- Policy ID/version/digest, exception ID/status/exact scope/expiry, independent authority evidence URI, request actor, reviewer actor, evaluation time.
- Canonical input digest; `decision`, rule version, causal reasons, `abstention_reason`, observation time, result expiry and audit correlation ID.
- The source provenance and uncertainty of each enrichment. An E2 inference cannot be promoted to E3 by joining with another inferred dataset.

**Illustrative keys are design obligations, not proof these fields are accessible in every GitHub edition/API.** Security architects must approve schema and allowed payload classification before a pilot. No private source paths or raw vulnerable code belong in the public documents.

## 3. Contract and control crosswalk

| Trace ID | Origin -> consumer | Contract / invariant | Primary source | Failure and verification |
|---|---|---|---|---|
| INT-01 | Scope authority -> collector | Only explicitly authorized installation/repository scopes; stable repository IDs | Discovery implementation workbook; AppSec integration guide | Denied/scope drift -> abstain; test unauthorized repository |
| INT-02 | Collector -> graph catalog | E1 path/revision; E2 rule + uncertainty; E3 corroboration; complete denominators | Discovery guide; Discovery viewpoint | Missing/duplicate/ambiguous relations are unresolved, never zero |
| INT-03 | Graph -> alert enricher | Repository/component/owner mapping is advisory; E2 cannot authorize dismissal | Discovery evidence workbook; AppSec AD | Incomplete owner mapping routes to stewardship |
| INT-04 | GitHub -> alert/PR adapters | PR head/base, alert instance, scan ref, configured checks and rules are observed separately | Merge-blocker reference; integration guide | API denial, stale ref or missing tool -> abstain |
| INT-05 | Adapters -> policy evaluator | Versioned canonical input and policy hashes; deterministic precedence | Policy-as-code reference; offline engine tests | Unknown, policy mismatch and stale decisions cannot write |
| INT-06 | Policy -> delegated review | Review route, not self-approval; verified authority and evidence independent of requester | Delegated-dismissal reference; dismissal-review form | Reject self approval, weak reason tests, scope mismatch |
| INT-07 | Authorized review -> future executor | Executor is separate identity with narrow permissions and fresh precondition checks | Privileged access review; ADR-003 | No executor exists in repo; pilot must prove token isolation |
| INT-08 | Executor -> GitHub | Idempotent correlation, audited outcome, read-after-write and cross-branch impact | GitHub integration guide; operations playbook | Conflicts/retries never silently claim success |
| INT-09 | Audit -> KPI and incident review | Versioned immutable receipt, actor and denominator; redact sensitive payload | KPI reference; evidence form | Missing denominator or unverifiable provenance -> unreported |
| INT-10 | Operations -> architecture governance | Owner reconciliation, exception expiry, control drift, ADR impact review | Operations playbook; readiness backlog | Unknown owner and unauthorized changes escalate |

## 3A. End-to-end requirement and evidence chains

The row IDs below connect the [requirements matrix](requirements-matrix.csv) to the [document register](document-register.csv). The `INT` crosswalk names logical controls, not installed enforcement mechanisms. Proposed ADRs remain unaccepted, and a cited form is never a completed evidence record.

| Business outcome → requirement | Component / proposed ADR | Control obligation | Operating procedure | Test → evidence record | Accountable role |
|---|---|---|---|---|---|
| Authorized coverage → GOV-05, DISC-01, INT-01 | Scope collector / APPSEC-001 | Restrict API scope; preserve denial/missing denominators | Discovery phase 0–1 implementation workbook | VER-01, VER-02 → approved installation and census record | Platform service owner |
| Trustworthy dependency map → DISC-03, DISC-04, INT-02 | E1/E2/E3 graph / APPSEC-001 | No E2 promotion to unproven E3 or dismissal authority | Discovery evidence/validation workbook | VER-03 → corroborated sampling record | Architecture steward |
| Reproducible decision → APP-03, APP-04, INT-05 | Deterministic evaluator / APPSEC-002 | Pinned inputs, policy digest, unknown-state abstention | Policy reference and decision-record form | VER-07, VER-09 → input/policy/evaluation digest | AppSec control owner |
| Correct merge diagnosis → MERGE-01, MERGE-02, INT-04 | Blocker adapter / APPSEC-002 | Separate scan rulesets, required checks, reviews and queue | Merge-blocker reference and root-cause form | VER-05 → read-only PR adjudication | GitHub platform owner |
| Independently authorized exception → DISM-01, DISM-02, INT-06 | Reviewer queue / APPSEC-003 | No reason-only or self approval; verify reviewer authority | Delegated dismissal reference and reviewer form | VER-06 → signed decision and entitlement proof | AppSec reviewer lead |
| Controlled execution boundary → DISM-05, PLAT-04, INT-07 | Future isolated executor / APPSEC-003 | Short-lived privilege; revalidate current state | Privileged access review and authorized change record | VER-01, VER-12 → negative scope test and approval | Platform security owner |
| Recover from wrongful disposition → OPS-04, SEC-04, INT-08 | Incident containment and reconciliation | Pause executor, trace branch effects, authorized corrective action | Operations playbook and threat model | VER-08 → witnessed incident/rollback drill | Incident response lead |
| Verifiable control effectiveness → EVID-02, KPI-02, INT-09 | Restricted audit and KPI pipeline | Immutable provenance, privacy, valid denominators | Evidence workbook and effectiveness scorecard | VER-09, VER-10 → restricted audit record and sampled metrics | Records custodian / AppSec owner |

Do not regard these links as proof that any restricted enterprise record exists. Assign actual approved identifiers only after deployment/tenant access is independently authorized.

## 4. GitHub security control distinctions

A PR may have simultaneously outstanding: (a) GitHub code scanning ruleset merge protection; (b) required status checks, including workflow success; (c) required human reviews; (d) queue or merge-group obligations; (e) a pending delegated dismissal review. They must be measured and resolved **independently**. Dismissing a code scanning alert can affect all branches; it is not a PR-local exception and cannot repair a failed scan or unrelated status check. Verify actual configuration read-only per target repository/edition.

## 5. Fail-closed / reconciliation contract

- **403/404 permissions:** distinguish inaccessible/unsupported from absent. Never automatically dismiss.
- **429/secondary rate-limit:** bounded backoff, checkpoint per identity, eventual retry and explicit stale-coverage metric. Avoid unbounded loops.
- **Conflicting evaluations:** bind decision to input/policy digest; recompute on new head SHA, scanner result, rule change, exception expiry or configuration drift.
- **Concurrency:** immutable idempotency key = exact subject + authorized operation + approved policy revision; execute with a state/version comparison and audit outbox. A retry does not independently create a new approval.
- **Recovery:** disable executor first, preserve evidence and impacted identity list, evaluate cross-branch alert state, obtain independent corrective approval, execute authorized reopen/reversal, verify observed GitHub state.
- **Data handling:** secrets, private paths, vulnerability exploit evidence and personal details remain in restricted evidence stores with enterprise-approved retention, not this Git repository.

## 6. Standards applicability (mapping only; no conformance claim)

| Framework | Relevant concept / use | Evidence needed before claiming effectiveness |
|---|---|---|
| NIST SSDF (SP 800-218) | Secure development, vulnerability response, integrity of evidence and tools | Reviewed workflow/control implementation and test results |
| NIST SP 800-53 | AC least privilege, AU audit accountability, CM configuration, RA risk, IR incident response | Approved tailored control baseline plus operating evidence |
| OWASP SAMM | Governance, design, implementation and verification maturity | Evidence-backed maturity assessment with named process owners |
| MITRE ATT&CK | Adversary behaviors such as credential abuse and CI pipeline compromise inform threat scenarios | Explicit technique-to-threat and mitigation mapping; not compliance |
| ISO/IEC 27001 and 27002 | ISMS risk governance, supplier/system access, logging and incident handling | Licensed/current applicable controls, SoA and audit proof maintained by authorized ISMS team |

The relevant enterprise policies, applicability and legal retention duties are **unverified**. Do not infer that a framework list constitutes certification.
