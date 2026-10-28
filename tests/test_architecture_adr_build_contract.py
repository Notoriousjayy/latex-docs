"""Regression checks for the ADR table and the sharded LaTeX runner."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ArchitectureAdrBuildContractTests(unittest.TestCase):
    def test_guide_table_header_is_terminated_before_midrule(self):
        source = (ROOT / "src/architecture/decisions/adr-lifecycle-and-review-guide.tex").read_text(encoding="utf-8")
        lines = source.splitlines()
        index = next(i for i, line in enumerate(lines) if r"\textbf{Decision responsibility}" in line)
        self.assertTrue(lines[index].endswith(r"\\"), lines[index])
        self.assertEqual(r"\midrule", lines[index + 1].strip())

    def test_tex_jobs_use_validated_ubuntu_image(self):
        workflow = (ROOT / ".github/workflows/_build-latex.yml").read_text(encoding="utf-8")
        for job_name in ("raster", "build"):
            block = re.search(rf"^  {job_name}:\n(.*?)(?=^  [a-z-]+:|\Z)", workflow, re.M | re.S)
            self.assertIsNotNone(block, job_name)
            self.assertIn("runs-on: ubuntu-24.04", block.group(1))

    def test_setup_verifies_actual_minted_execution(self):
        setup = (ROOT / ".github/actions/setup-latex/action.yml").read_text(encoding="utf-8")
        self.assertIn("Smoke test minted syntax highlighting", setup)
        self.assertIn(r"\begin{minted}{python}", setup)
        self.assertIn("pdflatex -shell-escape", setup)
