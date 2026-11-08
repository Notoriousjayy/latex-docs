"""Offline, deterministic AppSec governance reference. NO NETWORK OR MUTATION.

Decisions are advisory. GitHub checks, reviews and rulesets remain authoritative.
The input object is untrusted; even an exception match never changes an alert.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DECISIONS = (
    "ALLOW_MERGE", "FIX_REQUIRED", "AUTO_TRIAGE", "EXCEPTION_CANDIDATE",
    "DISMISSAL_REQUEST_REQUIRED", "APPSEC_REVIEW_REQUIRED",
    "RISK_ACCEPTANCE_REQUIRED", "INSUFFICIENT_EVIDENCE",
    "SCAN_INCOMPLETE", "POLICY_ERROR",
)
SEVERITY = {"low": 1, "medium": 2, "high": 3, "critical": 4}
SCAN_STATES = {"complete", "in_progress", "missing", "failed", "unknown"}
REQUIRED = ("repo_id", "head_sha", "policy_version", "scan_status", "alerts")


def canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def digest(data: Any) -> str:
    return hashlib.sha256(canonical(data).encode("utf-8")).hexdigest()


def _utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamp must be timezone aware")
    return dt.astimezone(timezone.utc)


def classify_merge_blockers(observation: dict[str, Any]) -> list[str]:
    """Distinct read-only indications; does not assert a real GitHub merge status."""
    blockers: list[str] = []
    if observation.get("required_review") == "pending":
        blockers.append("REQUIRED_REVIEW")
    if observation.get("required_check_state") in {"failed", "missing", "pending"}:
        blockers.append("REQUIRED_CHECK")
    if observation.get("ruleset_state") in {"blocking", "unknown"}:
        blockers.append("CODE_SCANNING_RULESET")
    if observation.get("dismissal_request_state") == "pending":
        blockers.append("DISMISSAL_REQUEST")
    if observation.get("merge_queue_state") in {"blocked", "unknown"}:
        blockers.append("MERGE_QUEUE")
    if observation.get("conflict") is True:
        blockers.append("MERGE_CONFLICT")
    return blockers


def valid_exception(alert: dict[str, Any], observation: dict[str, Any],
                    exception: dict[str, Any], now: str,
                    approved_policy_version: str) -> bool:
    """Matching eligibility is advisory; not proof an API action is authorized."""
    try:
        if not isinstance(exception, dict) or exception.get("status") != "approved":
            return False
        if exception.get("evidence_class") != "E3":
            return False
        if exception.get("independent_verification") is not True:
            return False
        if not exception.get("evidence_ref") or not exception.get("approval_id"):
            return False
        approver = exception.get("approver")
        requester = observation.get("requester")
        if not approver or not requester or approver == requester:
            return False
        keys = (
            ("repo_id", observation.get("repo_id")),
            ("head_sha", observation.get("head_sha")),
            ("rule_id", alert.get("rule_id")),
            ("fingerprint", alert.get("fingerprint")),
            ("tool", alert.get("tool")),
            ("component", alert.get("component")),
        )
        if any(not expected or exception.get(key) != expected for key, expected in keys):
            return False
        if exception.get("policy_version") != approved_policy_version:
            return False
        if not exception.get("approved_at") or not exception.get("expires_at"):
            return False
        return _utc(exception["approved_at"]) <= _utc(now) < _utc(exception["expires_at"])
    except (ValueError, TypeError, KeyError):
        return False


def evaluate(observation: dict[str, Any], policy: dict[str, Any],
             exceptions: list[dict[str, Any]] | None = None,
             now: str = "2026-11-08T00:00:00Z") -> dict[str, Any]:
    """Pure policy recommendation; cannot approve/dismiss or mark a check successful."""
    exceptions = exceptions or []
    def result(decision: str, reason: str, alert: dict[str, Any] | None = None):
        out = {
            "decision": decision,
            "reason": reason,
            "repo_id": observation.get("repo_id"),
            "head_sha": observation.get("head_sha"),
            "policy_version": policy.get("version"),
            "policy_digest": digest(policy),
            "input_digest": digest(observation),
            "alert_number": alert.get("number") if alert else None,
            "merge_authority": "GitHub rulesets, checks, reviews and queue",
            "mutation_permitted": False,
        }
        out["decision_digest"] = digest(out)
        return out

    if not isinstance(observation, dict) or not isinstance(policy, dict):
        return {"decision": "POLICY_ERROR", "reason": "invalid envelope", "mutation_permitted": False}
    if (not policy.get("version") or not policy.get("id") or
            any(key not in observation or observation[key] in (None, "") for key in REQUIRED) or
            observation.get("policy_version") != policy.get("version")):
        return result("POLICY_ERROR", "missing or mismatched required policy/input schema")
    if (not isinstance(observation["alerts"], list) or
            observation.get("scan_status") not in SCAN_STATES or
            not isinstance(policy.get("required_tools"), list) or
            not policy.get("required_tools")):
        return result("POLICY_ERROR", "malformed alerts, scans or required tool configuration")
    if (observation["scan_status"] != "complete" or
            not set(policy["required_tools"]).issubset(
                set(observation.get("completed_tools", [])))):
        return result("SCAN_INCOMPLETE", "required tool or analysis not successfully completed")
    if observation.get("coverage_status") != "complete":
        return result("INSUFFICIENT_EVIDENCE", "repository coverage incomplete or unknown")
    if observation.get("required_check_state") not in ("success", "not_required"):
        return result("INSUFFICIENT_EVIDENCE", "required check not confirmed successful")
    if observation.get("ruleset_state") not in ("enforced", "none"):
        return result("INSUFFICIENT_EVIDENCE", "effective ruleset not verified")
    if observation.get("required_review") == "pending":
        return result("APPSEC_REVIEW_REQUIRED", "independent PR reviewer still required")
    if observation.get("required_review") not in ("complete", "not_required"):
        return result("INSUFFICIENT_EVIDENCE", "PR review state not verified")
    if observation.get("conflict") or observation.get("merge_queue_state") == "blocked":
        return result("INSUFFICIENT_EVIDENCE", "merge mechanics remain blocked")

    threshold = policy.get("blocking_severity", "high")
    if threshold not in SEVERITY:
        return result("POLICY_ERROR", "unknown severity threshold")
    for alert in observation["alerts"]:
        if not isinstance(alert, dict):
            return result("INSUFFICIENT_EVIDENCE", "untyped alert")
        if not all(alert.get(k) for k in ("rule_id", "fingerprint", "tool", "component", "severity")):
            return result("INSUFFICIENT_EVIDENCE", "missing stable alert identity")
        if alert["severity"] not in SEVERITY:
            return result("INSUFFICIENT_EVIDENCE", "unknown alert severity")
        if alert.get("new_in_pr") is not True:
            if alert.get("new_in_pr") is not False:
                return result("INSUFFICIENT_EVIDENCE", "diff relevance unknown", alert)
            continue
        if SEVERITY[alert["severity"]] < SEVERITY[threshold]:
            continue
        if observation.get("requested_reason") == "wont_fix":
            return result("RISK_ACCEPTANCE_REQUIRED", "genuine risk requires formal authorized acceptance", alert)
        for exception in exceptions:
            if valid_exception(alert, observation, exception, now, policy["version"]):
                return result("EXCEPTION_CANDIDATE",
                              "exact approved exception matches; independent execution still required", alert)
        if observation.get("requested_reason") in {"false_positive", "used_in_tests"}:
            return result("APPSEC_REVIEW_REQUIRED", "technical validation and delegated review needed", alert)
        return result("FIX_REQUIRED", "new actionable blocking finding without approved exception", alert)

    if observation["alerts"]:
        return result("AUTO_TRIAGE", "no newly introduced blocking finding in evaluated set; retain other alerts")
    return result("ALLOW_MERGE", "no evaluated blocking findings; GitHub still enforces remaining controls")


def simulate_delegated_review(request: dict[str, Any], approver: str) -> dict[str, Any]:
    """Never sends PATCH. Human must verify authority and evidence outside this simulation."""
    if (not approver or approver == request.get("requester") or
            request.get("evidence_class") != "E3" or
            request.get("independently_verified") is not True):
        outcome = "ESCALATE"
    else:
        outcome = "REVIEW_ELIGIBLE"
    return {"mode": "dry-run", "recommended_route": outcome,
            "api_called": False, "request_digest": digest(request)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--exceptions", type=Path)
    parser.add_argument("--at", default="2026-11-08T00:00:00Z")
    args = parser.parse_args()
    observation = json.loads(args.fixture.read_text(encoding="utf-8"))
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    exceptions = (json.loads(args.exceptions.read_text(encoding="utf-8"))
                  if args.exceptions else [])
    print(json.dumps(evaluate(observation, policy, exceptions, args.at), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
