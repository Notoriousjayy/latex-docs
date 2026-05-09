#!/usr/bin/env python3
"""
Rename document files under a repository subtree based on internal titles,
using topic-first kebab-case filenames and explicitly avoiding ISO date prefixes.

Default behavior:
- scans ./src recursively
- targets document-like source files (.tex, .puml, .md, .markdown, .rst, .adoc, .txt)
- preserves directory location
- skips README files unless --rename-readmes is set
- performs a dry run unless --apply is provided
- can emit a JSON report

Examples:
  python rename_src_documents_no_iso_dates.py
  python rename_src_documents_no_iso_dates.py --apply
  python rename_src_documents_no_iso_dates.py --root src/architecture --write-json rename-plan.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, Optional, Sequence

DEFAULT_EXTENSIONS = {".tex", ".puml", ".md", ".markdown", ".rst", ".adoc", ".txt"}
WINDOWS_RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


@dataclass
class RenameDecision:
    path: str
    current_name: str
    extracted_title: Optional[str]
    proposed_name: Optional[str]
    status: str
    reason: Optional[str] = None


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rename documents under a repository subtree using internal titles, "
            "without ISO date prefixes."
        )
    )
    parser.add_argument(
        "--root",
        default="src",
        help="Root directory to scan recursively. Default: src",
    )
    parser.add_argument(
        "--extensions",
        default=",".join(sorted(DEFAULT_EXTENSIONS)),
        help=(
            "Comma-separated list of file extensions to process. "
            f"Default: {','.join(sorted(DEFAULT_EXTENSIONS))}"
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply renames. Without this flag, the script only prints a dry run.",
    )
    parser.add_argument(
        "--rename-readmes",
        action="store_true",
        help="Rename README-like files as well. By default, README files are preserved.",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=96,
        help="Maximum base filename length before extension. Default: 96",
    )
    parser.add_argument(
        "--write-json",
        default="",
        help="Optional path to write a JSON report.",
    )
    return parser.parse_args(argv)


def normalize_extensions(raw: str) -> set[str]:
    extensions: set[str] = set()
    for item in raw.split(","):
        ext = item.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = "." + ext
        extensions.add(ext)
    if not extensions:
        raise ValueError("At least one extension must be supplied.")
    return extensions


def iter_candidate_paths(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() or path.is_symlink():
            yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def remove_tex_comments(text: str) -> str:
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        i = 0
        escaped = False
        out: list[str] = []
        while i < len(line):
            ch = line[i]
            if ch == "\\":
                escaped = not escaped
                out.append(ch)
            elif ch == "%" and not escaped:
                break
            else:
                escaped = False
                out.append(ch)
            i += 1
        cleaned_lines.append("".join(out))
    return "\n".join(cleaned_lines)


def find_braced_argument(text: str, macro: str) -> Optional[str]:
    pattern = re.compile(r"\\" + re.escape(macro) + r"\*?(?:\[[^\]]*\])?\s*\{", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    start = match.end() - 1
    return extract_balanced_braces(text, start)


def extract_balanced_braces(text: str, brace_index: int) -> Optional[str]:
    if brace_index >= len(text) or text[brace_index] != "{":
        return None

    depth = 0
    result: list[str] = []
    for i in range(brace_index, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
            if depth > 1:
                result.append(ch)
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return "".join(result)
            result.append(ch)
        else:
            result.append(ch)
    return None


def strip_tex_markup(value: str) -> str:
    if not value:
        return value

    text = value
    replacements = {
        r"\\&": " and ",
        r"~": " ",
        r"\\_": "_",
        r"\\%": "%",
        r"\\#": "#",
        r"\\textbackslash": " ",
        r"\\/": "/",
        r"\\-": "-",
    }
    for source, target in replacements.items():
        text = re.sub(source, target, text)

    for _ in range(8):
        next_text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", text)
        if next_text == text:
            break
        text = next_text

    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def cleanup_plain_title(value: str) -> str:
    text = value.strip().strip('"\'')
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_meaningful_title(value: Optional[str]) -> bool:
    if not value:
        return False
    candidate = value.strip()
    if len(candidate) < 4:
        return False
    if candidate.lower() in {"document", "untitled", "title", "readme"}:
        return False
    if re.fullmatch(r"[-_=:#.\s]+", candidate):
        return False
    return True


def extract_title_from_tex(text: str) -> Optional[str]:
    cleaned = remove_tex_comments(text)

    for macro in ("title", "chapter", "section", "subsection", "subsubsection", "part"):
        value = find_braced_argument(cleaned, macro)
        if value:
            candidate = strip_tex_markup(value)
            if is_meaningful_title(candidate):
                return candidate

    heading_pattern = re.compile(
        r"\\(?:section|subsection|subsubsection|paragraph|subparagraph|chapter|part)"
        r"\*?(?:\[[^\]]*\])?\{([^{}]+)\}",
        re.MULTILINE,
    )
    for match in heading_pattern.finditer(cleaned):
        candidate = strip_tex_markup(match.group(1))
        if is_meaningful_title(candidate):
            return candidate

    return None


def extract_title_from_markdown(text: str) -> Optional[str]:
    front_matter = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if front_matter:
        for line in front_matter.group(1).splitlines():
            match = re.match(r"\s*title\s*:\s*(.+?)\s*$", line, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip().strip('"\'')
                if is_meaningful_title(candidate):
                    return candidate

    for line in text.splitlines():
        match = re.match(r"\s{0,3}#\s+(.+?)\s*$", line)
        if match:
            candidate = match.group(1).strip()
            if is_meaningful_title(candidate):
                return candidate

    lines = text.splitlines()
    for i in range(len(lines) - 1):
        heading = lines[i].strip()
        underline = lines[i + 1].strip()
        if heading and re.fullmatch(r"[=-]{3,}", underline):
            if is_meaningful_title(heading):
                return heading

    return None


def extract_title_from_rst_or_adoc(text: str) -> Optional[str]:
    lines = [line.rstrip() for line in text.splitlines()]

    for line in lines:
        if line.startswith("= "):
            candidate = line[2:].strip()
            if is_meaningful_title(candidate):
                return candidate

    for i in range(len(lines) - 1):
        heading = lines[i].strip()
        underline = lines[i + 1].strip()
        if not heading or not underline:
            continue
        if len(underline) < max(3, len(heading) // 2):
            continue
        if set(underline) <= set("=-~^\"'`:#*+_"):
            if is_meaningful_title(heading):
                return heading

    return None


def extract_title_from_puml(text: str) -> Optional[str]:
    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("'"):
            continue
        match = re.match(r"^(?:title|caption)\s+(.+?)\s*$", stripped, re.IGNORECASE)
        if match:
            candidate = cleanup_plain_title(match.group(1))
            if is_meaningful_title(candidate):
                return candidate

    label_patterns = [
        re.compile(
            r'^\s*(?:actor|participant|boundary|control|entity|database|queue|collections?|'
            r'component|node|cloud|folder|frame|package|rectangle|card|file|class|'
            r'interface|enum|annotation|usecase)\s+"([^"]+)"',
            re.IGNORECASE,
        ),
        re.compile(r'^\s*:[^:]+:\s*$', re.IGNORECASE),
        re.compile(r'^\s*note\s+(?:left|right|top|bottom)?(?:\s+of\s+\S+)?\s*:\s*(.+?)\s*$', re.IGNORECASE),
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("'"):
            continue
        for pattern in label_patterns:
            match = pattern.match(stripped)
            if not match:
                continue
            candidate = cleanup_plain_title(match.group(1) if match.lastindex else stripped.strip(": "))
            if is_meaningful_title(candidate):
                return candidate

    return None


def extract_title_generic(text: str) -> Optional[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "//", "/*", "*", "'", "%")):
            stripped = stripped.lstrip("#/*%' ").strip()
        candidate = cleanup_plain_title(stripped)
        if is_meaningful_title(candidate):
            return candidate
    return None


def choose_extractor(path: Path) -> Callable[[str], Optional[str]]:
    suffix = path.suffix.lower()
    if suffix == ".tex":
        return extract_title_from_tex
    if suffix == ".puml":
        return extract_title_from_puml
    if suffix in {".md", ".markdown"}:
        return extract_title_from_markdown
    if suffix in {".rst", ".adoc"}:
        return extract_title_from_rst_or_adoc
    return extract_title_generic


def slugify_title(title: str, max_length: int) -> str:
    value = title.strip()

    value = re.sub(r"^\s*(?:19|20)\d{2}[-_ ]\d{2}[-_ ]\d{2}(?:[-_ ]+)?", "", value)
    value = re.sub(r"^\s*(?:19|20)\d{6}(?:[-_ ]+)?", "", value)

    value = value.replace("&", " and ")
    value = value.replace("@", " at ")
    value = value.replace("+", " plus ")
    value = value.replace("/", " ")
    value = value.replace("\\", " ")
    value = value.replace(":", " ")
    value = value.replace("–", "-").replace("—", "-")
    value = strip_tex_markup(value)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")

    if not value:
        value = "document"

    if len(value) > max_length:
        value = value[:max_length].rstrip("-")

    if value in WINDOWS_RESERVED_NAMES:
        value = f"{value}-doc"

    return value


def make_unique_filename(target_dir: Path, stem: str, suffix: str, reserved_paths: set[Path]) -> str:
    candidate = target_dir / f"{stem}{suffix}"
    if candidate not in reserved_paths and not candidate.exists():
        reserved_paths.add(candidate)
        return candidate.name

    index = 2
    while True:
        alt = target_dir / f"{stem}-{index}{suffix}"
        if alt not in reserved_paths and not alt.exists():
            reserved_paths.add(alt)
            return alt.name
        index += 1


def plan_renames(root: Path, extensions: set[str], rename_readmes: bool, max_length: int) -> list[RenameDecision]:
    decisions: list[RenameDecision] = []
    reserved_paths: set[Path] = set()

    for path in iter_candidate_paths(root):
        suffix_lower = path.suffix.lower()

        if suffix_lower not in extensions:
            continue

        if path.is_symlink():
            decisions.append(
                RenameDecision(
                    path=str(path),
                    current_name=path.name,
                    extracted_title=None,
                    proposed_name=None,
                    status="skip",
                    reason="symlink-skipped",
                )
            )
            continue

        if not rename_readmes and path.stem.lower() == "readme":
            decisions.append(
                RenameDecision(
                    path=str(path),
                    current_name=path.name,
                    extracted_title=None,
                    proposed_name=None,
                    status="skip",
                    reason="readme-skipped-by-default",
                )
            )
            continue

        try:
            text = read_text(path)
        except OSError as exc:
            decisions.append(
                RenameDecision(
                    path=str(path),
                    current_name=path.name,
                    extracted_title=None,
                    proposed_name=None,
                    status="skip",
                    reason=f"read-error: {exc}",
                )
            )
            continue

        extractor = choose_extractor(path)
        extracted_title = extractor(text)
        if not extracted_title:
            decisions.append(
                RenameDecision(
                    path=str(path),
                    current_name=path.name,
                    extracted_title=None,
                    proposed_name=None,
                    status="skip",
                    reason="no-usable-title-found",
                )
            )
            continue

        proposed_stem = slugify_title(extracted_title, max_length=max_length)
        proposed_name = make_unique_filename(
            target_dir=path.parent,
            stem=proposed_stem,
            suffix=path.suffix,
            reserved_paths=reserved_paths,
        )

        if proposed_name == path.name:
            decisions.append(
                RenameDecision(
                    path=str(path),
                    current_name=path.name,
                    extracted_title=extracted_title,
                    proposed_name=proposed_name,
                    status="unchanged",
                    reason="already-matches",
                )
            )
        else:
            decisions.append(
                RenameDecision(
                    path=str(path),
                    current_name=path.name,
                    extracted_title=extracted_title,
                    proposed_name=proposed_name,
                    status="rename",
                )
            )

    return decisions


def apply_renames(decisions: list[RenameDecision]) -> None:
    for decision in decisions:
        if decision.status != "rename" or not decision.proposed_name:
            continue

        current_path = Path(decision.path)
        target_path = current_path.with_name(decision.proposed_name)

        try:
            current_path.rename(target_path)
            decision.status = "renamed"
        except OSError as exc:
            decision.status = "skip"
            decision.reason = f"rename-error: {exc}"


def print_report(decisions: Iterable[RenameDecision], applied: bool) -> None:
    action_label = "APPLY" if applied else "DRY-RUN"
    print(f"[{action_label}] Proposed document renames")
    print()

    renamed = 0
    unchanged = 0
    skipped = 0

    for decision in decisions:
        source = str(Path(decision.path))
        if decision.status in {"rename", "renamed"}:
            renamed += 1
            print(f"RENAME   {source} -> {Path(decision.path).with_name(decision.proposed_name)}")
        elif decision.status == "unchanged":
            unchanged += 1
            print(f"KEEP     {source}")
        else:
            skipped += 1
            reason = f" ({decision.reason})" if decision.reason else ""
            print(f"SKIP     {source}{reason}")

    print()
    print(f"summary: rename={renamed} unchanged={unchanged} skip={skipped}")
    if not applied:
        print("note: rerun with --apply to perform the renames.")


def write_json_report(path: Path, decisions: list[RenameDecision], argv: Sequence[str]) -> None:
    payload = {
        "command": [sys.executable, *argv],
        "decisions": [asdict(item) for item in decisions],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"error: root directory does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    try:
        extensions = normalize_extensions(args.extensions)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    decisions = plan_renames(
        root=root,
        extensions=extensions,
        rename_readmes=args.rename_readmes,
        max_length=args.max_length,
    )

    if args.apply:
        apply_renames(decisions)

    print_report(decisions, applied=args.apply)

    if args.write_json:
        write_json_report(Path(args.write_json), decisions, argv or sys.argv[1:])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
