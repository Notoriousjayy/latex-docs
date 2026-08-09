import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tooling.scripts.latex_build as latex_build
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

    def test_collect_changed_paths_accepts_explicit_revisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "architecture"
            src_dir.mkdir(parents=True)

            tex_path = src_dir / "sample-document.tex"
            tex_path.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")

            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            tex_path.write_text("\\documentclass{article}\n\\begin{document}\nUpdated\n\\end{document}\n", encoding="utf-8")
            subprocess.run(["git", "add", str(tex_path.relative_to(root))], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "update"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            with patch("tooling.scripts.latex_build.ROOT", root):
                with patch("tooling.scripts.latex_build.SRC_DIR", root / "src"):
                    changed = latex_build.collect_changed_paths(base_ref="HEAD~1", head_ref="HEAD")

            self.assertEqual(["src/architecture/sample-document.tex"], changed)

    def test_repo_has_latexmk_config_loaded_by_latexmk(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        latexmkrc_path = repo_root / ".latexmkrc"

        self.assertTrue(latexmkrc_path.exists(), "expected a repository .latexmkrc for latexmk discovery")
        text = latexmkrc_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("TEXINPUTS", text)


if __name__ == "__main__":
    unittest.main()
