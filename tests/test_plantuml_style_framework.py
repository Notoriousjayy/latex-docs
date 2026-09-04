"""Regression tests for the PlantUML style framework contract."""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

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

    def test_render_workflow_dispatches_pages_after_bot_push(self) -> None:
        """Prevent GITHUB_TOKEN image commits from leaving Pages on the pre-render revision."""
        workflow = (plantuml_lint.ROOT / ".github/workflows/render-plantuml.yml").read_text(encoding="utf-8")
        self.assertIn("actions: write", workflow)
        self.assertIn("gh workflow run latex-pages.yml --ref main", workflow)

    def test_framework_examples_compile_with_the_selected_engine(self) -> None:
        """Prevent include-chain or inherited-procedure regressions from reaching committed images."""
        if latex_build.check_plantuml_engine() is not None:
            self.skipTest("manifest-pinned PlantUML is not selected in this environment")
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(0, latex_build.smoke_plantuml(Path(directory)))


class PlantUMLIncludeContractTests(unittest.TestCase):
    """The include hierarchy is the framework; these tests must never pass by removing an include."""

    ROOT = plantuml_lint.ROOT
    BASE_DIR = plantuml_lint.ROOT / "tooling" / "plantuml"
    STYLE_DIR = plantuml_lint.ROOT / "tooling" / "styles" / "plantuml"

    def test_canonical_hierarchy_is_intact(self) -> None:
        """uml-base <- {structural, behavioral} <- interaction must stay exactly as declared."""
        for module, parent in (
            ("uml-structural.iuml", "uml-base.iuml"),
            ("uml-behavioral.iuml", "uml-base.iuml"),
            ("uml-interaction.iuml", "uml-behavioral.iuml"),
        ):
            path = self.BASE_DIR / module
            self.assertTrue(path.is_file(), f"{module} is missing")
            names = [Path(target).name for target in plantuml_lint._includes(path)]
            self.assertIn(parent, names, f"{module} must include {parent}")
        self.assertEqual([], plantuml_lint._includes(self.BASE_DIR / "uml-base.iuml"))

    def test_interaction_inherits_base_transitively_through_behavioral(self) -> None:
        """Interaction styles must reach uml-base only via uml-behavioral, never by a direct shortcut."""
        interaction = self.BASE_DIR / "uml-interaction.iuml"
        names = [Path(target).name for target in plantuml_lint._includes(interaction)]
        self.assertIn("uml-behavioral.iuml", names)
        self.assertNotIn("uml-base.iuml", names)
        behavioral = [Path(t).name for t in plantuml_lint._includes(self.BASE_DIR / "uml-behavioral.iuml")]
        self.assertIn("uml-base.iuml", behavioral)

    def test_every_leaf_style_includes_its_category_parent(self) -> None:
        """A leaf pointing at the wrong category silently drops that family's styling."""
        for category, parent in plantuml_lint.CATEGORY_PARENT.items():
            modules = sorted((self.STYLE_DIR / category).glob("*.iuml"))
            self.assertTrue(modules, f"no leaf modules found for {category}")
            for module in modules:
                names = [Path(target).name for target in plantuml_lint._includes(module)]
                self.assertIn(parent, names, f"{module.relative_to(self.ROOT)} must include {parent}")

    def test_every_renderable_diagram_retains_an_active_include(self) -> None:
        """A diagram that lost its !include renders unstyled instead of failing loudly."""
        for source in sorted(self.ROOT.joinpath("src").rglob("*.puml")):
            text = source.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"^@startuml", text, re.M):
                continue
            targets = plantuml_lint.INCLUDE.findall(text)
            self.assertTrue(targets, f"{source.relative_to(self.ROOT)} has no active !include")
            for target in targets:
                self.assertTrue(
                    any((base / target).is_file() for base in (source.parent, self.BASE_DIR, self.STYLE_DIR)),
                    f"{source.relative_to(self.ROOT)}: include {target} does not resolve",
                )

    def test_misspelled_and_shadowing_modules_are_rejected(self) -> None:
        """`.iml`, `interation` and a second copy of a canonical module all resolve to nothing at render time."""
        self.assertEqual([], [p for p in self.ROOT.rglob("*.iml") if ".git" not in p.parts])
        canonical = {"uml-base.iuml", *plantuml_lint.CANONICAL_PARENT}
        for duplicate in self.ROOT.rglob("uml-*.iuml"):
            if ".git" in duplicate.parts or duplicate.name not in canonical:
                continue
            self.assertEqual(self.BASE_DIR, duplicate.parent, f"{duplicate} shadows a canonical module")
        self.assertEqual([], [p for p in self.ROOT.rglob("*interation*") if ".git" not in p.parts])

    def test_lint_rejects_a_removed_include(self) -> None:
        """Guard the guard: the contract check must fail when a category link is deleted."""
        module = self.BASE_DIR / "uml-interaction.iuml"
        original = module.read_text(encoding="utf-8")
        stripped = "\n".join(
            line for line in original.splitlines() if not re.match(r"^\s*!include\s", line)
        )
        try:
            module.write_text(stripped + "\n", encoding="utf-8")
            problems = plantuml_lint.check_include_contract()
        finally:
            module.write_text(original, encoding="utf-8")
        self.assertTrue(
            any("uml-interaction.iuml" in problem and "uml-behavioral.iuml" in problem for problem in problems),
            "removing an include must be reported, never tolerated",
        )


