"""Regression tests for the PlantUML style framework contract."""

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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
            # c4-<level>-example.puml -> c4/<level>-diagram-style.iuml
            expected_path = expected_family.replace("c4-", "c4/") if expected_family.startswith("c4-") else expected_family
            self.assertIn(expected_path, include, f"{example.name} must include its own diagram-type module")
        families = {e.name.split("-example")[0] for e in (plantuml_lint.ROOT / "tooling/plantuml").glob("*-example.puml")}
        self.assertTrue({"c4-context", "c4-container"} <= families, "the C4 family must have authoring examples")

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
        """house-tokens <- {uml-base, c4-base}; uml-base <- {structural, behavioral} <- interaction, exactly as declared."""
        for module, parent in (
            ("uml-base.iuml", "house-tokens.iuml"),
            ("c4-base.iuml", "house-tokens.iuml"),
            ("uml-structural.iuml", "uml-base.iuml"),
            ("uml-behavioral.iuml", "uml-base.iuml"),
            ("uml-interaction.iuml", "uml-behavioral.iuml"),
        ):
            path = self.BASE_DIR / module
            self.assertTrue(path.is_file(), f"{module} is missing")
            names = [Path(target).name for target in plantuml_lint._includes(path)]
            self.assertIn(parent, names, f"{module} must include {parent}")
        # The neutral root includes nothing; uml-base includes only the neutral root (no UML module may
        # reach C4 and vice versa, so a palette change has exactly one owner).
        self.assertEqual([], plantuml_lint._includes(self.BASE_DIR / "house-tokens.iuml"))
        self.assertEqual(["house-tokens.iuml"], plantuml_lint._includes(self.BASE_DIR / "uml-base.iuml"))
        c4_includes = plantuml_lint._includes(self.BASE_DIR / "c4-base.iuml")
        self.assertEqual(["house-tokens.iuml"], [t for t in c4_includes if not t.startswith("<")])
        self.assertTrue(all(t in plantuml_lint.STDLIB_ALLOWED for t in c4_includes if t.startswith("<")), c4_includes)
        self.assertFalse(any("uml-" in t for t in c4_includes), "c4-base must not inherit UML skinparams")

    def test_palette_has_exactly_one_owner(self) -> None:
        """A second `!$theme_primary =` anywhere in the modules would silently fork the palette."""
        owners = [
            path for path in plantuml_lint._module_files()
            if re.search(r"^!\$(theme|fill|deep|line)_\w+\s*=", path.read_text(encoding="utf-8"), re.M)
        ]
        self.assertEqual([self.BASE_DIR / "house-tokens.iuml"], owners)
        base_text = (self.BASE_DIR / "uml-base.iuml").read_text(encoding="utf-8")
        self.assertNotRegex(base_text, r"^[^']*#[0-9A-Fa-f]{6}\b", "uml-base must consume tokens, not define hex")

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
        self.assertEqual({"structural", "behavioral", "interaction", "c4"}, set(plantuml_lint.CATEGORY_PARENT))
        for category, parent in plantuml_lint.CATEGORY_PARENT.items():
            modules = sorted((self.STYLE_DIR / category).glob("*.iuml"))
            self.assertTrue(modules, f"no leaf modules found for {category}")
            for module in modules:
                names = [Path(target).name for target in plantuml_lint._includes(module)]
                self.assertIn(parent, names, f"{module.relative_to(self.ROOT)} must include {parent}")
        self.assertEqual(
            {"context", "container", "component", "dynamic", "deployment"},
            {m.name.replace("-diagram-style.iuml", "") for m in (self.STYLE_DIR / "c4").glob("*.iuml")},
        )
        self.assertEqual(14, sum(len(list((self.STYLE_DIR / c).glob("*.iuml"))) for c in ("structural", "behavioral", "interaction")))

    def test_c4_library_comes_only_from_the_pinned_stdlib(self) -> None:
        """No module or source may pull C4-PlantUML from a URL or from anywhere but c4-base."""
        for module in plantuml_lint._module_files():
            for target in plantuml_lint._includes(module):
                self.assertNotIn("://", target, f"{module}: network include")
                if target.startswith("<"):
                    self.assertEqual("c4-base.iuml", module.name, f"{module}: stdlib include outside c4-base")
        pin = latex_build.load_plantuml_pin()
        self.assertRegex(pin.get("c4_plantuml", ""), r"^\d+\.\d+\.\d+$", "manifest must pin the bundled C4-PlantUML version")
        self.assertIn(pin["c4_plantuml"], (self.BASE_DIR / "c4-base.iuml").read_text(encoding="utf-8"))

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
        canonical = {"house-tokens.iuml", *plantuml_lint.CANONICAL_PARENT}
        for duplicate in list(self.ROOT.rglob("uml-*.iuml")) + list(self.ROOT.rglob("c4-*.iuml")) + list(self.ROOT.rglob("house-*.iuml")):
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
    """Every style entry point and every public notation helper must compile through its real include chain."""

    # One probe per leaf module (14 UML + 5 C4) exercising the helpers that module or its parents export.
    PROBES = {
        "class": ("structural/class-diagram-style.iuml",
                  "class A\nclass B\nclass C\nCLASS_INTERFACE(I)\nSTRUCT_ASSOCIATION(A, B)\nSTRUCT_DEPENDENCY(A, C, uses)\n"
                  "STRUCT_AGGREGATION(B, C)\nSTRUCT_COMPOSITION(A, C, owns)\nSTRUCT_NAVIGABLE(C, B)\nSTRUCT_GENERALIZATION(B, A)\n"
                  "STRUCT_REALIZATION(A, I)\nclass Bad <<invalid>>\nUML_NOTE_INFO(n1, A, base)\nUML_NOTE_WARN(n2, Bad, wrong)\n"
                  "UML_LEGEND_BEGIN()\nUML_LEGEND_ROLE(invalid, intentionally wrong)\nUML_LEGEND_END()\nUML_CAPTION(probe)\n"),
        "object": ("structural/object-diagram-style.iuml", "OBJ_INSTANCE(o1, Order)\nOBJ_INSTANCE(o2, Line)\no1 -- o2\n"),
        "component": ("structural/component-diagram-style.iuml",
                      "interface IOrders\ncomponent Svc\ncomponent Cli\ncomponent P\ncomponent Q\ncomponent F\ncomponent In\n"
                      "COMP_PROVIDES(Svc, IOrders)\nCOMP_REQUIRES(Cli, IOrders)\nCOMP_ASSEMBLY(P, IPay, Q)\nCOMP_DELEGATE(F, In)\n"
                      "component Ext <<external>>\n"),
        "deployment": ("structural/deployment-diagram-style.iuml",
                       "DEPLOY_DEVICE(srv, Server)\nDEPLOY_EXECENV(jvm, JVM)\nDEPLOY_ARTIFACT(war, app.war)\n"
                       "DEPLOY_COMMPATH(srv, jvm)\nDEPLOY_COMMPATH(jvm, war, hosts)\nUML_NOTE_INFO(n1, srv, structural)\n"),
        "package": ("structural/package-diagram-style.iuml", "package A\npackage B\npackage C\nPKG_IMPORT(A, B)\nPKG_MERGE(A, C)\nPKG_ACCESS(B, C)\n"),
        "composite": ("structural/composite-structure-diagram-style.iuml",
                      "component \"Sensor : Device\" as Sensor {\n  CSD_PORT(p1)\n  CSD_PORT_IN(pin)\n  CSD_PORT_OUT(pout)\n  CSD_PART(ADC, Converter)\n}\n"
                      "CSD_PART(Ctl, Controller)\nCSD_CONNECTOR(p1, Ctl, data)\nCSD_CONNECTOR(pin, Ctl)\nCSD_INTERFACE(IReading)\nCtl -( IReading\n"),
        "profile": ("structural/profile-diagram-style.iuml",
                    "class Component <<metaclass>>\nclass Bean <<stereotype>>\nclass Service <<stereotype>>\n"
                    "PROF_EXTENSION(Bean, Component)\nPROF_EXTENSION(Service, Component, required)\nPROF_GENERALIZATION(Service, Bean)\n"),
        "activity": ("behavioral/activity-diagram-style.iuml",
                     "ACT_LANE(Intake)\nstart\nACT_DO(work)\nACT_IF(ok)\nACT_DO(good)\nACT_ELSE()\n:bad; <<invalid>>\nACT_ENDIF()\nstop\n"
                     "UML_LEGEND_BEGIN(bottom)\nUML_LEGEND_ROLE(invalid, failure path)\nUML_LEGEND_END()\n"),
        "statemachine": ("behavioral/statemachine-diagram-style.iuml",
                         "state Idle\nstate Busy\nBEHAV_TRANSITION(Idle, Busy)\nBEHAV_GUARDED(Busy, Idle, done, ok, notify)\n"
                         "STM_ENTRY(Busy, start)\nSTM_EXIT(Busy, stop)\nSTM_DO(Busy, run)\nSTM_INTERNAL(Idle, tick, log)\n"),
        "usecase": ("behavioral/usecase-diagram-style.iuml",
                    "actor U\nactor Admin\nUC_SYSTEM(Shop)\nusecase Buy\nusecase Pay\nusecase Audit\nUC_END_SYSTEM()\n"
                    "U --> Buy\nUC_INCLUDE(Buy, Pay)\nUC_EXTEND(Audit, Buy)\nUC_ACTOR_GEN(Admin, U)\n"),
        "sequence": ("interaction/sequence-diagram-style.iuml",
                     "SEQ_ACTOR(u, User)\nSEQ_PARTICIPANT(s, Service)\nSEQ_DATABASE(d, Store)\nINTER_SYNC(u, s, op())\n"
                     "INTER_ACTIVATE(s)\nINTER_ASYNC(s, d, signal)\nINTER_RETURN(d, s, value)\nINTER_DEACTIVATE(s)\nUML_DIVIDER(phase two)\n"
                     "INTER_LOST(s, lost)\nINTER_FOUND(s, found)\nINTER_OUTGOING(u, gate out)\nINTER_INCOMING(u, gate in)\n"
                     "INTER_FRAGMENT_ALT(ok)\nINTER_SELF(s, retry)\nINTER_FRAGMENT_ELSE(fail)\nINTER_SYNC(s, u, error)\nINTER_FRAGMENT_END()\n"
                     "INTER_REF(sd Login, u, s)\nUML_NOTE_INFO(n1, s, interaction)\n"),
        "communication": ("interaction/communication-diagram-style.iuml", "participant A\nparticipant B\nCOMM_MSG(A, B, 1, request)\nCOMM_RET(B, A, 1.1, reply)\n"),
        "timing": ("interaction/timing-diagram-style.iuml", "TIM_ROBUST(w, Worker)\nTIM_CONCISE(q, Queue)\n@0\nw is Idle\nq is Empty\n@10\nw is Busy\nq is Full\n"),
        "interaction-overview": ("interaction/interaction-overview-diagram-style.iuml",
                                 "start\nACT_DO(prepare)\nIOV_REF_STEP(sd Login)\nACT_IF(ok)\nIOV_REF_STEP(sd Checkout)\nACT_ELSE()\nACT_DO(abort)\nACT_ENDIF()\nstop\n"),
        "c4-context": ("c4/context-diagram-style.iuml",
                       "C4_TITLE(Probe)\nPerson(u, \"User\")\nSystem(s, \"System\")\nSystem_Ext(x, \"Ext\", $tags=\"proposed\")\n"
                       "Rel(u, s, \"uses\", \"HTTPS\")\nRel(s, x, \"calls\", \"unknown\", $tags=\"invalid\")\nSHOW_LEGEND()\n"),
        "c4-container": ("c4/container-diagram-style.iuml",
                         "C4_TITLE(Probe, container)\nPerson(u, \"User\")\nSystem_Boundary(b, \"Sys\") {\n  Container(w, \"Web\", \"tech\")\n"
                         "  ContainerDb(d, \"DB\", \"tech\")\n  ContainerQueue(q, \"MQ\", \"tech\", $tags=\"ok\")\n}\nRel(u, w, \"uses\")\nRel(w, d, \"rw\")\nSHOW_LEGEND()\n"),
        "c4-component": ("c4/component-diagram-style.iuml",
                         "C4_TITLE(Probe)\nContainer_Boundary(c, \"API\") {\n  Component(a, \"Ctrl\", \"tech\")\n  Component(b, \"Repo\", \"tech\", $tags=\"caution\")\n}\n"
                         "ContainerDb(d, \"DB\")\nRel(a, b, \"uses\")\nRel(b, d, \"rw\")\nSHOW_LEGEND()\n"),
        "c4-dynamic": ("c4/dynamic-diagram-style.iuml",
                       "C4_TITLE(Probe)\nPerson(u, \"User\")\nContainer(w, \"Web\")\nContainerDb(d, \"DB\")\n"
                       "Rel(u, w, \"submit\", $index=Index())\nRel(w, d, \"insert\", $index=Index())\nRel_Back(w, u, \"201\", $index=Index())\nSHOW_LEGEND()\n"),
        "c4-deployment": ("c4/deployment-diagram-style.iuml",
                          "C4_TITLE(Probe)\nDeployment_Node(n, \"Region\", \"eu\") {\n  Deployment_Node(k, \"Cluster\") {\n    Container(a, \"API\", \"tech\")\n  }\n"
                          "  ContainerDb(d, \"DB\")\n}\nRel(a, d, \"rw\", \"TLS\")\nSHOW_LEGEND()\n"),
    }

    @classmethod
    def _render(cls, include_path: str, probes: dict) -> tuple:
        env = os.environ.copy()
        env["PLANTUML_INCLUDE_PATH"] = include_path
        prefix = latex_build.plantuml_command_prefix(env)
        directory = tempfile.mkdtemp(prefix="puml-probes-")
        work = Path(directory)
        for name, (include, body) in probes.items():
            (work / f"probe-{name}.puml").write_text(
                f"@startuml probe-{name}\n!include {include}\n{body}@enduml\n", encoding="ascii"
            )
        out = work / "out"
        out.mkdir()
        result = subprocess.run(
            [*prefix, "-failfast2", "-tsvg", "-o", str(out), *(f"probe-{n}.puml" for n in probes)],
            cwd=str(work), env=env, capture_output=True, text=True, check=False,
        )
        return result, out

    def test_every_leaf_and_public_helper_compiles_with_the_pinned_engine(self) -> None:
        if latex_build.check_plantuml_engine() is not None:
            self.skipTest("manifest-pinned PlantUML is not selected in this environment")
        include_path = ":".join(str(path) for path in latex_build.PLANTUML_INCLUDE_DIRS if path.exists())
        result, out = self._render(include_path, self.PROBES)
        self.assertEqual(0, result.returncode, result.stderr)
        leaves = {
            f"{c}/{p.name}"
            for c in ("structural", "behavioral", "interaction", "c4")
            for p in (latex_build.ROOT / "tooling/styles/plantuml" / c).glob("*.iuml")
        }
        self.assertEqual(leaves, {include for include, _ in self.PROBES.values()}, "every leaf module needs exactly one probe")
        for name in self.PROBES:
            svg = out / f"probe-{name}.svg"
            self.assertTrue(svg.is_file(), f"{name} probe produced no SVG")
            self.assertIsNone(latex_build.svg_error_text(svg), f"{name} probe rendered an error image")
            self.assertNotIn("\ufffd", svg.read_text(encoding="utf-8"), f"{name}: replacement glyph in output")

    def test_corrected_helpers_emit_the_intended_notation(self) -> None:
        """PROF_EXTENSION is a solid triangle line (not dashed realization); CSD_PORT a port; INTER_LOST a dotted end."""
        if latex_build.check_plantuml_engine() is not None:
            self.skipTest("manifest-pinned PlantUML is not selected in this environment")
        env = os.environ.copy()
        env["PLANTUML_INCLUDE_PATH"] = ":".join(str(p) for p in latex_build.PLANTUML_INCLUDE_DIRS if p.exists())
        prefix = latex_build.plantuml_command_prefix(env)
        cases = {
            "profile": ("structural/profile-diagram-style.iuml", "class M <<metaclass>>\nclass S <<stereotype>>\nPROF_EXTENSION(S, M)\n", ["S --|> M : <<extension>>"]),
            "composite": ("structural/composite-structure-diagram-style.iuml", "component X {\n  CSD_PORT(p)\n}\n", ["port p"]),
            "component": ("structural/component-diagram-style.iuml", "component P\ncomponent Q\nCOMP_ASSEMBLY(P, I, Q)\nCOMP_REQUIRES(Q, I2)\n", ["Q -(0- P : I", "Q -( I2"]),
            "sequence": ("interaction/sequence-diagram-style.iuml", "participant A\nINTER_LOST(A, x)\nINTER_FOUND(A, y)\n", ["A ->o] : x", "[o-> A : y"]),
            "class": ("structural/class-diagram-style.iuml", "class A\nclass B\nSTRUCT_ASSOCIATION(A, B)\n", ["A -- B \n"]),
        }
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for name, (include, body, expected) in cases.items():
                source = work / f"{name}.puml"
                source.write_text(f"@startuml {name}\n!include {include}\n{body}@enduml\n", encoding="ascii")
                result = subprocess.run([*prefix, "-preproc", str(source)], cwd=str(work), env=env, capture_output=True, text=True, check=False)
                self.assertEqual(0, result.returncode, result.stderr)
                preprocessed = (work / f"{name}.preproc").read_text(encoding="utf-8")
                for fragment in expected:
                    self.assertIn(fragment, preprocessed, f"{name}: expected {fragment!r}")
                self.assertNotIn("..|>", preprocessed if name == "profile" else "", "extension must not be a dashed realization")
                self.assertNotIn("() p", preprocessed if name == "composite" else "", "a port is not an interface lollipop")


