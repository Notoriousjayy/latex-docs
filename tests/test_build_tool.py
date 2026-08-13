import subprocess
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from contextlib import redirect_stderr
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

    def test_build_root_uses_source_dir_for_latexmk_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")

            output_dir = root / "public" / "pdfs"
            log_dir = root / "public" / "logs"

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                work_dir = Path(cwd)
                (work_dir / "sample.pdf").write_bytes(b"%PDF-1.4")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch("tooling.scripts.latex_build.subprocess.run", side_effect=fake_run) as run_mock:
                result = latex_build.build_root(tex_path, output_dir=output_dir, log_dir=log_dir)

            self.assertEqual(0, result)
            self.assertNotIn("-outdir", run_mock.call_args.args[0])
            self.assertTrue((src_dir / "sample.pdf").exists())
            self.assertTrue((output_dir / "docs" / "sample.pdf").exists())

    def test_github_security_sources_have_balanced_setminted_blocks(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        bad_files = []

        for tex_path in (repo_root / "src" / "security" / "github-advanced-security").rglob("*.tex"):
            text = tex_path.read_text(encoding="utf-8", errors="ignore")
            if "\\setminted{" not in text:
                continue

            start = text.find("\\setminted{")
            doc_pos = text.find("\\begin{document}")
            if doc_pos == -1:
                continue

            depth = 0
            cursor = text.find("{", start)
            while cursor != -1 and cursor < doc_pos:
                ch = text[cursor]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
                cursor += 1

            if depth != 0:
                bad_files.append(str(tex_path.relative_to(repo_root)))

        self.assertEqual([], bad_files)

    def test_discover_roots_ignores_generated_wrapper_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            source = src_dir / "sample.tex"
            source.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")
            wrapper = src_dir / ".sample.latex-build-wrapper.tex"
            wrapper.write_text("\\documentclass{article}\n\\begin{document}\nWrapper\n\\end{document}\n", encoding="utf-8")

            roots = discover_roots(root / "src")

            self.assertEqual([source.resolve()], roots)

    def test_build_root_injects_minted_package_for_minted_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\n\\begin{document}\n\\begin{minted}{text}\nhello\n\\end{minted}\n\\end{document}\n", encoding="utf-8")

            output_dir = root / "public" / "pdfs"
            log_dir = root / "public" / "logs"

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                work_dir = Path(cwd)
                wrapper_path = work_dir / cmd[-1]
                self.assertTrue(wrapper_path.exists())
                self.assertIn("\\usepackage[cache=false]{minted}", wrapper_path.read_text(encoding="utf-8", errors="ignore"))
                self.assertIn("-jobname=sample", cmd)
                (work_dir / "sample.pdf").write_bytes(b"%PDF-1.4")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch("tooling.scripts.latex_build.subprocess.run", side_effect=fake_run):
                result = latex_build.build_root(tex_path, output_dir=output_dir, log_dir=log_dir)

            self.assertEqual(0, result)
            self.assertTrue((output_dir / "docs" / "sample.pdf").exists())

    def test_build_root_does_not_publish_stale_pdf_after_failed_build(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")
            stale_pdf = src_dir / "sample.pdf"
            stale_pdf.write_bytes(b"%PDF-1.4 stale")

            output_dir = root / "public" / "pdfs"
            log_dir = root / "public" / "logs"

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                return subprocess.CompletedProcess(cmd, 12)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch("tooling.scripts.latex_build.subprocess.run", side_effect=fake_run):
                result = latex_build.build_root(tex_path, output_dir=output_dir, log_dir=log_dir)

            self.assertEqual(12, result)
            self.assertFalse((output_dir / "docs" / "sample.pdf").exists())

    def test_build_root_fails_when_pdf_is_missing_after_successful_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")

            output_dir = root / "public" / "pdfs"
            log_dir = root / "public" / "logs"

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                return subprocess.CompletedProcess(cmd, 0)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch("tooling.scripts.latex_build.subprocess.run", side_effect=fake_run):
                result = latex_build.build_root(tex_path, output_dir=output_dir, log_dir=log_dir)

            self.assertNotEqual(0, result)
            self.assertFalse((output_dir / "docs" / "sample.pdf").exists())
            stderr_log = log_dir / "sample.build.stderr.txt"
            self.assertTrue(stderr_log.exists())
            self.assertIn("Expected PDF output was not produced", stderr_log.read_text(encoding="utf-8"))

    def test_build_roots_reports_failures_with_log_locations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")
            log_dir = root / "public" / "logs"

            with patch("tooling.scripts.latex_build.build_root", return_value=9):
                stderr_buffer = StringIO()
                with redirect_stderr(stderr_buffer):
                    failures = latex_build.build_roots([tex_path], log_dir=log_dir)

            self.assertEqual(1, failures)
            self.assertIn("Build failed for", stderr_buffer.getvalue())
            self.assertIn("sample.build.stdout.txt", stderr_buffer.getvalue())

    def test_stage_pages_site_preserves_nested_paths_and_builds_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pdf_dir = root / "public" / "pdfs"
            nested_pdf = pdf_dir / "security" / "certifications" / "cissp" / "cornell-notes" / "01-security-and-risk-management-cornell-notes.pdf"
            nested_pdf.parent.mkdir(parents=True, exist_ok=True)
            nested_pdf.write_bytes(b"%PDF-1.4")

            other_pdf = pdf_dir / "architecture" / "guide.pdf"
            other_pdf.parent.mkdir(parents=True, exist_ok=True)
            other_pdf.write_bytes(b"%PDF-1.4")

            site_dir = root / "site"
            rel_paths = latex_build.stage_pages_site(pdf_dir, site_dir)

            self.assertEqual(
                [
                    Path("architecture/guide.pdf"),
                    Path("security/certifications/cissp/cornell-notes/01-security-and-risk-management-cornell-notes.pdf"),
                ],
                rel_paths,
            )
            self.assertTrue((site_dir / "pdfs" / "security" / "certifications" / "cissp" / "cornell-notes" / "01-security-and-risk-management-cornell-notes.pdf").exists())
            index_text = (site_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="pdfs/security/certifications/cissp/cornell-notes/01-security-and-risk-management-cornell-notes.pdf"', index_text)
            self.assertIn('href="pdfs/architecture/guide.pdf"', index_text)

    def test_discover_roots_includes_all_canonical_cornell_documents(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        roots = discover_roots(repo_root / "src")
        cornell_roots = sorted(path.relative_to(repo_root).as_posix() for path in roots if "src/security/certifications/cissp/cornell-notes/" in path.as_posix())

        self.assertEqual(
            [
                "src/security/certifications/cissp/cornell-notes/01-security-and-risk-management-cornell-notes.tex",
                "src/security/certifications/cissp/cornell-notes/02-asset-security-cornell-notes.tex",
                "src/security/certifications/cissp/cornell-notes/03-security-architecture-and-engineering-cornell-notes.tex",
                "src/security/certifications/cissp/cornell-notes/04-communication-and-network-security-cornell-notes.tex",
                "src/security/certifications/cissp/cornell-notes/05-identity-and-access-management-cornell-notes.tex",
                "src/security/certifications/cissp/cornell-notes/06-security-assessment-and-testing-cornell-notes.tex",
                "src/security/certifications/cissp/cornell-notes/07-security-operations-cornell-notes.tex",
                "src/security/certifications/cissp/cornell-notes/08-software-development-security-cornell-notes.tex",
            ],
            cornell_roots,
        )

    def test_pages_workflow_trigger_paths_cover_publication_inputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        workflow_text = (repo_root / ".github" / "workflows" / "latex-pages.yml").read_text(encoding="utf-8")

        self.assertIn("'src/**/*.tex'", workflow_text)
        self.assertIn("'tooling/**/*.sty'", workflow_text)
        self.assertIn("'tooling/scripts/**'", workflow_text)
        self.assertIn("'Makefile'", workflow_text)
        self.assertIn("'.latexmkrc'", workflow_text)
        self.assertIn("'.github/workflows/latex-pages.yml'", workflow_text)

    def test_resolve_texinputs_includes_cornell_style_tree(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with patch("tooling.scripts.latex_build.ROOT", repo_root):
            texinputs = latex_build.resolve_texinputs()

        self.assertIn(str(repo_root / "tooling" / "styles" / "latex") + "//", texinputs)

    def test_documents_using_calloutbox_define_the_macro(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        tex_path = repo_root / "src" / "security" / "application-security" / "dast" / "zap" / "core-concepts.tex"

        text = tex_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("\\providecommand{\\calloutbox}[2]{\\callout{#1}{#2}}", text)

    def test_repo_has_latexmk_config_loaded_by_latexmk(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        latexmkrc_path = repo_root / ".latexmkrc"

        self.assertTrue(latexmkrc_path.exists(), "expected a repository .latexmkrc for latexmk discovery")
        text = latexmkrc_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("TEXINPUTS", text)


if __name__ == "__main__":
    unittest.main()