class PlantUMLManagedOutputTests(unittest.TestCase):
    """Renders only ever land in <source>/png|svg|jpg; images elsewhere are never refreshed."""

    def test_no_generated_image_sits_beside_a_source(self) -> None:
        """255 syntax-error PNGs from PlantUML 1.2020.02 survived every fix by living outside png/."""
        self.assertEqual([], plantuml_lint.check_managed_outputs())

    def test_unmanaged_images_are_detected(self) -> None:
        """The renderer must report a flat image instead of silently leaving it in place."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "diagram.puml").write_text("@startuml\n@enduml\n", encoding="ascii")
            (root / "png").mkdir()
            (root / "png" / "diagram.png").write_bytes(b"managed")
            stale = root / "diagram.png"
            stale.write_bytes(b"stale")
            found = latex_build.unmanaged_diagram_images([root])
            self.assertEqual([stale], found)

    def test_render_workflow_triggers_on_every_rendering_input(self) -> None:
        """A renderer or manifest change that never re-renders leaves stale images published."""
        workflow = yaml.safe_load(
            (plantuml_lint.ROOT / ".github/workflows/render-plantuml.yml").read_text(encoding="utf-8")
        )
        paths = workflow[True]["push"]["paths"]
        for required in (
            "src/**/*.puml",
            "tooling/plantuml/**",
            "tooling/styles/plantuml/**",
            "tooling/manifests/plantuml.json",
            "tooling/scripts/latex_build.py",
            ".github/workflows/render-plantuml.yml",
        ):
            self.assertIn(required, paths)


class PlantUMLIncludeChainRenderTests(unittest.TestCase):
    """Every UML family must compile through its real include chain, macros included."""

    PROBES = {
        "base": ("uml-base.iuml", "class A\nUML_NOTE_INFO(n1, A, base)\n"),
        "structural": ("structural/deployment-diagram-style.iuml", "node S\nUML_NOTE_INFO(n1, S, structural)\n"),
        "behavioral": ("behavioral/activity-diagram-style.iuml", "start\n:work;\nstop\n"),
        "interaction": ("interaction/sequence-diagram-style.iuml", "participant C\nparticipant S\nC -> S : go\nUML_NOTE_INFO(n1, S, interaction)\n"),
    }

    def test_each_inheritance_level_compiles_through_its_includes(self) -> None:
        if latex_build.check_plantuml_engine() is not None:
            self.skipTest("manifest-pinned PlantUML is not selected in this environment")
        env = os.environ.copy()
        env["PLANTUML_INCLUDE_PATH"] = ":".join(
            str(path) for path in latex_build.PLANTUML_INCLUDE_DIRS if path.exists()
        )
        prefix = latex_build.plantuml_command_prefix(env)
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for name, (include, body) in self.PROBES.items():
                (work / f"probe-{name}.puml").write_text(
                    f"@startuml probe-{name}\n!include {include}\n{body}@enduml\n", encoding="ascii"
                )
            out = work / "out"
            out.mkdir()
            result = subprocess.run(
                [*prefix, "-failfast2", "-tsvg", "-o", str(out), *(f"probe-{n}.puml" for n in self.PROBES)],
                cwd=str(work), env=env, capture_output=True, text=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            for name in self.PROBES:
                svg = out / f"probe-{name}.svg"
                self.assertTrue(svg.is_file(), f"{name} probe produced no SVG")
                self.assertIsNone(latex_build.svg_error_text(svg), f"{name} probe rendered an error image")


if __name__ == "__main__":
    unittest.main()
