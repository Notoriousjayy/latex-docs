"""Correctness tests for the dependency-aware, sharded build pipeline."""
from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tooling.scripts import build_graph, latex_build


DOC_TEMPLATE = "\\documentclass{article}\n\\usepackage{%s}\n%s\\begin{document}x\\end{document}\n"


class _Workspace:
    """A throwaway repository layout wired into the module-level ROOT paths."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        (self.root / "src").mkdir()
        (self.root / "tooling" / "styles" / "latex").mkdir(parents=True)
        (self.root / "tooling" / "latex").mkdir(parents=True)
        self._patches = [
            patch.object(build_graph, "ROOT", self.root),
            patch.object(build_graph, "SRC_DIR", self.root / "src"),
        ]
        for item in self._patches:
            item.start()

    def close(self) -> None:
        for item in self._patches:
            item.stop()
        self._tmp.cleanup()

    def write(self, rel: str, text: str = "x") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def doc(self, rel: str, *, package: str = "base", extra: str = "") -> Path:
        return self.write(rel, DOC_TEMPLATE % (package, extra))

    def graph(self, **kwargs):
        return build_graph.build_graph(**kwargs)


class WorkspaceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.ws = _Workspace()
        self.addCleanup(self.ws.close)
        self.ws.write("tooling/styles/latex/base.sty", "% base")
        self.ws.write("tooling/styles/latex/cornell-notes.sty", "\\RequirePackage{base}\n")


class RootDiscoveryTests(WorkspaceTestCase):
    def test_standalone_roots_discovered_and_fragments_excluded(self) -> None:
        self.ws.doc("src/a/one.tex")
        self.ws.doc("src/a/two.tex")
        self.ws.write("src/a/fragment.tex", "This is included, not a root.\n")
        self.ws.write("src/a/.one.latex-build-wrapper.tex", DOC_TEMPLATE % ("base", ""))

        roots = build_graph.discover_roots()

        self.assertEqual(
            ["src/a/one.tex", "src/a/two.tex"],
            sorted(path.relative_to(self.ws.root).as_posix() for path in roots),
        )

    def test_expected_pdf_path_strips_the_src_prefix(self) -> None:
        self.assertEqual("a/b/doc.pdf", build_graph.expected_pdf_path("src/a/b/doc.tex"))


class ChangeDetectionTests(WorkspaceTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.ws.doc("src/alpha/main.tex", extra="\\input{shared}\n\\includegraphics{png/diagram.png}\n")
        self.ws.doc("src/beta/main.tex", package="cornell-notes")
        self.ws.doc("src/gamma/main.tex")
        self.ws.write("src/alpha/shared.tex", "shared fragment")
        self.ws.write("src/alpha/png/diagram.png", "PNG")
        self.graph = self.ws.graph()

    def select(self, *changed: str) -> list[str]:
        return build_graph.select_affected(self.graph, list(changed))[0]

    def test_changed_root_selects_only_itself(self) -> None:
        self.assertEqual(["src/alpha/main.tex"], self.select("src/alpha/main.tex"))

    def test_changed_local_input_selects_the_dependent_root(self) -> None:
        self.assertEqual(["src/alpha/main.tex"], self.select("src/alpha/shared.tex"))

    def test_changed_image_selects_the_dependent_root(self) -> None:
        self.assertEqual(["src/alpha/main.tex"], self.select("src/alpha/png/diagram.png"))

    def test_changed_bibliography_selects_the_dependent_root(self) -> None:
        self.ws.doc("src/delta/main.tex", extra="\\addbibresource{refs.bib}\n")
        self.ws.write("src/delta/refs.bib", "@book{a,title={T}}")
        graph = self.ws.graph()
        self.assertIn("src/delta/main.tex", build_graph.select_affected(graph, ["src/delta/refs.bib"])[0])

    def test_semantic_style_change_selects_only_its_consumers(self) -> None:
        selected = self.select("tooling/styles/latex/cornell-notes.sty")
        self.assertEqual(["src/beta/main.tex"], selected)

    def test_transitive_base_style_change_selects_every_consumer(self) -> None:
        # beta -> cornell-notes.sty -> base.sty must be followed transitively.
        selected = self.select("tooling/styles/latex/base.sty")
        self.assertEqual(
            ["src/alpha/main.tex", "src/beta/main.tex", "src/gamma/main.tex"], selected
        )

    def test_global_foundation_change_selects_every_root(self) -> None:
        selected, reason = build_graph.select_affected(self.graph, ["latexmkrc"])
        self.assertEqual("global", reason)
        self.assertEqual(3, len(selected))

    def test_build_tooling_change_is_global(self) -> None:
        self.assertTrue(build_graph.is_global_change("tooling/scripts/latex_build.py"))
        self.assertTrue(build_graph.is_global_change("Makefile"))
        self.assertFalse(build_graph.is_global_change("README.md"))

    def test_unrelated_file_selects_nothing(self) -> None:
        self.assertEqual([], self.select("README.md"))
        self.assertEqual([], self.select("docs/notes.md"))

    def test_unattributable_asset_falls_back_to_its_directory_subtree(self) -> None:
        # Documents reference generated diagrams through wrapper macros, so an
        # unreferenced .puml must still conservatively select nearby roots.
        self.ws.write("src/beta/diagrams/flow.puml", "@startuml\n@enduml\n")
        graph = self.ws.graph()
        selected, _ = build_graph.select_affected(graph, ["src/beta/diagrams/flow.puml"])
        self.assertEqual(["src/beta/main.tex"], selected)


class FingerprintTests(WorkspaceTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.ws.doc("src/alpha/main.tex", extra="\\input{shared}\n")
        self.ws.write("src/alpha/shared.tex", "v1")

    def fingerprint(self, *, toolchain: str = "tl2024") -> str:
        graph = self.ws.graph(toolchain_version=toolchain)
        return graph.by_source()["src/alpha/main.tex"].fingerprint

    def test_identical_inputs_produce_a_stable_fingerprint(self) -> None:
        self.assertEqual(self.fingerprint(), self.fingerprint())

    def test_transitive_dependency_change_changes_the_fingerprint(self) -> None:
        before = self.fingerprint()
        self.ws.write("src/alpha/shared.tex", "v2")
        self.assertNotEqual(before, self.fingerprint())

    def test_style_change_changes_the_fingerprint(self) -> None:
        before = self.fingerprint()
        self.ws.write("tooling/styles/latex/base.sty", "% base v2")
        self.assertNotEqual(before, self.fingerprint())

    def test_toolchain_change_changes_the_fingerprint(self) -> None:
        self.assertNotEqual(self.fingerprint(toolchain="tl2024"), self.fingerprint(toolchain="tl2025"))


class ShardPlanningTests(unittest.TestCase):
    @staticmethod
    def records(weights):
        return [
            build_graph.RootRecord(source=f"src/doc-{index}.tex", pdf=f"doc-{index}.pdf", category="c", weight=weight)
            for index, weight in enumerate(weights)
        ]

    def test_every_root_is_assigned_exactly_once(self) -> None:
        records = self.records([1.0] * 50)
        shards = build_graph.plan_shards(records, 7, min_roots_per_shard=1)
        assigned = [record.source for shard in shards for record in shard]
        self.assertEqual(sorted(assigned), sorted(record.source for record in records))
        self.assertEqual(len(assigned), len(set(assigned)), "a root was duplicated across shards")

    def test_no_empty_shards_are_emitted(self) -> None:
        shards = build_graph.plan_shards(self.records([1.0] * 3), 10, min_roots_per_shard=1)
        self.assertTrue(all(shards))

    def test_empty_selection_produces_no_shards(self) -> None:
        self.assertEqual([], build_graph.plan_shards([], 8))

    def test_weighting_balances_a_bimodal_workload(self) -> None:
        # Four heavy documents plus many trivial ones: count-based sharding
        # would put all heavy documents in one shard.
        records = self.records([100.0] * 4 + [1.0] * 96)
        shards = build_graph.plan_shards(records, 4, min_roots_per_shard=1)
        loads = [sum(record.weight for record in shard) for shard in shards]
        self.assertLess(max(loads) - min(loads), 0.25 * max(loads))
        self.assertTrue(all(any(record.weight == 100.0 for record in shard) for shard in shards))

    def test_min_roots_per_shard_limits_fan_out(self) -> None:
        shards = build_graph.plan_shards(self.records([1.0] * 30), 12, min_roots_per_shard=25)
        self.assertEqual(1, len(shards))

    def test_timing_history_round_trip_and_smoothing(self) -> None:
        merged = build_graph.merge_timing_history({"a": 10.0}, {"a": 20.0, "b": 5.0})
        self.assertEqual(15.0, merged["a"])
        self.assertEqual(5.0, merged["b"])

    def test_corrupt_timing_history_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "timings.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertEqual({}, build_graph.load_timing_history(path))


class AggregationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.pdf_dir = self.root / "pdfs"
        self.logs = self.root / "logs"
        self.out = self.root / "out"
        self.pdf_dir.mkdir()
        self.logs.mkdir()

        self.plan_path = self.root / "plan.json"
        self.plan_path.write_text(
            json.dumps(
                {
                    "mode": "changed",
                    "reason": "incremental",
                    "total_roots": 2,
                    "selected_roots": 1,
                    "skipped_roots": 1,
                    "expected_pdfs": ["a.pdf", "b.pdf"],
                    "shards": [{"index": 0, "name": "shard-00", "roots": ["src/a.tex"], "count": 1}],
                    "manifest": [
                        {"source": "src/a.tex", "pdf": "a.pdf", "selected": True},
                        {"source": "src/b.tex", "pdf": "b.pdf", "selected": False},
                    ],
                }
            ),
            encoding="utf-8",
        )

    def write_shard_summary(self, **overrides) -> None:
        summary = {
            "attempted_count": 1,
            "succeeded_count": 1,
            "failed_count": 0,
            "compile_seconds": 2.0,
            "wall_clock_seconds": 2.0,
            "durations": {"src/a.tex": 2.0},
            "first_errors": [],
            "failure_clusters": [],
        }
        summary.update(overrides)
        shard_dir = self.logs / "shard-0"
        shard_dir.mkdir(exist_ok=True)
        (shard_dir / "build-summary.json").write_text(json.dumps(summary), encoding="utf-8")

    def aggregate(self, **kwargs) -> int:
        return latex_build.aggregate_shards(
            plan_path=self.plan_path,
            logs_dir=self.logs,
            pdf_dir=self.pdf_dir,
            output_dir=self.out,
            **kwargs,
        )

    def result(self) -> dict:
        return json.loads((self.out / "build-aggregate.json").read_text(encoding="utf-8"))

    def test_complete_incremental_build_succeeds(self) -> None:
        self.write_shard_summary()
        (self.pdf_dir / "a.pdf").write_bytes(b"%PDF")
        (self.pdf_dir / "b.pdf").write_bytes(b"%PDF")
        self.assertEqual(0, self.aggregate(require_complete_corpus=True))
        self.assertEqual("success", self.result()["status"])

    def test_missing_expected_output_fails_the_build(self) -> None:
        self.write_shard_summary()
        (self.pdf_dir / "b.pdf").write_bytes(b"%PDF")
        self.assertEqual(1, self.aggregate())
        self.assertIn("produced no PDF", " ".join(self.result()["problems"]))

    def test_failed_shard_prevents_publication(self) -> None:
        self.write_shard_summary()
        (self.pdf_dir / "a.pdf").write_bytes(b"%PDF")
        (self.pdf_dir / "b.pdf").write_bytes(b"%PDF")
        self.assertEqual(1, self.aggregate(shard_result="failure"))
        self.assertEqual("failed", self.result()["status"])

    def test_incomplete_shard_reporting_is_detected(self) -> None:
        (self.pdf_dir / "a.pdf").write_bytes(b"%PDF")
        (self.pdf_dir / "b.pdf").write_bytes(b"%PDF")
        self.assertEqual(1, self.aggregate())  # no shard summaries at all
        self.assertIn("shards reported", " ".join(self.result()["problems"]))

    def test_deleted_root_leaves_no_stale_pdf(self) -> None:
        self.write_shard_summary()
        (self.pdf_dir / "a.pdf").write_bytes(b"%PDF")
        (self.pdf_dir / "b.pdf").write_bytes(b"%PDF")
        (self.pdf_dir / "removed.pdf").write_bytes(b"%PDF")
        self.assertEqual(0, self.aggregate(require_complete_corpus=True))
        self.assertFalse((self.pdf_dir / "removed.pdf").exists())
        self.assertEqual(["removed.pdf"], self.result()["stale_pdfs_removed"])

    def test_incomplete_corpus_blocks_publication_but_not_plain_ci(self) -> None:
        self.write_shard_summary()
        (self.pdf_dir / "a.pdf").write_bytes(b"%PDF")  # b.pdf absent from the corpus
        self.assertEqual(0, self.aggregate(require_complete_corpus=False))
        self.assertEqual(1, self.aggregate(require_complete_corpus=True))

    def test_manifest_is_written_only_for_a_successful_corpus(self) -> None:
        manifest = self.root / "corpus-manifest.json"
        self.write_shard_summary()
        (self.pdf_dir / "a.pdf").write_bytes(b"%PDF")
        self.aggregate(manifest_path=manifest, require_complete_corpus=True)
        self.assertFalse(manifest.exists())

        (self.pdf_dir / "b.pdf").write_bytes(b"%PDF")
        self.aggregate(manifest_path=manifest, require_complete_corpus=True)
        self.assertEqual(["a.pdf", "b.pdf"], json.loads(manifest.read_text(encoding="utf-8"))["pdfs"])


class CorpusManifestGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.plan = self.root / "plan.json"
        self.plan.write_text(json.dumps({"expected_pdfs": ["a.pdf", "b.pdf"]}), encoding="utf-8")
        self.manifest = self.root / "manifest.json"

    def test_missing_manifest_forces_a_full_rebuild(self) -> None:
        self.assertEqual(1, latex_build.check_corpus_manifest(self.manifest, self.plan))

    def test_corrupt_manifest_forces_a_full_rebuild(self) -> None:
        self.manifest.write_text("{broken", encoding="utf-8")
        self.assertEqual(1, latex_build.check_corpus_manifest(self.manifest, self.plan))

    def test_incomplete_manifest_forces_a_full_rebuild(self) -> None:
        self.manifest.write_text(json.dumps({"pdfs": ["a.pdf"]}), encoding="utf-8")
        self.assertEqual(1, latex_build.check_corpus_manifest(self.manifest, self.plan))

    def test_complete_manifest_permits_an_incremental_publish(self) -> None:
        self.manifest.write_text(json.dumps({"pdfs": ["a.pdf", "b.pdf", "extra.pdf"]}), encoding="utf-8")
        self.assertEqual(0, latex_build.check_corpus_manifest(self.manifest, self.plan))


class ShardCliTests(unittest.TestCase):
    """The workflow drives sharding through the CLI; verify that plumbing."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.plan_path = Path(self._tmp.name) / "plan.json"
        self.plan_path.write_text(
            json.dumps(
                {
                    "base_ref": "base1",
                    "head_ref": "head2",
                    "total_roots": 10,
                    "selected_roots": 3,
                    "skipped_roots": 7,
                    "shards": [
                        {"index": 0, "name": "shard-00", "roots": ["src/a.tex"], "count": 1},
                        {"index": 1, "name": "shard-01", "roots": ["src/b.tex", "src/c.tex"], "count": 2},
                    ],
                }
            ),
            encoding="utf-8",
        )

    def test_build_selection_builds_only_its_own_shard(self) -> None:
        with patch("tooling.scripts.latex_build.build_roots", return_value=0) as build_roots_mock:
            status = latex_build.main(
                ["build-selection", "--plan", str(self.plan_path), "--shard-index", "1", "--jobs", "3"]
            )

        self.assertEqual(0, status)
        roots, kwargs = build_roots_mock.call_args.args[0], build_roots_mock.call_args.kwargs
        self.assertEqual(
            ["src/b.tex", "src/c.tex"],
            [path.relative_to(latex_build.ROOT).as_posix() for path in roots],
        )
        self.assertEqual(3, kwargs["jobs"])
        self.assertEqual(1, kwargs["shard_index"])
        self.assertEqual(2, kwargs["shard_total"])
        self.assertEqual(7, kwargs["skipped_count"])
        self.assertEqual("base1", kwargs["base_revision"])

    def test_unknown_shard_index_is_a_configuration_error(self) -> None:
        with patch("tooling.scripts.latex_build.build_roots", return_value=0) as build_roots_mock:
            status = latex_build.main(["build-selection", "--plan", str(self.plan_path), "--shard-index", "9"])

        self.assertEqual(2, status)
        build_roots_mock.assert_not_called()

    def test_plan_outputs_emit_a_matrix_covering_every_shard(self) -> None:
        rendered = latex_build.plan_outputs(self.plan_path)
        matrix_line = next(line for line in rendered.splitlines() if line.startswith("matrix="))
        matrix = json.loads(matrix_line[len("matrix=") :])

        self.assertEqual([0, 1], [entry["index"] for entry in matrix["shard"]])
        self.assertIn("shard-count=2", rendered)

    def test_merge_timings_reads_shard_reports_recursively(self) -> None:
        logs = Path(self._tmp.name) / "logs" / "latex-shard-logs-0"
        logs.mkdir(parents=True)
        (logs / "build-timings.json").write_text(
            json.dumps({"durations": {"src/a.tex": 4.0}}), encoding="utf-8"
        )
        history = Path(self._tmp.name) / "history.json"

        status = latex_build.main(
            ["merge-timings", str(logs.parent), "--history", str(history)]
        )

        self.assertEqual(0, status)
        self.assertEqual({"src/a.tex": 4.0}, build_graph.load_timing_history(history))


