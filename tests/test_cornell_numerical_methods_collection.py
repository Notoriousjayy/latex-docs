import re
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

import tooling.scripts.latex_build as latex_build
from tooling.scripts.latex_build import discover_roots, stage_pages_site
from tooling.scripts.style_migration import strip_latex_comments


EXPECTED_NUMERICAL_METHODS = {
    "foundations": [
        "ch01-preliminaries-notes.tex",
    ],
    "linear-algebra": [
        "ch02-linear-equations-notes.tex",
        "ch11-eigensystems-notes.tex",
    ],
    "interpolation-integration-and-functions": [
        "ch03-interpolation-notes.tex",
        "ch04-integration-notes.tex",
        "ch05-function-evaluation-notes.tex",
        "ch06-special-functions-notes.tex",
    ],
    "randomization-and-ordering": [
        "ch07-random-numbers-notes.tex",
        "ch08-sorting-selection-notes.tex",
    ],
    "root-finding-and-optimization": [
        "ch09-root-finding-notes.tex",
        "ch10-optimization-notes.tex",
    ],
    "fourier-and-spectral-methods": [
        "ch12-fft-notes.tex",
        "ch13-spectral-applications-notes.tex",
    ],
    "statistics-modeling-and-inference": [
        "ch14-statistical-description-notes.tex",
        "ch15-data-modeling-notes.tex",
        "ch16-classification-inference-notes.tex",
    ],
    "differential-and-integral-equations": [
        "ch17-ordinary-differential-equations-notes.tex",
        "ch18-boundary-value-problems-notes.tex",
        "ch19-integral-equations-notes.tex",
        "ch20-partial-differential-equations-notes.tex",
    ],
    "computational-geometry": [
        "ch21-computational-geometry-notes.tex",
    ],
    "general-algorithms": [
        "ch22-general-algorithms-notes.tex",
    ],
}

EXPECTED_ELECTRONICS = {
    "foundations": [
        "ch01-foundations-notes.tex",
    ],
    "semiconductor-devices": [
        "ch02-bipolar-transistors-notes.tex",
        "ch03-field-effect-transistors-notes.tex",
    ],
    "analog-circuits": [
        "ch04-operational-amplifiers-notes.tex",
        "ch05-precision-circuits-notes.tex",
        "ch06-filters-notes.tex",
        "ch07-oscillators-and-timers-notes.tex",
        "ch08-low-noise-techniques-notes.tex",
    ],
    "power-electronics": [
        "ch09-voltage-regulation-and-power-conversion-notes.tex",
    ],
    "digital-logic-and-interfaces": [
        "ch10-digital-logic-notes.tex",
        "ch11-programmable-logic-devices-notes.tex",
        "ch12-logic-interfacing-notes.tex",
    ],
    "mixed-signal-systems": [
        "ch13-digital-meets-analog-notes.tex",
    ],
    "embedded-systems": [
        "ch14-computers-controllers-and-data-links-notes.tex",
        "ch15-microcontrollers-notes.tex",
    ],
}

