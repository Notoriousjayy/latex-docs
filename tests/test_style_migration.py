import unittest
from pathlib import Path

from tooling.scripts.style_migration import (
    classify_latex_style,
    classify_plantuml_style,
    validate_repo,
)


class StyleMigrationTests(unittest.TestCase):
    def test_classify_latex_style_for_personal_documents(self) -> None:
        path = Path("src/personal/finance/example.tex")
        self.assertEqual("financial", classify_latex_style(path))

    def test_classify_latex_style_for_technical_design_documents(self) -> None:
        path = Path("src/security/github-advanced-security/references/guide.tex")
        self.assertEqual("technical-design-spec", classify_latex_style(path))

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


if __name__ == "__main__":
    unittest.main()
