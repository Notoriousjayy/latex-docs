"""Regression coverage for reference placement, variants and asset URLs."""
import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote
from unittest.mock import patch

from tooling.scripts import latex_build


class PagesDiagramTests(unittest.TestCase):
    def test_staged_variants_follow_referencing_documents_not_basename(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src, pdfs, images, site = (root / name for name in ("src", "pdfs", "images", "site"))

            def write(path, value=b"fixture"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(value)

            write(src / "architecture" / "a" / "guide.tex", br"\input{fragment}")
            write(src / "architecture" / "a" / "fragment.tex", br"\graphicspath{{diagrams/png/}}\safeincludegraphics{overview}")
            write(src / "architecture" / "b" / "guide.tex", br"\includegraphics{diagrams/svg/overview.svg}")
            write(pdfs / "architecture" / "a" / "guide.pdf")
            write(pdfs / "architecture" / "b" / "guide.pdf")
            for fmt in ("png", "svg", "jpeg", "jpg"):
                write(src / "architecture" / "a" / "diagrams" / fmt / ("overview." + fmt))
            write(src / "architecture" / "b" / "diagrams" / "svg" / "overview.svg")
            write(src / "architecture" / "b" / "diagrams" / "png" / "unreferenced.png")
            with patch.object(latex_build, "ROOT", root):
                manifest = latex_build.collect_raster_corpus(src, images)
            self.assertEqual({"png": 2, "svg": 2, "jpeg": 1, "jpg": 1}, manifest["counts"])
            latex_build.stage_pages_site(pdfs, site, images, source_dir=src)
            page = (site / "index.html").read_text()
            a = page.index('href="pdfs/architecture/a/guide.pdf"')
            b = page.index('href="pdfs/architecture/b/guide.pdf"')
            other = page.index('id="plantuml-diagrams"')
            self.assertIn("Referenced diagrams", page[a:b])
            self.assertEqual(1, page[a:b].count('class="image-card"'))
            self.assertIn('src="images/src/architecture/a/diagrams/png/overview.png"', page[a:b])
            self.assertNotIn("architecture/b/diagrams", page[a:b])
            self.assertIn('src="images/src/architecture/b/diagrams/svg/overview.svg"', page[b:other])
            self.assertIn("unreferenced.png", page[other:])
            self.assertIn('data-format-link aria-current="true">PNG', page[a:b])
            for fmt in ("png", "svg", "jpeg", "jpg"):
                self.assertIn(f'images/src/architecture/a/diagrams/{fmt}/overview.{fmt}', page[a:b])
            for url in re.findall(r'(?:src|href)="(images/[^"]+)"', page):
                self.assertTrue((site / unquote(url)).is_file(), url)
            self.assertIn("image.src = link.href", page)

    def test_shared_asset_is_rendered_beneath_each_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src, pdfs, images, site = (root / name for name in ("src", "pdfs", "images", "site"))
            (src / "docs").mkdir(parents=True)
            (pdfs / "docs").mkdir(parents=True)
            (images / "src" / "docs" / "png").mkdir(parents=True)
            for name in ("one", "two"):
                (src / "docs" / (name + ".tex")).write_text(r"\includegraphics{png/shared.png}")
                (pdfs / "docs" / (name + ".pdf")).write_bytes(b"PDF")
            (images / "src" / "docs" / "png" / "shared.png").write_bytes(b"PNG")
            latex_build.stage_pages_site(pdfs, site, images, source_dir=src)
            page = (site / "index.html").read_text()
            self.assertEqual(2, page.count('src="images/src/docs/png/shared.png"'))
            self.assertIn("No unassociated diagram assets", page)
            self.assertNotIn("data-standalone>", page)


if __name__ == "__main__":
    unittest.main()