EXPECTED_COMBINATORIAL_ALGORITHMS = {
    "subset-generation": ["ch01-next-subset-of-an-n-set-notes.tex", "ch02-random-subset-of-an-n-set-notes.tex", "ch03-next-k-subset-of-an-n-set-notes.tex", "ch04-random-k-subset-of-an-n-set-notes.tex"],
    "compositions": ["ch05-next-composition-of-n-into-k-parts-notes.tex", "ch06-random-composition-of-n-into-k-parts-notes.tex"],
    "permutations": ["ch07-next-permutation-of-n-letters-notes.tex", "ch08-random-permutation-of-n-letters-notes.tex", "ch16-cycle-structure-of-a-permutation-notes.tex"],
    "integer-partitions": ["ch09-next-partition-of-integer-n-notes.tex", "ch10-random-partition-of-an-integer-n-notes.tex"],
    "set-partitions": ["ch11-next-partition-of-an-n-set-notes.tex", "ch12-random-partition-of-an-n-set-notes.tex"],
    "general-frameworks": ["ch13-general-combinatorial-family-algorithms-notes.tex"],
    "young-tableaux": ["ch14-young-tableaux-notes.tex"], "sorting": ["ch15-sorting-notes.tex"],
    "array-reindexing": ["ch17-renumbering-rows-and-columns-of-an-array-notes.tex"],
    "graph-algorithms": ["ch18-spanning-forest-of-a-graph-notes.tex", "ch20-chromatic-polynomial-of-a-graph-notes.tex", "ch22-network-flows-notes.tex"],
    "polynomial-algorithms": ["ch19-newton-forms-of-a-polynomial-notes.tex", "ch21-composition-of-power-series-notes.tex"],
    "matrix-and-array-algorithms": ["ch23-permanent-function-notes.tex", "ch24-invert-a-triangular-array-notes.tex"],
    "partially-ordered-sets": ["ch25-triangular-numbering-in-partially-ordered-sets-notes.tex", "ch26-mobius-function-notes.tex"],
    "backtracking": ["ch27-backtrack-method-notes.tex"],
    "tree-algorithms": ["ch28-labeled-trees-notes.tex", "ch29-random-unlabeled-rooted-trees-notes.tex", "ch30-tree-of-minimal-length-notes.tex"],
}

EXPECTED_COMPUTER_NETWORKS = {
    "foundations": ["ch01-introduction-cornell-notes.tex"], "physical-layer": ["ch02-physical-layer-cornell-notes.tex"],
    "data-link-layer": ["ch03-data-link-layer-cornell-notes.tex"], "medium-access-control": ["ch04-medium-access-control-sublayer-cornell-notes.tex"],
    "network-layer": ["ch05-network-layer-cornell-notes.tex"], "transport-layer": ["ch06-transport-layer-cornell-notes.tex"],
    "application-layer": ["ch07-application-layer-cornell-notes.tex"], "network-security": ["ch08-network-security-cornell-notes.tex"],
    "reference-material": ["ch09-reading-list-and-bibliography-cornell-notes.tex"],
}

EXPECTED_OPERATING_SYSTEMS = {
    "foundations": ["ch01-introduction-cornell-notes.tex"], "processes-and-threads": ["ch02-processes-and-threads-cornell-notes.tex"],
    "memory-management": ["ch03-memory-management-cornell-notes.tex"], "file-systems": ["ch04-file-systems-cornell-notes.tex"],
    "input-output": ["ch05-input-output-cornell-notes.tex"], "deadlocks": ["ch06-deadlocks-cornell-notes.tex"],
    "virtualization-and-cloud": ["ch07-virtualization-and-the-cloud-cornell-notes.tex"], "multiple-processor-systems": ["ch08-multiple-processor-systems-cornell-notes.tex"],
    "security": ["ch09-security-cornell-notes.tex"], "case-studies": ["ch10-case-study-1-unix-linux-and-android-cornell-notes.tex", "ch11-case-study-2-windows-8-cornell-notes.tex"],
    "operating-system-design": ["ch12-operating-system-design-cornell-notes.tex"], "reference-material": ["ch13-reading-list-and-bibliography-cornell-notes.tex"],
}

