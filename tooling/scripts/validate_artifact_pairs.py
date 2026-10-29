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

# TeX command options such as \item[Title] or \begin{description}[style=...]
# describe structure; the bracket marks are not actually printed.
TEX_OPTION = re.compile(r"\\(?:[A-Za-z@]+\*?|begin\{[^{}\n]+\})\s*\[[^\]\n]*\]")
VISIBLE_BRACKET = re.compile(r"\[[^\]\n]*[A-Za-z][^\]\n]*\]")
EMPTY_BRACKET = re.compile(r"\[\s*\]")


def printable_bracket_prompts(source: str) -> list[str]:
    """Identify literal bracketed text that would be visible in the PDF body.

    This deliberately excludes TeX option syntax and comments. Rendering macros
    that generate bracketed fields are handled separately by the macro guards.
    """
    body = source.split(r"\begin{document}", 1)[-1]
    body = "\n".join(line.split("%", 1)[0] for line in body.splitlines())
    body = TEX_OPTION.sub("", body)
    # In TeX a line-break followed by [8pt] is spacing syntax, not printed text.
    body = re.sub(r"\\\\\[[^\]\n]*\]", "", body)
    return [match.group(0) for match in VISIBLE_BRACKET.finditer(body)] + [
        match.group(0) for match in EMPTY_BRACKET.finditer(body)
    ]


def bracket_rendering_macros(source: str) -> list[str]:
    """Guard against helper macros reintroducing visible bracketed prompts."""
    return [
        match.group(0)
        for match in re.finditer(
            r"\\(?:emph|textit|textbf|texttt)\s*\{\s*\[(?:#\d+|[A-Za-z][^\]]*)\]",
            source,
        )
    ]



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
            if artifact.get("structure_rule") == "matching-fields":
                expected = set(HEADING.findall(contents["blank"])) - {"Identification", "Review / sign-off"}
                actual = set(HEADING.findall(contents["template"]))
                if not expected.issubset(actual):
                    issues.append(f"{artifact_id}: template missing blank response sections: {sorted(expected - actual)}")
            elif artifact.get("structure_rule") == "guided-instrument":
                if len(HEADING.findall(contents["template"])) < 3 or len(HEADING.findall(contents["blank"])) < 3:
                    issues.append(f"{artifact_id}: guided workbook or scorecard structure is incomplete")
            elif HEADING.findall(contents["template"]) != HEADING.findall(contents["blank"]):
                issues.append(f"{artifact_id}: sections/subsections are out of sync")
            if artifact["family"] == "architecture-decision-record":
                if r"\DocStatus}{Blank}" not in contents["blank"]:
                    issues.append(f"{artifact_id}: Blank has incorrect document status")
                if r"\newcommand{\BlankResponse}" not in contents["blank"]:
                    issues.append(f"{artifact_id}: Blank has no writable response rules")

        if "blank" in contents:
            blank = contents["blank"]
            visible = printable_bracket_prompts(blank)
            generators = bracket_rendering_macros(blank)
            if visible:
                issues.append(
                    f"{artifact_id}: printable bracketed placeholder(s) in Blank: "
                    + ", ".join(visible[:5])
                )
            if generators:
                issues.append(
                    f"{artifact_id}: macro still prints bracketed words: "
                    + ", ".join(generators[:5])
                )
            if "[To complete]" in blank or "[TODO]" in blank:
                issues.append(f"{artifact_id}: unremoved placeholder token in Blank")

        leaf = (root / artifact["blank"]).parent
        if not any((leaf / name).exists() for name in ("README.md", "readme.md")):
            issues.append(f"{artifact_id}: leaf directory missing README: {leaf}")

    reviewed = {entry["path"] for entry in data.get("review_queue", [])}
    for file in (root / "src").rglob("*.tex"):
        rel = file.relative_to(root).as_posix()
        if rel.endswith("-template.tex"):
            counterpart = rel[:-len("-template.tex")] + "-blank.tex"
            if not (root / counterpart).is_file() and rel not in reviewed and rel not in registered:
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
