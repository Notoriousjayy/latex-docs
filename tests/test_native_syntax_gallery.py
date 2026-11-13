"""Regression tests for complete native PNG syntax gallery publication."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tooling.scripts.generate_railroad_ebnf import LANGUAGES, rule_path, source_data
from tooling.scripts.stage_syntax_diagram_gallery import (
    HOME_NAV_MARKER, asset_path, stage_gallery,
)


class CompleteGrammarGalleryTests(unittest.TestCase):
    @staticmethod
    def make_site(root: Path, *, all_png: bool = True) -> int:
        (root / "index.html").write_text(
            '<nav class="jump" aria-label="Jump to category">' + HOME_NAV_MARKER,
            encoding="utf-8",
        )
        total = 0
        if all_png:
            for lang, _ in LANGUAGES:
                for index, item in enumerate(source_data(lang)["rules"], 1):
                    path = root / "images" / asset_path(lang, index, item["name"])
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic")
                    total += 1
        return total

    def test_all_1166_rules_have_verified_pngs_and_visible_text(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(self.make_site(root), 1166)
            out = stage_gallery(root)
            self.assertTrue(out.is_file())
            index = out.read_text(encoding="utf-8")
            self.assertIn("1,166 grammar productions", index)
            self.assertEqual(index.count('class="card"'), 5)
            total_cards = 0
            for language, title in LANGUAGES:
                page = (out.parent / (language + ".html")).read_text(encoding="utf-8")
                count = len(source_data(language)["rules"])
                self.assertEqual(page.count('class="rule"'), count)
                self.assertEqual(page.count('<img loading="lazy"'), count)
                self.assertIn("Full textual grammar definition", page)
                self.assertIn('id="rule-search"', page)
                self.assertNotIn(".svg", page)
                total_cards += count
            self.assertEqual(total_cards, 1166)
            self.assertIn("syntax-diagrams/", (root / "index.html").read_text(encoding="utf-8"))

    def test_missing_png_aborts_without_publishing_partial_gallery(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.make_site(root, all_png=False)
            with self.assertRaises(FileNotFoundError):
                stage_gallery(root)
            self.assertFalse((root / "syntax-diagrams/index.html").exists())

    def test_bad_png_signature_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.make_site(root)
            first = source_data(LANGUAGES[0][0])["rules"][0]
            path = root / "images" / asset_path(LANGUAGES[0][0], 1, first["name"])
            path.write_bytes(b"not really a png")
            with self.assertRaises(ValueError):
                stage_gallery(root)

    def test_generated_locations_are_stable_and_unique(self):
        seen = set()
        for language, _ in LANGUAGES:
            for i, item in enumerate(source_data(language)["rules"], 1):
                rel = rule_path(language, i, item["name"])
                self.assertNotIn(rel, seen)
                seen.add(rel)
                self.assertEqual(rel.suffix, ".puml")
                self.assertIn("part-", rel.as_posix())
        self.assertEqual(len(seen), 1166)


if __name__ == "__main__":
    unittest.main()
