#!/usr/bin/env python3
"""Canonical build helpers for the latex-docs repository."""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, List, Sequence, Set

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
LATEXMK = os.environ.get("LATEXMK", "latexmk")

FATAL_PATTERNS = [
    re.compile(r"LaTeX Error:\s+.+"),
    re.compile(r"Package\s+.+?\s+Error:\s+.+"),
    re.compile(r"Undefined control sequence"),
    re.compile(r"Emergency stop"),
    re.compile(r"Fatal error occurred, no output PDF file produced"),
    re.compile(r"File `[^`]+` not found"),
    re.compile(r"Runaway argument"),
    re.compile(r"Missing \\begin\{document\}"),
    re.compile(r"No \\title given"),
]

MISSING_FILE_PATTERNS = [
    re.compile(r"File `[^`]+` not found"),
    re.compile(r"File [\"']([^\"']+)[\"'] not found"),
    re.compile(r"I can't find file `[^`]+`"),
]

# Emitted by pdfTeX/LuaTeX/XeTeX when run with -file-line-error: e.g.
#   ./doc.tex:88: pdfTeX error (font expansion): ...
FILE_LINE_ERROR_PATTERN = re.compile(r"^(\.[/\\][^\s:]+?\.(?:tex|sty|cls)):(\d+):\s*(.*)$")

FULL_REBUILD_PREFIXES = (
    ".github/",
    "tooling/scripts/",
    "src/common/",
)

FULL_REBUILD_FILES = {
    "Makefile",
    ".latexmkrc",
    "latexmkrc",
}


class RevisionResolutionError(RuntimeError):
    """Raised when a Git revision pair cannot be resolved."""


@dataclass
class BuildSummary:
    mode: str
    base_revision: str
    head_revision: str
    root_count: int
    attempted_count: int
    succeeded_count: int
    failed_count: int
    skipped_count: int
    pdf_count: int
    log_count: int
    build_status: str
    first_errors: list[dict[str, Any]]
    failure_clusters: list[dict[str, str | int]]


def _resolve_repo_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


def _count_files(path: Path | None, pattern: str = "*") -> int:
    if path is None or not path.exists():
        return 0
    return sum(1 for candidate in path.rglob(pattern) if candidate.is_file())


def _normalize_build_status(exit_code: int) -> str:
    if exit_code == 0:
        return "success"
    if exit_code == 1:
        return "failed"
    return "invalid"