EXPECTED_TITLES = {
    "ch01-preliminaries-notes.tex": "Chapter 1: Preliminaries",
    "ch02-linear-equations-notes.tex": "Chapter 2: Solution of Linear Algebraic Equations",
    "ch03-interpolation-notes.tex": "Chapter 3: Interpolation and Extrapolation",
    "ch04-integration-notes.tex": "Chapter 4: Integration of Functions",
    "ch05-function-evaluation-notes.tex": "Chapter 5: Evaluation of Functions",
    "ch06-special-functions-notes.tex": "Chapter 6: Special Functions",
    "ch07-random-numbers-notes.tex": "Chapter 7: Random Numbers",
    "ch08-sorting-selection-notes.tex": "Chapter 8: Sorting and Selection",
    "ch09-root-finding-notes.tex": "Chapter 9: Root Finding and Nonlinear Sets of Equations",
    "ch10-optimization-notes.tex": "Chapter 10: Minimization or Maximization of Functions",
    "ch11-eigensystems-notes.tex": "Chapter 11: Eigensystems",
    "ch12-fft-notes.tex": "Chapter 12: Fast Fourier Transform",
    "ch13-spectral-applications-notes.tex": "Chapter 13: Fourier and Spectral Applications",
    "ch14-statistical-description-notes.tex": "Chapter 14: Statistical Description of Data",
    "ch15-data-modeling-notes.tex": "Chapter 15: Modeling of Data",
    "ch16-classification-inference-notes.tex": "Chapter 16: Classification and Inference",
    "ch17-ordinary-differential-equations-notes.tex": "Chapter 17: Integration of Ordinary Differential Equations",
    "ch18-boundary-value-problems-notes.tex": "Chapter 18: Two-Point Boundary Value Problems",
    "ch19-integral-equations-notes.tex": "Chapter 19: Integral Equations and Inverse Theory",
    "ch20-partial-differential-equations-notes.tex": "Chapter 20: Partial Differential Equations",
    "ch21-computational-geometry-notes.tex": "Chapter 21: Computational Geometry",
    "ch22-general-algorithms-notes.tex": "Chapter 22: General Algorithms",
}


class CornellNumericalMethodsCollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.nm_root = cls.repo_root / "src" / "cornell-notes" / "mathematics" / "numerical-methods"

    def _iter_expected_files(self) -> list[Path]:
        files: list[Path] = []
        for topic, names in EXPECTED_NUMERICAL_METHODS.items():
            for name in names:
                files.append(self.nm_root / topic / name)
        return files

    def test_expected_numerical_method_basenames_exist(self) -> None:
        expected = {path.name for path in self._iter_expected_files()}
        found = {path.name for path in self.nm_root.rglob("*.tex")}
        self.assertEqual(expected, found)

    def test_expected_electronics_basenames_exist(self) -> None:
        electronics_root = self.repo_root / "src" / "cornell-notes" / "electronics" / "electronic-circuits"
        expected = {name for names in EXPECTED_ELECTRONICS.values() for name in names}
        found = {path.name for path in electronics_root.rglob("*.tex")}
        self.assertEqual(15, len(found))
        self.assertEqual(expected, found)

    def test_new_computer_science_collections_match_canonical_topics(self) -> None:
        collections = {
            "combinatorial-algorithms": EXPECTED_COMBINATORIAL_ALGORITHMS,
            "computer-networks": EXPECTED_COMPUTER_NETWORKS,
            "operating-systems": EXPECTED_OPERATING_SYSTEMS,
        }
        root = self.repo_root / "src" / "cornell-notes" / "computer-science"
        for collection, expected_topics in collections.items():
            collection_root = root / collection
            expected_paths = {collection_root / topic / name for topic, names in expected_topics.items() for name in names}
            self.assertEqual(expected_paths, set(collection_root.rglob("*.tex")))

    def test_new_computer_science_collections_follow_shared_contract(self) -> None:
        root = self.repo_root / "src" / "cornell-notes" / "computer-science"
        paths = list((root / "combinatorial-algorithms").rglob("*.tex")) + list((root / "computer-networks").rglob("*.tex")) + list((root / "operating-systems").rglob("*.tex"))
        self.assertEqual(52, len(paths))
        for path in paths:
            text = strip_latex_comments(path.read_text(encoding="utf-8", errors="ignore"))
            self.assertIn("\\usepackage{cornell-notes}", text, str(path))
            self.assertEqual(1, text.count("\\documentclass"), str(path))
            self.assertEqual(1, text.count("\\begin{document}"), str(path))
            self.assertEqual(1, text.count("\\end{document}"), str(path))
            self.assertEqual(1, text.count("\\maketitle"), str(path))
            self.assertRegex(text, r"\\title\s*\{[^{}]+\}", str(path))
            self.assertLess(text.index("\\begin{document}"), text.index("\\maketitle"), str(path))
            self.assertNotRegex(path.as_posix(), r"\(\d+\)")
            self.assertNotIn("\\usepackage{listings}", text, str(path))

    def test_same_named_introduction_roots_have_unique_source_relative_outputs(self) -> None:
        cs_root = self.repo_root / "src" / "cornell-notes" / "computer-science"
        network = cs_root / "computer-networks" / "foundations" / "ch01-introduction-cornell-notes.tex"
        operating_systems = cs_root / "operating-systems" / "foundations" / "ch01-introduction-cornell-notes.tex"
        self.assertTrue(network.exists())
        self.assertTrue(operating_systems.exists())
        self.assertNotEqual(network.relative_to(self.repo_root / "src").with_suffix(".pdf"), operating_systems.relative_to(self.repo_root / "src").with_suffix(".pdf"))

    def test_stage_pages_groups_new_computer_science_collections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_dir = Path(temp_dir) / "pdfs"
            site_dir = Path(temp_dir) / "site"
            paths = (
                list((self.repo_root / "src" / "cornell-notes" / "computer-science" / "combinatorial-algorithms").rglob("*.tex"))
                + list((self.repo_root / "src" / "cornell-notes" / "computer-science" / "computer-networks").rglob("*.tex"))
                + list((self.repo_root / "src" / "cornell-notes" / "computer-science" / "operating-systems").rglob("*.tex"))
            )
            for path in paths:
                output = pdf_dir / path.relative_to(self.repo_root / "src").with_suffix(".pdf")
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"%PDF-1.4\n")

            staged = stage_pages_site(pdf_dir, site_dir)
            self.assertEqual(52, len(staged))
            index_text = (site_dir / "index.html").read_text(encoding="utf-8")
            for label in ("Combinatorial Algorithms", "Computer Networks", "Operating Systems"):
                self.assertIn(label, index_text)
            for topic in ("permutations", "graph-algorithms", "polynomial-algorithms", "transport-layer", "deadlocks", "operating-system-design"):
                self.assertIn(topic, index_text)
            self.assertIn("computer-networks/foundations/ch01-introduction-cornell-notes.pdf", index_text)
            self.assertIn("operating-systems/foundations/ch01-introduction-cornell-notes.pdf", index_text)
            self.assertNotRegex(index_text, r"\(\d+\)")

    def test_no_upload_copy_suffixes_in_numerical_method_filenames(self) -> None:
        for path in self._iter_expected_files():
            name = path.name
            self.assertNotRegex(name, r"\(\d+\)")
            self.assertNotRegex(name.lower(), r"copy")

    def test_numerical_method_files_are_under_math_numerical_methods_only(self) -> None:
        for path in self._iter_expected_files():
            rel = path.relative_to(self.repo_root).as_posix()
            self.assertTrue(rel.startswith("src/cornell-notes/mathematics/numerical-methods/"), rel)
            self.assertNotIn("/string-algorithms/", rel)

    def test_numerical_method_files_use_shared_cornell_style(self) -> None:
        for path in self._iter_expected_files():
            text = strip_latex_comments(path.read_text(encoding="utf-8", errors="ignore"))
            self.assertIn("\\usepackage{cornell-notes}", text, str(path))

    def test_numerical_method_title_and_maketitle_contract(self) -> None:
        titles: list[str] = []
        for path in self._iter_expected_files():
            text = strip_latex_comments(path.read_text(encoding="utf-8", errors="ignore"))
            self.assertEqual(1, text.count("\\documentclass"), str(path))
            self.assertEqual(1, text.count("\\begin{document}"), str(path))
            self.assertEqual(1, text.count("\\end{document}"), str(path))
            self.assertRegex(text, r"\\title\s*\{[^{}]+\}", str(path))
            self.assertEqual(1, text.count("\\maketitle"), str(path))
            self.assertLess(text.index("\\begin{document}"), text.index("\\maketitle"), str(path))

            match = re.search(r"\\title\s*\{([^{}]+)\}", text)
            assert match is not None
            title = match.group(1).strip()
            titles.append(title)
            self.assertEqual(EXPECTED_TITLES[path.name], title)

            self.assertIn("\\hypersetup{", text, str(path))
            self.assertIn(f"pdftitle={{{title}}}", text, str(path))

        self.assertEqual(22, len(titles))
        self.assertEqual(22, len(set(titles)))

    def test_numerical_method_docs_do_not_define_local_cornell_layout(self) -> None:
        forbidden_tokens = (
            "\\newcommand{\\CornellEntry}",
            "\\newtcolorbox{sectionsummary}",
            "\\newtcolorbox{warningbox}",
            "\\newtcolorbox{examplebox}",
            "\\newtcolorbox{chapterbox}",
            "\\definecolor{Primary}",
            "\\pagestyle{fancy}",
            "\\usepackage[margin=",
            "\\usepackage{titlesec}",
            "\\usepackage{fancyhdr}",
        )
        for path in self._iter_expected_files():
            text = strip_latex_comments(path.read_text(encoding="utf-8", errors="ignore"))
            for token in forbidden_tokens:
                self.assertNotIn(token, text, f"{path}: {token}")

    def test_root_discovery_includes_all_numerical_methods_once(self) -> None:
        roots = discover_roots(self.repo_root / "src")
        expected_rel = {
            path.relative_to(self.repo_root / "src").as_posix() for path in self._iter_expected_files()
        }
        found_rel = [
            root.relative_to(self.repo_root / "src").as_posix()
            for root in roots
            if "cornell-notes/mathematics/numerical-methods/" in root.relative_to(self.repo_root / "src").as_posix()
        ]
        self.assertEqual(22, len(found_rel))
        self.assertEqual(expected_rel, set(found_rel))

    def test_source_and_expected_pdf_paths_are_unique(self) -> None:
        source_paths = [path.relative_to(self.repo_root).as_posix() for path in self._iter_expected_files()]
        self.assertEqual(len(source_paths), len(set(source_paths)))

        pdf_paths = [
            str(Path("cornell-notes") / "mathematics" / "numerical-methods" / path.relative_to(self.nm_root)).replace(".tex", ".pdf")
            for path in self._iter_expected_files()
        ]
        self.assertEqual(len(pdf_paths), len(set(pdf_paths)))

    def test_stage_pages_generates_numerical_methods_hierarchy_and_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            pdf_dir = temp / "pdfs"
            site_dir = temp / "site"

            expected_rel = []
            for path in self._iter_expected_files():
                rel = Path("cornell-notes") / "mathematics" / "numerical-methods" / path.relative_to(self.nm_root)
                pdf_rel = rel.with_suffix(".pdf")
                out_path = pdf_dir / pdf_rel
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(b"%PDF-1.4\n")
                expected_rel.append(pdf_rel)

            staged = stage_pages_site(pdf_dir, site_dir)
            self.assertEqual(set(expected_rel), set(staged))

            index_text = (site_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("Cornell Notes", index_text)
            self.assertIn("Mathematics", index_text)
            self.assertIn("Numerical Methods", index_text)
            for topic in EXPECTED_NUMERICAL_METHODS:
                self.assertIn(topic, index_text)

            for _, basenames in EXPECTED_NUMERICAL_METHODS.items():
                positions = []
                for name in basenames:
                    needle = name.replace(".tex", "")
                    pos = index_text.find(needle)
                    self.assertNotEqual(-1, pos, needle)
                    positions.append(pos)
                self.assertEqual(sorted(positions), positions)

    def test_centralized_cornell_collection_counts_and_groups(self) -> None:
        cornell_root = self.repo_root / "src" / "cornell-notes"

        cissp = list((cornell_root / "security" / "certifications" / "cissp").glob("*.tex"))
        string_notes = list((cornell_root / "computer-science" / "string-algorithms").rglob("*.tex"))
        numerical = list((cornell_root / "mathematics" / "numerical-methods").rglob("*.tex"))

        self.assertEqual(8, len(cissp))
        self.assertEqual(19, len(string_notes))
        self.assertEqual(15, len(list((cornell_root / "electronics" / "electronic-circuits").rglob("*.tex"))))
        self.assertEqual(22, len(numerical))
        self.assertEqual(30, len(list((cornell_root / "computer-science" / "combinatorial-algorithms").rglob("*.tex"))))
        self.assertEqual(9, len(list((cornell_root / "computer-science" / "computer-networks").rglob("*.tex"))))
        self.assertEqual(13, len(list((cornell_root / "computer-science" / "operating-systems").rglob("*.tex"))))


if __name__ == "__main__":
    unittest.main()


class PagesHierarchyTests(unittest.TestCase):
    """The index hierarchy must come from each PDF's own path, not a collection allowlist."""

    CORNELL = Path("cornell-notes")

    def _stage(self, rel_paths, extra_files=()):
        temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp, ignore_errors=True)
        pdf_dir, site_dir = temp / "pdfs", temp / "site"
        for rel in rel_paths:
            target = pdf_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"%PDF-1.4\n")
        for rel, payload in extra_files:
            target = pdf_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(payload, encoding="utf-8")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        staged = stage_pages_site(pdf_dir, site_dir)
        return staged, (site_dir / "index.html").read_text(encoding="utf-8"), pdf_dir, site_dir

    @staticmethod
    def _repo_collection(*parts) -> list[Path]:
        repo_root = Path(__file__).resolve().parents[1]
        root = repo_root.joinpath("src", "cornell-notes", *parts)
        return [
            Path("cornell-notes").joinpath(*parts, source.relative_to(root)).with_suffix(".pdf")
            for source in sorted(root.rglob("*.tex"))
        ]

    def test_computer_science_collections_render_named_hierarchy(self) -> None:
        rels = (
            self._repo_collection("computer-science", "combinatorial-algorithms")
            + self._repo_collection("computer-science", "computer-networks")
            + self._repo_collection("computer-science", "operating-systems")
        )
        self.assertEqual(52, len(rels))
        _, index, _, _ = self._stage(rels)
        for label in ("Cornell Notes", "Computer Science", "Combinatorial Algorithms", "Computer Networks", "Operating Systems"):
            self.assertIn(f">{label}</h", index)
        for topic in ("Permutations", "Graph Algorithms", "Polynomial Algorithms", "Transport Layer", "Deadlocks", "Operating System Design"):
            self.assertIn(f">{topic}</h", index)

    def test_numerical_methods_and_string_algorithms_render_named_hierarchy(self) -> None:
        numerical = self._repo_collection("mathematics", "numerical-methods")
        strings = self._repo_collection("computer-science", "string-algorithms")
        self.assertEqual(22, len(numerical))
        self.assertEqual(19, len(strings))
        _, index, _, _ = self._stage(numerical + strings)
        for label in ("Mathematics", "Numerical Methods", "Linear Algebra", "Root Finding and Optimization", "String Algorithms"):
            self.assertIn(f">{label}</h", index)
        for topic in ("Computational Genomics", "Exact Matching", "Sequence Alignment", "Suffix Structures"):
            self.assertIn(f">{topic}</h", index)

    def test_no_fallback_grouping_for_structured_paths(self) -> None:
        _, index, _, _ = self._stage(self._repo_collection("computer-science", "string-algorithms"))
        self.assertNotIn("Other Cornell Notes", index)

    def test_documents_are_named_naturally_and_ordered_numerically(self) -> None:
        rels = [
            self.CORNELL / "computer-science/combinatorial-algorithms/permutations/ch07-next-permutation-of-n-letters-notes.pdf",
            self.CORNELL / "computer-science/combinatorial-algorithms/permutations/ch08-random-permutation-of-n-letters-notes.pdf",
            self.CORNELL / "computer-science/combinatorial-algorithms/permutations/ch16-cycle-structure-of-a-permutation-notes.pdf",
        ]
        _, index, _, _ = self._stage(rels)
        self.assertIn("Chapter 7: Next Permutation of N Letters", index)
        self.assertIn("Chapter 16: Cycle Structure of a Permutation", index)
        positions = [index.find(f"ch{n:02d}-") for n in (7, 8, 16)]
        self.assertEqual(sorted(positions), positions)
        self.assertNotIn(-1, positions)

    def test_relative_links_resolve_to_staged_pdfs(self) -> None:
        rels = self._repo_collection("computer-science", "string-algorithms")
        staged, index, _, site_dir = self._stage(rels)
        hrefs = re.findall(r'href="(pdfs/[^"]+)"', index)
        self.assertEqual(len(rels), len(hrefs))
        self.assertEqual(len(hrefs), len(set(hrefs)), "each document needs a unique link")
        for href in hrefs:
            self.assertTrue((site_dir / unquote(href)).is_file(), href)
        self.assertEqual(set(rels), set(staged))

    def test_identical_basenames_in_separate_collections_stay_distinct(self) -> None:
        rels = [
            self.CORNELL / "computer-science/computer-networks/foundations/ch01-introduction-cornell-notes.pdf",
            self.CORNELL / "computer-science/operating-systems/foundations/ch01-introduction-cornell-notes.pdf",
        ]
        _, index, _, _ = self._stage(rels)
        hrefs = re.findall(r'href="(pdfs/[^"]+)"', index)
        self.assertEqual(2, len(set(hrefs)))
        for rel in rels:
            self.assertIn(rel.as_posix(), index)

    def test_heading_ids_are_unique_and_stable(self) -> None:
        rels = self._repo_collection("computer-science", "string-algorithms")
        _, first, _, _ = self._stage(rels)
        _, second, _, _ = self._stage(rels)
        ids = re.findall(r'<h[2-6] id="([^"]+)"', first)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(re.findall(r'<h[2-6] id="([^"]+)"', second), ids)

    def test_output_is_deterministic(self) -> None:
        rels = self._repo_collection("mathematics", "numerical-methods")
        _, first, _, _ = self._stage(rels)
        _, second, _, _ = self._stage(rels)
        self.assertEqual(first, second)

    def test_html_is_escaped(self) -> None:
        rels = [self.CORNELL / 'weird <dir> & "quotes"' / "ch01-a-&-b-notes.pdf"]
        _, index, _, _ = self._stage(rels)
        self.assertNotIn("<dir>", index)
        self.assertIn("&lt;dir&gt;", index)
        self.assertIn("&amp;", index)

    def test_non_pdf_files_are_ignored(self) -> None:
        rels = self._repo_collection("computer-science", "string-algorithms")
        staged, index, _, _ = self._stage(rels, extra_files=((Path("notes.txt"), "ignored"),))
        self.assertEqual(len(rels), len(staged))
        self.assertNotIn("notes.txt", index)

    def test_empty_corpus_renders_without_documents(self) -> None:
        staged, index, _, _ = self._stage([])
        self.assertEqual([], staged)
        self.assertIn("No PDFs are currently staged for publication.", index)
        self.assertNotIn("Other Cornell Notes", index)

    def test_no_upload_copy_suffixes_are_published(self) -> None:
        _, index, _, _ = self._stage(self._repo_collection("computer-science", "string-algorithms"))
        self.assertNotRegex(index, r"\(\d+\)\.pdf")
        self.assertNotIn("-copy.pdf", index)


