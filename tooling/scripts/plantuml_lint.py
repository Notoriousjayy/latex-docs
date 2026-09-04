#!/usr/bin/env python3
"""Validate the repository PlantUML style and rendering contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOTS = (ROOT / "tooling" / "plantuml", ROOT / "tooling" / "styles" / "plantuml")
DEPRECATED = re.compile(r"^\s*skinparam\s+(padding|ParticipantPadding|handwritten)\b", re.I)
DIRECTIVE_SPACING = re.compile(r"^\s*!(?:unquoted|final)(?:[^ ]| {2,})")
GUARD_START = re.compile(r"^!ifndef ([A-Z0-9_]+_INCLUDED)$")
GUARD_DEFINE = re.compile(r"^!define ([A-Z0-9_]+_INCLUDED)$")


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
    if re.search(r"default:\s*['\"]latest['\"]", action):
        problems.append("render-plantuml action must not default PlantUML to latest")
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
