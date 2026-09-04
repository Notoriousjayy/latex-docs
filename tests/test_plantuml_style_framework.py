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
        self.assertNotIn("releases/latest", action)

    def test_manifest_is_the_only_plantuml_pin(self) -> None:
        """Prevent the CI jar, the action and the workflows from drifting to different versions."""
        pin = latex_build.load_plantuml_pin()
        action = (plantuml_lint.ROOT / ".github/actions/render-plantuml/action.yml").read_text(encoding="utf-8")
        self.assertIn("fetch-plantuml", action, "the action must install the jar through the checksummed fetch")
        self.assertNotIn(pin["version"], action, "the action must not repeat the version literal")
        for workflow in (plantuml_lint.ROOT / ".github/workflows").glob("*.yml"):
            self.assertNotRegex(workflow.read_text(encoding="utf-8"), r"plantuml-version:\s*\S", str(workflow))

    def test_render_workflow_pushes_only_from_main_with_safe_staging(self) -> None:
        """Prevent a dispatch from a branch pushing onto main and prevent the aborting literal pathspec add."""
        workflow = (plantuml_lint.ROOT / ".github/workflows/render-plantuml.yml").read_text(encoding="utf-8")
        self.assertIn("if: github.ref == 'refs/heads/main'", workflow)
        self.assertIn("stage-plantuml-images", workflow)
        self.assertNotIn("git add -A 'src/**", workflow)
        self.assertIn("smoke-plantuml", workflow)
        self.assertNotIn("|| true", workflow)

    def test_framework_examples_include_resolvable_modules(self) -> None:
        """Prevent an example pointing at the wrong leaf module (sequence-example once included the deployment style)."""
        for example in sorted((plantuml_lint.ROOT / "tooling/plantuml").glob("*-example.puml")):
            text = example.read_text(encoding="utf-8")
            include = next(line.split()[1] for line in text.splitlines() if line.startswith("!include "))
            self.assertTrue((plantuml_lint.ROOT / "tooling/styles/plantuml" / include).is_file(), f"{example.name}: {include}")
            expected_family = example.name.split("-example")[0]
            self.assertIn(expected_family, include, f"{example.name} must include its own diagram-type module")


if __name__ == "__main__":
    unittest.main()
