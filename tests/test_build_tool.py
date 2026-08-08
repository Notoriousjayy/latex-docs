import tempfile
import unittest
from pathlib import Path

from tooling.scripts.latex_build import determine_affected_roots, discover_roots


class BuildToolTests(unittest.TestCase):
    def test_discover_roots_finds_document_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "architecture"
            src_dir.mkdir(parents=True)

            root_doc = src_dir / "sample-document.tex"
            root_doc.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")
            non_root = src_dir / "notes.tex"
            non_root.write_text("Just a helper file\n", encoding="utf-8")

            roots = discover_roots(root / "src")

            self.assertEqual([root_doc.resolve()], roots)

    def test_determine_affected_roots_tracks_shared_includes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "architecture"
            src_dir.mkdir(parents=True)

            shared = src_dir / "shared.tex"
            shared.write_text("Shared content\n", encoding="utf-8")

            doc_a = src_dir / "doc-a.tex"
            doc_a.write_text("\\documentclass{article}\n\\input{shared}\n\\begin{document}\nA\n\\end{document}\n", encoding="utf-8")

            doc_b = src_dir / "doc-b.tex"
            doc_b.write_text("\\documentclass{article}\n\\input{shared}\n\\begin{document}\nB\n\\end{document}\n", encoding="utf-8")

            roots = discover_roots(root / "src")
            affected = determine_affected_roots(roots, changed_path=shared)

            self.assertEqual({doc_a.resolve(), doc_b.resolve()}, set(affected))


if __name__ == "__main__":
    unittest.main()
