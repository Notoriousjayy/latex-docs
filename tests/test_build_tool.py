import subprocess
import tempfile
import unittest
import shutil
import json
import re
import shlex
from io import StringIO
from pathlib import Path
from contextlib import redirect_stderr
from unittest.mock import patch

import tooling.scripts.latex_build as latex_build
from tooling.scripts.latex_build import determine_affected_roots, discover_roots


class BuildToolTests(unittest.TestCase):
    def _make_dry_run_command(self, *make_args: str) -> str:
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["make", "--dry-run", *make_args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        self.assertTrue(lines, "expected make --dry-run to emit a command")
        return lines[-1]

    def test_extract_first_error_detects_stdout_only_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex_log = root / "doc.log"
            stdout_log = root / "doc.stdout.txt"
            stderr_log = root / "doc.stderr.txt"
            tex_log.write_text("", encoding="utf-8")
            stdout_log.write_text("! Undefined control sequence.\nl.37 \\LdsCornellRenderTitle\n", encoding="utf-8")
            stderr_log.write_text("", encoding="utf-8")

            signature = latex_build._extract_first_error(tex_log, stdout_log, stderr_log)

            self.assertIn("Undefined control sequence", signature)
            self.assertIn("l.<n>", signature)

    def test_extract_first_error_detects_native_log_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex_log = root / "doc.log"
            stdout_log = root / "doc.stdout.txt"
            stderr_log = root / "doc.stderr.txt"
            tex_log.write_text("! LaTeX Error: Missing \\begin{document}.\nl.12\\end{titlepage}\n", encoding="utf-8")
            stdout_log.write_text("", encoding="utf-8")
            stderr_log.write_text("", encoding="utf-8")

            signature = latex_build._extract_first_error(tex_log, stdout_log, stderr_log)

            self.assertIn("LaTeX Error", signature)
            self.assertIn("l.<n>", signature)

    def test_extract_first_error_details_include_line_and_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex_log = root / "doc.log"
            stdout_log = root / "doc.stdout.txt"
            stderr_log = root / "doc.stderr.txt"
            tex_log.write_text(
                "(./doc.tex\n"
                "! LaTeX Error: Missing \\begin{document}.\n"
                "l.12 \\end{titlepage}\n"
                "See the LaTeX manual\n",
                encoding="utf-8",
            )
            stdout_log.write_text("", encoding="utf-8")
            stderr_log.write_text("", encoding="utf-8")

            details = latex_build._extract_first_error_details(tex_log, stdout_log, stderr_log)

            self.assertIn("LaTeX Error", details["signature"])
            self.assertIn("l.<n>", details["signature"])
            self.assertEqual("l.<n> \\end{titlepage}", details["line_ref"])
            self.assertIn("Missing \\begin{document}", details["context"])
            self.assertEqual("./doc.tex", details["source"])

    def test_extract_first_error_uses_unknown_only_when_all_sources_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex_log = root / "doc.log"
            stdout_log = root / "doc.stdout.txt"
            stderr_log = root / "doc.stderr.txt"
            tex_log.write_text("", encoding="utf-8")
            stdout_log.write_text("", encoding="utf-8")
            stderr_log.write_text("", encoding="utf-8")

            signature = latex_build._extract_first_error(tex_log, stdout_log, stderr_log)

            self.assertEqual("UNKNOWN", signature)

    def test_build_roots_clusters_normalized_package_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)
            tex_a = src_dir / "a.tex"
            tex_b = src_dir / "b.tex"
            tex_a.write_text("\\documentclass{article}\\begin{document}A\\end{document}", encoding="utf-8")
            tex_b.write_text("\\documentclass{article}\\begin{document}B\\end{document}", encoding="utf-8")
            log_dir = root / "public" / "logs"

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"):
                a_stdout, _ = latex_build._log_paths(tex_a, log_dir)
                b_stdout, _ = latex_build._log_paths(tex_b, log_dir)
                assert a_stdout is not None
                assert b_stdout is not None
                a_stdout.write_text("! Package cornell-notes Error: Cornell documents require an explicit \\title{...}.\nl.11 \\maketitle\n", encoding="utf-8")
                b_stdout.write_text("! Package cornell-notes Error: Cornell documents require an explicit \\title{...}.\nl.97 \\maketitle\n", encoding="utf-8")

                with patch("tooling.scripts.latex_build.build_root", side_effect=[12, 12]):
                    stderr_buffer = StringIO()
                    with redirect_stderr(stderr_buffer):
                        status = latex_build.build_roots([tex_a, tex_b], log_dir=log_dir)

            self.assertEqual(1, status)
            stderr_text = stderr_buffer.getvalue()
            self.assertIn("Failure clusters", stderr_text)
            self.assertIn("2 x Package cornell-notes Error", stderr_text)
            self.assertIn("l.<n>", stderr_text)

    def test_build_changed_includes_style_dependency_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)
            tex_path = src_dir / "a.tex"
            tex_path.write_text("\\documentclass{article}\\begin{document}A\\end{document}", encoding="utf-8")

            with patch("tooling.scripts.latex_build.collect_changed_paths", return_value=["tooling/styles/latex/cornell-notes.sty"]), patch(
                "tooling.scripts.latex_build.discover_roots", return_value=[tex_path]
            ), patch("tooling.scripts.latex_build.determine_affected_roots", return_value=[tex_path]), patch(
                "tooling.scripts.latex_build.build_roots", return_value=0
            ) as build_roots_mock:
                status = latex_build.build_changed(
                    base_ref="base",
                    head_ref="head",
                    jobs=2,
                    output_dir=root / "public" / "pdfs",
                    log_dir=root / "public" / "logs",
                    clean_output=True,
                )

            self.assertEqual(0, status)
            _, kwargs = build_roots_mock.call_args
            self.assertEqual(2, kwargs["jobs"])
            self.assertEqual(root / "public" / "pdfs", kwargs["output_dir"])
            self.assertEqual(root / "public" / "logs", kwargs["log_dir"])
            self.assertTrue(kwargs["clean_output"])

    def test_build_changed_with_zero_roots_still_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir(parents=True, exist_ok=True)
            output_dir = root / "public" / "pdfs"
            log_dir = root / "public" / "logs"

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch(
                "tooling.scripts.latex_build.collect_changed_paths", return_value=[]
            ), patch("tooling.scripts.latex_build.discover_roots", return_value=[]):
                status = latex_build.build_changed(
                    base_ref="HEAD~1",
                    head_ref="HEAD",
                    jobs=2,
                    output_dir=Path("public/pdfs"),
                    log_dir=Path("public/logs"),
                    clean_output=True,
                )

            self.assertEqual(0, status)
            summary_path = log_dir / "build-summary.json"
            self.assertTrue(summary_path.exists())
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual("changed", summary["mode"])
            self.assertEqual(0, summary["attempted_count"])
            self.assertEqual(0, summary["failed_count"])
            self.assertEqual("success", summary["build_status"])

    def test_build_changed_base_equals_head_writes_zero_root_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True, exist_ok=True)
            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n", encoding="utf-8")

            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"):
                status = latex_build.build_changed(
                    base_ref="HEAD",
                    head_ref="HEAD",
                    output_dir=root / "public" / "pdfs",
                    log_dir=root / "public" / "logs",
                    clean_output=True,
                )

            self.assertEqual(0, status)
            summary = json.loads((root / "public" / "logs" / "build-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(0, summary["root_count"])
            self.assertEqual(0, summary["attempted_count"])
            self.assertEqual("success", summary["build_status"])

    def test_build_changed_invalid_revision_returns_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src"
            src_dir.mkdir(parents=True, exist_ok=True)

            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            subprocess.run(["git", "commit", "--allow-empty", "-m", "initial"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            stderr_buffer = StringIO()
            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"):
                with redirect_stderr(stderr_buffer):
                    status = latex_build.build_changed(
                        base_ref="does-not-exist",
                        head_ref="HEAD",
                        output_dir=root / "public" / "pdfs",
                        log_dir=root / "public" / "logs",
                        clean_output=True,
                    )

            self.assertEqual(2, status)
            self.assertIn("Configuration error:", stderr_buffer.getvalue())
            summary = json.loads((root / "public" / "logs" / "build-summary.json").read_text(encoding="utf-8"))
            self.assertEqual("invalid", summary["build_status"])
            self.assertEqual("configuration", summary["first_errors"][0]["root"])

    def test_build_changed_rebuilds_all_roots_for_workflow_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex_a = root / "src" / "docs" / "a.tex"
            tex_b = root / "src" / "docs" / "b.tex"
            tex_a.parent.mkdir(parents=True, exist_ok=True)
            tex_a.write_text("\\documentclass{article}\\begin{document}A\\end{document}", encoding="utf-8")
            tex_b.write_text("\\documentclass{article}\\begin{document}B\\end{document}", encoding="utf-8")

            with patch("tooling.scripts.latex_build.collect_changed_paths", return_value=[".github/actions/build-documents/action.yml"]), patch(
                "tooling.scripts.latex_build.discover_roots", return_value=[tex_a, tex_b]
            ), patch("tooling.scripts.latex_build.build_roots", return_value=0) as build_roots_mock:
                status = latex_build.build_changed(base_ref="base", head_ref="head")

            self.assertEqual(0, status)
            build_roots_mock.assert_called_once()
            self.assertEqual([tex_a, tex_b], build_roots_mock.call_args.args[0])

    def test_build_root_resolves_relative_output_paths_from_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True, exist_ok=True)
            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\\begin{document}Hello\\end{document}", encoding="utf-8")

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                work_dir = Path(cwd)
                (work_dir / "sample.pdf").write_bytes(b"%PDF-1.4")
                (work_dir / "sample.log").write_text("! Sample failure line\n", encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch(
                "tooling.scripts.latex_build.subprocess.run", side_effect=fake_run
            ):
                status = latex_build.build_root(tex_path, output_dir=Path("public/pdfs"), log_dir=Path("public/logs"))

            self.assertEqual(0, status)
            self.assertTrue((root / "public" / "pdfs" / "docs" / "sample.pdf").exists())
            self.assertTrue((root / "public" / "logs" / "docs" / "sample.build.stdout.txt").exists())
            self.assertTrue((root / "public" / "logs" / "docs" / "sample.log.txt").exists())

    def test_build_summary_contains_required_contract_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True, exist_ok=True)
            tex_path = src_dir / "ok.tex"
            tex_path.write_text("\\documentclass{article}\\begin{document}OK\\end{document}", encoding="utf-8")

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                Path(cwd, "ok.pdf").write_bytes(b"%PDF-1.4")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch(
                "tooling.scripts.latex_build.subprocess.run", side_effect=fake_run
            ):
                status = latex_build.build_roots(
                    [tex_path],
                    output_dir=root / "public" / "pdfs",
                    log_dir=root / "public" / "logs",
                    clean_output=True,
                    mode="full",
                    base_revision="base123",
                    head_revision="head456",
                )

            self.assertEqual(0, status)
            summary = json.loads((root / "public" / "logs" / "build-summary.json").read_text(encoding="utf-8"))
            for key in (
                "mode",
                "base_revision",
                "head_revision",
                "root_count",
                "attempted_count",
                "succeeded_count",
                "failed_count",
                "skipped_count",
                "pdf_count",
                "log_count",
                "build_status",
            ):
                self.assertIn(key, summary)
            self.assertEqual("full", summary["mode"])
            self.assertEqual("base123", summary["base_revision"])
            self.assertEqual("head456", summary["head_revision"])

    def test_build_category_writes_mode_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "security"
            src_dir.mkdir(parents=True, exist_ok=True)
            tex_path = src_dir / "sample.tex"
            tex_path.write_text("\\documentclass{article}\\begin{document}x\\end{document}", encoding="utf-8")

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                Path(cwd, "sample.pdf").write_bytes(b"%PDF-1.4")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"), patch(
                "tooling.scripts.latex_build.subprocess.run", side_effect=fake_run
            ):
                status = latex_build.build_roots(
                    [tex_path],
                    output_dir=Path("public/pdfs"),
                    log_dir=Path("public/logs"),
                    clean_output=True,
                    mode="category",
                )

            self.assertEqual(0, status)
            summary = json.loads((root / "public" / "logs" / "build-summary.json").read_text(encoding="utf-8"))
            self.assertEqual("category", summary["mode"])

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

    def test_collect_dependencies_tracks_transitive_style_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            style_dir = root / "tooling" / "styles" / "latex"
            src_dir.mkdir(parents=True)
            style_dir.mkdir(parents=True)

            tex_path = src_dir / "sample.tex"
            tex_path.write_text(
                "\\documentclass{article}\n"
                "\\usepackage{outer-style}\n"
                "\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )
            (style_dir / "outer-style.sty").write_text("\\usepackage{inner-style}\n", encoding="utf-8")
            inner_style = style_dir / "inner-style.sty"
            inner_style.write_text("% shared inner style\n", encoding="utf-8")

            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"):
                roots = discover_roots(root / "src")
                affected = determine_affected_roots(roots, changed_path=inner_style)

            self.assertEqual([tex_path.resolve()], affected)

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
            stderr_log = log_dir / "docs" / "sample.build.stderr.txt"
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
                    status = latex_build.build_roots([tex_path], log_dir=log_dir)

            self.assertEqual(1, status)
            self.assertIn("Build failed for", stderr_buffer.getvalue())
            self.assertIn("Build summary: 0 succeeded, 1 failed, 1 total", stderr_buffer.getvalue())
            self.assertIn("sample.build.stdout.txt", stderr_buffer.getvalue())

    def test_build_roots_returns_one_not_failure_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            tex_a = src_dir / "a.tex"
            tex_b = src_dir / "b.tex"
            tex_a.write_text("\\documentclass{article}\n\\begin{document}\nA\n\\end{document}\n", encoding="utf-8")
            tex_b.write_text("\\documentclass{article}\n\\begin{document}\nB\n\\end{document}\n", encoding="utf-8")

            with patch("tooling.scripts.latex_build.build_root", side_effect=[5, 9]):
                stderr_buffer = StringIO()
                with redirect_stderr(stderr_buffer):
                    status = latex_build.build_roots([tex_a, tex_b], log_dir=root / "public" / "logs")

            self.assertEqual(1, status)
            self.assertIn("Build summary: 0 succeeded, 2 failed, 2 total", stderr_buffer.getvalue())

    def test_parallel_and_serial_use_same_failure_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)

            tex_files = []
            for name in ("a", "b", "c"):
                tex = src_dir / f"{name}.tex"
                tex.write_text("\\documentclass{article}\n\\begin{document}\nX\n\\end{document}\n", encoding="utf-8")
                tex_files.append(tex)

            with patch("tooling.scripts.latex_build.build_root", side_effect=[0, 12, 0]):
                serial_status = latex_build.build_roots(tex_files, jobs=1, log_dir=root / "public" / "logs")

            with patch("tooling.scripts.latex_build.build_root", side_effect=[0, 12, 0]):
                parallel_status = latex_build.build_roots(tex_files, jobs=2, log_dir=root / "public" / "logs")

            self.assertEqual(1, serial_status)
            self.assertEqual(1, parallel_status)

    def test_duplicate_stems_write_distinct_log_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src"
            left = src_dir / "left"
            right = src_dir / "right"
            left.mkdir(parents=True)
            right.mkdir(parents=True)

            tex_left = left / "shared.tex"
            tex_right = right / "shared.tex"
            tex_left.write_text("\\documentclass{article}\n\\begin{document}\nL\n\\end{document}\n", encoding="utf-8")
            tex_right.write_text("\\documentclass{article}\n\\begin{document}\nR\n\\end{document}\n", encoding="utf-8")

            log_dir = root / "public" / "logs"
            with patch("tooling.scripts.latex_build.ROOT", root), patch("tooling.scripts.latex_build.SRC_DIR", root / "src"):
                left_stdout, left_stderr = latex_build._log_paths(tex_left, log_dir)
                right_stdout, right_stderr = latex_build._log_paths(tex_right, log_dir)

            self.assertNotEqual(left_stdout, right_stdout)
            self.assertNotEqual(left_stderr, right_stderr)
            self.assertIn("left/shared.build.stdout.txt", str(left_stdout))
            self.assertIn("right/shared.build.stdout.txt", str(right_stdout))

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

    def test_reusable_workflow_uploads_logs_on_failure(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        workflow_text = (repo_root / ".github" / "workflows" / "_build-latex.yml").read_text(encoding="utf-8")

        self.assertIn("if: ${{ always() && inputs.upload-artifacts && steps.build-docs.outputs.has-logs == 'true' }}", workflow_text)
        self.assertIn("name: latex-logs", workflow_text)

    def test_reusable_workflow_uploads_pdfs_only_when_valid_outputs_exist(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        workflow_text = (repo_root / ".github" / "workflows" / "_build-latex.yml").read_text(encoding="utf-8")

        self.assertIn("steps.build-docs.outputs.build-status == 'success'", workflow_text)
        self.assertIn("steps.build-docs.outputs.has-pdfs == 'true'", workflow_text)

    def test_build_documents_action_exposes_artifact_contract_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        action_text = (repo_root / ".github" / "actions" / "build-documents" / "action.yml").read_text(encoding="utf-8")

        self.assertIn("root-count", action_text)
        self.assertIn("attempted-count", action_text)
        self.assertIn("success-count", action_text)
        self.assertIn("failure-count", action_text)
        self.assertIn("log-count", action_text)
        self.assertIn("has-pdfs", action_text)
        self.assertIn("has-logs", action_text)
        self.assertIn("build-status", action_text)

    def test_build_documents_action_preserves_failure_exit_status_after_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        action_text = (repo_root / ".github" / "actions" / "build-documents" / "action.yml").read_text(encoding="utf-8")

        self.assertIn("set +e", action_text)
        self.assertIn("build_status_code=$?", action_text)
        self.assertIn("exit \"$build_status_code\"", action_text)

    def test_build_documents_action_uses_canonical_make_revision_variables(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        action_text = (repo_root / ".github" / "actions" / "build-documents" / "action.yml").read_text(encoding="utf-8")

        self.assertIn('BASE_REF="$base_ref"', action_text)
        self.assertIn('HEAD_REF="$head_ref"', action_text)
        self.assertNotIn("BASE_REVISION", action_text)
        self.assertNotIn("HEAD_REVISION", action_text)

    def test_build_documents_action_manifest_schema_and_caller_compatibility(self) -> None:
        try:
            import yaml  # type: ignore
        except ImportError:
            self.skipTest("PyYAML is not available")

        repo_root = Path(__file__).resolve().parents[1]
        action_path = repo_root / ".github" / "actions" / "build-documents" / "action.yml"
        workflow_path = repo_root / ".github" / "workflows" / "_build-latex.yml"

        raw = action_path.read_text(encoding="utf-8")
        self.assertNotIn("\t", raw)

        data = yaml.safe_load(raw)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data.get("runs"), dict)
        self.assertEqual("composite", data["runs"].get("using"))
        self.assertIsInstance(data["runs"].get("steps"), list)
        self.assertGreater(len(data["runs"]["steps"]), 0)

        forbidden_root_keys = {"on", "jobs", "permissions", "concurrency", "env"}
        self.assertFalse(forbidden_root_keys.intersection(data.keys()))

        step_ids = {
            step.get("id")
            for step in data["runs"]["steps"]
            if isinstance(step, dict) and isinstance(step.get("id"), str)
        }
        for step in data["runs"]["steps"]:
            if isinstance(step, dict) and "run" in step:
                self.assertIn("shell", step)

        outputs = data.get("outputs")
        self.assertIsInstance(outputs, dict)
        for output_name, output_def in outputs.items():
            self.assertIsInstance(output_def, dict, output_name)
            self.assertIn("description", output_def, output_name)
            self.assertIn("value", output_def, output_name)

            value = str(output_def["value"])
            for ref_id in re.findall(r"steps\.([A-Za-z0-9_-]+)\.outputs", value):
                self.assertIn(ref_id, step_ids)

        expected_inputs = {"mode", "category", "jobs", "base-ref", "head-ref"}
        self.assertEqual(expected_inputs, set(data.get("inputs", {}).keys()))

        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        self.assertIsInstance(workflow, dict)
        build_steps = workflow["jobs"]["build"]["steps"]
        matching = [
            step
            for step in build_steps
            if isinstance(step, dict) and step.get("uses") == "./.github/actions/build-documents"
        ]
        self.assertEqual(1, len(matching))
        self.assertEqual(expected_inputs, set(matching[0].get("with", {}).keys()))

    def test_main_parses_build_changed_base_and_head_into_build_changed_call(self) -> None:
        with patch("tooling.scripts.latex_build.build_changed", return_value=0) as build_changed_mock:
            status = latex_build.main(["build-changed", "--base", "base123", "--head", "head456", "--jobs", "3"])

        self.assertEqual(0, status)
        build_changed_mock.assert_called_once_with(
            base_ref="base123",
            head_ref="head456",
            jobs=3,
            output_dir=None,
            log_dir=None,
            artifact_dir=None,
            clean_output=False,
            mode_name="changed",
        )

    def test_main_rejects_unknown_build_changed_revision_flags(self) -> None:
        stderr_buffer = StringIO()
        with redirect_stderr(stderr_buffer):
            with self.assertRaises(SystemExit) as exc:
                latex_build.main(["build-changed", "--base-revision", "base123"])

        self.assertEqual(2, exc.exception.code)
        self.assertIn("unrecognized arguments", stderr_buffer.getvalue())

    def test_make_build_changed_uses_canonical_revision_flags(self) -> None:
        command = self._make_dry_run_command(
            "build-changed",
            "OUTPUT_DIR=public/pdfs",
            "LOG_DIR=public/logs",
            "CLEAN_OUTPUT=true",
            "MODE_NAME=changed",
            "JOBS=4",
            "BASE_REF=base123",
            "HEAD_REF=head456",
        )

        self.assertIn("--base base123", command)
        self.assertIn("--head head456", command)
        self.assertIn("--output-dir public/pdfs", command)
        self.assertIn("--log-dir public/logs", command)
        self.assertIn("--mode-name changed", command)
        self.assertIn("--clean-output", command)
        self.assertNotIn("--base-revision", command)
        self.assertNotIn("--head-revision", command)

    def test_make_build_changed_maps_legacy_revision_variables_to_canonical_flags(self) -> None:
        command = self._make_dry_run_command(
            "build-changed",
            "BASE_REVISION=base123",
            "HEAD_REVISION=head456",
        )

        self.assertIn("--base base123", command)
        self.assertIn("--head head456", command)
        self.assertNotIn("--base-revision", command)
        self.assertNotIn("--head-revision", command)

    def test_make_build_changed_omits_empty_revision_flags(self) -> None:
        command = self._make_dry_run_command("build-changed")

        self.assertNotIn("--base", command)
        self.assertNotIn("--head", command)

    def test_make_build_changed_command_is_accepted_by_python_parser(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        command = self._make_dry_run_command(
            "build-changed",
            "OUTPUT_DIR=public/pdfs",
            "LOG_DIR=public/logs",
            "CLEAN_OUTPUT=true",
            "MODE_NAME=changed",
            "JOBS=1",
            "BASE_REF=HEAD",
            "HEAD_REF=HEAD",
        )

        result = subprocess.run(shlex.split(command), cwd=repo_root, check=False, capture_output=True, text=True)

        self.assertEqual(0, result.returncode, result.stderr)

    def test_build_documents_action_sets_has_logs_when_summary_exists(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        action_text = (repo_root / ".github" / "actions" / "build-documents" / "action.yml").read_text(encoding="utf-8")

        self.assertIn("if [[ -f \"public/logs/build-summary.json\" ]]; then", action_text)
        self.assertIn("has_logs=true", action_text)

    def test_pages_workflow_permissions_and_job_dependencies(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        workflow_text = (repo_root / ".github" / "workflows" / "latex-pages.yml").read_text(encoding="utf-8")

        self.assertIn("contents: read", workflow_text)
        self.assertIn("pages: write", workflow_text)
        self.assertIn("id-token: write", workflow_text)
        self.assertIn("needs: build", workflow_text)
        self.assertIn("needs: stage", workflow_text)

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

    def test_minimal_cornell_document_compiles_with_standard_maketitle(self) -> None:
        if shutil.which(latex_build.LATEXMK) is None:
            self.skipTest("latexmk is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex_path = root / "minimal-cornell.tex"
            tex_path.write_text(
                "\\documentclass[10pt,letterpaper]{article}\n"
                "\\usepackage{cornell-notes}\n"
                "\\title{Minimal Cornell Title}\n"
                "\\author{Test Author}\n"
                "\\date{\\today}\n"
                "\\setDocTitle{Minimal Cornell Title}\n"
                "\\begin{document}\n"
                "\\maketitle\n"
                "Body text.\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            output_dir = root / "public" / "pdfs"
            log_dir = root / "public" / "logs"
            result = latex_build.build_root(tex_path, output_dir=output_dir, log_dir=log_dir)

            self.assertEqual(0, result)
            self.assertTrue((output_dir / "minimal-cornell.pdf").exists())

    def test_minimal_cornell_document_without_title_fails_clearly(self) -> None:
        if shutil.which(latex_build.LATEXMK) is None:
            self.skipTest("latexmk is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex_path = root / "missing-title-cornell.tex"
            tex_path.write_text(
                "\\documentclass[10pt,letterpaper]{article}\n"
                "\\usepackage{cornell-notes}\n"
                "\\author{Test Author}\n"
                "\\date{\\today}\n"
                "\\begin{document}\n"
                "\\maketitle\n"
                "Body text.\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            output_dir = root / "public" / "pdfs"
            log_dir = root / "public" / "logs"
            result = latex_build.build_root(tex_path, output_dir=output_dir, log_dir=log_dir)

            self.assertNotEqual(0, result)
            stdout_log = log_dir / "missing-title-cornell.build.stdout.txt"
            self.assertTrue(stdout_log.exists())
            stdout_text = stdout_log.read_text(encoding="utf-8", errors="ignore")
            self.assertIn("Package cornell-notes Error:", stdout_text)
            self.assertIn("explicit \\title{...}", stdout_text)


if __name__ == "__main__":
    unittest.main()
