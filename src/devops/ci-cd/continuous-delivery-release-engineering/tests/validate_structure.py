"""Validate release engineering suite structure and printed blank-form rules."""
from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
for group in ("study-guides", "curriculum", "technical-documents", "laboratories", "workbooks", "templates", "scorecards", "diagrams", "examples"):
    assert (root / group / "README.md").exists(), f"Missing group README: {group}"
for group in ("templates", "workbooks", "scorecards"):
    templates = sorted((root / group).glob("*-template.tex"))
    blanks = sorted((root / group).glob("*-blank.tex"))
    assert len(templates) == len(blanks) and templates, f"Bad pairs in {group}"
    for template in templates:
        blank = template.with_name(template.name.replace("-template.tex", "-blank.tex"))
        assert blank.exists(), f"Missing {blank}"
        content = blank.read_text(encoding="utf-8")
        assert "Example entry:" not in content and "Illustrative completed" not in content, blank
        assert not re.search(r"\[(?:To complete|insert|placeholder|example|TBD)\]", content, re.I), blank
all_tex = list(root.rglob("*.tex"))
assert len(list((root / "study-guides").glob("chapter-*.tex"))) == 15
assert len(list((root / "laboratories").glob("lab-*.tex"))) == 12
for file in all_tex:
    assert "\\documentclass" in file.read_text(encoding="utf-8"), f"Not standalone: {file}"
print(f"PASS: {len(all_tex)} standalone LaTeX files; all paired forms and indexes present")
