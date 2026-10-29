#!/usr/bin/env python3
"""Structural governance checks for paired reusable LaTeX artifacts.

The validator does not establish semantic completeness or compile LaTeX PDFs.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tooling/manifests/reusable-artifact-pairs.json"
HEADING = re.compile(r"\\(?:section|subsection|subsubsection)\*?\{([^}]+)\}")


def validate(root: Path = ROOT, manifest_path: Path = MANIFEST) -> list[str]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues: list[str] = []
    registered: dict[str, str] = {}
    identifiers: set[str] = set()

    for artifact in data["pairs"]:
        artifact_id = artifact["id"]
        if artifact_id in identifiers:
            issues.append(f"Duplicate logical artifact ID: {artifact_id}")
        identifiers.add(artifact_id)
        contents: dict[str, str] = {}

        for variant in ("template", "blank"):
            rel = artifact[variant]
            path = root / rel
            if rel in registered:
                issues.append(f"Variant is registered more than once: {rel}")
            registered[rel] = artifact_id
            if not path.is_file():
                issues.append(f"{artifact_id}: missing {variant}: {rel}")
                continue
            contents[variant] = path.read_text(encoding="utf-8")
            if (r"\documentclass" not in contents[variant]
                    or r"\end{document}" not in contents[variant]):
                issues.append(f"{artifact_id}: expected standalone LaTeX root: {rel}")

        if len(contents) == 2:
            if contents["template"] == contents["blank"]:
                issues.append(f"{artifact_id}: Blank is identical to Template")
            if HEADING.findall(contents["template"]) != HEADING.findall(contents["blank"]):
                issues.append(f"{artifact_id}: sections/subsections are out of sync")
            if artifact["family"] == "architecture-decision-record":
                if r"\DocStatus}{Blank}" not in contents["blank"]:
                    issues.append(f"{artifact_id}: Blank has incorrect document status")
                if r"\emph{[To complete]}" not in contents["blank"]:
                    issues.append(f"{artifact_id}: Blank has no unfilled response fields")

        leaf = (root / artifact["blank"]).parent
        if not any((leaf / name).exists() for name in ("README.md", "readme.md")):
            issues.append(f"{artifact_id}: leaf directory missing README: {leaf}")

    reviewed = {entry["path"] for entry in data.get("review_queue", [])}
    for file in (root / "src").rglob("*.tex"):
        rel = file.relative_to(root).as_posix()
        if rel.endswith("-template.tex"):
            counterpart = rel[:-len("-template.tex")] + "-blank.tex"
            if not (root / counterpart).is_file() and rel not in reviewed:
                issues.append(f"Template is missing an explicit Blank: {rel} -> {counterpart}")
        if rel.endswith("-blank.tex"):
            counterpart = rel[:-len("-blank.tex")] + "-template.tex"
            if rel not in registered and not (root / counterpart).exists():
                issues.append(f"Unregistered Blank with missing Template: {rel}")
            if rel not in registered:
                issues.append(f"Unregistered Blank: {rel}")

    return issues


if __name__ == "__main__":
    errors = validate()
    if errors:
        for problem in errors:
            print(f"ERROR: {problem}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"PASS: {len(data['pairs'])} governed pairs; "
          f"{len(data.get('review_queue', []))} review-queue entries. "
          "This is a structural check, not a completed semantic audit.")
