# Verification and Evidence Protocol

**Status:** specification of tests and evidence obligations, not results from a live enterprise system. Report actual CI run IDs only after fetching their status.

## 1. Reproducible repository verification

From the repository root:

```bash
python3 tooling/scripts/validate_artifact_pairs.py
python3 tooling/scripts/semantic_content_audit.py --check
python3 tooling/scripts/build_semantic_catalogs.py --check
python3 tooling/scripts/plantuml_lint.py
python3 -m unittest discover -s tests -p 'test_enterprise_discovery_suite.py'
python3 -m unittest discover -s tests -p 'test_enterprise_appsec_governance.py'
python3 -m unittest discover -s tests -p 'test_enterprise_github_sufficiency.py'
make preflight
make build-category-architecture
make build-category-security
```

The new matrix contract test detects malformed row IDs, missing canonical source paths, duplicate requirements and unsupported readiness assertions. Its pass does **not** prove field-level sufficiency or correct GitHub permissions. The existing security/offline engine suite covers deterministic classification and synthetic negative paths only. Use repository CI and approved tools to record actual LaTeX compilation outcomes.

## 2. Source-backed verification cases

| Test ID | Question | Required observation | Repository artifact for record |
|---|---|---|---|
| VER-01 | Is the collector read-only and scope-limited? | Effective GitHub App installation rights and negative write test | Discovery implementation workbook; privileged access form |
| VER-02 | Is inventory complete with sound denominators? | Authorized census, successful API inventory, missing/denied/stale counts | Discovery evidence workbook |
| VER-03 | Are E2 inferences separated from E3 verification? | Independent relationship sample, rule versions, corroboration proof | Discovery viewpoint and evidence workbook |
| VER-04 | Are critical alerts evaluated with correct source/analysis revision? | Real read-only alert sample and pinned PR/head SHA | AppSec evidence validation workbook |
| VER-05 | Are separate merge controls correctly diagnosed? | Effective rulesets, check runs, reviews and queue sample | Merge blocker root cause form |
| VER-06 | Does reviewer authority prevent self-approval? | Effective reviewer roles, negative self-approval test in approved pilot | Dismissal review and privileged access forms |
| VER-07 | Does invalid/missing evidence abstain? | Negative fixtures plus data-denied pilot test | Automated triage decision record |
| VER-08 | Can an incorrect disposition be detected and contained? | Controlled incident/rollback drill with affected branches | Threat model and pilot readiness forms |
| VER-09 | Are evidence and policies immutable enough for audit? | Controlled policy digest, outbox/audit integrity and access validation | Control-to-evidence crosswalk |
| VER-10 | Are error budgets/SLOs derived from observed denominators? | Sample-period dataset, rulebook and owner-approved targets | Effectiveness scorecard |
| VER-11 | Are version/edition API permissions compatible? | Official product spec, actual tenant, permissions and feature availability | Integration guide and privileged access review |
| VER-12 | Is the change authorized? | Signed roles, ADR decision evidence, approved pilot/production change | Pilot readiness and risk acceptance forms |

For each case capture: authorized environment, unique test ID, tester and independent reviewer, source commit, subject IDs, observed UTC time, actual/expected result, redacted evidence URI, digest, API edition/version, exception status, and conclusion PASS/FAIL/UNTESTED. **Do not populate this repository with real alert details or privileged identifiers.**

## 3. Sufficiency calculation and gating

The [requirements matrix](requirements-matrix.csv) provides a **document coverage** estimate, not an assertion that controls work. Report total and P0 counts by `coverage` and `operational_evidence`; no single numeric percentage is an adequate production readiness proof. A P0 `partial` or `missing` cannot disappear without a reviewed canonical source change. Any P0 external requirement with `unverified` evidence is a pilot/production blocker until satisfied by authorized observation.

When calculating readiness:
- L1: all applicable P0 document requirements covered and reviewed, with consistent references and accepted relevant ADRs.
- L2: L1 plus real scoping/owner authority, read-only API proof, pilot permission and measured baseline, positive/negative test evidence, signed pilot gate.
- L3: L2 plus separately authorized executor, immutable audit/evidence custody, tested recovery, demonstrated least privilege, performance/security validation and signed production change.
- An unfilled Template/Blank, a test run over synthetic examples, and an unaccepted ADR never satisfy an approval gate.

## 4. Documentation maintenance and change impact

Every controlled source change must update requirement IDs, canonical paths, owner/reviewer roles, ADR implications, evidence test IDs, and open findings. Run all applicable categories. Preserve source-controlled LaTeX as canonical; PDFs are derivative. For a new LaTeX root, update the semantic inventory and generated catalogs and validate standalone compilation. For any rendered PNG/SVG leaf, retain a navigable README. Never weaken taxonomy, pair, style or build checks to obtain a green CI.
