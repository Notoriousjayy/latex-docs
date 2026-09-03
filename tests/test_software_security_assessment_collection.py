import re
import unittest
from pathlib import Path

from tooling.scripts.migrate_software_security_assessment import RANGES, SECTIONS, TITLES
from tooling.scripts.style_migration import classify_latex_style, filename_policy_violations


ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "src/cornell-notes/security/application-security/software-security-assessment"
EXPECTED_GROUPS = {
    **{n: "assessment-foundations" for n in range(1, 5)},
    **{n: "implementation-security" for n in range(5, 9)},
    **{n: "platform-security" for n in range(9, 14)},
    **{n: "network-and-web-security" for n in range(14, 19)},
}
EXPECTED_NAMES = {
    1: "01-vulnerability-fundamentals-cornell-notes.tex", 2: "02-design-review-cornell-notes.tex",
    3: "03-operational-review-cornell-notes.tex", 4: "04-application-review-process-cornell-notes.tex",
    5: "05-memory-corruption-cornell-notes.tex", 6: "06-c-language-issues-cornell-notes.tex",
    7: "07-program-building-blocks-cornell-notes.tex", 8: "08-strings-metacharacters-cornell-notes.tex",
    9: "09-unix-privileges-files-cornell-notes.tex", 10: "10-unix-processes-cornell-notes.tex",
    11: "11-windows-objects-filesystem-cornell-notes.tex", 12: "12-windows-ipc-cornell-notes.tex",
    13: "13-synchronization-state-cornell-notes.tex", 14: "14-network-protocols-cornell-notes.tex",
    15: "15-firewalls-cornell-notes.tex", 16: "16-network-app-protocols-cornell-notes.tex",
    17: "17-web-applications-cornell-notes.tex", 18: "18-web-technologies-cornell-notes.tex",
}


class SoftwareSecurityAssessmentCollectionTests(unittest.TestCase):
    def test_collection_contract_and_source_counts(self) -> None:
        paths = sorted(COLLECTION.rglob("*.tex"))
        self.assertEqual(18, len(paths))
        numbers = []
        for path in paths:
            number = int(path.name[:2])
            numbers.append(number)
            text = path.read_text(encoding="utf-8")
            self.assertEqual(EXPECTED_GROUPS[number], path.parent.name)
            self.assertEqual(EXPECTED_NAMES[number], path.name)
            self.assertEqual([], filename_policy_violations(path))
            self.assertEqual("cornell-notes", classify_latex_style(path))
            packages = re.findall(r"\\usepackage(?:\[[^]]*\])?\{([^}]+)\}", text)
            self.assertEqual(["cornell-notes"], [package for package in packages if package in {"base", "cornell-notes", "technical-design-spec", "technical-implementation"}])
            self.assertRegex(text, rf"\\title\{{Chapter {number}: {re.escape(TITLES[number])}\}}")
            self.assertEqual(1, len(re.findall(r"\\maketitle\b", text)))
            self.assertNotRegex(text, r"\\(?:makecornelltitle|CornellMakeTitle)|\\begin\{titlepage\}|listings|\\lst")
            self.assertIn(f"Coverage range:}} {RANGES[number]}", text)
            self.assertEqual(SECTIONS, re.findall(r"^\\section\{([^}]*)\}", text, re.MULTILINE))
            self.assertIn(r"\subsection*{Answer Key}", text)
            self.assertGreaterEqual(len(re.findall(r"^\\term\{", text, re.MULTILINE)), 1)
            self.assertGreaterEqual(len(re.findall(r"^\\checkbox\s+|^\\item ", text, re.MULTILINE)), 1)
        self.assertEqual(list(range(1, 19)), sorted(numbers))


if __name__ == "__main__":
    unittest.main()