#!/usr/bin/env python3
"""Validate the repository PlantUML style and rendering contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOTS = (ROOT / "tooling" / "plantuml", ROOT / "tooling" / "styles" / "plantuml")
DEPRECATED = re.compile(r"^\s*skinparam\s+(padding|ParticipantPadding|handwritten)\b", re.I)
DIRECTIVE_SPACING = re.compile(r"^\s*!(?:unquoted|final)(?:[^ ]| {2,})")
GUARD_START = re.compile(r"^!ifndef ([A-Z0-9_]+_INCLUDED)$")
GUARD_DEFINE = re.compile(r"^!define ([A-Z0-9_]+_INCLUDED)$")
INCLUDE = re.compile(r"^\s*!include(?:sub|url)?\s+(\S+)", re.M)
MANAGED_FORMATS = ("png", "svg", "jpg", "jpeg")
# The one hierarchy every diagram inherits through; see tooling/plantuml/README.md.
CANONICAL_PARENT = {
    "uml-structural.iuml": "uml-base.iuml",
    "uml-behavioral.iuml": "uml-base.iuml",
    "uml-interaction.iuml": "uml-behavioral.iuml",
}
CATEGORY_PARENT = {
    "structural": "uml-structural.iuml",
    "behavioral": "uml-behavioral.iuml",
    "interaction": "uml-interaction.iuml",
}


def _includes(path: Path) -> list[str]:
    return INCLUDE.findall(path.read_text(encoding="utf-8", errors="replace"))


def check_include_contract() -> list[str]:
    """The include hierarchy is the framework: a broken link silently drops every style."""
    problems: list[str] = []
    base_dir = ROOT / "tooling" / "plantuml"
    style_dir = ROOT / "tooling" / "styles" / "plantuml"

    for name, parent in CANONICAL_PARENT.items():
        module = base_dir / name
        if not module.is_file():
            problems.append(f"tooling/plantuml/{name}: canonical module is missing")
            continue
        if parent not in [Path(target).name for target in _includes(module)]:
            problems.append(f"tooling/plantuml/{name}: must include {parent}")

    if (base_dir / "uml-base.iuml").is_file() and _includes(base_dir / "uml-base.iuml"):
        problems.append("tooling/plantuml/uml-base.iuml: the base module must not include another module")

    # A module reachable only under a misspelling would resolve to nothing at render time.
    for stray in sorted(ROOT.rglob("*.iml")):
        if ".git" not in stray.parts:
            problems.append(f"{stray.relative_to(ROOT)}: style modules must use the .iuml extension")
    for duplicate in sorted(ROOT.rglob("uml-*.iuml")):
        if ".git" in duplicate.parts:
            continue
        if duplicate.name in CANONICAL_PARENT or duplicate.name == "uml-base.iuml":
            if duplicate.parent != base_dir:
                problems.append(f"{duplicate.relative_to(ROOT)}: shadows the canonical module in tooling/plantuml")

    for category, parent in CATEGORY_PARENT.items():
        for module in sorted((style_dir / category).glob("*.iuml")) if (style_dir / category).is_dir() else []:
            if parent not in [Path(target).name for target in _includes(module)]:
                problems.append(f"{module.relative_to(ROOT)}: must include {parent}")

    for source in sorted(ROOT.joinpath("src").rglob("*.puml")):
        text = source.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^@startuml", text, re.M):
            continue
        targets = INCLUDE.findall(text)
        if not targets:
            problems.append(f"{source.relative_to(ROOT)}: renderable diagram has no active !include")
            continue
        for target in targets:
            if not any((base / target).is_file() for base in (source.parent, base_dir, style_dir)):
                problems.append(f"{source.relative_to(ROOT)}: include {target} does not resolve")
    return problems


def check_managed_outputs() -> list[str]:
    """Renders only ever land in <source>/png|svg|jpg; anything else is never refreshed."""
    problems: list[str] = []
    for directory in sorted({source.parent for source in ROOT.joinpath("src").rglob("*.puml")}):
        for candidate in sorted(directory.iterdir()):
            if candidate.is_file() and candidate.suffix.lower().lstrip(".") in MANAGED_FORMATS:
                problems.append(
                    f"{candidate.relative_to(ROOT)}: generated image must live in "
                    f"{directory.name}/{candidate.suffix.lstrip('.').lower()}/"
                )
    return problems


def _module_files() -> list[Path]:
    return sorted(path for root in MODULE_ROOTS for path in root.rglob("*.iuml"))


def check() -> list[str]:
    problems: list[str] = []
    for path in _module_files():
        relative = path.relative_to(ROOT)
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            problems.append(f"{relative}: UTF-8 BOM is not allowed")
        if any(byte > 0x7F for byte in raw):
            problems.append(f"{relative}: module must be ASCII")
        if b"\r" in raw:
            problems.append(f"{relative}: module must use LF line endings")

        lines = raw.decode("ascii", errors="ignore").splitlines()
        for number, line in enumerate(lines, 1):
            if line.startswith("!") and ("\t" in line or DIRECTIVE_SPACING.search(line)):
                problems.append(f"{relative}:{number}: directive has non-canonical spacing")
            if DEPRECATED.match(line):
                problems.append(f"{relative}:{number}: deprecated skinparam")

        guard_lines = [
            (number, line)
            for number, line in enumerate(lines, 1)
            if not line.strip().startswith("'") and line.strip()
        ]
        if len(guard_lines) < 2:
            problems.append(f"{relative}: missing include guard")
            continue
        start_number, start_line = guard_lines[0]
        define_number, define_line = guard_lines[1]
        start = GUARD_START.match(start_line)
        define = GUARD_DEFINE.match(define_line)
        if not start or not define or start.group(1) != define.group(1):
            problems.append(f"{relative}:{start_number}: include guard must have matching ifndef/define")
        content_lines = [line for line in lines if line.strip() and not line.strip().startswith("'")]
        if not content_lines or content_lines[-1] != "!endif":
            problems.append(f"{relative}: include guard must end with !endif")

    for path in sorted(ROOT.joinpath("src").rglob("*.puml")) + sorted(ROOT.joinpath("tooling").rglob("*.puml")):
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if DEPRECATED.match(line):
                problems.append(f"{path.relative_to(ROOT)}:{number}: deprecated skinparam")

    action = (ROOT / ".github" / "actions" / "render-plantuml" / "action.yml").read_text(encoding="utf-8")
    if re.search(r"default:\s*['\"]latest['\"]", action) or "releases/latest" in action:
        problems.append("render-plantuml action must not resolve PlantUML to latest")

    manifest = ROOT / "tooling" / "manifests" / "plantuml.json"
    try:
        pin = json.loads(manifest.read_text(encoding="utf-8"))
        version = str(pin.get("version", ""))
        if not re.fullmatch(r"1\.\d{4}\.\d+", version):
            problems.append(f"{manifest.relative_to(ROOT)}: version {version!r} is not a PlantUML release")
        if not re.fullmatch(r"[0-9a-f]{64}", str(pin.get("sha256", ""))):
            problems.append(f"{manifest.relative_to(ROOT)}: sha256 must be a 64-hex digest")
    except (OSError, ValueError) as exc:
        problems.append(f"{manifest.relative_to(ROOT)}: unreadable pin ({exc})")
        version = ""
    for workflow in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        for number, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), 1):
            match = re.search(r"plantuml-version:\s*['\"]?v?([^'\"\s]+)", line)
            if match and match.group(1) != version:
                problems.append(f"{workflow.relative_to(ROOT)}:{number}: plantuml-version {match.group(1)} differs from the manifest pin {version}")

    include_dirs = [ROOT / "tooling" / "plantuml", ROOT / "tooling" / "styles" / "plantuml"]
    for example in sorted((ROOT / "tooling" / "plantuml").glob("*-example.puml")):
        text = example.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^@startuml", text, re.M):
            problems.append(f"{example.relative_to(ROOT)}: missing @startuml")
        for number, line in enumerate(text.splitlines(), 1):
            match = re.match(r"^!include\s+(\S+)", line)
            if match and not any((base / match.group(1)).is_file() for base in [example.parent, *include_dirs]):
                problems.append(f"{example.relative_to(ROOT)}:{number}: include {match.group(1)} does not resolve on PLANTUML_INCLUDE_PATH")

    problems.extend(check_include_contract())
    problems.extend(check_managed_outputs())
    return problems


def main() -> int:
    problems = check()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print("PlantUML lint: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
