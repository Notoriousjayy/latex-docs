"""The syntax gallery must publish PNG images via the existing Pages site."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tooling.scripts.stage_syntax_diagram_gallery import (
    LANGUAGES, REPO_ASSET_PATH, stage_gallery,
)


class NativeSyntaxGalleryTests(unittest.TestCase):
    def test_gallery_uses_pngs_from_verified_site_raster_layout(self):
        with tempfile.TemporaryDirectory() as folder:
            site = Path(folder)
            (site / "index.html").write_text(
                '<nav class="jump" aria-label="Jump to category">'
                '</nav></section><section class="library" aria-label="Published documents">',
                encoding="utf-8",
            )
            for slug, _, _ in LANGUAGES:
                png = site / "images" / REPO_ASSET_PATH / (slug + ".png")
                png.parent.mkdir(parents=True, exist_ok=True)
                png.write_bytes(b"\x89PNG\r\n\x1a\nDATA")
            page = stage_gallery(site)
            text = page.read_text(encoding="utf-8")
            self.assertEqual(text.count("<img "), 5)
            self.assertIn("../images/src/programming/languages/syntax-diagrams/railroad-samples/png/", text)
            self.assertNotIn(".svg", text)
            self.assertNotIn("react", text.casefold().split("<footer>")[0])
            self.assertIn("syntax-diagrams/", (site / "index.html").read_text(encoding="utf-8"))

    def test_missing_png_fails_before_publishing_broken_images(self):
        with tempfile.TemporaryDirectory() as folder:
            site = Path(folder)
            (site / "index.html").write_text(
                '</nav></section><section class="library" aria-label="Published documents">',
                encoding="utf-8",
            )
            with self.assertRaises(FileNotFoundError):
                stage_gallery(site)
            self.assertFalse((site / "syntax-diagrams/index.html").exists())


if __name__ == "__main__":
    unittest.main()
