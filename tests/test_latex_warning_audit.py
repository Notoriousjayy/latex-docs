"""Regression tests for final-pass LaTeX warning collection."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tooling.scripts.latex_build import _audit_final_log


class LatexWarningAuditTests(unittest.TestCase):
    def audit(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "document.log"
            if text is not None:
                p.write_text(text, encoding="utf-8")
            return _audit_final_log(p)

    def test_clean_final_pass(self):
        self.assertEqual("clean", self.audit("LaTeX Font Info: loading font\nOutput written on doc.pdf (1 page).\n")["status"])

    def test_missing_or_incomplete_final_log(self):
        for text in (None, "", "LaTeX Warning: Reference undefined.\n"):
            self.assertEqual("missing-log", self.audit(text)["status"])

    def test_native_warnings_and_boxes(self):
        result = self.audit(
            "LaTeX Warning: Reference undefined on input line 3.\n"
            "Package hyperref Warning: Token not allowed in a PDF string\n"
            "(hyperref)                removing math shift on input line 7.\n"
            "Overfull \\hbox (1.0pt too wide) in paragraph at lines 9--10\n"
            "Underfull \\vbox (badness 10000) has occurred while \\output is active\n"
            "LaTeX Font Warning: Some font shapes were not available.\n"
            "Missing character: There is no x in font y!\n"
            "pdfTeX warning (ext4): destination with the same identifier\n"
            "Output written on doc.pdf (2 pages).\n"
        )
        self.assertEqual("warnings", result["status"])
        self.assertEqual(7, result["warning_count"])
        self.assertIn("removing math shift", result["diagnostics"][1]["message"])
        self.assertEqual(4, result["diagnostics"][2]["log_line"])

    @unittest.skipUnless(shutil.which("latexmk") and shutil.which("pdflatex"), "LaTeX toolchain not installed")
    def test_narrow_table_paragraphs_compile_without_warnings(self):
        package_dir = Path(__file__).resolve().parents[1] / "tooling" / "latex"
        source = r"""
\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{tabularx}
\usepackage{lds-table-layout}
\begin{document}
\noindent\begin{tabular}{p{1in} >{\centering\arraybackslash}p{1in} >{\raggedleft\arraybackslash}p{1in}}
An engineering workflow with very narrow text columns & Centered text in a narrow column & Explicitly right aligned text.\\
\end{tabular}\par
\noindent\begin{tabularx}{\linewidth}{p{1in} X}
An engineering workflow with very narrow text columns & Flexible column used to display relevant additional detail for this example.\\
\end{tabularx}\par
\begin{longtable}{p{1in} >{\centering\arraybackslash}p{1in}}
An engineering workflow with very narrow text columns & Centered text in a narrow column.\\
\end{longtable}
\end{document}
"""
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "document.tex").write_text(source, encoding="utf-8")
            env = dict(os.environ)
            env["TEXINPUTS"] = str(package_dir) + os.pathsep + env.get("TEXINPUTS", "") + os.pathsep
            result = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "document.tex"],
                cwd=work, env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            audit = _audit_final_log(work / "document.log")
            self.assertEqual("clean", audit["status"], audit)