def _write_build_summary(log_dir: Path | None, summary: BuildSummary, output_dir: Path | None) -> None:
    if log_dir is None:
        return

    log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = log_dir / "build-summary.json"
    text_summary_path = log_dir / "build-summary.txt"
    first_errors_path = log_dir / "build-first-errors.json"
    failure_clusters_path = log_dir / "build-failure-clusters.json"
    manifest_path = log_dir / "build-manifest.txt"

    summary_dict = asdict(summary)
    summary_path.write_text(json.dumps(summary_dict, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        f"mode: {summary.mode}",
        f"base revision: {summary.base_revision or '-'}",
        f"head revision: {summary.head_revision or '-'}",
        f"root count: {summary.root_count}",
        f"attempted count: {summary.attempted_count}",
        f"succeeded count: {summary.succeeded_count}",
        f"failed count: {summary.failed_count}",
        f"skipped count: {summary.skipped_count}",
        f"PDF count: {summary.pdf_count}",
        f"log count: {summary.log_count}",
        f"build status: {summary.build_status}",
    ]
    text_summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    first_errors_path.write_text(json.dumps(summary.first_errors, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    failure_clusters_path.write_text(json.dumps(summary.failure_clusters, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _display_path(path: Path) -> str:
        try:
            return path.relative_to(ROOT).as_posix()
        except ValueError:
            return str(path)

    manifest_lines: list[str] = []
    if output_dir is not None and output_dir.exists():
        manifest_lines.append("[pdfs]")
        for pdf_path in sorted(path for path in output_dir.rglob("*.pdf") if path.is_file()):
            manifest_lines.append(_display_path(pdf_path))
    if log_dir.exists():
        manifest_lines.append("[logs]")
        for log_path in sorted(path for path in log_dir.rglob("*") if path.is_file()):
            manifest_lines.append(_display_path(log_path))
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")


def _is_generated_wrapper(path: Path) -> bool:
    return path.name.startswith(".") and path.name.endswith(".latex-build-wrapper.tex")


def discover_roots(src_root: Path | None = None) -> List[Path]:
    search_root = (src_root or SRC_DIR).resolve()
    if not search_root.exists():
        return []

    roots: List[Path] = []
    for path in sorted(search_root.rglob("*.tex")):
        if not path.is_file() or _is_generated_wrapper(path):
            continue
        if contains_documentclass(path):
            roots.append(path.resolve())
    return roots


def discover_categories(src_root: Path | None = None) -> List[str]:
    search_root = (src_root or SRC_DIR).resolve()
    if not search_root.exists():
        return []

    return [child.name for child in sorted(search_root.iterdir()) if child.is_dir() and not child.name.startswith(".")]


def contains_documentclass(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return bool(re.search(r"^\s*\\documentclass", text, re.MULTILINE))


def resolve_texinputs() -> str:
    paths = [
        ROOT / "tooling" / "latex",
        ROOT / "tooling" / "styles" / "latex",
        ROOT / "src",
        ROOT / "src" / "architecture" / "style-system",
        ROOT / "sty",
        ROOT / "tex",
    ]
    entries = [str(path) + "//" for path in paths if path.exists()]
    current = os.environ.get("TEXINPUTS", "")
    if entries:
        base = ":" + ":".join(entries) + ":"
        if current:
            return base + current + ":"
        return base
    return current


def reset_output_tree(path: Path | None) -> None:
    if path is None:
        return
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)


def _relative_root_path(tex_path: Path) -> Path:
    try:
        return tex_path.relative_to(SRC_DIR)
    except ValueError:
        return Path(tex_path.name)


def _log_paths(tex_path: Path, log_dir: Path | None) -> tuple[Path | None, Path | None]:
    if log_dir is None:
        return None, None

    rel_path = _relative_root_path(tex_path)
    log_leaf = rel_path.with_suffix("")
    stdout_path = (log_dir / log_leaf).with_suffix(".build.stdout.txt")
    stderr_path = (log_dir / log_leaf).with_suffix(".build.stderr.txt")
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    return stdout_path, stderr_path


def _native_log_copy_path(tex_path: Path, log_dir: Path | None) -> Path | None:
    if log_dir is None:
        return None

    rel_path = _relative_root_path(tex_path)
    log_leaf = rel_path.with_suffix("")
    native_log_path = (log_dir / log_leaf).with_suffix(".log.txt")
    native_log_path.parent.mkdir(parents=True, exist_ok=True)
    return native_log_path


def _extract_first_error_details(root_log: Path | None, stdout_path: Path | None, stderr_path: Path | None) -> dict[str, str]:
    def _read_text(path: Path | None) -> str:
        if path is None or not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")

    def _normalize_signature(text: str) -> str:
        normalized = text.strip()
        if not normalized:
            return ""
        normalized = normalized.replace(str(ROOT), "<repo>")
        normalized = re.sub(r"/tmp/[^\s:;,)]+", "<tmp>", normalized)
        normalized = re.sub(r"l\.\d+", "l.<n>", normalized)
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()

    def _join_wrapped_lines(raw_lines: list[str]) -> str:
        """Rejoin pdfTeX's hard-wrapped log lines without corrupting tokens.

        pdfTeX wraps long log lines at a fixed column (commonly 79 chars)
        without regard for word boundaries, so a token such as "LaTeX" or
        "sequence." can be split mid-word across two physical lines. The raw
        (unstripped) line already preserves a trailing space when the wrap
        happened to land on a genuine word boundary; when it does not, the
        line ends with a non-space character and the next physical line is a
        direct continuation of the same token. Concatenating the raw lines
        with no inserted separator therefore preserves genuine word
        boundaries (where a trailing space already exists) while avoiding a
        spurious space inside a split token.
        """
        if not raw_lines:
            return ""
        joined = raw_lines[0]
        for raw_line in raw_lines[1:]:
            joined += raw_line
        return re.sub(r"[ \t]+", " ", joined).strip()

    def _first_file_line_error_details(text: str) -> dict[str, str]:
        lines = text.splitlines()
        for idx, raw in enumerate(lines):
            match = FILE_LINE_ERROR_PATTERN.match(raw)
            if not match:
                continue
            source_file, line_no, message = match.groups()

            # pdfTeX wraps long log lines (commonly at column 79); rejoin
            # continuation lines that are not the start of a new log entry.
            message_lines = [message]
            next_idx = idx + 1
            while next_idx < len(lines) and next_idx < idx + 4:
                stripped = lines[next_idx].strip()
                if not stripped:
                    break
                if FILE_LINE_ERROR_PATTERN.match(lines[next_idx]):
                    break
                if re.match(r"^[<(\[!]", stripped):
                    break
                if re.match(r"^(Package|LaTeX|Overfull|Underfull|Runaway|Output written|l\.\d+)", stripped):
                    break
                message_lines.append(lines[next_idx])
                next_idx += 1
                if stripped.endswith((".", "!", "?")):
                    break
            full_message = _join_wrapped_lines(message_lines) or "LaTeX fatal error"

            line_ref = f"l.{line_no}"
            for next_line in lines[idx + 1 : idx + 8]:
                candidate = next_line.strip()
                if re.match(r"l\.\d+", candidate):
                    line_ref = candidate
                    break

            context_lines = [raw.strip()] + [
                stripped for stripped in (line.strip() for line in lines[idx + 1 : idx + 4]) if stripped
            ]

            signature = f"{full_message} ({line_ref})" if line_ref else full_message

            return {
                "signature": _normalize_signature(signature),
                "message": full_message,
                "line_ref": _normalize_signature(line_ref),
                "line": line_no,
                "context": _normalize_signature(" | ".join(context_lines)),
                "source": source_file,
            }
        return {}

    def _first_bang_details(text: str) -> dict[str, str]:
        lines = text.splitlines()
        for idx, raw in enumerate(lines):
            line = raw.strip()
            if not line.startswith("!"):
                continue

            # The "!" line itself may be hard-wrapped across physical lines
            # (e.g. "! Undefined control sequen" / "ce."); rejoin continuation
            # lines up to the first `l.<n>` context line or a blank line.
            message_lines = [raw[raw.index("!") + 1 :]]
            next_idx = idx + 1
            while next_idx < len(lines) and next_idx < idx + 4:
                stripped = lines[next_idx].strip()
                if not stripped or re.match(r"l\.\d+", stripped):
                    break
                message_lines.append(lines[next_idx])
                next_idx += 1
                if stripped.endswith((".", "!", "?")):
                    break
            message = _join_wrapped_lines(message_lines) or "LaTeX fatal error"

            line_ref = ""
            line_number = ""
            for next_line in lines[idx + 1 : idx + 6]:
                next_line = next_line.strip()
                ref_match = re.match(r"l\.(\d+)", next_line)
                if ref_match:
                    line_ref = next_line
                    line_number = ref_match.group(1)
                    break
            context_lines = [line]
            for next_line in lines[idx + 1 : idx + 4]:
                stripped = next_line.strip()
                if stripped:
                    context_lines.append(stripped)

            source_file = ""
            for prev_line in reversed(lines[max(0, idx - 12) : idx + 1]):
                tex_matches = re.findall(r"([^()\s]+\.tex)", prev_line)
                if tex_matches:
                    source_file = tex_matches[-1]
                    break

            signature = message
            if line_ref:
                signature = f"{message} ({line_ref})"

            return {
                "signature": _normalize_signature(signature),
                "message": message,
                "line_ref": _normalize_signature(line_ref),
                "line": line_number,
                "context": _normalize_signature(" | ".join(context_lines)),
                "source": source_file,
            }
        return {}

    sources: list[tuple[str, str]] = [
        ("log", _read_text(root_log)),
        ("stdout", _read_text(stdout_path)),
        ("stderr", _read_text(stderr_path)),
    ]
    non_empty_sources = [(name, text) for name, text in sources if text.strip()]
    if not non_empty_sources:
        return {
            "signature": "UNKNOWN",
            "message": "UNKNOWN",
            "line_ref": "",
            "line": "",
            "context": "",
            "source": "",
        }

    # 1) File-and-line errors emitted with -file-line-error are the most
    #    specific diagnostic and are preferred even over a bare `!` line,
    #    since some pdfTeX-internal fatal errors never emit a `!` prefix.
    for _, text in non_empty_sources:
        details = _first_file_line_error_details(text)
        if details:
            return details

    # 2) TeX-leading `!` errors with line context are next highest signal.
    for _, text in non_empty_sources:
        details = _first_bang_details(text)
        if details:
            return details

    # 3..7) Canonical LaTeX/package fatal signatures.
    precedence_patterns = [
        re.compile(r"LaTeX Error:\s*.+"),
        re.compile(r"Package\s+[^\s]+\s+Error:\s*.+"),
        re.compile(r"Undefined control sequence"),
    ]

    for missing_file_pattern in MISSING_FILE_PATTERNS:
        precedence_patterns.append(missing_file_pattern)

    precedence_patterns.extend(
        [
            re.compile(r"Emergency stop"),
            re.compile(r"Fatal error(?: occurred, no output PDF file produced)?"),
        ]
    )

    for pattern in precedence_patterns:
        for _, text in non_empty_sources:
            match = pattern.search(text)
            if match:
                message = _normalize_signature(match.group(0))
                return {
                    "signature": message,
                    "message": message,
                    "line_ref": "",
                    "line": "",
                    "context": message,
                    "source": "",
                }

    # 8) latexmk-level failure phrasing.
    latexmk_pattern = re.compile(r"Latexmk:.*(?:error|failed|failure|stopping).+", re.IGNORECASE)
    for _, text in non_empty_sources:
        for line in text.splitlines():
            match = latexmk_pattern.search(line)
            if match:
                message = _normalize_signature(match.group(0))
                return {
                    "signature": message,
                    "message": message,
                    "line_ref": "",
                    "line": "",
                    "context": message,
                    "source": "",
                }

    # 9) Last non-empty line fallback from collected sources.
    for _, text in non_empty_sources:
        for line in reversed(text.splitlines()):
            stripped = line.strip()
            if stripped:
                message = _normalize_signature(stripped)
                return {
                    "signature": message,
                    "message": message,
                    "line_ref": "",
                    "line": "",
                    "context": message,
                    "source": "",
                }

    return {
        "signature": "UNKNOWN",
        "message": "UNKNOWN",
        "line_ref": "",
        "line": "",
        "context": "",
        "source": "",
    }


def _extract_first_error(root_log: Path | None, stdout_path: Path | None, stderr_path: Path | None) -> str:
    return _extract_first_error_details(root_log, stdout_path, stderr_path).get("signature", "UNKNOWN")


def _resolve_package_path(package_name: str) -> Path | None:
    candidates = [
        ROOT / "tooling" / "latex" / f"{package_name}.sty",
        ROOT / "tooling" / "styles" / "latex" / f"{package_name}.sty",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def _collect_dependencies(path: Path, seen: Set[Path] | None = None) -> Set[Path]:
    deps: Set[Path] = set()
    resolved_path = path.resolve()
    visited = seen if seen is not None else set()
    if resolved_path in visited or not resolved_path.exists():
        return deps

    visited.add(resolved_path)

    text = resolved_path.read_text(encoding="utf-8", errors="ignore")
    base_dir = resolved_path.parent

    for match in re.finditer(r"\\(?:input|include)\{([^}]+)\}", text):
        include_name = match.group(1)
        candidates = [
            (base_dir / include_name).resolve(),
            (base_dir / f"{include_name}.tex").resolve(),
            (base_dir / f"{include_name}.sty").resolve(),
        ]
        for candidate in candidates:
            if candidate.exists():
                deps.add(candidate)
                deps.update(_collect_dependencies(candidate, visited))
                break

    for match in re.finditer(r"\\usepackage\{([^}]+)\}", text):
        package_name = match.group(1)
        package_path = _resolve_package_path(package_name)
        if package_path is not None:
            deps.add(package_path)
            deps.update(_collect_dependencies(package_path, visited))

    return deps


def _requires_full_rebuild(changed_path: str) -> bool:
    normalized = changed_path.strip().replace("\\", "/")
    if not normalized:
        return False
    if normalized in FULL_REBUILD_FILES:
        return True
    if normalized.startswith(FULL_REBUILD_PREFIXES):
        return True
    return normalized.startswith("tooling/") and normalized.endswith(".tex")


def _write_empty_summary(
    *,
    log_dir: Path | None,
    output_dir: Path | None,
    mode: str,
    base_revision: str,
    head_revision: str,
    exit_code: int,
    error_message: str = "",
) -> None:
    summary = BuildSummary(
        mode=mode,
        base_revision=base_revision,
        head_revision=head_revision,
        root_count=0,
        attempted_count=0,
        succeeded_count=0,
        failed_count=0,
        skipped_count=0,
        pdf_count=_count_files(output_dir, "*.pdf"),
        log_count=_count_files(log_dir),
        build_status=_normalize_build_status(exit_code),
        first_errors=(
            [{"root": "configuration", "signature": error_message, "exit_code": str(exit_code)}]
            if error_message
            else []
        ),
        failure_clusters=([{"signature": error_message, "count": 1}] if error_message else []),
    )
    _write_build_summary(log_dir, summary, output_dir)


def determine_affected_roots(roots: Sequence[Path], changed_path: Path | None = None) -> List[Path]:
    if not changed_path:
        return list(roots)

    changed_path = changed_path.resolve()
    affected: Set[Path] = set()
    for root in roots:
        if changed_path == root:
            affected.add(root)
            continue
        deps = _collect_dependencies(root)
        if changed_path in deps:
            affected.add(root)
    return sorted(affected)


def _detect_engine(tex_path: Path) -> str:
    try:
        text = tex_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "pdflatex"
    if re.search(r"^\s*%\s*!TeX\s+program\s*=\s*lualatex", text, re.MULTILINE):
        return "lualatex"
    if re.search(r"^\s*%\s*!TeX\s+program\s*=\s*xelatex", text, re.MULTILINE):
        return "xelatex"
    return "pdflatex"


def _uses_minted_syntax(text: str) -> bool:
    return any(marker in text for marker in ("\\begin{minted}", "\\mintinline", "\\inputminted", "\\setminted{"))


def _split_option_list(option_text: str) -> list[str]:
    items: list[str] = []
    token: list[str] = []
    depth = 0
    for char in option_text:
        if char == "{":
            depth += 1
        elif char == "}" and depth > 0:
            depth -= 1

        if char == "," and depth == 0:
            item = "".join(token).strip()
            if item:
                items.append(item)
            token = []
            continue

        token.append(char)

    item = "".join(token).strip()
    if item:
        items.append(item)
    return items


def _sanitize_minted_blocks(text: str) -> str:
    def _normalize_begin(options: str, language: str) -> str:
        lang = language.strip()
        keep_items: list[str] = []
        for item in _split_option_list(options):
            if "=" not in item:
                keep_items.append(item)
                continue

            key, value = item.split("=", 1)
            normalized_key = key.strip().lower()
            normalized_value = value.strip()

            # Legacy listings-style keys need migration for minted.
            if normalized_key == "language":
                if normalized_value:
                    lang = normalized_value
                continue
            if normalized_key in {"caption", "label", "style"}:
                continue

            keep_items.append(item)

        if keep_items:
            return f"\\begin{{minted}}[{','.join(keep_items)}]{{{lang}}}"
        return f"\\begin{{minted}}{{{lang}}}"

    # Fix legacy ordering: \begin{minted}{lang}[opts]
    text = re.sub(
        r"\\begin\{minted\}\{([^}]+)\}\[([^\]]+)\]",
        lambda match: _normalize_begin(match.group(2), match.group(1)),
        text,
    )

    # Sanitize modern ordering options list.
    text = re.sub(
        r"\\begin\{minted\}\[([^\]]+)\]\{([^}]+)\}",
        lambda match: _normalize_begin(match.group(1), match.group(2)),
        text,
    )

    return text


def _prepare_build_input(tex_path: Path) -> tuple[Path, bool]:
    try:
        text = tex_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return tex_path, False

    uses_minted = _uses_minted_syntax(text)
    if not uses_minted:
        return tex_path, False

    sanitized_text = _sanitize_minted_blocks(text)
    requires_minted_package = not re.search(r"\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\{minted\}", sanitized_text)
    needs_wrapper = sanitized_text != text or requires_minted_package
    if not needs_wrapper:
        return tex_path, False

    lines = sanitized_text.splitlines()
    insert_at = 0
    for index, line in enumerate(lines):
        if line.lstrip().startswith(r"\documentclass"):
            insert_at = index + 1
            break

    wrapper_lines = lines
    if requires_minted_package:
        wrapper_lines = lines[:insert_at] + [r"\usepackage[cache=false]{minted}", ""] + lines[insert_at:]
    wrapper_path = tex_path.with_name(f".{tex_path.stem}.latex-build-wrapper.tex")
    wrapper_path.write_text("\n".join(wrapper_lines) + "\n", encoding="utf-8")
    return wrapper_path, True


def stage_pages_site(pdf_dir: Path, site_dir: Path) -> List[Path]:
    pdf_dir = pdf_dir.resolve()
    site_dir = site_dir.resolve()
    site_pdf_dir = site_dir / "pdfs"

    if not pdf_dir.exists():
        raise FileNotFoundError(pdf_dir)

    reset_output_tree(site_dir)
    shutil.copytree(pdf_dir, site_pdf_dir, dirs_exist_ok=True)

    pdf_rel_paths = sorted(path.relative_to(site_pdf_dir) for path in site_pdf_dir.rglob("*.pdf") if path.is_file())

    index_path = site_dir / "index.html"
    with index_path.open("w", encoding="utf-8") as handle:
        handle.write("<!doctype html><html><body><h1>LaTeX PDFs</h1><ul>")
        for rel_path in pdf_rel_paths:
            rel_posix = rel_path.as_posix()
            escaped = html.escape(rel_posix)
            handle.write(f'<li><a href="pdfs/{escaped}">{escaped}</a></li>')
        handle.write("</ul></body></html>")

    return pdf_rel_paths


def build_root(tex_path: Path, output_dir: Path | None = None, log_dir: Path | None = None, artifact_dir: Path | None = None) -> int:
    tex_path = tex_path.resolve()
    output_dir = _resolve_repo_path(output_dir)
    log_dir = _resolve_repo_path(log_dir)
    artifact_dir = _resolve_repo_path(artifact_dir)
    if not tex_path.exists():
        raise FileNotFoundError(tex_path)

    work_dir = tex_path.parent
    stem = tex_path.stem
    mint_dir = work_dir / f"_minted-{stem}"
    mint_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["TEXINPUTS"] = resolve_texinputs() + (":" + env.get("TEXINPUTS", "") if env.get("TEXINPUTS") else "")
    env.setdefault("BIBINPUTS", "")
    env.setdefault("BSTINPUTS", "")

    rc_file = ROOT / ".latexmkrc"
    if not rc_file.exists():
        rc_file = ROOT / "latexmkrc"
    # No "-f" (force mode): the Python orchestrator already isolates and
    # aggregates results per document, so forcing latexmk to keep re-running
    # a broken document only produces misleading "force_mode" downstream
    # noise instead of the earliest actionable error.
    base_cmd = [LATEXMK, "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-shell-escape", "-synctex=1"]
    if rc_file.exists():
        base_cmd.extend(["-r", str(rc_file)])
    engine = _detect_engine(tex_path)
    if engine == "lualatex":
        base_cmd.extend(["-pdflatex=lualatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-shell-escape", "%O", "%S"])
    elif engine == "xelatex":
        base_cmd.extend(["-pdflatex=xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-shell-escape", "%O", "%S"])

    build_dir = work_dir
    if output_dir is not None:
        rel_dir = _relative_root_path(tex_path).parent
        build_dir = output_dir / rel_dir
        build_dir.mkdir(parents=True, exist_ok=True)

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)

    build_input_path, used_wrapper = _prepare_build_input(tex_path)
    cmd = [*base_cmd, build_input_path.name]
    if used_wrapper:
        cmd = [*base_cmd, f"-jobname={stem}", build_input_path.name]
    stdout_path, stderr_path = _log_paths(tex_path, log_dir)
    native_log_copy_path = _native_log_copy_path(tex_path, log_dir)

    stdout_handle = stdout_path.open("w", encoding="utf-8") if stdout_path else None
    stderr_handle = stderr_path.open("w", encoding="utf-8") if stderr_path else None
    try:
        result = subprocess.run(
            cmd,
            cwd=str(work_dir),
            env=env,
            stdout=stdout_handle if stdout_handle is not None else subprocess.DEVNULL,
            stderr=stderr_handle if stderr_handle is not None else subprocess.DEVNULL,
            check=False,
        )
    finally:
        if stdout_handle is not None:
            stdout_handle.close()
        if stderr_handle is not None:
            stderr_handle.close()

    source_log_path = work_dir / f"{stem}.log"
    if native_log_copy_path is not None and source_log_path.exists():
        shutil.copy2(source_log_path, native_log_copy_path)

    source_pdf_path = work_dir / f"{stem}.pdf"
    published_pdf_path = build_dir / f"{stem}.pdf"

    # Clear any previous staged output for this root so failures cannot leave stale files.
    if output_dir is not None and published_pdf_path.exists():
        try:
            published_pdf_path.unlink()
        except OSError:
            pass

    if used_wrapper and build_input_path.exists():
        try:
            build_input_path.unlink()
        except OSError:
            pass

    if result.returncode == 0 and not source_pdf_path.exists():
        if stderr_path is not None:
            with stderr_path.open("a", encoding="utf-8") as handle:
                handle.write(f"Expected PDF output was not produced: {source_pdf_path}\n")
        if output_dir is not None and published_pdf_path.exists():
            try:
                published_pdf_path.unlink()
            except OSError:
                pass
        return 2

    if output_dir is not None and result.returncode == 0 and source_pdf_path.exists():
        build_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_pdf_path, published_pdf_path)

    if artifact_dir is not None:
        rel_dir = _relative_root_path(tex_path).parent
        dest_dir = artifact_dir / rel_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        if result.returncode == 0 and source_pdf_path.exists():
            shutil.copy2(source_pdf_path, dest_dir / f"{stem}.pdf")

    if result.returncode == 0:
        return 0

    if output_dir is not None and published_pdf_path.exists():
        try:
            published_pdf_path.unlink()
        except OSError:
            pass

    return result.returncode


def build_roots(
    tex_paths: Sequence[Path],
    jobs: int = 1,
    output_dir: Path | None = None,
    log_dir: Path | None = None,
    artifact_dir: Path | None = None,
    clean_output: bool = False,
    mode: str = "full",
    base_revision: str = "",
    head_revision: str = "",
) -> int:
    output_dir = _resolve_repo_path(output_dir)
    log_dir = _resolve_repo_path(log_dir)
    artifact_dir = _resolve_repo_path(artifact_dir)

    if clean_output:
        reset_output_tree(output_dir)
        reset_output_tree(log_dir)

    failures: List[tuple[Path, int, dict[str, str]]] = []

    def report_failure(tex_path: Path, result_code: int) -> None:
        stdout_path, stderr_path = _log_paths(tex_path, log_dir)
        native_log_path = _native_log_copy_path(tex_path, log_dir)
        if native_log_path is None or not native_log_path.exists():
            native_log_path = tex_path.with_suffix(".log")
        details = _extract_first_error_details(native_log_path, stdout_path, stderr_path)
        # Per-document output uses the actual (non-normalized) message, source,
        # and line number; the normalized "signature" is reserved for cluster
        # fingerprinting only (see failure_clusters below).
        first_error = details.get("message") or details.get("signature", "UNKNOWN")
        message = f"Build failed for {tex_path} (exit {result_code})"
        if log_dir is not None:
            message += f"; logs: log={native_log_path} stdout={stdout_path} stderr={stderr_path}"
        if first_error:
            message += f"; first_error={first_error}"
        if details.get("source"):
            message += f"; source={details['source']}"
        if details.get("line"):
            message += f"; line={details['line']}"
        print(message, file=sys.stderr)
        failures.append((tex_path, result_code, details))

    if jobs <= 1:
        failure_count = 0
        for tex_path in tex_paths:
            result_code = build_root(tex_path, output_dir=output_dir, log_dir=log_dir, artifact_dir=artifact_dir)
            if result_code != 0:
                failure_count += 1
                report_failure(tex_path, result_code)
        print(f"Build summary: {len(tex_paths) - failure_count} succeeded, {failure_count} failed, {len(tex_paths)} total", file=sys.stderr)
        exit_code = 0
        if failure_count:
            clusters = Counter(detail.get("signature", "UNKNOWN") for _, _, detail in failures)
            print("Failure clusters:", file=sys.stderr)
            for signature, count in clusters.most_common(10):
                print(f"  {count} x {signature}", file=sys.stderr)
            exit_code = 1

        cluster_counts = Counter(detail.get("signature", "UNKNOWN") for _, _, detail in failures)
        summary = BuildSummary(
            mode=mode,
            base_revision=base_revision,
            head_revision=head_revision,
            root_count=len(tex_paths),
            attempted_count=len(tex_paths),
            succeeded_count=len(tex_paths) - failure_count,
            failed_count=failure_count,
            skipped_count=0,
            pdf_count=_count_files(output_dir, "*.pdf"),
            log_count=_count_files(log_dir),
            build_status=_normalize_build_status(exit_code),
            first_errors=[
                {
                    "root": tex_path.relative_to(ROOT).as_posix() if tex_path.is_relative_to(ROOT) else str(tex_path),
                    "signature": details.get("signature", "UNKNOWN"),
                    "exit_code": str(result_code),
                    "message": details.get("message", ""),
                    "line": details.get("line", ""),
                    "line_ref": details.get("line_ref", ""),
                    "context": details.get("context", ""),
                    "source": details.get("source", ""),
                }
                for tex_path, result_code, details in failures
            ],
            failure_clusters=[
                {"signature": signature, "count": count}
                for signature, count in cluster_counts.most_common()
            ],
        )
        _write_build_summary(log_dir, summary, output_dir)
        return exit_code

    failure_count = 0
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
        futures = [executor.submit(build_root, tex_path, output_dir, log_dir, artifact_dir) for tex_path in tex_paths]
        for tex_path, future in zip(tex_paths, futures):
            result = future.result()
            if result != 0:
                failure_count += 1
                report_failure(tex_path, result)
    print(f"Build summary: {len(tex_paths) - failure_count} succeeded, {failure_count} failed, {len(tex_paths)} total", file=sys.stderr)
    exit_code = 0
    if failure_count:
        clusters = Counter(detail.get("signature", "UNKNOWN") for _, _, detail in failures)
        print("Failure clusters:", file=sys.stderr)
        for signature, count in clusters.most_common(10):
            print(f"  {count} x {signature}", file=sys.stderr)
        exit_code = 1

    cluster_counts = Counter(detail.get("signature", "UNKNOWN") for _, _, detail in failures)
    summary = BuildSummary(
        mode=mode,
        base_revision=base_revision,
        head_revision=head_revision,
        root_count=len(tex_paths),
        attempted_count=len(tex_paths),
        succeeded_count=len(tex_paths) - failure_count,
        failed_count=failure_count,
        skipped_count=0,
        pdf_count=_count_files(output_dir, "*.pdf"),
        log_count=_count_files(log_dir),
        build_status=_normalize_build_status(exit_code),
        first_errors=[
            {
                "root": tex_path.relative_to(ROOT).as_posix() if tex_path.is_relative_to(ROOT) else str(tex_path),
                "signature": details.get("signature", "UNKNOWN"),
                "exit_code": str(result_code),
                "message": details.get("message", ""),
                "line": details.get("line", ""),
                "line_ref": details.get("line_ref", ""),
                "context": details.get("context", ""),
                "source": details.get("source", ""),
            }
            for tex_path, result_code, details in failures
        ],
        failure_clusters=[
            {"signature": signature, "count": count}
            for signature, count in cluster_counts.most_common()
        ],
    )
    _write_build_summary(log_dir, summary, output_dir)
    return exit_code


def collect_changed_paths(base_ref: str | None = None, head_ref: str | None = None) -> List[str]:
    if base_ref and head_ref:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref]
    elif base_ref:
        cmd = ["git", "diff", "--name-only", base_ref]
    elif head_ref:
        cmd = ["git", "diff", "--name-only", head_ref]
    else:
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

    result = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git diff failed").strip().splitlines()[-1]
        raise RevisionResolutionError(
            f"unable to calculate changed paths for base={base_ref or '-'} head={head_ref or '-'}: {detail}"
        )

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def build_changed(
    base_ref: str | None = None,
    head_ref: str | None = None,
    jobs: int = 1,
    output_dir: Path | None = None,
    log_dir: Path | None = None,
    artifact_dir: Path | None = None,
    clean_output: bool = False,
    mode_name: str = "changed",
) -> int:
    output_dir = _resolve_repo_path(output_dir)
    log_dir = _resolve_repo_path(log_dir)
    artifact_dir = _resolve_repo_path(artifact_dir)

    try:
        changed_paths = collect_changed_paths(base_ref=base_ref, head_ref=head_ref)
    except RevisionResolutionError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        if clean_output:
            reset_output_tree(output_dir)
            reset_output_tree(log_dir)
        _write_empty_summary(
            log_dir=log_dir,
            output_dir=output_dir,
            mode=mode_name,
            base_revision=base_ref or "",
            head_revision=head_ref or "",
            exit_code=2,
            error_message=str(exc),
        )
        return 2

    roots = discover_roots()
    if any(_requires_full_rebuild(changed_path) for changed_path in changed_paths):
        return build_roots(
            roots,
            jobs=jobs,
            output_dir=output_dir,
            log_dir=log_dir,
            artifact_dir=artifact_dir,
            clean_output=clean_output,
            mode=mode_name,
            base_revision=base_ref or "",
            head_revision=head_ref or "",
        )

    affected = []
    for changed_path in changed_paths:
        path = (ROOT / changed_path).resolve()
        if not path.exists():
            continue
        if path.suffix.lower() not in {".tex", ".sty", ".cls"}:
            continue
        affected.extend(determine_affected_roots(roots, path))
    unique_roots = sorted({path.resolve() for path in affected})
    return build_roots(
        unique_roots,
        jobs=jobs,
        output_dir=output_dir,
        log_dir=log_dir,
        artifact_dir=artifact_dir,
        clean_output=clean_output,
        mode=mode_name,
        base_revision=base_ref or "",
        head_revision=head_ref or "",
    )


def render_plantuml(source_dir: Path | None = None, formats: Sequence[str] | None = None) -> int:
    search_root = (source_dir or SRC_DIR).resolve()
    if not search_root.exists():
        return 0

    config_names = ["plantuml-config.puml", "config.puml"]
    formats = list(formats or ["png", "svg"])
    include_paths = [ROOT / "tooling" / "plantuml", ROOT / "tooling" / "styles" / "plantuml"]
    env = os.environ.copy()
    env["PLANTUML_INCLUDE_PATH"] = ":".join(str(path) for path in include_paths if path.exists())

    diagram_count = 0
    failures = 0
    for path in sorted(search_root.rglob("*.puml")):
        if not path.is_file() or path.name.lower() in {name.lower() for name in config_names}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "@startuml" not in text:
            continue

        diagram_count += 1
        config_path = None
        current = path.parent
        while current != current.parent:
            for config_name in config_names:
                candidate = current / config_name
                if candidate.exists():
                    config_path = candidate
                    break
            if config_path is not None:
                break
            current = current.parent

        for fmt in formats:
            output_dir = path.parent / fmt
            output_dir.mkdir(parents=True, exist_ok=True)
            cmd = ["plantuml", f"-t{fmt}", "-o", str(output_dir)]
            if config_path is not None:
                cmd.extend(["-config", str(config_path)])
            cmd.append(str(path.name))
            result = subprocess.run(cmd, cwd=str(path.parent), env=env, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                failures += 1
    return 1 if failures else 0


def clean() -> int:
    for tex_path in discover_roots():
        work_dir = tex_path.parent
        subprocess.run([LATEXMK, "-c", tex_path.name], cwd=str(work_dir), check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage LaTeX document builds")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-roots")
    subparsers.add_parser("list-categories")

    build_parser = subparsers.add_parser("build-all")
    build_parser.add_argument("--jobs", type=int, default=1)
    build_parser.add_argument("--parallel", action="store_true")
    build_parser.add_argument("--output-dir", type=Path, default=None)
    build_parser.add_argument("--log-dir", type=Path, default=None)
    build_parser.add_argument("--artifact-dir", type=Path, default=None)
    build_parser.add_argument("--clean-output", action="store_true")
    build_parser.add_argument("--mode-name", default="full")
    build_parser.add_argument("--base", "--base-revision", dest="base_ref", default="")
    build_parser.add_argument("--head", "--head-revision", dest="head_ref", default="")

    category_parser = subparsers.add_parser("build-category")
    category_parser.add_argument("category")
    category_parser.add_argument("--jobs", type=int, default=1)
    category_parser.add_argument("--output-dir", type=Path, default=None)
    category_parser.add_argument("--log-dir", type=Path, default=None)
    category_parser.add_argument("--artifact-dir", type=Path, default=None)
    category_parser.add_argument("--clean-output", action="store_true")
    category_parser.add_argument("--mode-name", default="category")
    category_parser.add_argument("--base", "--base-revision", dest="base_ref", default="")
    category_parser.add_argument("--head", "--head-revision", dest="head_ref", default="")

    changed_parser = subparsers.add_parser("build-changed")
    changed_parser.add_argument("--base", dest="base_ref", default=None, help="Base Git revision used to calculate changed paths")
    changed_parser.add_argument("--head", dest="head_ref", default=None, help="Head Git revision used to calculate changed paths")
    changed_parser.add_argument("--jobs", type=int, default=1)
    changed_parser.add_argument("--output-dir", type=Path, default=None)
    changed_parser.add_argument("--log-dir", type=Path, default=None)
    changed_parser.add_argument("--artifact-dir", type=Path, default=None)
    changed_parser.add_argument("--clean-output", action="store_true")
    changed_parser.add_argument("--mode-name", default="changed")

    render_parser = subparsers.add_parser("render-plantuml")
    render_parser.add_argument("--source-dir", type=Path, default=None)
    render_parser.add_argument("--formats", nargs="*", default=["png", "svg"])

    stage_parser = subparsers.add_parser("stage-pages")
    stage_parser.add_argument("--pdf-dir", type=Path, required=True)
    stage_parser.add_argument("--site-dir", type=Path, required=True)

    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("--jobs", type=int, default=1)

    args = parser.parse_args(argv)

    if args.command == "list-roots":
        for path in discover_roots():
            print(path)
        return 0

    if args.command == "list-categories":
        for category in discover_categories():
            print(category)
        return 0

    if args.command == "build-all":
        jobs = max(1, args.jobs if args.parallel else 1)
        return build_roots(
            discover_roots(),
            jobs=jobs,
            output_dir=args.output_dir,
            log_dir=args.log_dir,
            artifact_dir=args.artifact_dir,
            clean_output=args.clean_output,
            mode=args.mode_name,
            base_revision=args.base_ref,
            head_revision=args.head_ref,
        )

    if args.command == "build-category":
        roots = [root for root in discover_roots() if root.is_relative_to(SRC_DIR / args.category)]
        return build_roots(
            roots,
            jobs=args.jobs,
            output_dir=args.output_dir,
            log_dir=args.log_dir,
            artifact_dir=args.artifact_dir,
            clean_output=args.clean_output,
            mode=args.mode_name,
            base_revision=args.base_ref,
            head_revision=args.head_ref,
        )

    if args.command == "build-changed":
        return build_changed(
            base_ref=args.base_ref,
            head_ref=args.head_ref,
            jobs=args.jobs,
            output_dir=args.output_dir,
            log_dir=args.log_dir,
            artifact_dir=args.artifact_dir,
            clean_output=args.clean_output,
            mode_name=args.mode_name,
        )

    if args.command == "stage-pages":
        stage_pages_site(args.pdf_dir, args.site_dir)
        return 0

    if args.command == "render-plantuml":
        return render_plantuml(source_dir=args.source_dir, formats=args.formats)

    if args.command == "clean":
        return clean()

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
