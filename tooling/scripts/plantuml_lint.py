#!/usr/bin/env python3
"""Validate the repository PlantUML style and rendering contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOTS = (ROOT / "tooling" / "plantuml", ROOT / "tooling" / "styles" / "plantuml")
DEPRECATED = re.compile(r"^\s*skinparam\s+(padding|ParticipantPadding|handwritten)\b", re.I)
DIRECTIVE_SPACING = re.compile(r"^\s*!(?:unquoted|final)(?:[^ ]| {2,})")
GUARD_START = re.compile(r"^!ifndef ([A-Z0-9_]+_INCLUDED)$")
GUARD_DEFINE = re.compile(r"^!define ([A-Z0-9_]+_INCLUDED)$")
INCLUDE = re.compile(r"^\s*!include(?:sub|url)?\s+(\S+)", re.M)
MANAGED_FORMATS = ("png", "svg", "jpg", "jpeg")
# Standard-library includes resolve inside the pinned jar; only C4-PlantUML is used and only from c4-base.
STDLIB_ALLOWED = {
    "<C4/C4>",
    "<C4/C4_Context>",
    "<C4/C4_Container>",
    "<C4/C4_Component>",
    "<C4/C4_Dynamic>",
    "<C4/C4_Deployment>",
}
STDLIB_OWNER = "c4-base.iuml"
# The one hierarchy every diagram inherits through; see tooling/plantuml/README.md.
# house-tokens is the neutral root: it includes nothing and both notation bases include it.
NEUTRAL_ROOT = "house-tokens.iuml"
CANONICAL_PARENT = {
    "uml-base.iuml": NEUTRAL_ROOT,
    "c4-base.iuml": NEUTRAL_ROOT,
    "uml-structural.iuml": "uml-base.iuml",
    "uml-behavioral.iuml": "uml-base.iuml",
    "uml-interaction.iuml": "uml-behavioral.iuml",
}
CATEGORY_PARENT = {
    "structural": "uml-structural.iuml",
    "behavioral": "uml-behavioral.iuml",
    "interaction": "uml-interaction.iuml",
    "c4": "c4-base.iuml",
}
# Source diagrams reach the shared style only through a leaf module.
LEAF_INCLUDE = re.compile(r"tooling/styles/plantuml/(structural|behavioral|interaction|c4)/[a-z0-9-]+-diagram-style\.iuml$")
HEX_LITERAL = re.compile(r"#[0-9A-Fa-f]{6}\b")
THEME_DIRECTIVE = re.compile(r"^\s*!theme\b", re.I)
# Colour and typography are owned by the shared modules; layout hints (nodesep, ranksep, linetype,
# componentStyle, wrapWidth ...) remain legitimate local decisions.
HOUSE_OWNED_SKINPARAM = re.compile(
    r"^\s*skinparam\s+(?!\w*<<)[A-Za-z]*(Color|FontSize|FontStyle|FontName|BackgroundColor|BorderColor|RoundCorner|Shadowing)\b",
    re.I,
)
SKINPARAM_BLOCK_OPEN = re.compile(r"^\s*skinparam\s+([A-Za-z]+)(<<[^>]+>>)?\s*\{\s*$")
BLOCK_HOUSE_OWNED = re.compile(r"^\s*[A-Za-z]*(Color|FontSize|FontStyle|FontName|RoundCorner|Shadowing)\b", re.I)
# A hidden role stereotype carries no label of its own, so the legend is the only place its meaning can live.
# Token use on arrows and notes sits next to the text that explains it and is not subject to this rule.
ROLE_NEEDING_LEGEND = re.compile(r"<<(primary|dynamic|ok|caution|invalid|alt|neutral|external)>>")
LEGEND_PRESENT = re.compile(r"^\s*legend\b|UML_LEGEND_BEGIN|SHOW_LEGEND|SHOW_FLOATING_LEGEND", re.M)


def _includes(path: Path) -> list[str]:
    return INCLUDE.findall(path.read_text(encoding="utf-8", errors="replace"))


def _resolves(target: str, bases: Sequence[Path]) -> bool:
    if target.startswith("<"):
        return target in STDLIB_ALLOWED
    if "://" in target:
        return False
    return any((base / target).is_file() for base in bases)


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

    neutral = base_dir / NEUTRAL_ROOT
    if not neutral.is_file():
        problems.append(f"tooling/plantuml/{NEUTRAL_ROOT}: neutral root module is missing")
    elif _includes(neutral):
        problems.append(f"tooling/plantuml/{NEUTRAL_ROOT}: the neutral root must not include another module")

    # Stdlib and URL includes: the C4 library comes from the pinned jar, from one module, never from the network.
    for module in sorted(path for root in MODULE_ROOTS for path in root.rglob("*.iuml")):
        for target in _includes(module):
            if "://" in target:
                problems.append(f"{module.relative_to(ROOT)}: include {target} is an unpinned network include")
            elif target.startswith("<"):
                if target not in STDLIB_ALLOWED:
                    problems.append(f"{module.relative_to(ROOT)}: stdlib include {target} is not in the verified allowlist")
                elif module.name != STDLIB_OWNER:
                    problems.append(f"{module.relative_to(ROOT)}: only {STDLIB_OWNER} may include the C4 standard library")

    # A module reachable only under a misspelling would resolve to nothing at render time.
    for stray in sorted(ROOT.rglob("*.iml")):
        if ".git" not in stray.parts:
            problems.append(f"{stray.relative_to(ROOT)}: style modules must use the .iuml extension")
    canonical_names = {NEUTRAL_ROOT, *CANONICAL_PARENT}
    for duplicate in sorted(list(ROOT.rglob("uml-*.iuml")) + list(ROOT.rglob("c4-*.iuml")) + list(ROOT.rglob("house-*.iuml"))):
        if ".git" in duplicate.parts:
            continue
        if duplicate.name in canonical_names and duplicate.parent != base_dir:
            problems.append(f"{duplicate.relative_to(ROOT)}: shadows the canonical module in tooling/plantuml")

    for category, parent in CATEGORY_PARENT.items():
        modules = sorted((style_dir / category).glob("*.iuml")) if (style_dir / category).is_dir() else []
        if not modules:
            problems.append(f"tooling/styles/plantuml/{category}: category has no leaf modules")
        for module in modules:
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
        leaf_targets = [target for target in targets if LEAF_INCLUDE.search((source.parent / target).as_posix())]
        if not leaf_targets:
            problems.append(f"{source.relative_to(ROOT)}: must include exactly one leaf style from tooling/styles/plantuml/<category>/")
        elif len(leaf_targets) > 1:
            problems.append(f"{source.relative_to(ROOT)}: includes more than one leaf style ({', '.join(Path(t).name for t in leaf_targets)})")
        for target in targets:
            if target.startswith("<") or "://" in target:
                problems.append(f"{source.relative_to(ROOT)}: include {target} must go through the shared modules, not a stdlib/URL include")
            elif not _resolves(target, (source.parent, base_dir, style_dir)):
                problems.append(f"{source.relative_to(ROOT)}: include {target} does not resolve")
    return problems


def check_source_style_discipline() -> list[str]:
    """Colour and typography live in the shared modules; a source diagram may only use role tokens.

    Layout hints (nodesep, ranksep, linetype, direction, componentStyle ...) stay local.
    Diagrams whose meaning relies on the ok/caution/invalid roles must carry a legend.
    """
    problems: list[str] = []
    for source in sorted(ROOT.joinpath("src").rglob("*.puml")):
        text = source.read_text(encoding="utf-8", errors="replace")
        relative = source.relative_to(ROOT)
        if not re.search(r"^@startuml", text, re.M):
            # Include-only fragments beside diagrams are domain helpers; configs are rendering-only.
            if HEX_LITERAL.search(text):
                problems.append(f"{relative}: hex colour literal in a fragment; use house tokens")
            continue
        in_block = False
        for number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("'"):
                continue
            if HEX_LITERAL.search(line):
                problems.append(f"{relative}:{number}: hex colour literal; use a $fill_/$deep_/$line_ token or a role stereotype")
            if THEME_DIRECTIVE.match(line):
                problems.append(f"{relative}:{number}: !theme is not allowed; the shared modules are the theme")
            if stripped.startswith("<style>"):
                problems.append(f"{relative}:{number}: local <style> block; move the rule into the shared modules or use a role stereotype")
            if HOUSE_OWNED_SKINPARAM.match(line):
                problems.append(f"{relative}:{number}: colour/typography skinparam is owned by the shared modules")
            opened = SKINPARAM_BLOCK_OPEN.match(line)
            if opened:
                in_block = opened.group(2) is None
                continue
            if in_block:
                if stripped == "}":
                    in_block = False
                elif BLOCK_HOUSE_OWNED.match(line):
                    problems.append(f"{relative}:{number}: colour/typography inside a local skinparam block is owned by the shared modules")
        if ROLE_NEEDING_LEGEND.search(text) and not LEGEND_PRESENT.search(text):
            problems.append(f"{relative}: applies a hidden role stereotype but has no legend (UML_LEGEND_BEGIN/SHOW_LEGEND)")
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
            if match and not _resolves(match.group(1), [example.parent, *include_dirs]):
                problems.append(f"{example.relative_to(ROOT)}:{number}: include {match.group(1)} does not resolve on PLANTUML_INCLUDE_PATH")
            if HEX_LITERAL.search(line) and not line.strip().startswith("'"):
                problems.append(f"{example.relative_to(ROOT)}:{number}: examples must use house tokens, not hex literals")

    problems.extend(check_include_contract())
    problems.extend(check_managed_outputs())
    problems.extend(check_source_style_discipline())
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
