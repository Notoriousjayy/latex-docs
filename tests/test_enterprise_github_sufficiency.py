"""Contract checks for the integrated enterprise discovery and AppSec document register."""
from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from tooling.scripts import audit_enterprise_github_docs as audit

ROOT = Path(__file__).resolve().parents[1]
SUFF = ROOT / ("src/security/github-advanced-security/code-scanning/"
               "enterprise-triage-governance/sufficiency")
PAIR_MANIFEST = ROOT / "tooling/manifests/reusable-artifact-pairs.json"


class IntegratedSufficiencyTests(unittest.TestCase):
    def test_requirements_and_register_paths_and_domains(self):
        report = audit.inspect()
        self.assertTrue(report["checks_pass"], report["problems"])
        self.assertEqual(15, report["domain_count"])
        self.assertGreaterEqual(report["requirement_count"], 70)
        self.assertGreaterEqual(report["document_count"], 50)
        self.assertEqual("provisional_unapproved", report["readiness"]["L1"])
        self.assertNotEqual("ready", report["readiness"]["L3"])

    def test_approved_runtime_evidence_is_not_manufactured(self):
        matrix = audit.load(audit.MATRIX)
        self.assertTrue(any(r["priority"] == "P0" and r["coverage"] == "partial" for r in matrix))
        self.assertTrue(all(r["operational_evidence"] == "unverified" for r in matrix))
        self.assertTrue(all(r["earliest_gate"] in {"L1", "L2", "L3"} for r in matrix))
        self.assertEqual(len(matrix), len({r["requirement_id"] for r in matrix}))

    def test_all_sixteen_existing_template_blank_pairs_reused(self):
        pairs = json.loads(PAIR_MANIFEST.read_text(encoding="utf-8"))["pairs"]
        relevant = [
            pair for pair in pairs
            if pair["id"].startswith("ARCH-GHA-DISCOVERY-")
            or ("/enterprise-triage-governance/forms/" in pair["template"])
        ]
        self.assertEqual(16, len(relevant))
        registered = {row["canonical_path"] for row in audit.load(audit.REGISTER)}
        for pair in relevant:
            with self.subTest(pair=pair["id"]):
                self.assertIn(pair["template"], registered)
                self.assertIn(pair["blank"], registered)
                self.assertTrue((ROOT / pair["blank"]).is_file())

    def test_adrs_remain_proposed_and_legacy_approval_is_disclaimed(self):
        rows = audit.load(audit.REGISTER)
        proposed = [r for r in rows if r["artifact_kind"] == "architecture-decision"]
        self.assertEqual(3, len(proposed))
        self.assertTrue(all(r["source_status"] == "PROPOSED" for r in proposed))
        legacy = [r for r in rows if r["artifact_kind"] == "legacy-field-guide"]
        self.assertEqual(1, len(legacy))
        self.assertEqual("NONAUTHORITATIVE_FOR_APPROVAL", legacy[0]["source_status"])

    def test_readiness_controls_and_navigation_express_boundaries(self):
        text = "\n".join(
            (SUFF / filename).read_text(encoding="utf-8")
            for filename in ("README.md", "architecture-and-controls.md",
                             "governance-operations.md", "readiness-backlog.md",
                             "verification.md")
        )
        for phrase in ("E1", "E2", "E3", "P0", "L1", "L2", "L3",
                       "read-only", "independent", "unverified"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_never_claims_prod_authorization(self):
        summary = audit.inspect()
        self.assertEqual("not_evidenced", summary["readiness"]["L2"])
        self.assertEqual("not_evidenced", summary["readiness"]["L3"])
        self.assertEqual(0, sum(
            n for status,n in summary["operational_evidence_counts"].items()
            if status not in audit.EVIDENCE
        ))


if __name__ == "__main__":
    unittest.main()
