"""Governed LaTeX template/blank variant checks."""
import json
import unittest
from pathlib import Path

from tooling.scripts.validate_artifact_pairs import (
    bracket_rendering_macros, printable_bracket_prompts, validate,
)

ROOT = Path(__file__).resolve().parents[1]


class ReusableArtifactPairTests(unittest.TestCase):
    def test_registered_pairs_are_structurally_valid(self):
        self.assertEqual([], validate())

    def test_architecture_description_and_decision_records_are_distinct(self):
        data = json.loads(
            (ROOT / "tooling/manifests/reusable-artifact-pairs.json").read_text(encoding="utf-8")
        )
        families = {record["family"] for record in data["pairs"]}
        self.assertIn("architecture-description", families)
        self.assertIn("architecture-decision-record", families)
        self.assertEqual(len(data["pairs"]), len({r["id"] for r in data["pairs"]}))

    def test_completed_startup_example_is_preserved(self):
        original = ROOT / "src/startups/templates/startup-plan-template-worksheet.tex"
        self.assertIn("Smart Building Manager", original.read_text(encoding="utf-8"))


    def test_startup_blank_keeps_latex_options_and_checkbox_semantics(self):
        template = (ROOT / "src/startups/templates/startup-plan-template.tex").read_text(encoding="utf-8")
        blank = (ROOT / "src/startups/templates/startup-plan-blank.tex").read_text(encoding="utf-8")
        # Replacing *all* square-bracket groups damages package options and enumitem.
        for original in (
            r"\usepackage[letterpaper,margin=0.45in]{geometry}",
            r"\setlist[enumerate]{leftmargin=1.5em,itemsep=1pt,topsep=2pt,parsep=0pt,partopsep=0pt}",
            r"\newcommand{\checkitem}[1]{\item[$\square$] #1}",
        ):
            self.assertIn(original, template)
            self.assertIn(original, blank)
        self.assertNotIn(r"\usepackage[To complete]", blank)
        self.assertNotIn(r"\setlist[To complete]", blank)

    def test_letterhead_blank_avoids_bracketed_optional_spacing(self):
        blank = (ROOT / "src/documentation/templates/letterhead-blank.tex").read_text(
            encoding="utf-8"
        )
        self.assertIn(r"\newcommand{\BlankField}[1]{\rule{1.15in}{0.4pt}}", blank)
        self.assertIn(r"\opening{Dear \BlankField{Recipient name},}", blank)
        self.assertIn(r"\signature{\vspace{1.2em}\BlankField{Sender name}", blank)
        self.assertIn(r"\begin{letter}{\BlankField{Recipient name}", blank)
        live_tex = "\n".join(
            line for line in blank.splitlines() if not line.lstrip().startswith("%")
        )
        self.assertNotIn(r"\\[Recipient", live_tex)
        self.assertNotIn(r"\\[Sender", live_tex)


    def test_every_printable_blank_has_no_bracketed_words(self):
        data = json.loads(
            (ROOT / "tooling/manifests/reusable-artifact-pairs.json").read_text(encoding="utf-8")
        )
        for pair in data["pairs"]:
            source = (ROOT / pair["blank"]).read_text(encoding="utf-8")
            with self.subTest(artifact=pair["id"]):
                self.assertEqual([], printable_bracket_prompts(source))
                self.assertEqual([], bracket_rendering_macros(source))
                self.assertNotIn("[To complete]", source)
                self.assertNotIn("[TODO]", source)

    def test_placeholder_detector_distinguishes_tex_options_from_printed_text(self):
        options = r"""
\documentclass[11pt]{article}
\begin{document}
\begin{description}[leftmargin=3cm]
\item[Decision title:] \rule[-0.4em]{0pt}{2em}
\end{description}
\end{document}
"""
        self.assertEqual([], printable_bracket_prompts(options))
        example = r"\begin{document}" + "\n" + r"\textit{[To complete]}" + "\n"
        self.assertEqual(["[To complete]"], printable_bracket_prompts(example))
        generated = r"\newcommand{\placeholder}[1]{\textit{[#1]}}"
        self.assertTrue(bracket_rendering_macros(generated))


if __name__ == "__main__":
    unittest.main()
