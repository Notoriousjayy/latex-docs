"""Regression and adversarial checks for the offline companion reference."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "src/security/github-advanced-security/code-scanning/enterprise-triage-governance"
LABS = SUITE / "labs"
sys.path.insert(0, str(LABS))
import engine  # noqa: E402
import metrics  # noqa: E402

POLICY = json.loads((LABS / "policy.example.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((LABS / "synthetic-alert.example.json").read_text(encoding="utf-8"))
EXCEPTIONS = json.loads((LABS / "exceptions.example.json").read_text(encoding="utf-8"))


class OfflinePolicyTests(unittest.TestCase):
    def e(self, **changes):
        obs = copy.deepcopy(SAMPLE)
        obs.update(changes)
        return engine.evaluate(obs, POLICY)

    def test_no_alerts_advisory_merge(self):
        r = self.e(alerts=[])
        self.assertEqual("ALLOW_MERGE", r["decision"])
        self.assertFalse(r["mutation_permitted"])
        self.assertIn("GitHub", r["merge_authority"])

    def test_actionable_high_requires_fix(self):
        obs = copy.deepcopy(SAMPLE)
        obs.pop("requested_reason")
        self.assertEqual("FIX_REQUIRED", engine.evaluate(obs, POLICY)["decision"])

    def test_unknown_scan_blocks(self):
        self.assertEqual("SCAN_INCOMPLETE", self.e(scan_status="unknown")["decision"])

    def test_missing_required_tool_blocks(self):
        self.assertEqual("SCAN_INCOMPLETE", self.e(completed_tools=[])["decision"])

    def test_failed_scan_blocks(self):
        self.assertEqual("SCAN_INCOMPLETE", self.e(scan_status="failed")["decision"])

    def test_unknown_coverage_abstains(self):
        self.assertEqual("INSUFFICIENT_EVIDENCE", self.e(coverage_status="denied")["decision"])

    def test_pending_review_is_separate_block(self):
        self.assertEqual("APPSEC_REVIEW_REQUIRED", self.e(required_review="pending")["decision"])

    def test_required_check_is_separate_block(self):
        self.assertEqual("INSUFFICIENT_EVIDENCE", self.e(required_check_state="failed")["decision"])

    def test_not_required_check_is_not_a_blocker(self):
        self.assertEqual("ALLOW_MERGE", self.e(alerts=[], required_check_state="not_required")["decision"])

    def test_unknown_review_abstains(self):
        self.assertEqual("INSUFFICIENT_EVIDENCE", self.e(alerts=[], required_review="unknown")["decision"])

    def test_unknown_ruleset_abstains(self):
        self.assertEqual("INSUFFICIENT_EVIDENCE", self.e(ruleset_state="unknown")["decision"])

    def test_false_positive_claim_not_approved(self):
        self.assertEqual("APPSEC_REVIEW_REQUIRED", self.e()["decision"])

    def test_wont_fix_not_false_positive(self):
        self.assertEqual("RISK_ACCEPTANCE_REQUIRED", self.e(requested_reason="wont_fix")["decision"])

    def test_nonblocking_alert_remains_triaged(self):
        obs = copy.deepcopy(SAMPLE)
        obs["alerts"][0]["severity"] = "low"
        self.assertEqual("AUTO_TRIAGE", engine.evaluate(obs, POLICY)["decision"])

    def test_exact_exception_is_candidate_not_dismissal(self):
        r = engine.evaluate(copy.deepcopy(SAMPLE), POLICY, EXCEPTIONS)
        self.assertEqual("EXCEPTION_CANDIDATE", r["decision"])
        self.assertFalse(r["mutation_permitted"])

    def test_expired_exception_rejected(self):
        r = engine.evaluate(SAMPLE, POLICY, EXCEPTIONS, "2026-12-01T00:00:00Z")
        self.assertEqual("APPSEC_REVIEW_REQUIRED", r["decision"])

    def test_mismatched_head_rejected(self):
        r = engine.evaluate(dict(SAMPLE, head_sha="another-commit"), POLICY, EXCEPTIONS)
        self.assertNotEqual("EXCEPTION_CANDIDATE", r["decision"])

    def test_mismatched_fingerprint_rejected(self):
        obs = copy.deepcopy(SAMPLE)
        obs["alerts"][0]["fingerprint"] = "other-fingerprint"
        self.assertNotEqual("EXCEPTION_CANDIDATE", engine.evaluate(obs, POLICY, EXCEPTIONS)["decision"])

    def test_cross_repository_scope_rejected(self):
        self.assertNotEqual("EXCEPTION_CANDIDATE", engine.evaluate(dict(SAMPLE, repo_id=202), POLICY, EXCEPTIONS)["decision"])

    def test_self_approval_rejected(self):
        exc = copy.deepcopy(EXCEPTIONS)
        exc[0]["approver"] = SAMPLE["requester"]
        self.assertNotEqual("EXCEPTION_CANDIDATE", engine.evaluate(SAMPLE, POLICY, exc)["decision"])

    def test_missing_e3_verification_rejected(self):
        exc = copy.deepcopy(EXCEPTIONS)
        exc[0]["evidence_class"] = "E2"
        self.assertNotEqual("EXCEPTION_CANDIDATE", engine.evaluate(SAMPLE, POLICY, exc)["decision"])

    def test_policy_version_mismatch(self):
        self.assertEqual("POLICY_ERROR", self.e(policy_version="changed-in-pr")["decision"])

    def test_missing_policy_id(self):
        p = dict(POLICY, id="")
        self.assertEqual("POLICY_ERROR", engine.evaluate(SAMPLE, p)["decision"])

    def test_identical_input_stable_evidence(self):
        first = engine.evaluate(SAMPLE, POLICY)
        second = engine.evaluate(copy.deepcopy(SAMPLE), dict(POLICY))
        self.assertEqual(first["decision_digest"], second["decision_digest"])

    def test_blocker_taxonomy_not_equivalent_to_alerts(self):
        b = engine.classify_merge_blockers({"required_review": "pending",
             "required_check_state": "failed", "dismissal_request_state": "pending"})
        self.assertEqual(["REQUIRED_REVIEW", "REQUIRED_CHECK", "DISMISSAL_REQUEST"], b)

    def test_delegated_review_simulation_has_no_patch(self):
        r = engine.simulate_delegated_review(
            {"requester": "dev", "evidence_class": "E3",
             "independently_verified": True}, "independent-appsec")
        self.assertEqual("REVIEW_ELIGIBLE", r["recommended_route"])
        self.assertFalse(r["api_called"])

    def test_delegated_review_self_approval_rejected(self):
        r = engine.simulate_delegated_review({"requester":"dev"}, "dev")
        self.assertEqual("ESCALATE", r["recommended_route"])

    def test_metrics_are_noncausal_and_bounded(self):
        r = metrics.summary([10, 30, 50, 70], 10, 3, 20, 1)
        self.assertEqual(0.3, r["blocked_pr_rate"])
        self.assertEqual(0.05, r["incorrect_dismissal_sample_rate"])
        self.assertEqual(40.0, r["wait_median_minutes"])
        self.assertIn("no causal claim", r["caveat"])

    def test_all_pairs_registered_and_printable(self):
        data = json.loads((ROOT / "tooling/manifests/reusable-artifact-pairs.json").read_text(encoding="utf-8"))
        pairs = [p for p in data["pairs"] if "/enterprise-triage-governance/forms/" in p["template"]]
        self.assertEqual(12, len(pairs))
        for p in pairs:
            with self.subTest(pair=p["id"]):
                template = (ROOT / p["template"]).read_text(encoding="utf-8")
                blank = (ROOT / p["blank"]).read_text(encoding="utf-8")
                self.assertIn(r"\documentclass", blank)
                self.assertIn(r"\rule{", blank)
                self.assertNotEqual(template, blank)
                self.assertNotIn("[TODO]", blank)
                self.assertNotIn("[To complete]", blank)

    def test_workflow_example_is_not_active(self):
        self.assertFalse((ROOT / ".github/workflows/readonly-workflow.example.yml").exists())
        self.assertTrue((LABS / "readonly-workflow.example.yml").is_file())
        script = (LABS / "engine.py").read_text(encoding="utf-8")
        self.assertNotIn("requests.patch", script)
        self.assertNotIn("urllib.request", script)


if __name__ == "__main__":
    unittest.main()
