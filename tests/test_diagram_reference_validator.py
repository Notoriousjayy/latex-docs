import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import tooling.scripts.diagram_reference_validator as drv
from tooling.scripts.diagram_reference_validator import (
    find_missing_or_case_mismatched_graphics,
    find_unsynchronized_renamed_assets,
    validate_repo,
)


class DiagramReferenceValidatorTests(unittest.TestCase):
    def test_repository_diagram_references_validate(self) -> None:
        self.assertEqual(0, validate_repo())

    def test_unsynchronized_renamed_assets_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src = root / "src" / "demo"
            (src / "png").mkdir(parents=True, exist_ok=True)
            (src / "svg").mkdir(parents=True, exist_ok=True)
            (src / "new-name.puml").write_text("@startuml\nAlice->Bob: hi\n@enduml\n", encoding="utf-8")
            # png/svg targets intentionally missing to trigger sync failure.
            pairs = [
                ("src/demo/old-name.puml", "src/demo/new-name.puml"),
                ("src/demo/png/old-name.png", "src/demo/png/new-name.png"),
                ("src/demo/svg/old-name.svg", "src/demo/svg/new-name.svg"),
            ]
            with patch.object(drv, "ROOT", root):
                issues = find_unsynchronized_renamed_assets(pairs)
            self.assertTrue(any("missing-synchronized-rendered-asset" in issue for issue in issues))

    def test_latex_reference_resolution_detects_missing_graphic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tex = root / "src" / "demo" / "sample.tex"
            tex.parent.mkdir(parents=True, exist_ok=True)
            tex.write_text(
                "\\documentclass{article}\n"
                "\\begin{document}\n"
                "\\includegraphics{images/new-name.png}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            rename_pairs = [("src/demo/old-name.puml", "src/demo/new-name.puml")]
            with patch.object(drv, "ROOT", root):
                issues = find_missing_or_case_mismatched_graphics([tex], rename_pairs)
            self.assertTrue(any("missing-graphic:" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
