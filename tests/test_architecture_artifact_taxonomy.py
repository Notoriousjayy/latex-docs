"""Architectural artifact taxonomy and cross-document governance regression tests.

These checks validate metadata and navigation, not ISO 42010 conformance.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tooling/manifests/reusable-artifact-pairs.json"
HANDOUT = ROOT / "src/architecture/technical-documents/adr-ad-viewpoint-governance-handout.tex"
REVIEWED = {
    "src/architecture/templates/42010-vp-template-polished.tex": "architecture-viewpoint-guide",
    "src/architecture/templates/viewpoint-template-polished.tex": "architecture-viewpoint",
    "src/architecture/standards/iso-iec-ieee-42010/02-ad-templates.tex": "architecture-description-composite",
    "src/architecture/cloud/engineering-suite/05-architecture-documentation-templates.tex": "mixed-cloud-architecture-instruments",
    "src/architecture/cloud/engineering-suite/06-security-governance-templates.tex": "cloud-security-governance-instruments",
}


class ArchitectureArtifactTaxonomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_three_governed_families_are_separate(self):
        pair_families = {p["family"] for p in self.manifest["pairs"]}
        policy_families = set(self.manifest["classification_policy"]["artifact_families"])
        required = {"architecture-decision-record", "architecture-description",
                    "architecture-viewpoint"}
        self.assertTrue(required.issubset(pair_families))
        self.assertTrue(required.issubset(policy_families))

    def test_composite_sources_are_reviewed_not_falsely_registered(self):
        paired_paths = {v for p in self.manifest["pairs"]
                        for v in (p["template"], p["blank"])}
        queue = {entry["path"]: entry for entry in self.manifest["review_queue"]}
        for path, family in REVIEWED.items():
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())
                self.assertNotIn(path, paired_paths)
                self.assertIn(path, queue)
                self.assertEqual(family, queue[path]["family"])
                self.assertTrue(queue[path]["reason"].strip())
                self.assertTrue(queue[path]["next_action"].strip())

    def test_viewpoint_worksheet_still_requires_a_blank(self):
        queue = {entry["path"]: entry for entry in self.manifest["review_queue"]}
        self.assertEqual("TEMPLATE_ONLY",
                         queue["src/architecture/templates/viewpoint-template-polished.tex"]["state"])
        self.assertEqual("REVIEWED_GUIDE_WITH_EXAMPLE",
                         queue["src/architecture/templates/42010-vp-template-polished.tex"]["state"])

    def test_handout_is_not_in_pair_manifest_and_is_navigable(self):
        rel = HANDOUT.relative_to(ROOT).as_posix()
        self.assertTrue(HANDOUT.is_file())
        self.assertNotIn(rel, {v for p in self.manifest["pairs"]
                              for v in (p["template"], p["blank"])})
        technical_index = (ROOT / "src/architecture/technical-documents/README.md").read_text()
        self.assertIn(HANDOUT.name, technical_index)
        architecture_index = (ROOT / "src/architecture/README.md").read_text()
        self.assertIn(HANDOUT.name, architecture_index)

    def test_no_conformance_claim_for_templates(self):
        self.assertIn("not prescribed by ISO 42010",
                      self.manifest["classification_policy"]["policy_note"])


if __name__ == "__main__":
    unittest.main()
