#!/usr/bin/env python3
"""Generate/check pdfLaTeX-compatible grammar source fragments from pinned JSON.

Only the grammar text is rendered. Original diagram-factory sources are inert
provenance snapshots; diagrams are authored separately in PlantUML EBNF.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLLECTION = ROOT / "src/programming/languages/syntax-diagrams"
EXPECTED = {
    "ecmascript-2025": (261, 261, 5),
    "cpp23": (351, 351, 13),
    "c23": (96, 94, 6),
    "java-25": (253, 253, 9),
    "python-314": (205, 205, 24),
}


def printable(text: str) -> str:
    """Keep all original UTF-8 data in JSON; use ASCII labels for pdfLaTeX listings."""
    return "".join(ch if ord(ch) < 128 else f"[U+{ord(ch):04X}]" for ch in text)


def render(data: dict) -> str:
    names = {entry["name"]: entry["text"] for entry in data["rules"]}
    if len(names) != len(data["rules"]):
        raise ValueError(f"Duplicate rule names in {data['language']}")
    sections = data["sections"]
    output = [
        "% Generated from pinned grammar JSON; printable non-ASCII characters use [U+XXXX] escapes.",
        "",
    ]
    visited: set[str] = set()

    def add_rule(name: str) -> None:
        if name in visited:
            raise ValueError(f"Duplicate section membership for {name}")
        if name not in names:
            raise ValueError(f"Unresolved section production {name}")
        visited.add(name)
        output.extend(
            (
                r"\noindent\textbf{\texttt{\detokenize{" + name + r"}}}\par",
                r"\begin{lstlisting}",
                printable(names[name]),
                r"\end{lstlisting}",
                "",
            )
        )

    for section in sections:
        title = section["id"].replace("_", " ").replace("-", " ")
        output.extend((r"\section{" + title + "}", ""))
        for name in section["ruleNames"]:
            add_rule(name)
    extra = [entry["name"] for entry in data["rules"] if entry["name"] not in visited]
    if extra:
        output.extend((r"\section{Unregistered source productions}", ""))
        for name in extra:
            add_rule(name)
    if len(visited) != len(names):
        raise ValueError("Lost imported grammar data")
    return "\n".join(output) + "\n"


def validate(data: dict) -> None:
    language = data["language"]
    expected = EXPECTED[language]
    if data.get("schemaVersion") != 1:
        raise ValueError(f"Unsupported grammar schema: {language}")
    if len(data["rules"]) != expected[0] or data["sourceFactoryCount"] != expected[1]:
        raise ValueError(f"Migration baseline count drift: {language}")
    if len(data["sections"]) != expected[2]:
        raise ValueError(f"Section count drift: {language}")
    if len(set(x["name"] for x in data["rules"])) != len(data["rules"]):
        raise ValueError(f"Duplicate grammar key: {language}")
    recorded = set(data.get("missingSourceFactories", []))
    sectioned = {name for part in data["sections"] for name in part["ruleNames"]}
    missing = set(x["name"] for x in data["rules"]) - sectioned
    if missing != recorded:
        raise ValueError(f"Unexpected text-only grammar rules for {language}: {missing ^ recorded}")
    if data.get("textualRuleCount") != len(data["rules"]):
        raise ValueError(f"Textual count mismatch: {language}")
    if not data["sourceRevision"] or len(data["sourceRevision"]) != 40:
        raise ValueError(f"Unpinned source revision: {language}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail on outdated generated LaTeX")
    args = parser.parse_args()
    errors = []
    for language in EXPECTED:
        source = COLLECTION / "data" / f"{language}.json"
        destination = COLLECTION / "generated" / f"{language}-rules.tex"
        data = json.loads(source.read_text(encoding="utf-8"))
        validate(data)
        rendered = render(data)
        if args.check:
            if not destination.is_file() or destination.read_text(encoding="utf-8") != rendered:
                errors.append(str(destination.relative_to(ROOT)))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"{language}: {len(data['rules'])} textual productions, {len(data['sections'])} sections")
    if errors:
        for error in errors:
            print(f"Generated fragment out of date: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
