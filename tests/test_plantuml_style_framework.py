"""Regression tests for the PlantUML style framework contract."""

import os
import tempfile
import unittest
from pathlib import Path

import tooling.scripts.latex_build as latex_build
from tooling.scripts import plantuml_lint


class PlantUMLStyleFrameworkTests(unittest.TestCase):
    def test_framework_modules_are_ascii_lf_and_guarded(self) -> None:
        """Prevent invisible bytes and broken guards from reaching PlantUML."""
        self.assertEqual([], plantuml_lint.check())

    def test_deprecated_skinparams_are_absent(self) -> None:
        """Prevent PlantUML from drawing deprecation warnings into committed images."""
        self.assertFalse(any("deprecated skinparam" in problem for problem in plantuml_lint.check()))

    def test_renderer_invalidates_outputs_when_shared_style_changes(self) -> None:
        """Prevent shared style edits from leaving newer-looking stale images."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "diagram.puml"
            style = root / "style.iuml"
            output = root / "diagram.svg"
            source.write_text("@startuml\n@enduml\n", encoding="ascii")
            style.write_text("skinparam shadowing false\n", encoding="ascii")
            output.write_text("old\n", encoding="ascii")
            now = max(source.stat().st_mtime, output.stat().st_mtime)
            os.utime(output, (now + 10, now + 10))
            os.utime(style, (now + 20, now + 20))
            self.assertFalse(latex_build._plantuml_is_current(source, None, [output], [style]))

    def test_action_does_not_default_to_latest(self) -> None:
        """Prevent upstream PlantUML releases from silently changing output."""
        action = (plantuml_lint.ROOT / ".github/actions/render-plantuml/action.yml").read_text(encoding="utf-8")
        self.assertNotIn("default: 'latest'", action)


if __name__ == "__main__":
    unittest.main()
