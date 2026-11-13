"""Validate the native syntax-diagram migration without a React/Node runtime."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tooling.scripts.generate_syntax_references import COLLECTION, EXPECTED, render, validate, printable
from tooling.scripts import latex_build


class SyntaxDiagramCollectionTests(unittest.TestCase):
    def test_source_inventory_and_reproducible_latex(self) -> None:
        total = 0
        for language, (text_count, factory_count, section_count) in EXPECTED.items():
            with self.subTest(language=language):
                data = json.loads((COLLECTION / "data" / f"{language}.json").read_text(encoding="utf-8"))
                validate(data)
                self.assertEqual(text_count, len(data["rules"]))
                self.assertEqual(factory_count, data["sourceFactoryCount"])
                self.assertEqual(section_count, len(data["sections"]))
                self.assertEqual(
                    render(data),
                    (COLLECTION / "generated" / f"{language}-rules.tex").read_text(encoding="utf-8")
                )
                self.assertTrue((COLLECTION / "data/upstream" / f"{language}-factory-source.txt").is_file())
                self.assertEqual(data["language"], language)
                names = [rule["name"] for rule in data["rules"]]
                self.assertEqual(len(names), len(set(names)))
                total += len(names)
        self.assertEqual(total, 1166)

    def test_known_upstream_mismatches_are_not_erased(self) -> None:
        c23 = json.loads((COLLECTION / "data/c23.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(c23["missingSourceFactories"]),
            {"argument-expression-list", "compound-literal"},
        )
        java = json.loads((COLLECTION / "data/java-25.json").read_text(encoding="utf-8"))
        self.assertIn("java21-syntax-diagrams", java["sourceRepository"])

    def test_native_ebnf_sources_have_expected_render_locations(self) -> None:
        for language in EXPECTED:
            with self.subTest(language=language):
                source = COLLECTION / "railroad-samples" / f"{language}.puml"
                self.assertTrue(source.exists())
                text = source.read_text(encoding="utf-8")
                self.assertIn("@startebnf", text)
                self.assertIn("@endebnf", text)
                self.assertEqual(
                    latex_build.plantuml_output_paths(source, "png", text),
                    [source.parent / "png" / f"{language}.png"],
                )
                self.assertTrue((COLLECTION / f"{language}-syntax-reference.tex").exists())

    def test_printable_unicode_fallback(self) -> None:
        self.assertEqual(printable("a \N{NOT EQUAL TO} b"), "a [U+2260] b")
        self.assertEqual(printable("ASCII_123"), "ASCII_123")

    def test_no_web_application_is_migrated(self) -> None:
        self.assertFalse((COLLECTION.parents[3] / "tooling/web/syntax-diagrams").exists())


if __name__ == "__main__":
    unittest.main()