class PagesHumanizationTests(unittest.TestCase):
    def test_acronyms_and_minor_words(self) -> None:
        self.assertEqual("Computer Science", latex_build._humanize_segment("computer-science"))
        self.assertEqual("Root Finding and Optimization", latex_build._humanize_segment("root-finding-and-optimization"))
        self.assertEqual("C++ 2024", latex_build._humanize_segment("cpp-2024"))
        self.assertEqual("CISSP", latex_build._humanize_segment("cissp"))
        self.assertEqual("ISO IEC IEEE 42010 2022", latex_build._humanize_segment("iso-iec-ieee-42010-2022"))

    def test_document_labels(self) -> None:
        self.assertEqual("Chapter 7: Next Permutation of N Letters", latex_build._document_label("ch07-next-permutation-of-n-letters-notes"))
        self.assertEqual("Chapter 1: Introduction", latex_build._document_label("ch01-introduction-cornell-notes"))
        self.assertEqual("Annex A: Scope", latex_build._document_label("annex-a-scope-notes"))

    def test_natural_key_orders_numbers_numerically(self) -> None:
        names = ["ch10-x", "ch2-x", "ch1-x"]
        self.assertEqual(["ch1-x", "ch2-x", "ch10-x"], sorted(names, key=latex_build._natural_key))
