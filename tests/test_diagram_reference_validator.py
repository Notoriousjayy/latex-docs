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

    def test_diagram_shorthand_and_managed_output_references_must_resolve(self) -> None:
        """48 `\\diagram{01-...}` references once pointed at outputs that no source produced; safe macros hid it."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            doc_dir = root / "src" / "demo"
            (doc_dir / "png").mkdir(parents=True)
            (doc_dir / "png" / "present.png").write_bytes(b"png")
            tex = doc_dir / "sample.tex"
            tex.write_text(
                "\\documentclass{article}\n"
                "\\newcommand{\\diagram}[2][]{\\safeincludegraphics[#1]{png/#2.png}}\n"
                "\\begin{document}\n"
                "\\diagram[width=\\linewidth]{present}\n"
                "\\diagram{01-renamed-away}\n"
                "\\includegraphics{png/present.png}\n"
                "\\includegraphics{svg/never-rendered.svg}\n"
                "\\includegraphics{figures/hand-drawn.png}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            with patch.object(drv, "ROOT", root):
                issues = drv.find_unresolved_managed_diagram_references([tex])
            self.assertEqual(
                [
                    "missing-managed-diagram-output: src/demo/sample.tex: svg/never-rendered.svg",
                    "missing-managed-diagram-output: src/demo/sample.tex: png/01-renamed-away.png",
                ],
                issues,
            )

    def test_live_repository_has_no_unresolved_managed_diagram_references(self) -> None:
        tex_files = sorted(path for path in drv.SRC_DIR.rglob("*.tex") if path.is_file())
        self.assertEqual([], drv.find_unresolved_managed_diagram_references(tex_files))


if __name__ == "__main__":
    unittest.main()
