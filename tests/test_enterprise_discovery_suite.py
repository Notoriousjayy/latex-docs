"""Regression tests for the GitHub Actions architecture discovery documentation suite."""
import json
import unittest
from pathlib import Path

from tooling.scripts.validate_artifact_pairs import printable_bracket_prompts

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "src/architecture/technical-documents/github-actions-architecture-discovery-enterprise-scale.tex"
MANIFEST = ROOT / "tooling/manifests/reusable-artifact-pairs.json"
IDS = {
    "ARCH-GHA-DISCOVERY-AD",
    "ARCH-GHA-DISCOVERY-VIEWPOINT",
    "ARCH-GHA-DISCOVERY-IMPLEMENTATION",
    "ARCH-GHA-DISCOVERY-EVIDENCE",
}


class EnterpriseDiscoverySuiteTests(unittest.TestCase):
    def test_uploaded_reference_is_preserved_at_known_blob(self):
        # Authored LaTeX reference is retained verbatim (including terminal newline).
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertTrue(guide.startswith("% !TeX program = pdflatex"))
        self.assertTrue(guide.endswith("\\end{document}\n"))
        for phrase in (
            "REPOSITORY_HAS_WORKFLOW",
            "JOB_CALLS_WORKFLOW",
            "ARTIFACT_DEPLOYED_TO",
            "monorepo",
            "source_uri",
            "GitHub App",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guide)

    def test_all_four_families_are_registered(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        records = {p["id"]: p for p in manifest["pairs"] if p["id"] in IDS}
        self.assertEqual(IDS, set(records))
        self.assertEqual(
            {"architecture-description", "architecture-viewpoint",
             "discovery-implementation-workbook", "discovery-evidence-workbook"},
            {r["family"] for r in records.values()},
        )
        for item in records.values():
            with self.subTest(item=item["id"]):
                template = (ROOT / item["template"]).read_text(encoding="utf-8")
                blank = (ROOT / item["blank"]).read_text(encoding="utf-8")
                self.assertIn(r"\\documentclass", template)
                self.assertIn(r"\\documentclass", blank)
                self.assertIn(r"\\end{document}", blank)
                self.assertNotEqual(template, blank)
                self.assertEqual([], printable_bracket_prompts(blank))
                self.assertNotIn("[To complete]", blank)
                self.assertNotIn("[TODO]", blank)
                self.assertIn(r"\\rule", blank)

    def test_suite_navigation_exists(self):
        page = ROOT / "src/architecture/github-actions-discovery-suite.md"
        text = page.read_text(encoding="utf-8")
        for item in IDS:
            with self.subTest(item=item):
                self.assertTrue(any(
                    part in text for part in (
                        "AD Blank", "Viewpoint Blank", "Implementation Blank", "Evidence Blank"
                    )
                ))


if __name__ == "__main__":
    unittest.main()
