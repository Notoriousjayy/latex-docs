import re
import tempfile
import unittest
from pathlib import Path

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
        all_roots = sorted(cornell_root.rglob("*.tex"))
        self.assertEqual(64, len(all_roots))

        cissp = list((cornell_root / "security" / "certifications" / "cissp").glob("*.tex"))
        string_notes = list((cornell_root / "computer-science" / "string-algorithms").rglob("*.tex"))
        numerical = list((cornell_root / "mathematics" / "numerical-methods").rglob("*.tex"))

        self.assertEqual(8, len(cissp))
        self.assertEqual(19, len(string_notes))
        self.assertEqual(15, len(list((cornell_root / "electronics" / "electronic-circuits").rglob("*.tex"))))
        self.assertEqual(22, len(numerical))


if __name__ == "__main__":
    unittest.main()
