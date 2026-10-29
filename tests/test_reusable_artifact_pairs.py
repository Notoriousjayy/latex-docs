"""Governed LaTeX template/blank variant checks."""
import json
import unittest
from pathlib import Path

from tooling.scripts.validate_artifact_pairs import validate

ROOT = Path(__file__).resolve().parents[1]


class ReusableArtifactPairTests(unittest.TestCase):
    def test_registered_pairs_are_structurally_valid(self):
        self.assertEqual([], validate())

    def test_architecture_description_and_decision_records_are_distinct(self):
        data = json.loads(
            (ROOT / "tooling/manifests/reusable-artifact-pairs.json").read_text(encoding="utf-8")
        )
        families = {record["family"] for record in data["pairs"]}
        self.assertIn("architecture-description", families)
        self.assertIn("architecture-decision-record", families)
        self.assertEqual(len(data["pairs"]), len({r["id"] for r in data["pairs"]}))

    def test_completed_startup_example_is_preserved(self):
        original = ROOT / "src/startups/templates/startup-plan-template-worksheet.tex"
        self.assertIn("Smart Building Manager", original.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
