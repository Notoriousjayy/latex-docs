"""No React: test deterministic generation of native PlantUML EBNF sources."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tooling.scripts.generate_railroad_ebnf import (
    LANGUAGES, build_rule, generate, grammar_parts, source_data, COLLECTION,
)


class RailroadConversionTests(unittest.TestCase):
    def test_generate_complete_inventory_in_check_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            result = generate(Path(temp), check_only=True)
            self.assertEqual(result["total"], 1166)
            self.assertEqual(sum(item["count"] for item in result["languages"].values()), 1166)
            self.assertGreaterEqual(result["modes"].get("factory-derived", 0), 500)

    def test_emitted_samples_use_native_ebnf_without_web_app(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = generate(root, limit_per_language=2)
            self.assertEqual(result["total"], 10)
            sources = list(root.rglob("*.puml"))
            self.assertEqual(len(sources), 10)
            for file in sources:
                body = file.read_text(encoding="utf-8")
                self.assertTrue(body.startswith("@startebnf\n"))
                self.assertIn("@endebnf\n", body)
                self.assertIn(" = ", body)
                self.assertFalse((root / "index.html").exists())

    def test_factory_derivation_preserves_visible_alternatives(self):
        body = '() => Diagram(Choice(0, T("return"), NT("expression")));'
        text, mode = build_rule("test", "sample", body)
        self.assertEqual(mode, "factory-derived")
        self.assertIn('"return" | expression', text)

    def test_unsupported_rules_do_not_invent_grammar_equivalence(self):
        text, mode = build_rule("c23", "compound-literal", None)
        self.assertEqual(mode, "text-only")
        self.assertIn("See complete source production below", text)

    def test_all_archived_factory_counts_match_snapshots(self):
        for language, _ in LANGUAGES:
            with self.subTest(language=language):
                data = source_data(language)
                module = COLLECTION / "data/upstream" / (language + "-factory-source.txt")
                factories = grammar_parts(module.read_text(encoding="utf-8"))
                self.assertEqual(len(factories), data["sourceFactoryCount"])


if __name__ == "__main__":
    unittest.main()
