import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "src/cornell-notes/programming/languages/cpp/cpp-2024"
MANIFEST = ROOT / "tooling/manifests/cpp-2024-top-level-intake.json"


class CppTopLevelCollectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_collection_has_exactly_33_canonical_clause_roots(self) -> None:
        roots = sorted(COLLECTION.glob("clauses/*/*.tex"))
        self.assertEqual(33, len(roots))
        self.assertEqual(list(range(1, 34)), [int(path.name[:2]) for path in roots])

    def test_documents_use_opt_in_profile_and_title_contract(self) -> None:
        for path in sorted(COLLECTION.glob("clauses/*/*.tex")):
            text = path.read_text(encoding="utf-8")
            self.assertIn(r"\usepackage[technical-reference]{cornell-notes}", text)
            self.assertEqual(1, len(re.findall(r"^\\documentclass", text, re.M)))
            self.assertEqual(1, text.count(r"\begin{document}"))
            self.assertEqual(1, text.count(r"\end{document}"))
            self.assertEqual(1, len(re.findall(r"^\\title\{[^{}]+\}", text, re.M)))
            self.assertEqual(1, len(re.findall(r"^\\author\{", text, re.M)))
            self.assertEqual(1, len(re.findall(r"^\\date\{", text, re.M)))
            self.assertEqual(1, text.count(r"\maketitle"))
            self.assertNotRegex(text, r"\\usepackage(?:\[[^]]*\])?\{(?:style|base)\}")
            self.assertNotRegex(text, r"\\(?:usepackage\{listings\}|lst(?:set|def|inline|inputlisting)|begin\{lstlisting\})")
            self.assertNotIn(r"\begin{titlepage}", text)
            self.assertNotIn(r"\makecornelltitle", text)

    def test_manifest_hashes_and_transformed_paths_are_consistent(self) -> None:
        self.assertEqual("cpp-2024-top-level", self.data["collection"])
        self.assertEqual(33, self.data["expected_records"])
        self.assertEqual(33, len(self.data["records"]))
        for record in self.data["records"]:
            target = ROOT / record["canonical_destination"]
            self.assertTrue(target.exists(), target)
            self.assertEqual(record["transformed_sha256"], hashlib.sha256(target.read_bytes()).hexdigest())
            self.assertNotRegex(record["canonical_filename"], r"[() ]")
            self.assertEqual(record["status"], "source_removed")
            self.assertEqual(record["source_counts"], record["transformed_counts"])


if __name__ == "__main__":
    unittest.main()