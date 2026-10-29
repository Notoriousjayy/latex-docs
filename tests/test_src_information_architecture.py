"""Regression gates for the source-first information architecture."""
from pathlib import Path
from urllib.parse import unquote
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

MOVED_TEX = {
    "src/templates/architecture/42010-ad-template-polished.tex": "src/architecture/templates/42010-ad-template-polished.tex",
    "src/templates/architecture/42010-vp-template-polished.tex": "src/architecture/templates/42010-vp-template-polished.tex",
    "src/templates/architecture/viewpoint-section.tex": "src/architecture/templates/viewpoint-section.tex",
    "src/templates/architecture/viewpoint-template-polished.tex": "src/architecture/templates/viewpoint-template-polished.tex",
    "src/architecture/examples/shems/shems-architecture-description.tex": "src/architecture/examples/shems-architecture-description.tex",
    "src/data-systems/streaming/kafka/how-write-effective-user-stories-quick-guide.tex": "src/data-systems/workbooks/kafka-study-plan-user-stories.tex",
    "src/security/infrastructure-security/vulnerability-management/trivy/trivy-scope-and-objectives.tex": "src/security/technical-documents/trivy-scope-and-objectives.tex",
    "src/startups/curricula/quality/minimum-checklist.tex": "src/startups/workbooks/minimum-curriculum-quality-checklist.tex",
    "src/startups/support/sba/top-3-nearby-options.tex": "src/startups/technical-documents/sba-local-assistance-intake.tex",
}


class SourceArchitectureTests(unittest.TestCase):
    def test_each_domain_has_one_canonical_readme(self):
        self.assertTrue((SRC / "README.md").is_file())
        self.assertFalse((SRC / "readme.md").exists())
        for domain in (p for p in SRC.iterdir() if p.is_dir()):
            with self.subTest(domain=domain.name):
                self.assertTrue((domain / "README.md").is_file())
                self.assertFalse((domain / "readme.md").exists())

    def test_top_level_readmes_have_navigation_contract(self):
        headings = [
            "## Overview",
            "## Scope and boundaries",
            "## Directory map and documentation catalog",
            "## Recommended navigation",
            "## Build and validate",
            "## Maintenance conventions",
            "## Related domains",
        ]
        for document in sorted(SRC.glob("*/README.md")):
            source = document.read_text(encoding="utf-8")
            for heading in headings:
                with self.subTest(document=str(document), heading=heading):
                    self.assertIn(heading, source)

    def test_top_level_local_links_resolve(self):
        # Only validate the scope owned by this change; nested historical
        # collections can have unrelated pre-existing references.
        readmes = [SRC / "README.md", *sorted(SRC.glob("*/README.md")),
                   SRC / "architecture" / "templates" / "README.md"]
        for document in readmes:
            content = document.read_text(encoding="utf-8")
            for match in re.finditer(r"\]\(([^)\n]+)\)", content):
                target = match.group(1).split("#", 1)[0].split("?", 1)[0]
                if not target or target.startswith("/") or re.match(r"[a-z][a-z0-9+.-]*:", target, re.I):
                    continue
                resolved = (document.parent / unquote(target)).resolve()
                with self.subTest(document=str(document), target=target):
                    self.assertTrue(resolved.is_relative_to(ROOT), "reference escapes repository")
                    self.assertTrue(resolved.exists(), "missing local Markdown target")

    def test_all_selected_tex_roots_moved_without_duplicates(self):
        for old, new in MOVED_TEX.items():
            with self.subTest(destination=new):
                self.assertFalse((ROOT / old).exists())
                self.assertTrue((ROOT / new).is_file())

    def test_architecture_template_distinction(self):
        index = (SRC / "architecture" / "templates" / "README.md").read_text(encoding="utf-8")
        self.assertIn("architecture decision record (ADR)", index)
        self.assertIn("Non-standalone", index)

    def test_recorded_migration_crosswalk_exists(self):
        report = ROOT / "tooling" / "reports" / "src-information-architecture-2026-10-29" / "migration-crosswalk.csv"
        self.assertTrue(report.is_file())


if __name__ == "__main__":
    unittest.main()
