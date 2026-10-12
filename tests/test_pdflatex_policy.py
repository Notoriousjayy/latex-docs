"""pdfLaTeX-only compiler policy and Cornell table-safety regression tests.

Covers the two CI failure clusters from workflow run 38311143100
(commit 168f1333):

* fontspec/engine-magic documents that compiled locally but failed on CI
  runners without the referenced system fonts ("The font 'Inter' cannot be
  found"), eliminated by the repository-wide pdfLaTeX-only contract; and
* "Misplaced \\noalign" aborts caused by typesetting tcolorbox inside
  longtable cells, where the emitted \\pagebreak[0] is only legal between
  rows and whether it is emitted depends on the installed tcolorbox release.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tooling.scripts.latex_build as latex_build

REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE_DIRS = (
    REPO_ROOT / "tooling" / "styles" / "latex",
    REPO_ROOT / "tooling" / "latex",
)

_HAS_PDFLATEX = shutil.which("pdflatex") is not None


class PdfLatexPreflightTests(unittest.TestCase):
    """Unit coverage for the preflight scanner (no TeX toolchain required)."""

    def _scan(self, text: str) -> list:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "doc.tex"
            path.write_text(text, encoding="utf-8")
            return latex_build.pdflatex_preflight_file(path)

    def test_detects_lualatex_magic_comment(self) -> None:
        violations = self._scan("% !TeX program = lualatex\n\\documentclass{article}\n")
        self.assertEqual(1, len(violations))
        self.assertIn("lualatex", str(violations[0]["construct"]))

    def test_detects_xelatex_magic_comment_case_insensitive(self) -> None:
        violations = self._scan("%!tex PROGRAM=XeLaTeX\n")
        self.assertEqual(1, len(violations))

    def test_detects_active_fontspec_package(self) -> None:
        violations = self._scan("\\usepackage{fontspec}\n")
        self.assertEqual(1, len(violations))
        self.assertIn("fontspec", str(violations[0]["construct"]))

    def test_detects_fontspec_in_package_list(self) -> None:
        violations = self._scan("\\usepackage{graphicx, fontspec ,xcolor}\n")
        self.assertEqual(1, len(violations))

    def test_detects_unicode_math_and_font_commands(self) -> None:
        text = "\\usepackage{unicode-math}\n\\setmainfont{Inter}\n\\setmathfont{STIX Two Math}\n"
        violations = self._scan(text)
        self.assertEqual(3, len(violations))

    def test_ignores_commented_out_fontspec(self) -> None:
        text = "% \\usepackage{fontspec}\n%\\setmainfont{Inter}\nx % \\setmonofont{Y}\n"
        self.assertEqual([], self._scan(text))

    def test_ignores_fontspec_inside_listings(self) -> None:
        text = (
            "\\begin{lstlisting}\n\\usepackage{fontspec}\n\\setmainfont{Inter}\n\\end{lstlisting}\n"
            "\\begin{minted}{latex}\n% !TeX program = lualatex\n\\setmonofont{X}\n\\end{minted}\n"
            "\\begin{verbatim}\n\\usepackage{unicode-math}\n\\end{verbatim}\n"
        )
        self.assertEqual([], self._scan(text))

    def test_ignores_inline_verbatim_and_prose(self) -> None:
        text = (
            "Historically this used \\verb|\\setmainfont{Inter}| via fontspec.\n"
            "\\lstinline|\\usepackage{fontspec}| is no longer allowed.\n"
        )
        self.assertEqual([], self._scan(text))

    def test_escaped_percent_does_not_hide_directive(self) -> None:
        violations = self._scan("\\% comment-looking \\usepackage{fontspec}\n")
        self.assertEqual(1, len(violations))

    def test_reports_line_numbers_after_verbatim_blanking(self) -> None:
        text = "line1\n\\begin{verbatim}\nx\ny\n\\end{verbatim}\n\\usepackage{fontspec}\n"
        violations = self._scan(text)
        self.assertEqual(1, len(violations))
        self.assertEqual(6, violations[0]["line"])

    def test_corpus_is_clean(self) -> None:
        violations = latex_build.pdflatex_preflight()
        self.assertEqual(
            [],
            violations,
            "first-party LaTeX sources must not use LuaLaTeX/XeLaTeX-only constructs",
        )


class PdfLatexEngineContractTests(unittest.TestCase):
    """The build orchestrator must only ever invoke pdflatex via latexmk -pdf."""

    def test_build_root_rejects_engine_magic_comment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)
            tex_path = src_dir / "sample.tex"
            tex_path.write_text(
                "% !TeX program = lualatex\n\\documentclass{article}\n\\begin{document}\nx\n\\end{document}\n",
                encoding="utf-8",
            )
            log_dir = root / "logs"

            with patch("tooling.scripts.latex_build.ROOT", root), patch(
                "tooling.scripts.latex_build.SRC_DIR", root / "src"
            ), patch("tooling.scripts.latex_build.subprocess.run") as run_mock:
                result = latex_build.build_root(tex_path, log_dir=log_dir)

            self.assertEqual(2, result)
            run_mock.assert_not_called()
            stderr_log = log_dir / "docs" / "sample.build.stderr.txt"
            self.assertTrue(stderr_log.exists())
            self.assertIn("pdfLaTeX policy violation", stderr_log.read_text(encoding="utf-8"))

    def test_build_root_command_uses_pdf_mode_without_engine_switches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src" / "docs"
            src_dir.mkdir(parents=True)
            tex_path = src_dir / "sample.tex"
            tex_path.write_text(
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )

            def fake_run(cmd, cwd, env, stdout=None, stderr=None, check=False):
                (Path(cwd) / "sample.pdf").write_bytes(b"%PDF-1.4")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("tooling.scripts.latex_build.ROOT", root), patch(
                "tooling.scripts.latex_build.SRC_DIR", root / "src"
            ), patch("tooling.scripts.latex_build.subprocess.run", side_effect=fake_run) as run_mock:
                result = latex_build.build_root(tex_path)

            self.assertEqual(0, result)
            cmd = run_mock.call_args.args[0]
            self.assertIn("-pdf", cmd)
            for forbidden in ("-lualatex", "-xelatex", "-pdflua", "-pdfxe", "%O", "%S"):
                self.assertNotIn(forbidden, cmd)

    def test_build_script_has_no_alternative_engine_invocations(self) -> None:
        source = (REPO_ROOT / "tooling" / "scripts" / "latex_build.py").read_text(encoding="utf-8")
        for token in ('"-lualatex"', '"-xelatex"', "'-lualatex'", "'-xelatex'"):
            self.assertNotIn(token, source, f"latex_build.py must not pass {token} to latexmk")

    def test_latexmkrc_pins_pdf_mode(self) -> None:
        rc_text = (REPO_ROOT / ".latexmkrc").read_text(encoding="utf-8")
        self.assertIn("$pdf_mode = 1", rc_text.replace("my ", ""))
        self.assertNotIn("lualatex", rc_text)
        self.assertNotIn("xelatex", rc_text)


class CornellFormulaTableSafetyTests(unittest.TestCase):
    """The shared formula cell must be built from primitive boxes only."""

    STY_PATH = REPO_ROOT / "tooling" / "styles" / "latex" / "cornell-notes.sty"

    def _formula_section(self) -> str:
        text = self.STY_PATH.read_text(encoding="utf-8")
        start = text.index("3b. Table-safe formula rendering")
        end = text.index("% ---", start + 200)
        section = text[start:end]
        # Assertions target active code only; the explanatory comment block
        # legitimately names the forbidden constructs.
        return "\n".join(
            line for line in section.splitlines() if not line.lstrip().startswith("%")
        )

    def test_formula_macro_avoids_tcolorbox(self) -> None:
        section = self._formula_section()
        self.assertIn("\\fcolorbox", section)
        self.assertNotIn("\\begin{tcolorbox}", section)
        self.assertNotIn("newtcolorbox", section)
        self.assertNotIn("nobeforeafter", section)

    def test_formula_macro_has_no_pagebreak_tokens(self) -> None:
        section = self._formula_section()
        self.assertNotIn("\\pagebreak", section)
        self.assertNotIn("\\nopagebreak", section)
        self.assertNotIn("\\noalign", section)

    @unittest.skipUnless(_HAS_PDFLATEX, "pdflatex not installed")
    def test_multipage_longtable_formula_fixture_compiles(self) -> None:
        rows = []
        for n in range(40):
            rows.append(
                "\\cornellcuerow{Recall %d?}{\\formula{\\int_a^b f(x)\\,dx="
                "\\lim_{n\\to\\infty}\\sum_{i=1}^n f(x_i^*)\\,\\Delta x_{%d}}}" % (n, n)
            )
            rows.append(
                "\\cornellcuerow{Text row %d}{Mixed text content between formula rows"
                " to vary cell heights across page boundaries.}" % n
            )
        fixture = (
            "\\documentclass[11pt]{article}\n"
            "\\usepackage{cornell-notes}\n"
            "\\title{Cornell formula longtable regression fixture}\n"
            "\\author{CI}\n\\date{2026}\n"
            "\\definecolor{Sky}{HTML}{DDEEF1}\n"
            "\\definecolor{Cue}{HTML}{EEF2F5}\n"
            "\\newcommand{\\cornellcuehead}{\\rowcolor{Navy}\\color{white}\\bfseries Cue &"
            " \\color{white}\\bfseries Notes \\\\\\endhead}\n"
            "\\newcommand{\\cornellcuerow}[2]{\\rowcolor{Cue}#1 & #2 \\\\\\addlinespace[3pt]}\n"
            "\\newcommand{\\formula}[1]{\\CornellFormula[colback=Sky,colframe=Teal]{#1}}\n"
            "\\newcolumntype{C}{>{\\raggedright\\arraybackslash}p{0.29\\linewidth}}\n"
            "\\newcolumntype{N}{>{\\raggedright\\arraybackslash}p{0.65\\linewidth}}\n"
            "\\begin{document}\n"
            "\\begin{longtable}{C N}\\cornellcuehead\n" + "\n".join(rows) + "\n"
            "\\end{longtable}\n"
            "\\end{document}\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            (work / "fixture.tex").write_text(fixture, encoding="utf-8")
            texinputs = "".join(f"{style_dir}//:" for style_dir in STYLE_DIRS)
            env = dict(**__import__("os").environ, TEXINPUTS=texinputs)
            for _ in range(2):  # two passes: longtable needs one rerun for widths
                proc = subprocess.run(
                    [
                        "pdflatex",
                        "-shell-escape",
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        "fixture.tex",
                    ],
                    cwd=work,
                    env=env,
                    capture_output=True,
                    text=True,
                )
            log_text = (work / "fixture.log").read_text(encoding="utf-8", errors="ignore")
            self.assertEqual(0, proc.returncode, f"fixture failed:\n{log_text[-3000:]}")
            self.assertNotIn("Misplaced \\noalign", log_text)
            self.assertTrue((work / "fixture.pdf").exists())


if __name__ == "__main__":
    unittest.main()
