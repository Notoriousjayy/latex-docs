"""Run with python -m unittest discover -s examples -v from suite root."""
import json
import unittest
from harness_demo import Harness, Scope, investigate


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.scope = Scope("training", "demo/repo", "revision-1")
        self.run = Harness(self.scope)
        self.proposal = {
            "tool": "read_evidence", "repository": "demo/repo",
            "revision": "revision-1", "finding_id": "F-1",
        }

    def call(self, **changes):
        return self.run.step(json.dumps(self.proposal | changes))

    def test_read(self):
        receipt, evidence = self.call()
        self.assertEqual(receipt.outcome, "allow")
        self.assertEqual(evidence["credential_value"], "[REDACTED]")
        self.assertEqual(len(receipt.evidence_digest), 64)

    def test_wrong_repo(self):
        self.assertEqual(self.call(repository="other/repo")[0].outcome, "deny")

    def test_stale_revision(self):
        self.assertEqual(self.call(revision="revision-0")[0].outcome, "deny")

    def test_extra_field(self):
        self.assertEqual(self.call(approved=True)[0].outcome, "deny")

    def test_unknown_tool(self):
        self.assertEqual(self.call(tool="dismiss_alert")[0].outcome, "deny")

    def test_wrong_tenant(self):
        self.run = Harness(Scope("other", "demo/repo", "revision-1"))
        receipt, evidence = self.call()
        self.assertEqual(receipt.outcome, "abstain")
        self.assertIsNone(evidence)

    def test_missing_evidence(self):
        self.assertEqual(self.call(finding_id="missing")[0].outcome, "abstain")

    def test_budget(self):
        self.run = Harness(self.scope, budget=1)
        self.call(tool="not-allowed")
        self.assertEqual(self.call()[0].reason, "budget-exhausted")

    def test_malformed(self):
        self.assertEqual(self.run.step("{")[0].reason, "invalid-proposal")

    def test_duplicate_field(self):
        raw = json.dumps(self.proposal)[:-1] + ', "tool": "read_evidence"}'
        self.assertEqual(self.run.step(raw)[0].outcome, "deny")

    def test_provider_failure(self):
        def unavailable():
            raise RuntimeError("sensitive provider details")
        receipt, evidence = investigate(self.run, unavailable)
        self.assertEqual(receipt.reason, "model-unavailable")
        self.assertIsNone(evidence)


if __name__ == "__main__":
    unittest.main()
