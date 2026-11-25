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
            for fmt in ("png", "svg"):
                write(src / "architecture" / "a" / "diagrams" / fmt / ("overview." + fmt))
            write(src / "architecture" / "b" / "diagrams" / "svg" / "overview.svg")
            write(src / "architecture" / "b" / "diagrams" / "png" / "unreferenced.png")
            with patch.object(latex_build, "ROOT", root):
                manifest = latex_build.collect_raster_corpus(src, images)
            self.assertEqual({"png": 2, "svg": 2, "jpeg": 0, "jpg": 0}, manifest["counts"])
            latex_build.stage_pages_site(pdfs, site, images, source_dir=src)
            page = (site / "index.html").read_text()
            # Include each document's opening list item (and its data-search
            # attribute), not just the PDF anchor. Otherwise the next document's
            # search metadata is mistakenly treated as part of the first row.
            a = page.rfind('<li class="document-row"', 0, page.index('href="pdfs/architecture/a/guide.pdf"'))
            b = page.rfind('<li class="document-row"', 0, page.index('href="pdfs/architecture/b/guide.pdf"'))
            self.assertGreaterEqual(a, 0)
            self.assertGreater(b, a)
            other = page.index('<div class="diagram-gallery" data-diagram-gallery>', b)
            self.assertNotIn('id="plantuml-diagrams"', page)
            self.assertLess(page.index('id="section-architecture-b"'), other)
            self.assertLess(other, page.index('</section>', b))
            self.assertIn("Related diagrams", page[a:b])
            self.assertEqual(1, page[a:b].count('class="image-card"'))
            self.assertIn('src="images/src/architecture/a/diagrams/png/overview.png"', page[a:b])
            self.assertNotIn("architecture/b/diagrams", page[a:b])
            self.assertIn('src="images/src/architecture/b/diagrams/svg/overview.svg"', page[b:other])
            self.assertNotIn("architecture/a/diagrams", page[b:other])
            self.assertEqual(1, page[b:other].count('class="image-card"'))
            self.assertIn("unreferenced.png", page[other:])
            self.assertEqual(1, page.count('src="images/src/architecture/b/diagrams/png/unreferenced.png"'))
            self.assertNotIn("unreferenced.png", page[b:other])
            self.assertIn('data-format-link aria-current="true">PNG', page[a:b])
            for fmt in ("png", "svg"):
                self.assertIn(f'images/src/architecture/a/diagrams/{fmt}/overview.{fmt}', page[a:b])
            for url in re.findall(r'(?:src|href)="(images/[^"]+)"', page):
                self.assertTrue((site / unquote(url)).is_file(), url)
            self.assertIn("image.src = link.href", page)

    def test_unassociated_assets_follow_deepest_existing_taxonomy_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src, pdfs, images, site = (root / name for name in ("src", "pdfs", "images", "site"))

            def write(path):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture")

            write(pdfs / "architecture" / "c4-model" / "guide.pdf")
            write(pdfs / "security" / "appsec" / "guide.pdf")
            for fmt in ("png", "svg"):
                write(images / "src" / "architecture" / "c4-model" / "diagrams" / fmt / ("context." + fmt))
            write(images / "src" / "architecture" / "new-topic" / "png" / "overview.png")
            write(images / "security" / "appsec" / "png" / "flow.png")
            write(images / "tooling" / "plantuml" / "architecture" / "png" / "shared.png")
            latex_build.stage_pages_site(pdfs, site, images, source_dir=src)
            page = (site / "index.html").read_text()
            from html.parser import HTMLParser

            class GalleryParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.sections = []
                    self.groups = []
                    self.placements = {}

                def handle_starttag(self, tag, attrs):
                    attrs = dict(attrs)
                    if tag == "section":
                        self.sections.append(attrs.get("id"))
                    elif tag == "details":
                        self.groups.append([attrs, None])
                        if "diagram-gallery" in attrs.get("class", ""):
                            self.assert_closed(attrs)
                    elif tag in ("h2", "h3", "h4", "h5", "h6") and self.groups:
                        self.groups[-1][1] = attrs.get("id")
                    elif tag == "img":
                        self.placements[attrs["src"]] = (
                            self.sections[-1],
                            tuple(group[1] for group in self.groups),
                        )

                @staticmethod
                def assert_closed(attrs):
                    if "open" in attrs:
                        raise AssertionError("gallery must start closed")

                def handle_endtag(self, tag):
                    if tag == "section":
                        self.sections.pop()
                    elif tag == "details":
                        self.groups.pop()

            parser = GalleryParser()
            parser.feed(page)
            context = parser.placements["images/src/architecture/c4-model/diagrams/png/context.png"]
            overview = parser.placements["images/src/architecture/new-topic/png/overview.png"]
            flow = parser.placements["images/security/appsec/png/flow.png"]
            shared = parser.placements["images/tooling/plantuml/architecture/png/shared.png"]
            self.assertEqual("category-architecture", context[0])
            self.assertIn("section-architecture-c4-model", context[1])
            self.assertEqual("category-architecture", overview[0])
            self.assertNotIn("section-architecture-c4-model", overview[1])
            self.assertEqual("category-security", flow[0])
            self.assertIn("section-security-appsec", flow[1])
            self.assertEqual("plantuml-diagrams", shared[0])
            # Local cards are immediately visible when their owning category
            # opens; only the genuinely unmatched gallery has a disclosure.
            self.assertEqual(2, len(context[1]))
            self.assertEqual(1, len(overview[1]))
            self.assertEqual(2, len(flow[1]))
            self.assertEqual(1, len(shared[1]))
            self.assertEqual(3, page.count('<div class="diagram-gallery" data-diagram-gallery>'))
            self.assertEqual(1, page.count('<details class="document-group diagram-gallery">'))
            self.assertEqual(4, page.count('data-standalone>'))
            self.assertEqual(4, len(parser.placements))
            self.assertIn('data-format-link>SVG', page)
            self.assertIn("Showing 6 of 6 assets", page)

    def test_unique_authored_collection_and_unmatched_gallery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src, pdfs, images, site = (root / name for name in ("src", "pdfs", "images", "site"))
            topic = Path("security/appsec")
            (src / topic / "diagrams").mkdir(parents=True)
            (pdfs / topic).mkdir(parents=True)
            (src / topic / "guide.tex").write_text(r"\section{Application security}")
            (src / topic / "diagrams" / "flow.puml").write_text("@startuml\nA -> B\n@enduml\n")
            (pdfs / topic / "guide.pdf").write_bytes(b"PDF")
            for fmt in ("png", "svg"):
                out = images / "src" / topic / "diagrams" / fmt / ("flow." + fmt)
                out.parent.mkdir(parents=True)
                out.write_bytes(b"image")
            latex_build.stage_pages_site(pdfs, site, images, source_dir=src)
            page = (site / "index.html").read_text()
            self.assertIn("Related diagrams", page)
            self.assertIn('data-format-link>SVG', page)
            self.assertNotIn('id="plantuml-diagrams"', page)

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
            self.assertNotIn('id="plantuml-diagrams"', page)
            self.assertNotIn("PlantUML Diagrams — other assets", page)
            self.assertNotIn("data-standalone>", page)


if __name__ == "__main__":
    unittest.main()
