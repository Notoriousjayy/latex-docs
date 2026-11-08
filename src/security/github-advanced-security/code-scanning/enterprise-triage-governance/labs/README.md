# Synthetic, offline reference laboratories

**Not deployed. No network calls, no privileged tokens, no GitHub mutation, and no active workflow.** The scripts demonstrate classification and traceable evidence, not GitHub merge authorization.

Run from repository root:

```bash
python3 -m unittest discover -s tests -p 'test_enterprise_appsec_governance.py'
python3 src/security/github-advanced-security/code-scanning/enterprise-triage-governance/labs/engine.py --fixture src/security/github-advanced-security/code-scanning/enterprise-triage-governance/labs/synthetic-alert.example.json --policy src/security/github-advanced-security/code-scanning/enterprise-triage-governance/labs/policy.example.json
python3 src/security/github-advanced-security/code-scanning/enterprise-triage-governance/labs/engine.py --fixture src/security/github-advanced-security/code-scanning/enterprise-triage-governance/labs/synthetic-alert.example.json --policy src/security/github-advanced-security/code-scanning/enterprise-triage-governance/labs/policy.example.json --exceptions src/security/github-advanced-security/code-scanning/enterprise-triage-governance/labs/exceptions.example.json
```

- `engine.py`: pure deterministic policy evaluator, exact-scope exception matcher, blocker taxonomy and dry-run delegated review simulation.
- `metrics.py`: baseline metric helpers with explicit denominators and missing-value semantics.
- `synthetic-alert.example.json`: invented alert and repository IDs.
- `policy.example.json`: deliberately unapproved example policy; thresholds are **not** organizational policy.
- `exceptions.example.json`: synthetic E3 authorization fixture for testing only; boolean fixture labels are **not** real cryptographic verification or sufficient production authorization.
- `github-app-permissions.example.json`: conceptual least-privilege read-only collector manifest, not a GitHub App registration schema.
- `readonly-workflow.example.yml`: intentionally outside `.github/workflows`; must undergo security review and pinning before any adoption.

The existing [delegated-review field guide](../../../administration/automating-review-github-advanced-sec-alert.tex) uses illustrative comment-length and reason checks. These are insufficient to approve real dismissal requests. All actual delegated approvals must be independently verified by an authorized reviewer, with an explicit security decision and future executor design.
