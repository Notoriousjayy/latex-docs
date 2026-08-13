import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import tooling.scripts.style_migration as sm
from tooling.scripts.style_migration import (
    classify_latex_style,
    classify_plantuml_style,
    filename_policy_violations,
    _validate_naming,
    validate_repo,
)


class StyleMigrationTests(unittest.TestCase):
    def test_classify_latex_style_for_personal_documents(self) -> None:
        path = Path("src/personal/finance/example.tex")
        self.assertEqual("financial", classify_latex_style(path))

    def test_classify_latex_style_for_technical_design_documents(self) -> None:
        path = Path("src/security/github-advanced-security/references/guide.tex")
        self.assertEqual("technical-design-spec", classify_latex_style(path))

    def test_classify_latex_style_for_cornell_notes_path(self) -> None:
        path = Path("src/security/certifications/cissp/cornell-notes/01-security-and-risk-management-cornell-notes.tex")
        self.assertEqual("cornell-notes", classify_latex_style(path))

    def test_classify_latex_style_cornell_precedence_inside_security(self) -> None:
        path = Path("src/security/certifications/cissp/cornell-notes/06-security-assessment-and-testing-cornell-notes.tex")
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
        cornell_dir = repo_root / "src" / "security" / "certifications" / "cissp" / "cornell-notes"
        for tex_path in sorted(cornell_dir.glob("*.tex")):
            text = tex_path.read_text(encoding="utf-8", errors="ignore")
            self.assertIn("\\usepackage{cornell-notes}", text, str(tex_path))

    def test_cornell_package_inherits_from_base(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        style_path = repo_root / "tooling" / "styles" / "latex" / "cornell-notes.sty"
        text = style_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("\\RequirePackage{base}", text)
        self.assertIn("\\LdsRegisterModule{cornell-notes}{Study / Cornell Notes}", text)

    def test_repo_validator_enforces_no_direct_style_or_base_imports(self) -> None:
        self.assertEqual(0, validate_repo())


if __name__ == "__main__":
    unittest.main()
