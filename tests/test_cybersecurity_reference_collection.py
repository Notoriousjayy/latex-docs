"""Regression contract for the cybersecurity Cornell-notes collection."""

import json
import re
import unittest
from pathlib import Path

from tooling.scripts.latex_build import discover_roots
from tooling.scripts.style_migration import filename_policy_violations


REPO_ROOT = Path(__file__).resolve().parents[1]
COLLECTION = REPO_ROOT / "src/cornell-notes/security/cybersecurity-reference"
MANIFEST_PATH = REPO_ROOT / "tooling/manifests/cybersecurity-reference-intake.json"
GROUP_RANGES = {
    "foundations-and-core-defense": range(1, 11),
    "platform-network-and-iot": range(11, 24),
    "governance-risk-and-resilience": range(24, 41),
    "forensics-and-incident-response": range(41, 47),
    "cryptography-identity-and-privacy": range(47, 59),
    "network-cloud-and-virtualization": range(59, 71),
    "physical-operational-and-assurance": range(71, 84),
    "critical-infrastructure-and-emerging-threats": range(84, 105),
}
REQUIRED_SECTIONS = (
    "Learning Objectives",
    "Cornell Cue-and-Notes",
    "Threat-and-Control Map",
    "Practical Security Checklist",
    "Self-Test Questions",
    "Answer Key",
    "Key-Term Recap",
)
CALLOUT_LABELS = (
    "Chapter Orientation",
    "Topic Summary",
    "Defensive Guidance",
    "Historical Context",
    "Chapter Synthesis",
    "One-Sentence Takeaway",
)


def chapter_number(path: Path) -> int:
    return int(re.match(r"ch(\d+)-", path.name).group(1))


class CybersecurityReferenceCollectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text())
        cls.entries = cls.manifest["chapters"]
        cls.tex_files = sorted(COLLECTION.rglob("*.tex"))

    def test_manifest_and_filesystem_agree_exactly(self):
        manifest_paths = {(e["topical_group"], e["canonical_filename"]) for e in self.entries}
        filesystem_paths = {(p.parent.name, p.name) for p in self.tex_files}
        self.assertEqual(manifest_paths, filesystem_paths)
        self.assertEqual({chapter_number(p) for p in self.tex_files}, set(range(1, 105)))
        self.assertEqual(len(self.tex_files), 104)

    def test_manifest_entries_resolve_once_and_no_orphans_exist(self):
        for entry in self.entries:
            expected = COLLECTION / entry["topical_group"] / entry["canonical_filename"]
            self.assertEqual(list(expected.parent.glob(expected.name)), [expected])

    def test_all_topical_groups_have_exact_ranges(self):
        self.assertEqual(set(GROUP_RANGES), {p.name for p in COLLECTION.iterdir() if p.is_dir()})
        for group, expected in GROUP_RANGES.items():
            actual = {chapter_number(p) for p in (COLLECTION / group).glob("*.tex")}
            self.assertEqual(actual, set(expected), group)

    def test_filenames_follow_real_repository_policy(self):
        for path in self.tex_files:
            self.assertEqual(filename_policy_violations(path), [], path)
            self.assertRegex(path.name, r"^ch\d{2,3}-[a-z0-9]+(?:-[a-z0-9]+)*-cornell-notes\.tex$")
            self.assertNotIn("--", path.name)
            self.assertNotRegex(path.name, r"-(?:i|orga|authent|and)-cornell-notes")

    def test_every_root_is_discovered_and_staged_paths_are_unique(self):
        roots = {p.relative_to(REPO_ROOT / "src") for p in discover_roots(REPO_ROOT / "src")}
        expected = {p.relative_to(REPO_ROOT / "src") for p in self.tex_files}
        self.assertTrue(expected <= roots)
        staged = {
            (Path("cornell-notes") / p.relative_to(REPO_ROOT / "src/cornell-notes")).with_suffix(".pdf")
            for p in self.tex_files
        }
        self.assertEqual(len(staged), 104)
        self.assertTrue(all(p.parts[:3] == ("cornell-notes", "security", "cybersecurity-reference") for p in staged))

    def test_every_document_is_a_standalone_public_cornell_root(self):
        for path in self.tex_files:
            text = path.read_text()
            self.assertRegex(text, r"(?m)^\\documentclass\[11pt,letterpaper\]\{article\}")
            self.assertEqual(len(re.findall(r"\\usepackage(?:\[[^]]*\])?\{cornell-notes\}", text)), 1, path)
            self.assertNotRegex(text, r"\\usepackage(?:\[[^]]*\])?\{(?:style|base)\}")
            self.assertNotRegex(text, r"\\usepackage\{(?:listings|minted)\}|\\lst[a-zA-Z]*")
            self.assertRegex(text, r"(?m)^\\title\{\\CornellDocumentTitle\}$")
            self.assertRegex(text, r"(?m)^\\author\{\}$")
            self.assertRegex(text, r"(?m)^\\date\{\}$")
            self.assertEqual(len(re.findall(r"\\maketitle", text)), 1)
            document_end = text.index(r"\begin{document}") + len(r"\begin{document}")
            self.assertEqual(text[document_end:].lstrip().find(r"\maketitle"), 0)
            self.assertNotRegex(text, r"makecornelltitle|CornellMakeTitle|titlepage")

    def test_every_document_uses_public_semantic_structures(self):
        for path in self.tex_files:
            text = path.read_text()
            self.assertNotIn(r"\CornellHeader", text)
            self.assertNotRegex(text, r"orientationbox|topicsummary|defensebox|historybox|synthesisbox|takeawaybox")
            self.assertNotRegex(text, r"\\definecolor|\\colorlet|\\newcommand\{\\(?:Navy|Teal|CueGray)")
            self.assertGreaterEqual(text.count(r"\begin{CornellNotesTable}"), 1)
            self.assertEqual(text.count(r"\begin{CornellNotesTable}"), text.count(r"\end{CornellNotesTable}"))
            self.assertEqual(text.count(r"\begin{CornellChecklist}"), 1)
            self.assertEqual(text.count(r"\begin{CornellRecallList}"), 1)
            self.assertGreater(text.count(r"\CornellNoteRow{"), 0)
            for label in CALLOUT_LABELS:
                self.assertIn(label, text, path)

    def test_required_sections_are_ordered_and_question_keys_match(self):
        for path in self.tex_files:
            text = path.read_text()
            positions = [text.index(r"\section*{" + section + "}") for section in REQUIRED_SECTIONS]
            self.assertEqual(positions, sorted(positions), path)
            questions = text.split(r"\section*{Self-Test Questions}", 1)[1].split(r"\section*{Answer Key}", 1)[0]
            answers = text.split(r"\section*{Answer Key}", 1)[1].split(r"\section*{Key-Term Recap}", 1)[0]
            self.assertGreaterEqual(questions.count(r"\item"), 1, path)
            self.assertEqual(questions.count(r"\item"), answers.count(r"\item"), path)

    def test_manifest_metadata_and_chapter_16(self):
        self.assertEqual(self.manifest["metadata"]["chapter_count"], 104)
        self.assertEqual(self.manifest["metadata"]["missing_chapters"], [])
        chapter16 = next(e for e in self.entries if e["chapter_number"] == 16)
        self.assertEqual(chapter16["canonical_filename"], "ch16-local-area-network-security-cornell-notes.tex")
        self.assertEqual(chapter16["topical_group"], "platform-network-and-iot")


if __name__ == "__main__":
    unittest.main()