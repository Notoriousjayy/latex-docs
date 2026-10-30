#!/usr/bin/env python3
"""Validate section coverage, local LaTeX inputs and independent blank/pair contracts.
Run: python3 qa/validate_suite.py
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PAIRS = json.loads((ROOT / "references/template-blank-pairs.json").read_text())["pairs"]
PREFIX = Path("src/business-analysis/parliamentary-procedure-and-governance")
assert len(PAIRS) == 31, "Unexpected pair count"
assert len({(p["artifact_family"], p["artifact_id"]) for p in PAIRS}) == len(PAIRS), "Duplicate pair IDs"

guides = list((ROOT / "study-guides").glob("section-*.tex"))
assert len(guides) == 63, "Expected 63 original study guides"
assert {int(p.name.split("-")[1]) for p in guides} == set(range(1, 64)), "Missing/duplicate study guide"

for item in PAIRS:
    for key in ("template", "blank"):
        path = ROOT / Path(item[key]).relative_to(PREFIX)
        assert path.is_file(), str(path)
        content = path.read_text(encoding="utf-8")
        assert "\\documentclass" in content, str(path)
    blank = ROOT / Path(item["blank"]).relative_to(PREFIX)
    content = blank.read_text(encoding="utf-8")
    assert "\\Field{" in content or "\\GovCheckbox" in content, str(blank)
    assert not re.search(r"\[(?:To complete|Insert|Enter|Placeholder|Example)[^\]]*\]", content, re.I), str(blank)
    assert "Illustrative entry" not in content and "fictional example" not in content.lower(), str(blank)

roots = 0
for path in ROOT.rglob("*.tex"):
    content = path.read_text(encoding="utf-8")
    if "\\documentclass" not in content:
        continue
    roots += 1
    match = re.search(r"\\input\{([^}]+)\}", content)
    assert match, str(path)
    assert (path.parent / match.group(1)).is_file(), (str(path), match.group(1))
assert roots == 166, f"Expected 166 independent roots; observed {roots}"
print(f"PASS: {len(guides)} section guides, {len(PAIRS)} pairs, {roots} LaTeX document roots")
