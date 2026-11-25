# Operational runbook

## Intake and dispatch
1. Validate owner, classification, repository and base commit; specify allowed effects, tests, risk tier and deadline.
2. Verify pinned CLI/SDK version and approved skills/tools. Allocate an ephemeral environment without production credentials. Record effective policy and check egress.
3. Dispatch the bounded task. Stop on authorization denial, budget exhaustion or unexpected side effects.

## Verification and handoff
1. Collect candidate diff and digest, sanitized events and independent check results. Reject missing evidence and edits to protected files. Do not rely on model claims.
2. Review candidate against requirements. An authorized reviewer must approve the exact digest, operation and target. Any candidate change invalidates approval.
3. Use a protected PR and separate release identity. The local prototype ends at awaiting_human_review; no automated approval or deployment is implemented.

## Failure and incident response
- Test failure: allow a bounded repair; preserve the original checks. Escalate if the budget is exhausted.
- Policy denial: stop, record and refer to the policy owner. Do not retry with elevated permissions.
- Suspected injection or exfiltration: terminate the isolated worker, revoke scoped credentials, quarantine artifacts, preserve redacted evidence and notify security. Assess downstream effects before rerun.
- Stale baseline or conflicting changes: obtain a new approved task contract and reverify against the new base.
- Rollback: use the organization-approved revert/release procedure and independent checks; never force-push as a recovery shortcut.

## Ownership
Task sponsor owns requirements; platform owner owns sandbox and credentials; verification owner owns checks; security owner handles incidents; release owner owns deployment approvals. Retain sanitized task and candidate evidence according to applicable retention policy.
