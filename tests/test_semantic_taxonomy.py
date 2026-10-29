"""Semantic taxonomy and cross-domain discovery regression gates.

The inventory explicitly distinguishes reviewed evidence from provisional path inference.
These tests validate traceability and link integrity, not substantive content quality.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CATALOG = ROOT / "catalog"
MANIFEST = ROOT / "tooling" / "manifests" / "semantic-document-inventory.json"
PAIR_MANIFEST = ROOT / "tooling" / "manifests" / "reusable-artifact-pairs.json"

TYPES = {
    "technical-reference", "implementation-guide", "handbook", "runbook",
    "template", "workbook", "scorecard", "checklist", "user-stories",
    "study-guide", "study-notes", "laboratory", "assessment",
    "policy-standard", "decision-record", "architecture-document",
    "business-plan", "latex-fragment",
}

RELOCATED = {
    **{
        "src/security/application-security/secure-coding/secure-coding-standard-" + language + ".tex":
        "src/programming/languages/" + destination + "/secure-coding-standard-" + language + ".tex"
        for language, destination in {
            "c": "c-cpp/secure-coding",
            "cpp": "c-cpp/secure-coding",
            "csharp": "csharp",
            "go": "go",
            "java": "java/secure-coding",
            "javascript": "ecmascript",
            "kotlin": "kotlin",
            "python": "python",
            "ruby": "ruby",
            "rust": "rust",
            "swift": "swift",
            "typescript": "typescript",
        }.items()
    },
    "src/security/application-security/fundamentals/user-stories-by-chapter-ci-cd-github-actions.tex":
    "src/devops/github-actions/user-stories-by-chapter-ci-cd-github-actions.tex",
}


class SemanticTaxonomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.entries = cls.inventory["sources"]

    def test_complete_tracked_latex_inventory(self):
        registered = [entry["path"] for entry in self.entries]
        self.assertEqual(len(registered), len(set(registered)), "duplicate canonical paths")
        physical = sorted(path.relative_to(ROOT).as_posix() for path in SRC.rglob("*.tex"))
        managed = json.loads(PAIR_MANIFEST.read_text(encoding="utf-8"))
        variants = {pair["blank"] for pair in managed["pairs"]}
        self.assertTrue(variants.issubset(set(physical)), "registered Blank missing")
        self.assertEqual(sorted(registered), sorted(set(physical) - variants),
                         "canonical metadata is stale or incomplete")
        self.assertEqual(1055, len(set(physical) - variants))

    def test_unique_document_ids_and_classification_evidence(self):
        ids = [entry["id"] for entry in self.entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.entries), self.inventory["document_count"])
        reviewed = 0
        for entry in self.entries:
            with self.subTest(source=entry["path"]):
                self.assertIn(entry["primary_type"], TYPES)
                self.assertTrue(entry["domain"])
                self.assertEqual(entry["domain"], Path(entry["path"]).parts[1])
                self.assertTrue(entry["primary_subject"])
                self.assertIn(
                    entry["review_status"],
                    ("targeted-content-reviewed", "path-inferred-not-fully-reviewed"),
                )
                if entry["review_status"] == "path-inferred-not-fully-reviewed":
                    self.assertIsNone(entry["summary"], "unreviewed source claims a summary")
                else:
                    reviewed += 1
                    self.assertTrue(entry["summary"])
                    if entry["primary_type"] == "latex-fragment":
                        self.assertIs(entry["standalone_latex"], False)
        self.assertEqual(reviewed, self.inventory["reviewed_items"])

    def test_language_specific_secure_coding_colocation(self):
        for source, destination in RELOCATED.items():
            with self.subTest(source=source):
                self.assertFalse((ROOT / source).exists())
                self.assertTrue((ROOT / destination).is_file())
        self.assertFalse((SRC / "security/application-security/secure-coding").exists())
        self.assertTrue((SRC / "programming/languages/README.md").is_file())

    def test_all_leaf_indexes_still_exist(self):
        for folder in (path for path in SRC.rglob("*") if path.is_dir()):
            if any(p.is_dir() for p in folder.iterdir()):
                continue
            with self.subTest(directory=str(folder.relative_to(ROOT))):
                self.assertTrue(
                    (folder / "README.md").is_file()
                    or (folder / "readme.md").is_file()
                )

    def test_catalogs_exist_and_local_links_resolve(self):
        required = {
            "README.md", "by-domain.md", "by-document-type.md", "by-subject.md",
            "user-stories.md", "templates.md", "workbooks.md",
            "scorecards.md", "checklists.md", "technical-references.md",
            "secure-coding.md", "assessments.md", "runbooks.md", "study-guides.md",
        }
        self.assertTrue(required.issubset({p.name for p in CATALOG.glob("*.md")}))
        for page in CATALOG.glob("*.md"):
            body = page.read_text(encoding="utf-8")
            for match in re.finditer(r"\]\(([^)\n]+)\)", body):
                href = match.group(1).split("#", 1)[0].split("?", 1)[0]
                if (
                    not href
                    or href.startswith("/")
                    or re.match(r"[a-z][a-z0-9+.-]*:", href, re.I)
                ):
                    continue
                target = (page.parent / unquote(href)).resolve()
                with self.subTest(page=page.name, href=href):
                    self.assertTrue(target.is_relative_to(ROOT), "link escapes repository")
                    self.assertTrue(target.exists(), "broken catalog link")


if __name__ == "__main__":
    unittest.main()
