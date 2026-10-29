"""Navigation contracts for domain-first artifact types and leaf indexes."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
MANIFEST = ROOT / "tooling" / "reports" / "domain-document-types-2026-10-29" / "migrations.json"
KINDS = {"technical-documents", "templates", "workbooks", "study-guides", "study-notes"}


class DocumentTypeAndLeafReadmeTests(unittest.TestCase):
    def test_migration_paths_and_unchanged_tex_count(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        seen_destinations: set[str] = set()
        for move in data["relocations"]:
            source, target = move["from"], move["to"]
            with self.subTest(target=target):
                self.assertFalse((ROOT / source).exists(), "stale source path")
                self.assertTrue((ROOT / target).is_file(), "missing relocated file")
                self.assertIn(Path(target).parts[2], KINDS)
                self.assertNotIn(target, seen_destinations)
                seen_destinations.add(target)
        variants = json.loads((ROOT / "tooling" / "manifests" /
                               "reusable-artifact-pairs.json").read_text(encoding="utf-8"))
        governed = {item["blank"] for item in variants["pairs"]}
        physical = {p.relative_to(ROOT).as_posix() for p in SRC.rglob("*.tex")}
        self.assertTrue(governed.issubset(physical), "governed Blank missing")
        self.assertEqual(1055, len(physical - governed),
                         "the original taxonomy migration must preserve all canonical roots")

    def test_every_leaf_directory_has_readme(self):
        directories = [p for p in SRC.rglob("*") if p.is_dir()]
        for folder in directories:
            if any(p.is_dir() for p in folder.iterdir()):
                continue
            with self.subTest(directory=str(folder.relative_to(ROOT))):
                self.assertTrue(
                    (folder / "README.md").is_file() or (folder / "readme.md").is_file(),
                    "leaf directory is missing its source/asset index",
                )

    def test_leaf_and_domain_navigation_targets_exist(self):
        directories = [p for p in SRC.rglob("*") if p.is_dir()]
        leaves = [p for p in directories if not any(c.is_dir() for c in p.iterdir())]
        documents = [SRC / "README.md", *SRC.glob("*/README.md")]
        for folder in leaves:
            index = folder / "README.md"
            if not index.exists():
                index = folder / "readme.md"
            documents.append(index)
        for document in documents:
            body = document.read_text(encoding="utf-8")
            for match in re.finditer(r"\]\(([^)\n]+)\)", body):
                href = match.group(1).split("#", 1)[0].split("?", 1)[0]
                if not href or href.startswith("/") or re.match(r"[a-z][a-z0-9+.-]*:", href, re.I):
                    continue
                target = (document.parent / unquote(href)).resolve()
                with self.subTest(index=str(document.relative_to(ROOT)), href=href):
                    self.assertTrue(target.is_relative_to(ROOT), "link outside repository")
                    self.assertTrue(target.exists(), "broken local index link")

    def test_type_directories_have_a_readme(self):
        for folder in SRC.glob("*/*"):
            if folder.is_dir() and folder.name in KINDS:
                with self.subTest(type_dir=str(folder.relative_to(ROOT))):
                    self.assertTrue((folder / "README.md").is_file())

    def test_source_catalog_explains_both_types_and_exceptions(self):
        catalog = (SRC / "README.md").read_text(encoding="utf-8")
        self.assertIn("domain", catalog.lower())
        self.assertIn("technical-documents/", catalog)
        self.assertIn("workbooks/", catalog)
        self.assertIn("subject collection", catalog.lower())


if __name__ == "__main__":
    unittest.main()
