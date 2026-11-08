"""Regression tests: rendered PlantUML assets must have writable indexes."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tooling.scripts.ensure_plantuml_asset_readmes import MARKER, ensure_index


class PlantUMLAssetIndexTests(unittest.TestCase):
    def test_companion_images_are_indexed(self):
        base = (Path(__file__).resolve().parents[1] /
                "src/security/github-advanced-security/code-scanning/"
                "enterprise-triage-governance/diagrams")
        for ext in ("png", "svg"):
            with self.subTest(ext=ext):
                index = base / ext / "README.md"
                self.assertTrue(index.is_file(), str(index))
                self.assertIn(MARKER, index.read_text(encoding="utf-8"))

    def test_new_index_is_generated_and_idempotent(self):
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            leaf = root / "src" / "demo" / "diagrams" / "png"
            leaf.mkdir(parents=True)
            first = leaf / "alpha.png"
            first.write_bytes(b"PNG-synthetic")
            index = ensure_index(first, root)
            self.assertEqual(leaf / "README.md", index)
            self.assertIn("alpha.png", index.read_text(encoding="utf-8"))
            self.assertIsNone(ensure_index(first, root))
            second = leaf / "beta.png"
            second.write_bytes(b"PNG-synthetic2")
            self.assertEqual(index, ensure_index(second, root))
            self.assertIn("beta.png", index.read_text(encoding="utf-8"))
            self.assertEqual(b"PNG-synthetic", first.read_bytes())

    def test_existing_curated_readme_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            leaf = root / "src" / "demo" / "svg"
            leaf.mkdir(parents=True)
            image = leaf / "alpha.svg"
            image.write_text("<svg/>", encoding="utf-8")
            readme = leaf / "README.md"
            readme.write_text("# Curated\n", encoding="utf-8")
            self.assertIsNone(ensure_index(image, root))
            self.assertEqual("# Curated\n", readme.read_text(encoding="utf-8"))

    def test_other_directories_and_non_images_are_ignored(self):
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            for name in ("src/demo/assets/alpha.png", "other/demo/png/alpha.png",
                         "src/demo/png/document.txt"):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b"synthetic")
                with self.subTest(name=name):
                    self.assertIsNone(ensure_index(p, root))


if __name__ == "__main__":
    unittest.main()