class PlantUMLRendererAccountingTests(unittest.TestCase):
    """Result accounting, freshness through transitive includes, and failure preservation."""

    def _engine_env(self, root: Path) -> dict:
        from tests.test_plantuml_pipeline import _fake_engine

        (root / "bin").mkdir(exist_ok=True)
        _fake_engine(root / "bin", latex_build.load_plantuml_pin()["version"])
        env = dict(os.environ)
        env["PATH"] = f"{root / 'bin'}{os.pathsep}{env.get('PATH', '')}"
        env.pop("PLANTUML_JAR", None)
        return env

    def test_result_json_distinguishes_files_blocks_configs_and_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / "src"
            (src / "a").mkdir(parents=True)
            (src / "a" / "one.puml").write_text("@startuml named-one\nA -> B\n@enduml\n@startuml\nA -> C\n@enduml\n", encoding="ascii")
            (src / "a" / "helper.puml").write_text("' include-only fragment\n!$x = 1\n", encoding="ascii")
            (src / "a" / "plantuml-config.puml").write_text("skinparam dpi 100\n", encoding="ascii")
            (src / "a" / "bad.puml").write_text("@startuml ../escape\n@enduml\n", encoding="ascii")
            result_path = root / "result.json"
            with patch.dict(os.environ, self._engine_env(root), clear=True):
                status = latex_build.render_plantuml(source_dir=src, formats=["svg"], force=True, result_path=result_path)
            self.assertEqual(1, status)
            data = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(4, data["discovered_files"])
            self.assertEqual(1, data["config_files"])
            self.assertEqual(1, data["include_only_files"])
            self.assertEqual(2, data["diagram_sources"])
            self.assertEqual(3, data["diagram_blocks"])
            self.assertEqual(1, data["rendered_diagrams"])
            self.assertEqual(1, data["failed_diagrams"])
            self.assertEqual(1, data["invalid_named_diagrams"])
            self.assertEqual({"named-one.svg", "one_001.svg"}, {Path(p).name for p in data["changed_files"]})
            self.assertTrue(data["has_changes"])
            self.assertEqual(["bad.puml"], [Path(f["source"]).name for f in data["failures"]])

    def test_unchanged_rerender_reports_no_changes(self) -> None:
        """A second forced run over identical inputs must not claim changed files (CI commits nothing)."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / "src"
            src.mkdir()
            (src / "d.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
            env = self._engine_env(root)
            with patch.dict(os.environ, env, clear=True):
                latex_build.render_plantuml(source_dir=src, formats=["svg"], force=True, result_path=root / "r1.json")
                latex_build.render_plantuml(source_dir=src, formats=["svg"], force=True, result_path=root / "r2.json")
            first = json.loads((root / "r1.json").read_text(encoding="utf-8"))
            second = json.loads((root / "r2.json").read_text(encoding="utf-8"))
            self.assertTrue(first["has_changes"])
            self.assertFalse(second["has_changes"])
            self.assertEqual(1, second["rendered_diagrams"])

    def test_empty_expected_root_fails_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / "src"
            src.mkdir()
            (src / "only-config.puml").write_text("skinparam dpi 100\n", encoding="ascii")
            with patch.dict(os.environ, self._engine_env(root), clear=True):
                self.assertEqual(1, latex_build.render_plantuml(source_dir=src, formats=["svg"], require_diagrams=True, result_path=root / "r.json"))
                self.assertEqual(0, latex_build.render_plantuml(source_dir=src, formats=["svg"], require_diagrams=False, result_path=root / "r.json"))

    def test_transitive_include_change_invalidates_the_diagram(self) -> None:
        """A diagram includes a local domain helper which includes a leaf; touching the helper must re-render."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / "src"
            src.mkdir()
            leaf = root / "leaf.iuml"
            leaf.write_text("skinparam shadowing false\n", encoding="ascii")
            helper = src / "domain.iuml"
            helper.write_text(f"!include {leaf}\n", encoding="ascii")
            source = src / "d.puml"
            source.write_text("@startuml\n!include domain.iuml\nA -> B\n@enduml\n", encoding="ascii")
            includes = latex_build.plantuml_includes(source, include_dirs=())
            self.assertEqual({helper.resolve(), leaf.resolve()}, {p.resolve() for p in includes})
            output = src / "svg" / "d.svg"
            output.parent.mkdir()
            output.write_text("<svg/>", encoding="ascii")
            now = max(source.stat().st_mtime, helper.stat().st_mtime, leaf.stat().st_mtime)
            os.utime(output, (now + 10, now + 10))
            self.assertTrue(latex_build._plantuml_is_current(source, None, [output], list(includes)))
            os.utime(leaf, (now + 20, now + 20))
            self.assertFalse(latex_build._plantuml_is_current(source, None, [output], list(includes)))

    def test_existing_jpg_derivative_is_refreshed_even_when_not_requested(self) -> None:
        """An optional jpg/ output must not keep an older theme after a png/svg-only render."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / "src"
            (src / "jpg").mkdir(parents=True)
            (src / "d.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
            (src / "jpg" / "d.jpg").write_bytes(b"\xff\xd8\xffold")
            png_magic = b"\x89PNG\r\n\x1a\nimg"

            def fake_run(command, **kwargs):
                if "-version" in command:
                    return SimpleNamespace(returncode=0, stdout="PlantUML version " + latex_build.load_plantuml_pin()["version"], stderr="")
                if "-stdlib" in command:
                    return SimpleNamespace(returncode=0, stdout="c4\nVersion " + latex_build.load_plantuml_pin().get("c4_plantuml", ""), stderr="")
                if command[0] == "fake-convert":
                    Path(command[-1]).write_bytes(b"\xff\xd8\xffnew")
                    return SimpleNamespace(returncode=0, stdout="", stderr="")
                out = Path(command[command.index("-o") + 1])
                out.mkdir(parents=True, exist_ok=True)
                fmt = next(a[2:] for a in command if a.startswith("-t"))
                for name in command:
                    if name.endswith(".puml"):
                        (out / f"{Path(name).stem}.{fmt}").write_bytes(png_magic if fmt == "png" else b"<svg/>")
                return SimpleNamespace(returncode=0, stdout="", stderr=b"")

            with patch("tooling.scripts.latex_build.subprocess.run", side_effect=fake_run), \
                    patch("tooling.scripts.latex_build.image_magick_convert", return_value="fake-convert"):
                status = latex_build.render_plantuml(source_dir=src, formats=["svg"], force=True, result_path=root / "r.json")
            self.assertEqual(0, status)
            self.assertEqual(b"\xff\xd8\xffnew", (src / "jpg" / "d.jpg").read_bytes())
            data = json.loads((root / "r.json").read_text(encoding="utf-8"))
            self.assertEqual({"svg": 1, "jpg": 1}, data["outputs_by_format"])

    def test_render_outputs_come_from_the_result_not_from_globbing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = latex_build.PlantUMLRenderResult(
                engine_version="1.2026.7", c4_version="2.13.0", formats=["png", "svg"], discovered_files=5,
                config_files=1, include_only_files=1, diagram_sources=3, diagram_blocks=3, rendered_diagrams=2,
                reused_diagrams=0, failed_diagrams=1, outputs_by_format={"png": 2, "svg": 2},
                changed_files=["src/a/png/x.png"], failures=[{"source": "src/a/y.puml", "format": "svg", "reason": "boom"}],
            )
            path = Path(directory) / "r.json"
            result.write(path)
            outputs = dict(line.split("=", 1) for line in latex_build.plantuml_render_outputs(path).splitlines())
            self.assertEqual("3", outputs["diagram_count"])
            self.assertEqual("2", outputs["rendered_count"])
            self.assertEqual("1", outputs["failed_count"])
            self.assertEqual("1", outputs["skipped_count"])
            self.assertEqual("true", outputs["has_changes"])
            self.assertEqual('["src/a/png/x.png"]', outputs["files"])
            summary = latex_build.plantuml_render_outputs(path, markdown=True)
            self.assertIn("| Rendered / reused / failed | 2 / 0 / 1 |", summary)
            self.assertIn("src/a/y.puml", summary)


if __name__ == "__main__":
    unittest.main()
