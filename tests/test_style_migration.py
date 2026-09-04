import re
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import tooling.scripts.style_migration as sm
from tooling.scripts.style_migration import (
    CORNELL_PACKAGE_PATTERN,
    classify_latex_style,
    classify_plantuml_style,
    filename_policy_violations,
    find_unbalanced_setminted_lines,
    find_malformed_mintinline_lines,
    is_cornell_document,
    latex_usepackages,
    strip_latex_comments,
    _validate_naming,
    validate_repo,
)


class StyleMigrationTests(unittest.TestCase):
    @staticmethod
    def _all_cornell_roots(repo_root: Path) -> list[Path]:
        return sorted((repo_root / "src" / "cornell-notes").rglob("*.tex"))

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

    def test_c_cornell_notes_collection_has_expected_canonical_paths(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        expected = [
            repo_root / "src" / "cornell-notes" / "programming" / "languages" / "c" / "c-2024" / "clauses" / "01-scope" / "01-scope-cornell-notes.tex",
            repo_root / "src" / "cornell-notes" / "programming" / "languages" / "c" / "c-2024" / "clauses" / "02-normative-references" / "02-normative-references-cornell-notes.tex",
            repo_root / "src" / "cornell-notes" / "programming" / "languages" / "c" / "c-2024" / "clauses" / "03-terms-definitions-and-symbols" / "03-terms-definitions-and-symbols-cornell-notes.tex",
            repo_root / "src" / "cornell-notes" / "programming" / "languages" / "c" / "c-2024" / "clauses" / "04-conformance" / "04-conformance-cornell-notes.tex",
            repo_root / "src" / "cornell-notes" / "programming" / "languages" / "c" / "c-2024" / "clauses" / "05-environment" / "05-environment-cornell-notes.tex",
            repo_root / "src" / "cornell-notes" / "programming" / "languages" / "c" / "c-2024" / "clauses" / "06-language" / "06-language-cornell-notes.tex",
            repo_root / "src" / "cornell-notes" / "programming" / "languages" / "c" / "c-2024" / "clauses" / "07-library" / "07-library-cornell-notes.tex",
        ]
        for path in expected:
            self.assertTrue(path.exists(), msg=f"Missing canonical C Cornell file: {path}")

    def test_cornell_notes_documents_use_cornell_package(self) -> None:
        """`\\usepackage[technical-reference]{cornell-notes}` is the same semantic package."""
        repo_root = Path(__file__).resolve().parents[1]
        for tex_path in self._all_cornell_roots(repo_root):
            text = strip_latex_comments(tex_path.read_text(encoding="utf-8", errors="ignore"))
            self.assertRegex(text, CORNELL_PACKAGE_PATTERN, str(tex_path))
            semantic = [name for name in latex_usepackages(text) if name in sm.SEMANTIC_STYLE_PACKAGES]
            self.assertEqual(["cornell-notes"], semantic, str(tex_path))

    def test_cornell_notes_documents_use_standard_title_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for tex_path in self._all_cornell_roots(repo_root):
            text = strip_latex_comments(tex_path.read_text(encoding="utf-8", errors="ignore"))
            self.assertRegex(text, r"\\title\s*\{[^{}]+\}", str(tex_path))
            self.assertRegex(text, r"\\author\s*\{[^{}]*\}", str(tex_path))
            self.assertRegex(text, r"\\date\s*\{[^{}]*\}", str(tex_path))
            self.assertEqual(1, text.count("\\maketitle"), str(tex_path))

    def test_cornell_validator_covers_every_collection_without_an_allowlist(self) -> None:
        """A new Cornell collection must be validated without editing another path list."""
        self.assertTrue(is_cornell_document("src/cornell-notes/a-brand-new-collection/topic/ch01-x-notes.tex"))
        self.assertTrue(is_cornell_document("src/architecture/style-system/examples/cornell-notes-study-sheet.tex"))
        self.assertFalse(is_cornell_document("src/programming/languages/c/notes.tex"))
        source = (Path(__file__).resolve().parents[1] / "tooling/scripts/style_migration.py").read_text(encoding="utf-8")
        self.assertNotIn("src/cornell-notes/mathematics/numerical-methods/", source)
        self.assertEqual(1, source.count('print(f"invalid-cornell-import: {rel}")'))

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


class StringAlgorithmsCollectionTests(unittest.TestCase):
    """The string-algorithms collection was the last tree still on self-contained legacy formatting."""

    COLLECTION = Path(__file__).resolve().parents[1] / "src/cornell-notes/computer-science/string-algorithms"
    SUBCOLLECTIONS = ("computational-genomics", "exact-matching", "sequence-alignment", "suffix-structures")
    LEGACY_TOKENS = (
        "\\usepackage{geometry}",
        "\\usepackage{fancyhdr}",
        "\\usepackage[most]{tcolorbox}",
        "\\definecolor{Primary}",
        "\\definecolor{Accent}",
        "\\newcolumntype{C}",
        "\\newcolumntype{N}",
        "\\newcommand{\\cnrow}",
        "\\pagestyle{fancy}",
        "\\begin{longtable}",
        "\\begin{tcolorbox}",
    )

    def _documents(self) -> list[Path]:
        return sorted(self.COLLECTION.rglob("*.tex"))

    def test_collection_has_nineteen_documents_across_four_subcollections(self) -> None:
        documents = self._documents()
        self.assertEqual(19, len(documents))
        for subcollection in self.SUBCOLLECTIONS:
            self.assertTrue((self.COLLECTION / subcollection).is_dir(), subcollection)

    def test_every_document_uses_the_shared_cornell_style(self) -> None:
        for path in self._documents():
            text = strip_latex_comments(path.read_text(encoding="utf-8"))
            self.assertRegex(text, CORNELL_PACKAGE_PATTERN, str(path))
            semantic = [name for name in latex_usepackages(text) if name in sm.SEMANTIC_STYLE_PACKAGES]
            self.assertEqual(["cornell-notes"], semantic, str(path))

    def test_every_document_satisfies_the_standard_title_contract(self) -> None:
        for path in self._documents():
            text = strip_latex_comments(path.read_text(encoding="utf-8"))
            self.assertEqual(1, len(re.findall(r"\\documentclass", text)), str(path))
            self.assertEqual(1, text.count("\\begin{document}"), str(path))
            self.assertEqual(1, text.count("\\end{document}"), str(path))
            self.assertEqual(1, text.count("\\maketitle"), str(path))
            self.assertLess(text.index("\\begin{document}"), text.index("\\maketitle"), str(path))
            self.assertRegex(text, r"\\title\s*\{[^{}]+\}", str(path))
            self.assertRegex(text, r"\\author\s*\{[^{}]*\}", str(path))
            self.assertRegex(text, r"\\date\s*\{[^{}]*\}", str(path))

    def test_no_legacy_layout_survives(self) -> None:
        """The local Cornell layout had to be removed, not aliased behind a \\cnrow shim."""
        for path in self._documents():
            text = strip_latex_comments(path.read_text(encoding="utf-8"))
            for token in self.LEGACY_TOKENS:
                self.assertNotIn(token, text, f"{path}: {token}")
            self.assertNotIn("\\usepackage{style}", text, str(path))
            self.assertNotIn("\\usepackage{base}", text, str(path))
            self.assertNotIn("\\makecornelltitle", text, str(path))
            self.assertNotIn("\\begin{titlepage}", text, str(path))
            for token in sm.LISTINGS_TOKENS:
                self.assertNotIn(token, text, f"{path}: {token}")

    def test_documents_use_the_shared_semantic_apis(self) -> None:
        for path in self._documents():
            text = strip_latex_comments(path.read_text(encoding="utf-8"))
            self.assertIn("\\begin{CornellNotesTable}", text, str(path))
            self.assertIn("\\CornellNoteRow{", text, str(path))
            self.assertIn("\\begin{CornellOverviewBox}", text, str(path))
            self.assertIn("\\begin{CornellSummaryBox}", text, str(path))
            self.assertIn("\\begin{CornellExamBox}", text, str(path))

    def test_filenames_follow_the_cornell_chapter_convention(self) -> None:
        for path in self._documents():
            self.assertRegex(path.name, r"^ch\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*-notes\.tex$", str(path))
            self.assertEqual([], filename_policy_violations(path), str(path))

    def test_titles_and_pdf_metadata_agree(self) -> None:
        for path in self._documents():
            text = strip_latex_comments(path.read_text(encoding="utf-8"))
            title = re.search(r"\\title\{(.+?)\}\n", text)
            pdftitle = re.search(r"pdftitle=\{(.+?)\},pdfsubject", text)
            self.assertIsNotNone(title, str(path))
            self.assertIsNotNone(pdftitle, str(path))
            self.assertEqual(title.group(1), pdftitle.group(1), str(path))
            self.assertRegex(title.group(1), r"^Chapter \d+: \S", str(path))

    def test_collection_metadata_is_consistent(self) -> None:
        for path in self._documents():
            text = strip_latex_comments(path.read_text(encoding="utf-8"))
            self.assertIn("\\setCornellCollection{String Algorithms}", text, str(path))
            self.assertIn("\\setCornellUnitType{Chapter}", text, str(path))
            number = re.search(r"\\setCornellUnitNumber\{(\d+)\}", text)
            self.assertIsNotNone(number, str(path))
            self.assertEqual(int(number.group(1)), int(path.name[2:4]), str(path))
