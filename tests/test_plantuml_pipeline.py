"""Regression tests for the PlantUML renderer, engine pin and generated-image staging."""

import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

import tooling.scripts.latex_build as latex_build

PIN = latex_build.load_plantuml_pin()


def _fake_engine(directory: Path, version: str, *, exit_code: int = 0, svg_body: str = "<svg></svg>") -> Path:
    """A `plantuml` on PATH that answers -version and writes one SVG per input into -o."""
    script = directory / "plantuml"
    script.write_text(
        textwrap.dedent(
            f"""\
            #!/bin/sh
            if [ "$1" = "-version" ]; then echo "PlantUML version {version} (fake)"; exit 0; fi
            out=""; prev=""
            for arg in "$@"; do [ "$prev" = "-o" ] && out="$arg"; prev="$arg"; done
            for arg in "$@"; do
              case "$arg" in *.puml) mkdir -p "$out"; printf '%s' '{svg_body}' > "$out/$(basename "$arg" .puml).svg";; esac
            done
            exit {exit_code}
            """
        ),
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


class PlantUMLEngineSelectionTests(unittest.TestCase):
    def _env(self, bin_dir: Path) -> dict:
        env = dict(os.environ)
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
        env.pop("PLANTUML_JAR", None)
        return env

    def test_outdated_distribution_binary_is_rejected(self) -> None:
        """Prevent the apt plantuml (1.2020.02) from silently producing syntax-error images."""
        with tempfile.TemporaryDirectory() as directory:
            _fake_engine(Path(directory), "1.2020.02")
            message = latex_build.check_plantuml_engine(self._env(Path(directory)))
            self.assertIsNotNone(message)
            self.assertIn("1.2020.02", message)
            self.assertIn(PIN["version"], message)

    def test_pinned_binary_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _fake_engine(Path(directory), PIN["version"])
            self.assertIsNone(latex_build.check_plantuml_engine(self._env(Path(directory))))

    def test_plantuml_jar_env_selects_a_headless_java_invocation(self) -> None:
        """Prevent CI and local runs from diverging: PLANTUML_JAR is the single engine hand-off."""
        prefix = latex_build.plantuml_command_prefix({"PLANTUML_JAR": "some/plantuml.jar"})
        self.assertEqual(["java", "-Djava.awt.headless=true", "-jar"], prefix[:3])
        self.assertTrue(Path(prefix[3]).is_absolute())

    def test_render_refuses_to_run_with_an_unpinned_engine(self) -> None:
        """Prevent a wrong engine from touching any committed image."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _fake_engine(root / "bin", "1.2024.8") if (root / "bin").mkdir() is None else None
            (root / "src").mkdir()
            (root / "src" / "d.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
            with patch.dict(os.environ, self._env(root / "bin"), clear=True):
                status = latex_build.render_plantuml(source_dir=root / "src", formats=["svg"], force=True)
            self.assertEqual(2, status)
            self.assertFalse((root / "src" / "svg").exists())


class PlantUMLRenderTests(unittest.TestCase):
    def _run(self, root: Path, engine_kwargs: dict, *, formats=("svg",)) -> int:
        (root / "bin").mkdir(exist_ok=True)
        _fake_engine(root / "bin", PIN["version"], **engine_kwargs)
        env = dict(os.environ)
        env["PATH"] = f"{root / 'bin'}{os.pathsep}{env.get('PATH', '')}"
        env.pop("PLANTUML_JAR", None)
        with patch.dict(os.environ, env, clear=True):
            return latex_build.render_plantuml(source_dir=root / "src", formats=list(formats), force=True)

    def test_nonzero_engine_exit_fails_the_render(self) -> None:
        """Prevent -failfast2 syntax failures from being reported as success."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "d.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
            self.assertEqual(1, self._run(root, {"exit_code": 1}))

    def test_failed_png_render_preserves_the_existing_output(self) -> None:
        """Prevent a failed PNG batch from replacing a previously valid committed image."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = root / "src"
            source_dir.mkdir()
            (source_dir / "d.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
            png_dir = source_dir / "png"
            png_dir.mkdir()
            (png_dir / "d.png").write_bytes(b"valid image")
            self.assertEqual(1, self._run(root, {"exit_code": 1}, formats=("png",)))
            self.assertEqual(b"valid image", (png_dir / "d.png").read_bytes())

    def test_error_text_drawn_into_an_svg_fails_the_render(self) -> None:
        """Prevent a banner or error image (exit 0) from being committed."""
        body = "<svg><text>Please\u00a0use\u00a0CSS\u00a0style\u00a0instead\u00a0of\u00a0skinparam\u00a0padding</text></svg>"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            source = root / "src" / "d.puml"
            source.write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
            valid_output = root / "src" / "svg"
            valid_output.mkdir()
            (valid_output / "d.svg").write_text("valid committed image", encoding="ascii")
            self.assertEqual(1, self._run(root, {"svg_body": body}))
            self.assertEqual("valid committed image", (valid_output / "d.svg").read_text(encoding="ascii"))

    def test_clean_render_succeeds_and_writes_beside_the_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src" / "deep").mkdir(parents=True)
            (root / "src" / "deep" / "d.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
            self.assertEqual(0, self._run(root, {}))
            self.assertTrue((root / "src" / "deep" / "svg" / "d.svg").is_file())
            self.assertEqual([], [p for p in root.rglob("src/*/src")], "no nested src/**/src output tree")


class PlantUMLOutputPathTests(unittest.TestCase):
    def test_output_dir_is_absolute_so_cwd_cannot_nest_the_tree(self) -> None:
        """Prevent src/**/src/**/png trees: a relative -o is joined to each source directory by PlantUML."""
        cmd = latex_build.plantuml_render_command(["plantuml"], "png", Path("src/a/png"), None, ["x.puml"])
        self.assertIn("-failfast2", cmd)
        out = cmd[cmd.index("-o") + 1]
        self.assertTrue(Path(out).is_absolute(), out)
        self.assertTrue(out.endswith(os.sep.join(["src", "a", "png"])))

    def test_named_startuml_blocks_determine_output_names(self) -> None:
        """Prevent named diagrams from being considered permanently stale (PlantUML names outputs after @startuml)."""
        source = Path("src/x/15-metacloud.puml")
        self.assertEqual([Path("src/x/svg/metacloud.svg")], latex_build.plantuml_output_paths(source, "svg", "@startuml metacloud\n@enduml\n"))
        self.assertEqual([Path("src/x/png/15-metacloud.png")], latex_build.plantuml_output_paths(source, "png", "@startuml\n@enduml\n"))
        two = latex_build.plantuml_output_paths(source, "svg", "@startuml\n@enduml\n@startuml\n@enduml\n")
        self.assertEqual(["15-metacloud.svg", "15-metacloud_001.svg"], [p.name for p in two])
        self.assertEqual(["15-metacloud.svg"], [p.name for p in latex_build.plantuml_output_paths(source, "svg", "@startuml ../outside\n@enduml\n")])

    def test_manifest_changes_invalidate_outputs(self) -> None:
        """Prevent a PlantUML version or checksum bump from leaving old images current."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "d.puml"
            manifest = root / "plantuml.json"
            output = root / "d.svg"
            source.write_text("@startuml\n@enduml\n", encoding="ascii")
            manifest.write_text("pin", encoding="ascii")
            output.write_text("old", encoding="ascii")
            future = max(source.stat().st_mtime, manifest.stat().st_mtime, output.stat().st_mtime) + 10
            os.utime(output, (future, future))
            os.utime(manifest, (future + 10, future + 10))
            self.assertFalse(latex_build._plantuml_is_current(source, None, [output], [manifest]))


class SvgErrorTextTests(unittest.TestCase):
    def _svg(self, directory: str, text: str) -> Path:
        path = Path(directory) / "d.svg"
        path.write_text(f"<svg><text>{text}</text></svg>", encoding="utf-8")
        return path

    def test_detects_syntax_error_and_css_banner_with_nbsp(self) -> None:
        """Prevent NBSP-spaced PlantUML text from slipping past the scan."""
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual("Syntax Error", latex_build.svg_error_text(self._svg(directory, "Syntax\u00a0Error?")))
            self.assertEqual("Please use CSS style", latex_build.svg_error_text(self._svg(directory, "Please\u00a0use\u00a0CSS\u00a0style\u00a0instead")))

    def test_clean_svg_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(latex_build.svg_error_text(self._svg(directory, "Order Fulfilment Workflow")))


class GeneratedImageStagingTests(unittest.TestCase):
    """Each scenario runs in a throwaway git repository; nothing touches the real worktree."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.email", "t@example.com")
        self._git("config", "user.name", "t")
        self.diagrams = self.repo / "src" / "area" / "diagrams"
        (self.diagrams / "png").mkdir(parents=True)
        (self.diagrams / "svg").mkdir()
        (self.diagrams / "d.puml").write_text("@startuml\n@enduml\n", encoding="ascii")
        (self.diagrams / "png" / "d.png").write_bytes(b"png1")
        (self.diagrams / "svg" / "d.svg").write_text("<svg/>", encoding="ascii")
        (self.repo / "src" / "area" / "doc.tex").write_text("\\documentclass{article}", encoding="ascii")
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "seed")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True).stdout

    def _stage(self) -> list:
        return latex_build.stage_generated_images(self.repo)

    def _cached(self) -> str:
        return self._git("diff", "--cached", "--name-status")

    def test_png_and_svg_changes_without_any_jpg_are_staged(self) -> None:
        """Prevent `fatal: pathspec 'src/**/jpg/*.jpg' did not match any files` from aborting the commit step."""
        (self.diagrams / "png" / "d.png").write_bytes(b"png2")
        (self.diagrams / "svg" / "new.svg").write_text("<svg/>", encoding="ascii")
        staged = self._stage()
        self.assertEqual({"M\tsrc/area/diagrams/png/d.png", "A\tsrc/area/diagrams/svg/new.svg"}, set(staged))
        self.assertFalse(list(self.repo.rglob("jpg")), "no jpg directory may be created to satisfy the pathspec")

    def test_only_png_changes(self) -> None:
        (self.diagrams / "png" / "d.png").write_bytes(b"png2")
        self.assertEqual(["M\tsrc/area/diagrams/png/d.png"], self._stage())

    def test_only_svg_changes(self) -> None:
        (self.diagrams / "svg" / "d.svg").write_text("<svg>2</svg>", encoding="ascii")
        self.assertEqual(["M\tsrc/area/diagrams/svg/d.svg"], self._stage())

    def test_jpg_outputs_are_staged_when_present(self) -> None:
        (self.diagrams / "jpg").mkdir()
        (self.diagrams / "jpg" / "d.jpg").write_bytes(b"jpg")
        self.assertEqual(["A\tsrc/area/diagrams/jpg/d.jpg"], self._stage())

    def test_deleted_tracked_image_is_staged_as_a_deletion(self) -> None:
        """Prevent renamed @startuml outputs from lingering: deletions must be staged too."""
        (self.diagrams / "png" / "d.png").unlink()
        self.assertEqual(["D\tsrc/area/diagrams/png/d.png"], self._stage())

    def test_no_diagram_changes_stages_nothing(self) -> None:
        self.assertEqual([], self._stage())
        self.assertEqual("", self._cached())

    def test_unrelated_src_changes_are_not_staged(self) -> None:
        """Prevent the bot commit from sweeping up .tex, .puml, config or stray files under src."""
        (self.repo / "src" / "area" / "doc.tex").write_text("changed", encoding="ascii")
        (self.diagrams / "d.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="ascii")
        (self.diagrams / "notes.txt").write_text("scratch", encoding="ascii")
        (self.diagrams / "stray.png").write_bytes(b"not in png/")
        (self.diagrams / "png" / "readme.md").write_text("not an image", encoding="ascii")
        (self.diagrams / "png" / "d.png").write_bytes(b"png2")
        self.assertEqual(["M\tsrc/area/diagrams/png/d.png"], self._stage())

    def test_filenames_with_spaces_and_unicode_are_staged(self) -> None:
        (self.diagrams / "svg" / "two words.svg").write_text("<svg/>", encoding="ascii")
        (self.diagrams / "png" / "caf\u00e9 \u2192 bar.png").write_bytes(b"png")
        staged = self._stage()
        self.assertEqual(2, len(staged))
        self.assertIn("A\tsrc/area/diagrams/svg/two words.svg", staged)
        self.assertTrue(any(entry.startswith("A\t") and entry.endswith(".png") for entry in staged))
        self.assertEqual(2, len([line for line in self._cached().splitlines() if line]))


if __name__ == "__main__":
    unittest.main()