class OutputTreeSafetyTests(unittest.TestCase):
    def test_no_test_executes_a_real_build_against_the_public_tree(self) -> None:
        # A test that really ran `build-changed CLEAN_OUTPUT=true OUTPUT_DIR=public/pdfs`
        # deleted the published corpus of any concurrent build. Asserting on a
        # dry-run command string is fine; executing one is not.
        tests_dir = Path(__file__).resolve().parent
        offenders = []
        for path in sorted(tests_dir.glob("test_*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                    continue
                if node.name == "test_no_test_executes_a_real_build_against_the_public_tree":
                    continue
                body = ast.unparse(node)
                if "subprocess.run" in body and ("OUTPUT_DIR=public/" in body or "LOG_DIR=public/" in body):
                    offenders.append(f"{path.name}::{node.name}")

        self.assertEqual([], offenders, "executed builds must target a temporary directory")


class TexinputsRegressionTests(unittest.TestCase):
    def test_texinputs_excludes_the_recursive_src_tree(self) -> None:
        # A recursive kpathsea entry over src/ made every lookup re-walk the
        # whole content tree: 63s/document instead of 2s/document.
        texinputs = latex_build.resolve_texinputs()
        self.assertNotIn(f"{latex_build.ROOT}/src//", texinputs)
        self.assertIn("tooling/latex//", texinputs)
        self.assertIn("tooling/styles/latex//", texinputs)

    def test_latexmkrc_does_not_add_a_recursive_src_path(self) -> None:
        text = (latex_build.ROOT / "latexmkrc").read_text(encoding="utf-8")
        active = [line for line in text.splitlines() if not line.strip().startswith("#")]
        self.assertFalse(
            [line for line in active if '$root/src//' in line],
            "latexmkrc must not put a recursive path over src/ on any kpathsea variable",
        )


if __name__ == "__main__":
    unittest.main()
