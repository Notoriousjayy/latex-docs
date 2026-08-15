import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import tooling.scripts.style_migration as sm
from tooling.scripts.style_migration import (
    classify_latex_style,
    classify_plantuml_style,
    filename_policy_violations,
    find_unbalanced_setminted_lines,
    find_malformed_mintinline_lines,
    strip_latex_comments,
    _validate_naming,
    validate_repo,
)


class StyleMigrationTests(unittest.TestCase):
    @staticmethod
    def _all_cornell_roots(repo_root: Path) -> list[Path]:
        computer_science_root = repo_root / "src" / "cornell-notes" / "computer-science"
        computer_science = (
            sorted((computer_science_root / "combinatorial-algorithms").rglob("*.tex"))
            + sorted((computer_science_root / "computer-networks").rglob("*.tex"))
            + sorted((computer_science_root / "operating-systems").rglob("*.tex"))
        )
        electronics = sorted((repo_root / "src" / "cornell-notes" / "electronics" / "electronic-circuits").rglob("*.tex"))
        cissp = sorted((repo_root / "src" / "cornell-notes" / "security" / "certifications" / "cissp").glob("*.tex"))
        numerical = sorted((repo_root / "src" / "cornell-notes" / "mathematics" / "numerical-methods").rglob("*.tex"))
        return computer_science + electronics + cissp + numerical

    def test_classify_latex_style_for_personal_documents(self) -> None:
        path = Path("src/personal/finance/example.tex")
        self.assertEqual("financial", classify_latex_style(path))

    def test_classify_latex_style_for_technical_design_documents(self) -> None:
        path = Path("src/security/github-advanced-security/references/guide.tex")
        self.assertEqual("technical-design-spec", classify_latex_style(path))

    def test_classify_latex_style_for_cornell_notes_path(self) -> None:
        path = Path("src/cornell-notes/security/certifications/cissp/01-security-and-risk-management-cornell-notes.tex")
        self.assertEqual("cornell-notes", classify_latex_style(path))

    def test_classify_latex_style_cornell_precedence_inside_security(self) -> None:
        path = Path("src/cornell-notes/security/certifications/cissp/06-security-assessment-and-testing-cornell-notes.tex")
        self.assertEqual("cornell-notes", classify_latex_style(path))

    def test_classify_latex_style_for_numerical_methods_cornell_path(self) -> None:
        path = Path("src/cornell-notes/mathematics/numerical-methods/foundations/ch01-preliminaries-notes.tex")
        self.assertEqual("cornell-notes", classify_latex_style(path))

    def test_classify_plantuml_style_for_activity_diagrams(self) -> None:
        self.assertEqual(
            "tooling/styles/plantuml/behavioral/activity-diagram-style.iuml",
            classify_plantuml_style(Path("example.puml"), "@startuml\nstart\n:step;\nstop\n@enduml"),
        )

    def test_classify_plantuml_style_for_sequence_diagrams(self) -> None:
        self.assertEqual(
            "tooling/styles/plantuml/interaction/sequence-diagram-style.iuml",
            classify_plantuml_style(Path("example.puml"), "@startuml\nAlice -> Bob: hello\n@enduml"),
        )

    def test_repo_validator_rejects_listings_usage(self) -> None:
        with patch.object(sm, "_validate_naming", return_value=0):
            self.assertEqual(0, validate_repo())

    def test_repo_validator_flags_direct_listings_packages(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        sample = repo_root / "src" / "security" / "github-advanced-security" / "references" / "key-concepts.tex"
        text = sample.read_text(encoding="utf-8", errors="ignore")
        self.assertNotIn("\\usepackage{listings}", text)
        self.assertNotIn("\\begin{lstlisting}", text)

    def test_repo_validator_flags_listings_macros(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        sample = repo_root / "src" / "devops" / "github-actions" / "ci-cd-starter-github-actions-and-ghcr.tex"
        text = sample.read_text(encoding="utf-8", errors="ignore")
        self.assertNotIn("\\lstset", text)
        self.assertNotIn("\\lstdefinelanguage", text)

    def test_filename_length_50_including_extension_passes(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        # 46-char stem + 4-char extension = 50 total
        path = repo_root / "src" / "tests" / ("a" * 46 + ".tex")
        self.assertEqual([], filename_policy_violations(path))

    def test_filename_length_51_including_extension_fails(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        # 47-char stem + 4-char extension = 51 total
        path = repo_root / "src" / "tests" / ("a" * 47 + ".tex")
        violations = filename_policy_violations(path)
        self.assertIn("filename-too-long", violations)

    def test_clear_short_filename_under_30_passes(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        path = repo_root / "src" / "tests" / "api-guide.tex"
        self.assertEqual([], filename_policy_violations(path))

    def test_nested_directory_length_not_counted(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        deep = repo_root / "src" / "very" / "long" / "nested" / "directory" / "tree"
        path = deep / "api-guide.tex"
        self.assertEqual([], filename_policy_violations(path))

    def test_validate_naming_flags_case_insensitive_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            file_a = base / "src" / "demo" / "alpha.tex"
            file_b = base / "src" / "demo" / "Alpha.tex"
            file_a.parent.mkdir(parents=True, exist_ok=True)
            file_a.write_text("x", encoding="utf-8")
            file_b.write_text("x", encoding="utf-8")
            with patch.object(sm, "ROOT", base):
                with patch.object(sm, "SRC_DIR", base / "src"):
                    result = _validate_naming([file_a, file_b])
            self.assertNotEqual(0, result)

    def test_cornell_notes_documents_use_cornell_package(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for tex_path in self._all_cornell_roots(repo_root):
            text = tex_path.read_text(encoding="utf-8", errors="ignore")
            self.assertIn("\\usepackage{cornell-notes}", text, str(tex_path))

    def test_cornell_notes_documents_use_standard_title_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for tex_path in self._all_cornell_roots(repo_root):
            text = strip_latex_comments(tex_path.read_text(encoding="utf-8", errors="ignore"))
            self.assertRegex(text, r"\\title\s*\{[^{}]+\}", str(tex_path))
            self.assertRegex(text, r"\\author\s*\{[^{}]*\}", str(tex_path))
            self.assertRegex(text, r"\\date\s*\{[^{}]*\}", str(tex_path))
            self.assertEqual(1, text.count("\\maketitle"), str(tex_path))

    def test_cornell_notes_documents_avoid_legacy_title_page_calls(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for tex_path in self._all_cornell_roots(repo_root):
            text = strip_latex_comments(tex_path.read_text(encoding="utf-8", errors="ignore"))
            self.assertNotIn("\\makecornelltitle", text, str(tex_path))
            self.assertNotIn("\\begin{titlepage}", text, str(tex_path))
            self.assertNotIn("\\end{titlepage}", text, str(tex_path))

    def test_cornell_notes_example_uses_standard_title_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        example = repo_root / "src" / "architecture" / "style-system" / "examples" / "cornell-notes-study-sheet.tex"
        text = strip_latex_comments(example.read_text(encoding="utf-8", errors="ignore"))
        self.assertIn("\\usepackage{cornell-notes}", text)
        self.assertRegex(text, r"\\title\s*\{[^{}]+\}")
        self.assertRegex(text, r"\\author\s*\{[^{}]*\}")
        self.assertRegex(text, r"\\date\s*\{[^{}]*\}")
        self.assertEqual(1, text.count("\\maketitle"))
        self.assertNotIn("\\makecornelltitle", text)

    def test_modular_style_architecture_doc_keeps_technical_semantic_package(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        doc_path = repo_root / "src" / "architecture" / "style-system" / "modular-latex-style-module-architecture.tex"
        text = strip_latex_comments(doc_path.read_text(encoding="utf-8", errors="ignore"))
        self.assertIn("\\usepackage{technical-design-spec}", text)

    def test_cornell_package_inherits_from_base(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        style_path = repo_root / "tooling" / "styles" / "latex" / "cornell-notes.sty"
        text = style_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("\\RequirePackage{base}", text)
        self.assertIn("\\LdsRegisterModule{cornell-notes}{Study / Cornell Notes}", text)

    def test_cornell_package_specializes_maketitle_and_keeps_alias(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        style_path = repo_root / "tooling" / "styles" / "latex" / "cornell-notes.sty"
        text = style_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("\\renewcommand{\\maketitle}{\\LdsCornellRenderTitle}", text)
        self.assertIn("\\providecommand{\\makecornelltitle}{\\maketitle}", text)
        self.assertNotIn("\\newcommand{\\makecornelltitle}{\\CornellMakeTitle}", text)

        house_style_path = repo_root / "tooling" / "latex" / "style.sty"
        house_style = house_style_path.read_text(encoding="utf-8", errors="ignore")
        self.assertNotIn("LdsCornellRenderTitle", house_style)

    def test_find_unbalanced_setminted_lines_reports_line_number(self) -> None:
        text = """\\documentclass{article}
\\setminted{
  fontsize=\\small,
\\begin{document}
\\end{document}
"""
        self.assertEqual([2], find_unbalanced_setminted_lines(text))

    def test_find_unbalanced_setminted_lines_accepts_balanced_block(self) -> None:
        text = """\\documentclass{article}
\\setminted{fontsize=\\small,breaklines=true}
\\begin{document}
\\end{document}
"""
        self.assertEqual([], find_unbalanced_setminted_lines(text))

    def test_find_malformed_mintinline_lines_reports_line_number(self) -> None:
        text = """\\documentclass{article}
\\textbf{Distribution.} Uniform over all \\passthrough{\\mintinline"n!"} permutations.
\\begin{document}
\\end{document}
"""
        self.assertEqual([2], find_malformed_mintinline_lines(text))

    def test_find_malformed_mintinline_lines_accepts_brace_form(self) -> None:
        text = "\\mintinline{c}{int x;}\n"
        self.assertEqual([], find_malformed_mintinline_lines(text))

    def test_repo_validator_rejects_duplicate_shared_minted_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            tex_path = repo_root / "src" / "docs" / "dup-helper.tex"
            tex_path.parent.mkdir(parents=True, exist_ok=True)
            tex_path.write_text(
                "\\documentclass{article}\n"
                "\\usepackage{technical-installation}\n"
                "\\newminted[yamlcode]{yaml}{}\n"
                "\\begin{document}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            with patch.object(sm, "ROOT", repo_root):
                with patch.object(sm, "SRC_DIR", repo_root / "src"):
                    with patch.object(sm, "_tracked_src_files", return_value=[tex_path]):
                        with patch.object(sm, "discover_latex_roots", return_value=[tex_path]):
                            with patch.object(sm, "_validate_naming", return_value=0):
                                self.assertNotEqual(0, validate_repo())

    def test_repo_validator_rejects_unbalanced_setminted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            tex_path = repo_root / "src" / "docs" / "bad-setminted.tex"
            tex_path.parent.mkdir(parents=True, exist_ok=True)
            tex_path.write_text(
                "\\documentclass{article}\n"
                "\\usepackage{technical-installation}\n"
                "\\setminted{\n"
                "  fontsize=\\small,\n"
                "\\begin{document}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            with patch.object(sm, "ROOT", repo_root):
                with patch.object(sm, "SRC_DIR", repo_root / "src"):
                    with patch.object(sm, "_tracked_src_files", return_value=[tex_path]):
                        with patch.object(sm, "discover_latex_roots", return_value=[tex_path]):
                            with patch.object(sm, "_validate_naming", return_value=0):
                                self.assertNotEqual(0, validate_repo())

    def test_comment_stripping_ignores_commented_cornell_commands(self) -> None:
        sample = """\\title{Visible}\n% \\title{Hidden}\n\\maketitle\n% \\makecornelltitle\n"""
        stripped = strip_latex_comments(sample)
        self.assertIn("\\title{Visible}", stripped)
        self.assertNotIn("Hidden", stripped)
        self.assertNotIn("\\makecornelltitle", stripped)

    def test_repo_validator_enforces_no_direct_style_or_base_imports(self) -> None:
        with patch.object(sm, "_validate_naming", return_value=0):
            self.assertEqual(0, validate_repo())

    def test_repo_validator_rejects_cornell_document_missing_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            tex_path = repo_root / "src" / "cornell-notes" / "security" / "certifications" / "cissp" / "01-domain-cornell-notes.tex"
            tex_path.parent.mkdir(parents=True, exist_ok=True)
            tex_path.write_text(
                "\\documentclass[10pt,letterpaper]{article}\n"
                "\\usepackage{cornell-notes}\n"
                "\\author{Example}\n"
                "\\date{\\today}\n"
                "\\begin{document}\n"
                "\\maketitle\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            with patch.object(sm, "ROOT", repo_root):
                with patch.object(sm, "SRC_DIR", repo_root / "src"):
                    with patch.object(sm, "_tracked_src_files", return_value=[tex_path]):
                        with patch.object(sm, "discover_latex_roots", return_value=[tex_path]):
                            with patch.object(sm, "_validate_naming", return_value=0):
                                self.assertNotEqual(0, validate_repo())


if __name__ == "__main__":
    unittest.main()
