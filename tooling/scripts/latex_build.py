#!/usr/bin/env python3
"""Canonical build helpers for the latex-docs repository."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, List, Sequence, Set
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_graph  # noqa: E402  (local module, resolved via the path insert above)

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
LATEXMK = os.environ.get("LATEXMK", "latexmk")
TIMING_HISTORY_PATH = ROOT / "tooling" / "manifests" / "build-timings.json"
RASTER_SUFFIXES = {".png": "png", ".jpg": "jpg", ".jpeg": "jpeg"}

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
    shard_index: int = 0
    shard_total: int = 1
    wall_clock_seconds: float = 0.0
    compile_seconds: float = 0.0
    durations: dict[str, float] = field(default_factory=dict)
    timing_stats: dict[str, float] = field(default_factory=dict)
    slowest_roots: list[dict[str, Any]] = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return round(ordered[index], 3)


def _timing_stats(durations: Sequence[float]) -> dict[str, float]:
    if not durations:
        return {}
    total = sum(durations)
    return {
        "count": len(durations),
        "total": round(total, 3),
        "mean": round(total / len(durations), 3),
        "median": _percentile(durations, 0.50),
        "p90": _percentile(durations, 0.90),
        "p95": _percentile(durations, 0.95),
        "p99": _percentile(durations, 0.99),
        "max": round(max(durations), 3),
        "min": round(min(durations), 3),
    }


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
        f"shard: {summary.shard_index + 1}/{summary.shard_total}",
        f"root count: {summary.root_count}",
        f"attempted count: {summary.attempted_count}",
        f"succeeded count: {summary.succeeded_count}",
        f"failed count: {summary.failed_count}",
        f"skipped count: {summary.skipped_count}",
        f"cache hits: {summary.cache_hits}",
        f"PDF count: {summary.pdf_count}",
        f"log count: {summary.log_count}",
        f"wall clock seconds: {summary.wall_clock_seconds}",
        f"compile seconds: {summary.compile_seconds}",
        f"build status: {summary.build_status}",
    ]
    for key, value in sorted(summary.timing_stats.items()):
        lines.append(f"timing {key}: {value}")
    text_summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    (log_dir / "build-timings.json").write_text(
        json.dumps(
            {
                "shard_index": summary.shard_index,
                "shard_total": summary.shard_total,
                "wall_clock_seconds": summary.wall_clock_seconds,
                "compile_seconds": summary.compile_seconds,
                "stats": summary.timing_stats,
                "slowest_roots": summary.slowest_roots,
                "durations": summary.durations,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

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
    """Return the TEXINPUTS prefix for document builds.

    PERFORMANCE: keep this list narrow and never add a recursive entry over a
    large content tree. A recursive ``src//`` entry previously forced kpathsea
    to re-walk the whole 4,900-file src/ tree on every file lookup, costing
    ~63s per document instead of ~2s. No .sty/.cls files live under src/.
    """
    paths = [
        ROOT / "tooling" / "latex",
        ROOT / "tooling" / "styles" / "latex",
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


PAGES_ACRONYMS = {
    "ai": "AI", "api": "API", "c": "C", "ci": "CI", "cd": "CD", "cissp": "CISSP",
    "cpp": "C++", "cpu": "CPU", "css": "CSS", "dna": "DNA", "dp": "DP", "fft": "FFT",
    "gpu": "GPU", "html": "HTML", "http": "HTTP", "iec": "IEC", "ieee": "IEEE",
    "io": "I/O", "iso": "ISO", "lcp": "LCP", "ml": "ML", "os": "OS", "pdf": "PDF",
    "sql": "SQL", "tls": "TLS", "ui": "UI", "uml": "UML", "unix": "UNIX",
    "url": "URL", "xml": "XML",
}
# Lowercased only in interior positions, so "Next Permutation of N Letters" reads naturally.
PAGES_MINOR_WORDS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "into", "of", "on", "or", "the", "to", "with"}


def _humanize_segment(segment: str) -> str:
    """Turn a kebab-case directory or file segment into a human-readable label."""
    words = [word for word in re.split(r"[-_\s]+", segment) if word]
    if not words:
        return segment
    rendered = []
    for index, word in enumerate(words):
        lowered = word.casefold()
        if lowered in PAGES_ACRONYMS:
            rendered.append(PAGES_ACRONYMS[lowered])
        elif index and lowered in PAGES_MINOR_WORDS:
            rendered.append(lowered)
        else:
            rendered.append(word[:1].upper() + word[1:])
    return " ".join(rendered)


def _document_label(stem: str) -> str:
    """Human-readable document name; the canonical path stays visible as secondary text."""
    name = re.sub(r"-(?:cornell-)?notes$", "", stem)
    chapter = re.match(r"^ch(\d+)[-_](.+)$", name, re.I)
    if chapter:
        return f"Chapter {int(chapter.group(1))}: {_humanize_segment(chapter.group(2))}"
    annex = re.match(r"^annex-([a-z])[-_](.+)$", name, re.I)
    if annex:
        return f"Annex {annex.group(1).upper()}: {_humanize_segment(annex.group(2))}"
    numbered = re.match(r"^(\d+(?:[-_]\d+)*)[-_](.+)$", name)
    if numbered:
        return f"{numbered.group(1).replace('_', '.').replace('-', '.')} {_humanize_segment(numbered.group(2))}"
    return _humanize_segment(name) or stem


def _natural_key(text: str) -> tuple:
    """Order chapter and clause prefixes numerically rather than lexically."""
    return tuple(
        (0, int(part), "") if part.isdigit() else (1, 0, part)
        for part in re.split(r"(\d+)", text.casefold())
        if part
    )


def stage_pages_site(pdf_dir: Path, site_dir: Path, image_dir: Path | None = None) -> List[Path]:
    pdf_dir = pdf_dir.resolve()
    site_dir = site_dir.resolve()
    site_pdf_dir = site_dir / "pdfs"

    if not pdf_dir.exists():
        raise FileNotFoundError(pdf_dir)

    reset_output_tree(site_dir)
    shutil.copytree(pdf_dir, site_pdf_dir, dirs_exist_ok=True)

    if image_dir is not None:
        image_dir = image_dir.resolve()
        if image_dir.exists():
            for source in sorted(image_dir.rglob("*")):
                if not source.is_file() or source.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
                    continue
                rel_path = source.relative_to(image_dir)
                target = site_dir / "images" / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    pdf_rel_paths = sorted(path.relative_to(site_pdf_dir) for path in site_pdf_dir.rglob("*.pdf") if path.is_file())
    raster_rel_paths = []
    images_dir = site_dir / "images"
    if images_dir.exists():
        raster_rel_paths = sorted(
            path.relative_to(images_dir)
            for path in images_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
        )

    def _numeric_chapter_key(path: Path) -> tuple[int, str]:
        match = re.match(r"ch(\d+)-", path.name)
        if match:
            return int(match.group(1)), path.name
        match = re.match(r"chapter_(\d+)_", path.name)
        if match:
            return int(match.group(1)), path.name
        return (10**9, path.name)

    def _collection_path_key(path: Path) -> tuple[object, ...]:
        name = path.name.lower()
        annex = re.match(r"annex-([a-f])-([0-9-]+)-", name)
        if annex:
            numbers = tuple(int(part) for part in annex.group(2).split("-"))
            return (1, annex.group(1), numbers, name)
        numbers = tuple(int(part) for part in re.match(r"([0-9]+(?:-[0-9]+)*)-", name).group(1).split("-")) if re.match(r"([0-9]+(?:-[0-9]+)*)-", name) else (10**9,)
        return (0, numbers, name)

    cornell_paths = sorted(path for path in pdf_rel_paths if path.parts and path.parts[0] == "cornell-notes")
    non_cornell_paths = sorted(path for path in pdf_rel_paths if not (path.parts and path.parts[0] == "cornell-notes"))

    heading_counter = 0

    def _heading(level: int, text: str, *, anchor: str | None = None) -> str:
        nonlocal heading_counter
        heading_counter += 1
        heading_id = anchor or f"heading-{heading_counter}"
        return f'<h{level} id="{html.escape(heading_id, quote=True)}">{html.escape(text)}</h{level}>'

    def _emit_links(handle: Any, paths: list[Path], sort_by_chapter: bool = False) -> None:
        ordered = sorted(paths, key=_collection_path_key if sort_by_chapter else lambda path: (path.as_posix(),))
        handle.write('<ul class="document-list">')
        for rel_path in ordered:
            rel_posix = rel_path.as_posix()
            label = html.escape(rel_posix)
            target = html.escape("pdfs/" + quote(rel_posix, safe="/:@-._~"), quote=True)
            search_text = html.escape(rel_posix.casefold(), quote=True)
            handle.write(
                f'<li class="document-row" data-search="{search_text}">'
                f'<a href="{target}" title="Open {label}"><span class="document-name">{label}</span>'
                f'<span class="document-path">{label}</span></a></li>'
            )
        handle.write("</ul>")

    def _emit_tree_links(handle: Any, paths: list[Path]) -> None:
        """Human label plus the canonical relative path, so identical basenames stay distinguishable."""
        handle.write('<ul class="document-list">')
        for rel_path in sorted(paths, key=lambda path: _natural_key(path.name)):
            rel_posix = rel_path.as_posix()
            name = html.escape(_document_label(rel_path.stem))
            path_label = html.escape(rel_posix)
            target = html.escape("pdfs/" + quote(rel_posix, safe="/:@-._~"), quote=True)
            search_text = html.escape(f"{_document_label(rel_path.stem)} {rel_posix}".casefold(), quote=True)
            handle.write(
                f'<li class="document-row" data-search="{search_text}">'
                f'<a href="{target}" title="Open {path_label}"><span class="document-name">{name}</span>'
                f'<span class="document-path">{path_label}</span></a></li>'
            )
        handle.write("</ul>")

    def _emit_directory_tree(handle: Any, paths: list[Path], depth: int, level: int) -> None:
        """Render the hierarchy from each PDF's own directory path; no collection allowlist."""
        here = [path for path in paths if len(path.parts) == depth + 1]
        if here:
            _emit_tree_links(handle, here)
        groups: dict[str, list[Path]] = {}
        for path in paths:
            if len(path.parts) > depth + 1:
                groups.setdefault(path.parts[depth], []).append(path)
        for segment in sorted(groups, key=_natural_key):
            anchor = "section-" + re.sub(r"[^a-z0-9]+", "-", "/".join(groups[segment][0].parts[: depth + 1]).casefold()).strip("-")
            handle.write(_heading(min(level, 6), _humanize_segment(segment), anchor=anchor))
            _emit_directory_tree(handle, groups[segment], depth + 1, level + 1)

    def _emit_raster_cards(handle: Any) -> None:
        if not raster_rel_paths:
            handle.write('<p>No PlantUML raster assets are staged.</p>')
            return
        handle.write('<ul class="image-grid">')
        for rel_path in raster_rel_paths:
            rel_posix = rel_path.as_posix()
            image_href = "images/" + rel_posix
            href = html.escape(image_href, quote=True)
            img_src = html.escape(image_href, quote=True)
            title = html.escape(rel_path.name)
            handle.write(
                f'<li class="image-card" data-search="{html.escape(rel_posix.casefold(), quote=True)}">'
                f'<a href="{href}" target="_blank" rel="noopener noreferrer"><img src="{img_src}" alt="{title}" loading="lazy" /></a>'
                f'<div class="image-meta"><a href="{href}" title="Open {title}">{title}</a></div>'
                f'</li>'
            )
        handle.write("</ul>")

    index_path = site_dir / "index.html"
    with index_path.open("w", encoding="utf-8") as handle:
        total_documents = len(pdf_rel_paths)
        total_png = sum(1 for rel in raster_rel_paths if rel.suffix.lower() == ".png")
        total_jpg = sum(1 for rel in raster_rel_paths if rel.suffix.lower() in {".jpg", ".jpeg"})
        category_count = len({path.parts[0] for path in pdf_rel_paths if path.parts})
        handle.write("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LaTeX document library</title>
<style>
:root { color-scheme: light; --page: #f5f7f9; --panel: #ffffff; --text: #17212b; --muted: #5c6b78; --accent: #126782; --border: #d8e0e6; --hover: #eaf4f6; --focus: #d97706; --shadow: 0 8px 24px rgba(23, 33, 43, .07); }
@media (prefers-color-scheme: dark) { :root { color-scheme: dark; --page: #11181d; --panel: #1b252c; --text: #edf3f5; --muted: #b4c3ca; --accent: #76d0e5; --border: #3a4a54; --hover: #263943; --focus: #f7bd63; --shadow: 0 8px 24px rgba(0, 0, 0, .24); } }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--page); color: var(--text); font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
.skip-link { position: absolute; left: 1rem; top: -4rem; padding: .6rem .8rem; background: var(--panel); color: var(--text); border: 2px solid var(--focus); z-index: 2; }
.skip-link:focus { top: 1rem; }
.shell { width: min(1120px, calc(100% - 2rem)); margin: 0 auto; }
header { padding: 3.5rem 0 2.5rem; border-bottom: 1px solid var(--border); background: var(--panel); }
.eyebrow { margin: 0 0 .4rem; color: var(--accent); font-size: .78rem; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
h1 { max-width: 760px; margin: 0; font-size: clamp(2rem, 5vw, 3.4rem); line-height: 1.08; letter-spacing: 0; }
.subtitle { max-width: 680px; margin: 1rem 0 0; color: var(--muted); font-size: 1.08rem; }
main { padding: 2rem 0 4rem; }
.summary { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.summary-card { padding: 1.1rem 1.25rem; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; box-shadow: var(--shadow); }
.summary-value { display: block; font-size: 1.8rem; font-weight: 750; line-height: 1.1; }
.summary-label { display: block; margin-top: .3rem; color: var(--muted); }
.tools { display: grid; gap: 1rem; margin-bottom: 2.5rem; }
.search-label { font-weight: 700; }
.search-input { width: 100%; margin-top: .4rem; padding: .8rem .9rem; color: var(--text); background: var(--panel); border: 1px solid var(--border); border-radius: 6px; font: inherit; }
.search-input:focus-visible, a:focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; }
.result-count { margin: 0; color: var(--muted); }
.jump { display: flex; flex-wrap: wrap; gap: .55rem .8rem; align-items: baseline; }
.jump-title { font-weight: 700; margin-right: .25rem; }
a { color: var(--accent); }
.jump a { padding: .35rem .65rem; border: 1px solid var(--border); border-radius: 999px; text-decoration: none; }
.jump a:hover, .jump a:focus-visible { background: var(--hover); }
.library h2 { margin: 2.5rem 0 1rem; padding-bottom: .55rem; border-bottom: 2px solid var(--border); font-size: 1.7rem; }
.library h3 { margin: 2rem 0 .7rem; font-size: 1.3rem; }
.library h4 { margin: 1.35rem 0 .5rem; font-size: 1.08rem; }
.library h5, .library h6 { margin: 1rem 0 .35rem; color: var(--muted); font-size: 1rem; }
.document-list { display: grid; gap: .55rem; margin: 0; padding: 0; list-style: none; }
.document-row { min-width: 0; }
.document-row a { display: grid; gap: .1rem; min-width: 0; padding: .75rem .9rem; color: var(--text); background: var(--panel); border: 1px solid var(--border); border-radius: 6px; text-decoration: none; }
.document-row a:hover { background: var(--hover); border-color: var(--accent); }
.document-name, .document-path { overflow-wrap: anywhere; }
.document-name { font-weight: 650; }
.document-path { color: var(--muted); font-size: .87rem; }
.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin: 0; padding: 0; list-style: none; }
.image-card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: .75rem; box-shadow: var(--shadow); }
.image-card img { width: 100%; aspect-ratio: 4 / 3; object-fit: contain; border-radius: 6px; background: #f8fafc; border: 1px solid var(--border); display: block; }
.image-meta { margin-top: .65rem; font-size: .88rem; overflow-wrap: anywhere; }
.image-meta a { color: var(--text); text-decoration: none; }
footer { padding: 1.5rem 0 2rem; color: var(--muted); border-top: 1px solid var(--border); font-size: .9rem; }
@media (max-width: 600px) { .shell { width: min(100% - 1.25rem, 1120px); } header { padding: 2.4rem 0 1.8rem; } .summary { grid-template-columns: 1fr 1fr; } main { padding-top: 1.25rem; } }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to documents</a>
<header><div class="shell"><p class="eyebrow">Document library</p><h1>LaTeX PDFs & Diagram catalog</h1><p class="subtitle">Browse the published technical notes, guides, and PlantUML-derived diagram previews.</p></div></header>
<main id="main-content" class="shell">
<section class="summary" aria-label="Library summary">
<div class="summary-card"><span class="summary-value">""" + str(total_documents) + """</span><span class="summary-label">PDFs</span></div>
<div class="summary-card"><span class="summary-value">""" + str(total_png) + """</span><span class="summary-label">PNG diagrams</span></div>
<div class="summary-card"><span class="summary-value">""" + str(total_jpg) + """</span><span class="summary-label">JPG/JPEG diagrams</span></div>
<div class="summary-card"><span class="summary-value">""" + str(category_count) + """</span><span class="summary-label">categories</span></div>
</section>
<section class="tools" aria-label="Document tools">
<div><label class="search-label" for="document-search">Search documents</label><input class="search-input" id="document-search" type="search" placeholder="Search by name, label, format, or path" autocomplete="off"></div>
<p class="result-count" id="result-count" aria-live="polite">Showing """ + str(total_documents + total_png + total_jpg) + """ of """ + str(total_documents + total_png + total_jpg) + """ assets</p>
<nav class="jump" aria-label="Jump to category"><span class="jump-title">Jump to</span>""")

        if cornell_paths:
            handle.write('<a href="#category-cornell-notes">Cornell Notes</a>')
        if non_cornell_paths:
            handle.write('<a href="#category-other-pdfs">Other PDFs</a>')
        handle.write('</nav></section><section class="library" aria-label="Published documents">')

        handle.write(_heading(2, "Documents"))

        if cornell_paths:
            handle.write(_heading(3, "Cornell Notes", anchor="category-cornell-notes"))
            _emit_directory_tree(handle, cornell_paths, depth=1, level=4)

        if non_cornell_paths:
            handle.write(_heading(3, "Other PDFs", anchor="category-other-pdfs"))
            _emit_links(handle, non_cornell_paths)

        if not pdf_rel_paths:
            handle.write("<p>No PDFs are currently staged for publication.</p>")

        handle.write(_heading(2, "PlantUML Diagrams"))
        _emit_raster_cards(handle)

        handle.write("""</section>
</main>
<footer><div class="shell">""" + str(total_documents) + """ PDFs and """ + str(total_png + total_jpg) + """ diagrams published</div></footer>
<script>
(function () {
    const input = document.getElementById('document-search');
    const count = document.getElementById('result-count');
    const rows = Array.from(document.querySelectorAll('.document-row, .image-card'));
    function update() {
        const query = (input ? input.value : '').trim().toLocaleLowerCase();
        let visible = 0;
        rows.forEach(function (row) {
            const searchText = (row.dataset.search || '').toLocaleLowerCase();
            const matches = !query || searchText.includes(query);
            row.hidden = !matches;
            if (matches) visible += 1;
        });
        count.textContent = 'Showing ' + visible + ' of ' + rows.length + ' assets';
    }
    if (input) {
        input.addEventListener('input', update);
        input.addEventListener('keydown', function (event) { if (event.key === 'Escape') { input.value = ''; update(); } });
    }
}());
</script>
</body></html>""")

    return pdf_rel_paths


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_raster_corpus(
    source_dir: Path | None,
    output_dir: Path,
    manifest_path: Path | None = None,
    *,
    require_nonempty: bool = False,
) -> dict[str, Any]:
    source_root = _resolve_repo_path(source_dir or SRC_DIR)
    output_root = _resolve_repo_path(output_dir)
    if source_root is None or output_root is None:
        raise ValueError("source and output directories are required")
    if not source_root.exists():
        raise FileNotFoundError(source_root)

    source_root = source_root.resolve()
    output_root = output_root.resolve()
    repo_root = ROOT.resolve()
    reset_output_tree(output_root)

    counts: Counter[str] = Counter({"png": 0, "jpg": 0, "jpeg": 0})
    files: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    seen_portable_paths: set[str] = set()

    for source in sorted(source_root.rglob("*"), key=lambda path: path.as_posix()):
        if source.is_symlink() and not source.exists():
            raise ValueError(f"broken raster symlink: {source}")
        if not source.is_file():
            continue
        suffix = source.suffix.lower()
        if suffix not in RASTER_SUFFIXES:
            continue

        resolved_source = source.resolve()
        try:
            resolved_source.relative_to(source_root)
        except ValueError as exc:
            raise ValueError(f"unsafe raster path escapes source root: {source}") from exc

        try:
            rel_path = source.relative_to(repo_root)
        except ValueError:
            rel_path = Path(source_root.name) / source.relative_to(source_root)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            raise ValueError(f"unsafe raster destination path: {rel_path}")

        rel_posix = rel_path.as_posix()
        portable_rel_posix = rel_posix.casefold()
        if rel_posix in seen_paths or portable_rel_posix in seen_portable_paths:
            raise ValueError(f"duplicate raster destination path: {rel_posix}")
        seen_paths.add(rel_posix)
        seen_portable_paths.add(portable_rel_posix)

        target = output_root / rel_path
        try:
            target.resolve().relative_to(output_root)
        except ValueError as exc:
            raise ValueError(f"unsafe raster destination path: {rel_path}") from exc
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

        stat = target.stat()
        kind = RASTER_SUFFIXES[suffix]
        counts[kind] += 1
        files.append({"path": rel_posix, "size": stat.st_size, "sha256": _sha256_file(target)})

    if require_nonempty and not files:
        raise ValueError(f"no raster files found under {source_root}")

    manifest = {
        "source_dir": source_root.relative_to(repo_root).as_posix() if source_root.is_relative_to(repo_root) else str(source_root),
        "output_dir": output_root.relative_to(repo_root).as_posix() if output_root.is_relative_to(repo_root) else str(output_root),
        "total": len(files),
        "counts": {key: counts[key] for key in ("png", "jpg", "jpeg")},
        "files": files,
    }
    if manifest_path is not None:
        resolved_manifest_path = _resolve_repo_path(manifest_path)
        if resolved_manifest_path is None:
            raise ValueError("manifest path is required")
        resolved_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def build_root(
    tex_path: Path,
    output_dir: Path | None = None,
    log_dir: Path | None = None,
    artifact_dir: Path | None = None,
) -> int:
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
        try:
            native_log_copy_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_log_path, native_log_copy_path)
        except OSError:
            pass

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


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(resolved)


def _prune_success_logs(tex_path: Path, log_dir: Path | None) -> None:
    """Drop per-document logs for a successful build.

    A full build produces three log files per root. At ~3,000 roots that is
    ~9,000 files of no diagnostic value that dominate artifact compression and
    upload time. Failure logs are always retained by ``report_failure``.
    """
    if log_dir is None:
        return
    stdout_path, stderr_path = _log_paths(tex_path, log_dir)
    for candidate in (stdout_path, stderr_path, _native_log_copy_path(tex_path, log_dir)):
        if candidate is None:
            continue
        try:
            candidate.unlink(missing_ok=True)
        except OSError:
            pass


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
    shard_index: int = 0,
    shard_total: int = 1,
    skipped_count: int = 0,
    cache_hits: int = 0,
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

    started = time.perf_counter()
    durations: dict[str, float] = {}

    def run_one(tex_path: Path) -> tuple[Path, int, float]:
        job_started = time.perf_counter()
        try:
            result_code = build_root(tex_path, output_dir=output_dir, log_dir=log_dir, artifact_dir=artifact_dir)
        except Exception as exc:  # one bad document must not abort the shard
            print(f"Unexpected build error for {tex_path}: {exc!r}", file=sys.stderr)
            result_code = 3
        return tex_path, result_code, time.perf_counter() - job_started

    results: List[tuple[Path, int, float]] = []
    if jobs <= 1:
        results = [run_one(tex_path) for tex_path in tex_paths]
    else:
        with ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
            results = list(executor.map(run_one, tex_paths))

    failure_count = 0
    for tex_path, result_code, duration in results:
        durations[_repo_relative(tex_path)] = round(duration, 3)
        if result_code != 0:
            failure_count += 1
            report_failure(tex_path, result_code)
        else:
            _prune_success_logs(tex_path, log_dir)

    wall_clock = time.perf_counter() - started
    compile_seconds = sum(durations.values())

    print(
        f"Build summary: {len(tex_paths) - failure_count} succeeded, {failure_count} failed, "
        f"{len(tex_paths)} total in {wall_clock:.1f}s wall / {compile_seconds:.1f}s compile",
        file=sys.stderr,
    )

    exit_code = 0
    cluster_counts = Counter(detail.get("signature", "UNKNOWN") for _, _, detail in failures)
    if failure_count:
        print("Failure clusters:", file=sys.stderr)
        for signature, count in cluster_counts.most_common(10):
            print(f"  {count} x {signature}", file=sys.stderr)
        exit_code = 1

    slowest = sorted(durations.items(), key=lambda item: -item[1])[:25]
    summary = BuildSummary(
        mode=mode,
        base_revision=base_revision,
        head_revision=head_revision,
        root_count=len(tex_paths),
        attempted_count=len(tex_paths),
        succeeded_count=len(tex_paths) - failure_count,
        failed_count=failure_count,
        skipped_count=skipped_count,
        pdf_count=_count_files(output_dir, "*.pdf"),
        log_count=_count_files(log_dir),
        build_status=_normalize_build_status(exit_code),
        first_errors=[
            {
                "root": _repo_relative(tex_path),
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
        shard_index=shard_index,
        shard_total=shard_total,
        wall_clock_seconds=round(wall_clock, 3),
        compile_seconds=round(compile_seconds, 3),
        durations=durations,
        timing_stats=_timing_stats(list(durations.values())),
        slowest_roots=[{"root": source, "seconds": seconds} for source, seconds in slowest],
        cache_hits=cache_hits,
        cache_misses=len(tex_paths),
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

    changed_paths = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if head_ref is None:
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        if untracked.returncode != 0:
            detail = (untracked.stderr or untracked.stdout or "git ls-files failed").strip().splitlines()[-1]
            raise RevisionResolutionError(f"unable to discover untracked changed paths: {detail}")
        changed_paths.update(line.strip() for line in untracked.stdout.splitlines() if line.strip())

    return sorted(changed_paths)


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

    # Dependency-aware selection: a changed path selects the roots that
    # transitively depend on it (styles, inputs, graphics, bibliographies),
    # not merely roots whose own .tex file changed.
    graph = build_graph.build_graph(roots, toolchain_version=build_graph.toolchain_version())
    selected_sources, reason = build_graph.select_affected(graph, changed_paths)
    unique_roots = [ROOT / source for source in selected_sources]
    print(
        f"Changed-root selection ({reason}): {len(unique_roots)} of {len(roots)} roots "
        f"from {len(changed_paths)} changed paths",
        file=sys.stderr,
    )
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
        skipped_count=len(roots) - len(unique_roots),
    )


def _selection_for_plan(
    graph: "build_graph.DependencyGraph",
    mode: str,
    base_ref: str | None,
    head_ref: str | None,
) -> tuple[list[str], str]:
    if mode == "full":
        return graph.root_sources(), "full"
    changed_paths = collect_changed_paths(base_ref=base_ref, head_ref=head_ref)
    selected, reason = build_graph.select_affected(graph, changed_paths)
    return selected, reason


def plan_build(
    *,
    mode: str = "changed",
    base_ref: str | None = None,
    head_ref: str | None = None,
    max_shards: int = 12,
    min_roots_per_shard: int = 25,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Produce the build plan (affected roots, shard matrix, manifest).

    Runs without any TeX dependency so the CI planning job stays cheap.
    """
    toolchain = build_graph.toolchain_version()
    weights = build_graph.load_timing_history(TIMING_HISTORY_PATH)
    graph = build_graph.build_graph(toolchain_version=toolchain, weights=weights)

    selected, reason = _selection_for_plan(graph, mode, base_ref, head_ref)
    by_source = graph.by_source()
    records = [by_source[source] for source in selected if source in by_source]

    shards = build_graph.plan_shards(records, max_shards, min_roots_per_shard=min_roots_per_shard)
    matrix = [
        {
            "index": index,
            "name": f"shard-{index:02d}",
            "roots": [record.source for record in bucket],
            "count": len(bucket),
            "estimated_seconds": round(sum(record.weight for record in bucket), 2),
        }
        for index, bucket in enumerate(shards)
    ]

    plan = {
        "mode": mode,
        "reason": reason,
        "base_ref": base_ref or "",
        "head_ref": head_ref or "",
        "toolchain_version": toolchain,
        "build_config_version": build_graph.BUILD_CONFIG_VERSION,
        "total_roots": len(graph.roots),
        "selected_roots": len(records),
        "skipped_roots": len(graph.roots) - len(records),
        "shard_count": len(matrix),
        "estimated_total_seconds": round(sum(record.weight for record in records), 2),
        "estimated_wall_seconds": round(max((entry["estimated_seconds"] for entry in matrix), default=0.0), 2),
        "timing_history_entries": len(weights),
        "shards": matrix,
        "expected_pdfs": sorted(record.pdf for record in graph.roots),
        "manifest": [
            {
                "source": record.source,
                "pdf": record.pdf,
                "category": record.category,
                "fingerprint": record.fingerprint,
                "dependencies": record.dependencies,
                "selected": record.source in set(selected),
            }
            for record in graph.roots
        ],
    }

    if output_path is not None:
        output_path = _resolve_repo_path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return plan


def verify_corpus(pdf_dir: Path, plan_path: Path, *, prune: bool = True) -> int:
    """Validate the published PDF corpus against the expected root manifest.

    Removes PDFs belonging to deleted or renamed roots and fails when an
    expected PDF is missing, so an incomplete corpus can never be deployed as
    though it were complete.
    """
    pdf_dir = _resolve_repo_path(pdf_dir)
    plan = json.loads(_resolve_repo_path(plan_path).read_text(encoding="utf-8"))
    expected = set(plan.get("expected_pdfs", []))

    present = {
        path.relative_to(pdf_dir).as_posix()
        for path in pdf_dir.rglob("*.pdf")
        if path.is_file()
    } if pdf_dir.exists() else set()

    stale = sorted(present - expected)
    missing = sorted(expected - present)

    if prune:
        for rel in stale:
            try:
                (pdf_dir / rel).unlink()
            except OSError:
                pass
        for directory in sorted((path for path in pdf_dir.rglob("*") if path.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass

    print(f"Corpus verification: expected={len(expected)} present={len(present)} stale={len(stale)} missing={len(missing)}", file=sys.stderr)
    for rel in missing[:25]:
        print(f"  missing: {rel}", file=sys.stderr)
    for rel in stale[:25]:
        print(f"  stale (removed): {rel}", file=sys.stderr)

    return 1 if missing else 0


def plan_outputs(plan_path: Path, *, markdown: bool = False) -> str:
    """Render a plan as GitHub Actions step outputs or a job-summary table."""
    plan = json.loads(_resolve_repo_path(plan_path).read_text(encoding="utf-8"))

    if not markdown:
        matrix = {
            "shard": [
                {"index": shard["index"], "name": shard["name"], "count": shard["count"]}
                for shard in plan["shards"]
            ]
        }
        return "\n".join(
            [
                "matrix=" + json.dumps(matrix, separators=(",", ":")),
                f"shard-count={len(plan['shards'])}",
                f"selected-roots={plan['selected_roots']}",
                f"total-roots={plan['total_roots']}",
            ]
        )

    rows = [
        ("Mode", plan["mode"]),
        ("Selection reason", plan["reason"]),
        ("Total roots", plan["total_roots"]),
        ("Selected roots", plan["selected_roots"]),
        ("Skipped roots", plan["skipped_roots"]),
        ("Shards", plan["shard_count"]),
        ("Estimated shard wall time (s)", plan["estimated_wall_seconds"]),
        ("Estimated total compile time (s)", plan["estimated_total_seconds"]),
        ("Timing history entries", plan["timing_history_entries"]),
        ("Toolchain version", plan["toolchain_version"]),
    ]
    lines = ["### LaTeX build plan", "", "| Metric | Value |", "| --- | --- |"]
    lines.extend(f"| {label} | {value} |" for label, value in rows)
    return "\n".join(lines)


def check_corpus_manifest(manifest_path: Path, plan_path: Path) -> int:
    """Verify a cached corpus manifest covers every currently expected PDF.

    Returns 0 when an incremental publish is safe, 1 when the caller must
    promote to a full rebuild. Any doubt resolves to "rebuild".
    """
    manifest_path = _resolve_repo_path(manifest_path)
    if not manifest_path.is_file():
        print("No cached corpus manifest; full rebuild required.", file=sys.stderr)
        return 1
    try:
        have = set(json.loads(manifest_path.read_text(encoding="utf-8"))["pdfs"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Unreadable corpus manifest ({exc}); full rebuild required.", file=sys.stderr)
        return 1

    want = set(json.loads(_resolve_repo_path(plan_path).read_text(encoding="utf-8"))["expected_pdfs"])
    missing = want - have
    if missing:
        print(f"Cached corpus is missing {len(missing)} of {len(want)} expected PDFs; full rebuild required.", file=sys.stderr)
        return 1

    print(f"Cached corpus covers all {len(want)} expected PDFs; incremental publish is safe.", file=sys.stderr)
    return 0


def aggregate_shards(
    *,
    plan_path: Path,
    logs_dir: Path,
    pdf_dir: Path,
    output_dir: Path,
    manifest_path: Path | None = None,
    shard_result: str = "success",
    require_complete_corpus: bool = False,
) -> int:
    """Merge shard summaries, validate the corpus and emit the build report."""
    plan = json.loads(_resolve_repo_path(plan_path).read_text(encoding="utf-8"))
    logs_dir = _resolve_repo_path(logs_dir)
    pdf_dir = _resolve_repo_path(pdf_dir)
    output_dir = _resolve_repo_path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []
    if logs_dir.exists():
        for summary_path in sorted(logs_dir.rglob("build-summary.json")):
            try:
                summaries.append(json.loads(summary_path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue

    attempted = sum(int(item.get("attempted_count", 0)) for item in summaries)
    succeeded = sum(int(item.get("succeeded_count", 0)) for item in summaries)
    failed = sum(int(item.get("failed_count", 0)) for item in summaries)
    compile_seconds = sum(float(item.get("compile_seconds", 0.0)) for item in summaries)
    wall_seconds = max((float(item.get("wall_clock_seconds", 0.0)) for item in summaries), default=0.0)

    first_errors: list[dict[str, Any]] = []
    clusters: Counter[str] = Counter()
    durations: dict[str, float] = {}
    for item in summaries:
        first_errors.extend(item.get("first_errors", []))
        for cluster in item.get("failure_clusters", []):
            clusters[str(cluster.get("signature", "UNKNOWN"))] += int(cluster.get("count", 0))
        durations.update(item.get("durations", {}))

    expected = set(plan.get("expected_pdfs", []))
    selected_pdfs = {
        entry["pdf"] for entry in plan.get("manifest", []) if entry.get("selected")
    }
    present = (
        {path.relative_to(pdf_dir).as_posix() for path in pdf_dir.rglob("*.pdf") if path.is_file()}
        if pdf_dir.exists()
        else set()
    )

    # Roots removed or renamed since the cached corpus was produced must not
    # linger in the published site.
    stale = sorted(present - expected)
    for rel in stale:
        try:
            (pdf_dir / rel).unlink()
        except OSError:
            pass
    if pdf_dir.exists():
        for directory in sorted((path for path in pdf_dir.rglob("*") if path.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass
        present = {path.relative_to(pdf_dir).as_posix() for path in pdf_dir.rglob("*.pdf") if path.is_file()}

    missing_selected = sorted(selected_pdfs - present)
    missing_corpus = sorted(expected - present)

    shards_expected = len(plan.get("shards", []))
    shards_reported = len(summaries)

    problems: list[str] = []
    if shard_result not in {"success", "skipped"}:
        problems.append(f"one or more build shards reported `{shard_result}`")
    if failed:
        problems.append(f"{failed} document(s) failed to compile")
    if shards_reported < shards_expected:
        problems.append(f"only {shards_reported} of {shards_expected} shards reported results")
    if missing_selected:
        problems.append(f"{len(missing_selected)} selected document(s) produced no PDF")
    if require_complete_corpus and missing_corpus:
        problems.append(f"published corpus is missing {len(missing_corpus)} PDF(s)")

    status = "failed" if problems else "success"

    if status == "success" and manifest_path is not None:
        manifest_path = _resolve_repo_path(manifest_path)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps({"commit": os.environ.get("GITHUB_SHA", ""), "pdfs": sorted(present)}, indent=0, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    aggregate = {
        "status": status,
        "mode": plan.get("mode"),
        "reason": plan.get("reason"),
        "total_roots": plan.get("total_roots", 0),
        "selected_roots": plan.get("selected_roots", 0),
        "skipped_roots": plan.get("skipped_roots", 0),
        "attempted_roots": attempted,
        "succeeded_roots": succeeded,
        "failed_roots": failed,
        "shards_expected": shards_expected,
        "shards_reported": shards_reported,
        "expected_pdfs": len(expected),
        "present_pdfs": len(present),
        "stale_pdfs_removed": stale,
        "missing_selected_pdfs": missing_selected,
        "missing_corpus_pdfs": missing_corpus[:100],
        "missing_corpus_pdf_count": len(missing_corpus),
        "shard_wall_seconds": round(wall_seconds, 2),
        "compile_seconds": round(compile_seconds, 2),
        "runner_minutes_estimate": round(compile_seconds / 60.0, 2),
        "slowest_roots": [
            {"root": source, "seconds": seconds}
            for source, seconds in sorted(durations.items(), key=lambda item: -item[1])[:25]
        ],
        "failure_clusters": [{"signature": signature, "count": count} for signature, count in clusters.most_common()],
        "first_errors": first_errors[:100],
        "problems": problems,
    }

    (output_dir / "build-aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        f"### LaTeX build result: **{status}**",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Mode | {aggregate['mode']} ({aggregate['reason']}) |",
        f"| Total roots | {aggregate['total_roots']} |",
        f"| Selected roots | {aggregate['selected_roots']} |",
        f"| Skipped (unaffected) roots | {aggregate['skipped_roots']} |",
        f"| Attempted | {attempted} |",
        f"| Succeeded | {succeeded} |",
        f"| Failed | {failed} |",
        f"| Shards reported | {shards_reported}/{shards_expected} |",
        f"| PDFs present / expected | {len(present)}/{len(expected)} |",
        f"| Stale PDFs removed | {len(stale)} |",
        f"| Missing corpus PDFs | {len(missing_corpus)} |",
        f"| Slowest shard wall time | {aggregate['shard_wall_seconds']}s |",
        f"| Total compile time | {aggregate['compile_seconds']}s |",
    ]
    if problems:
        report += ["", "#### Problems", ""] + [f"- {problem}" for problem in problems]
    if aggregate["failure_clusters"]:
        report += ["", "#### Failure clusters", "", "| Count | Signature |", "| --- | --- |"]
        report += [f"| {item['count']} | {item['signature'][:180]} |" for item in aggregate["failure_clusters"][:15]]
    if aggregate["slowest_roots"]:
        report += ["", "<details><summary>Slowest 25 documents</summary>", "", "| Seconds | Root |", "| --- | --- |"]
        report += [f"| {item['seconds']} | {item['root']} |" for item in aggregate["slowest_roots"]]
        report += ["", "</details>"]

    (output_dir / "build-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:20]), file=sys.stderr)

    return 1 if problems else 0


def _plantuml_config_for(path: Path, config_names: Sequence[str]) -> Path | None:
    current = path.parent
    while current != current.parent:
        for config_name in config_names:
            candidate = current / config_name
            if candidate.exists():
                return candidate
        current = current.parent
    return None


PLANTUML_MANIFEST = ROOT / "tooling" / "manifests" / "plantuml.json"
PLANTUML_FORMATS = ("png", "svg", "jpg")
PLANTUML_INCLUDE_DIRS = (ROOT / "tooling" / "plantuml", ROOT / "tooling" / "styles" / "plantuml")
PLANTUML_EXAMPLES_DIR = ROOT / "tooling" / "plantuml"
# PlantUML draws these into the image instead of failing; the SVG text uses U+00A0 for spaces.
PLANTUML_ERROR_TEXT = re.compile(
    r"Syntax Error|Please use CSS style|cannot include|Cannot include|"
    r"file does not exist|No such file|Error line \d+",
    re.IGNORECASE,
)
_PLANTUML_VERSION_RE = re.compile(r"PlantUML version (\S+)")
_STARTUML_RE = re.compile(r"^@startuml[ \t]*([^\s]*)[ \t]*$", re.MULTILINE)


def load_plantuml_pin(manifest: Path | None = None) -> dict[str, str]:
    data = json.loads((manifest or PLANTUML_MANIFEST).read_text(encoding="utf-8"))
    missing = [key for key in ("version", "jar_url", "sha256") if not data.get(key)]
    if missing:
        raise ValueError(f"{manifest or PLANTUML_MANIFEST}: missing {', '.join(missing)}")
    return data


def plantuml_command_prefix(env: dict[str, str] | None = None) -> list[str]:
    """PLANTUML_JAR wins so CI and local runs can point at the fetched pinned jar."""
    env = os.environ if env is None else env
    jar = env.get("PLANTUML_JAR")
    if jar:
        return ["java", "-Djava.awt.headless=true", "-jar", str(Path(jar).expanduser().resolve())]
    return ["plantuml"]


def plantuml_installed_version(prefix: Sequence[str], env: dict[str, str] | None = None) -> str | None:
    try:
        result = subprocess.run(
            [*prefix, "-version"], env=env, check=False, capture_output=True, text=True, timeout=120
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = _PLANTUML_VERSION_RE.search(result.stdout + result.stderr)
    return match.group(1) if match else None


def check_plantuml_engine(env: dict[str, str] | None = None, *, pin: dict[str, str] | None = None) -> str | None:
    """Return an error message unless the selected PlantUML binary is the pinned version."""
    pin = pin or load_plantuml_pin()
    prefix = plantuml_command_prefix(env)
    found = plantuml_installed_version(prefix, env)
    if found == pin["version"]:
        return None
    hint = "set PLANTUML_JAR to the jar produced by `latex_build.py fetch-plantuml`"
    if found is None:
        return f"PlantUML {pin['version']} is required but `{' '.join(prefix)}` did not run; {hint}"
    return f"PlantUML {pin['version']} is required but `{' '.join(prefix)}` is {found}; {hint}"


def _plantuml_output_names(source: Path, text: str) -> list[str]:
    """PlantUML names each output after `@startuml <name>`, else the file stem (then stem_001, ...)."""
    names: list[str] = []
    for index, match in enumerate(_STARTUML_RE.finditer(text)):
        explicit = match.group(1)
        if explicit and (explicit in {".", ".."} or "/" in explicit or "\\" in explicit):
            explicit = ""
        names.append(explicit if explicit else (source.stem if index == 0 else f"{source.stem}_{index:03d}"))
    return names


def plantuml_output_paths(source: Path, fmt: str, text: str | None = None) -> list[Path]:
    if text is None:
        text = source.read_text(encoding="utf-8", errors="ignore")
    return [source.parent / fmt / f"{name}.{fmt}" for name in _plantuml_output_names(source, text)]


def plantuml_render_command(prefix: Sequence[str], fmt: str, output_dir: Path, config: Path | None, names: Sequence[str]) -> list[str]:
    # An absolute -o is used verbatim; a relative one is joined to each source's directory,
    # which is how src/**/src/** trees were produced by runs started from the repository root.
    cmd = [*prefix, "-failfast2", f"-t{fmt}", "-o", str(output_dir.resolve())]
    if config is not None:
        cmd.extend(["-config", str(config)])
    cmd.extend(names)
    return cmd


def svg_error_text(path: Path) -> str | None:
    """First PlantUML error/deprecation phrase drawn into an SVG, after normalising U+00A0."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").replace("\u00a0", " ")
    except OSError:
        return None
    match = PLANTUML_ERROR_TEXT.search(text)
    return match.group(0) if match else None


def _plantuml_is_current(
    source: Path,
    config: Path | None,
    outputs: Sequence[Path],
    style_inputs: Sequence[Path] = (),
) -> bool:
    """Whether every rendered output is newer than the diagram and its config."""
    try:
        newest_input = source.stat().st_mtime
        if config is not None:
            newest_input = max(newest_input, config.stat().st_mtime)
        for style_input in style_inputs:
            if style_input.is_file():
                newest_input = max(newest_input, style_input.stat().st_mtime)
        return all(output.exists() and output.stat().st_mtime >= newest_input for output in outputs)
    except OSError:
        return False


def unmanaged_diagram_images(source_dirs: Iterable[Path]) -> list[Path]:
    """Image files sitting beside a .puml instead of in its png/svg/jpg directory."""
    found: list[Path] = []
    for directory in source_dirs:
        if not directory.is_dir():
            continue
        for candidate in directory.iterdir():
            if candidate.is_file() and candidate.suffix.lower().lstrip(".") in PLANTUML_FORMATS:
                found.append(candidate)
    return found


def render_plantuml(
    source_dir: Path | None = None,
    formats: Sequence[str] | None = None,
    *,
    force: bool = False,
) -> int:
    """Render PlantUML diagrams incrementally, batching JVM invocations.

    Two costs dominated the previous implementation: it spawned one JVM per
    (diagram x format) pair, and it re-rendered the whole corpus even when
    nothing had changed. Diagrams whose committed output is already newer than
    their source, config and the shared style modules are skipped, and the rest
    are rendered in batches that share a single JVM start.
    """
    search_root = (source_dir or SRC_DIR).resolve()
    if not search_root.exists():
        return 0

    env = os.environ.copy()
    engine_error = check_plantuml_engine(env)
    if engine_error:
        print(f"Configuration error: {engine_error}", file=sys.stderr)
        return 2
    prefix = plantuml_command_prefix(env)

    config_names = ["plantuml-config.puml", "config.puml"]
    lowered_config_names = {name.lower() for name in config_names}
    formats = list(formats or ["png", "svg"])
    unknown = [fmt for fmt in formats if fmt not in PLANTUML_FORMATS]
    if unknown:
        print(f"Configuration error: unsupported PlantUML format(s) {unknown}", file=sys.stderr)
        return 2

    include_paths = [path for path in PLANTUML_INCLUDE_DIRS if path.exists()]
    style_inputs = [path for root in include_paths for path in root.rglob("*.iuml") if path.is_file()]
    # The pin is an input too: a version bump must re-render everything.
    if PLANTUML_MANIFEST.exists():
        style_inputs.append(PLANTUML_MANIFEST)
    env["PLANTUML_INCLUDE_PATH"] = ":".join(str(path) for path in include_paths)

    # Batch key: (source directory, config, format); every batched file shares
    # a directory, so one absolute -o per batch keeps outputs beside sources.
    batches: dict[tuple[Path, str, str], list[str]] = {}
    expected_outputs: dict[Path, set[Path]] = {}
    source_dirs: set[Path] = set()
    diagram_count = 0
    skipped = 0
    invalid_names: list[Path] = []

    for path in sorted(search_root.rglob("*.puml")):
        if not path.is_file() or path.name.lower() in lowered_config_names:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not _STARTUML_RE.search(text):
            continue

        diagram_count += 1
        source_dirs.add(path.parent)
        if any(
            match.group(1)
            and (match.group(1) in {".", ".."} or "/" in match.group(1) or "\\" in match.group(1))
            for match in _STARTUML_RE.finditer(text)
        ):
            invalid_names.append(path)
            continue
        config_path = _plantuml_config_for(path, config_names)

        for fmt in formats:
            outputs = plantuml_output_paths(path, fmt, text)
            expected_outputs.setdefault(path.parent / fmt, set()).update(outputs)
            if not force and _plantuml_is_current(path, config_path, outputs, style_inputs):
                skipped += 1
                continue
            (path.parent / fmt).mkdir(parents=True, exist_ok=True)
            key = (path.parent, str(config_path) if config_path else "", fmt)
            batches.setdefault(key, []).append(path.name)

    failures = len(invalid_names)
    for path in invalid_names:
        print(f"PlantUML failed in {path}: @startuml name must not contain a path separator", file=sys.stderr)
    rendered = 0
    for (work_dir, config, fmt), names in sorted(batches.items(), key=lambda item: str(item[0])):
        with tempfile.TemporaryDirectory(prefix="plantuml-") as temp_dir:
            temp_output = Path(temp_dir)
            cmd = plantuml_render_command(
                prefix, fmt, temp_output, Path(config) if config else None, names
            )
            result = subprocess.run(
                cmd,
                cwd=str(work_dir),
                env=env,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            detail = (result.stderr or b"").decode("utf-8", errors="ignore").strip().splitlines()
            expected_names = [
                output.name
                for name in names
                for output in plantuml_output_paths(work_dir / name, fmt)
            ]
            missing = [name for name in expected_names if not (temp_output / name).is_file()]
            errors = [
                name for name in expected_names
                if fmt == "svg" and svg_error_text(temp_output / name)
            ]
            if result.returncode != 0 or missing or errors:
                failures += 1
                reason = detail[-1] if detail else "renderer failed"
                if missing:
                    reason = f"missing output(s): {', '.join(missing)}"
                elif errors:
                    reason = f"error text in {errors[0]}: {svg_error_text(temp_output / errors[0])}"
                print(f"PlantUML failed in {work_dir} ({fmt}): {reason}", file=sys.stderr)
                continue
            for name in expected_names:
                destination = work_dir / fmt / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(temp_output / name, destination)
            rendered += len(names)

    # Files in a png/svg/jpg directory that no source produces (e.g. left over from a
    # renamed @startuml) are reported, never deleted: deletion is a reviewed change.
    orphans = sorted(
        candidate
        for output_dir, produced in expected_outputs.items()
        if output_dir.is_dir()
        for candidate in output_dir.glob(f"*.{output_dir.name}")
        if candidate not in produced
    )
    for orphan in orphans:
        print(f"PlantUML: stale output without a source: {orphan.relative_to(ROOT) if orphan.is_relative_to(ROOT) else orphan}", file=sys.stderr)

    # Every render writes into <source>/png|svg|jpg, so an image sitting directly
    # beside a .puml came from an earlier flat-output run: it is never refreshed,
    # revalidated or overwritten here and will keep serving whatever it last held.
    unmanaged = sorted(unmanaged_diagram_images(source_dirs))
    for stale in unmanaged:
        print(
            f"PlantUML: image outside a managed output directory: "
            f"{stale.relative_to(ROOT) if stale.is_relative_to(ROOT) else stale}",
            file=sys.stderr,
        )

    print(
        f"PlantUML: {diagram_count} diagrams, {rendered} rendered, {skipped} already current, "
        f"{len(batches)} JVM invocations, {failures} failed batches, {len(orphans)} stale outputs, "
        f"{len(unmanaged)} unmanaged images",
        file=sys.stderr,
    )
    return 1 if failures else 0


def fetch_plantuml(dest: Path | None = None, *, pin: dict[str, str] | None = None) -> Path:
    """Download the pinned PlantUML jar into dest (default .build-cache) and verify its sha256."""
    pin = pin or load_plantuml_pin()
    version = pin["version"]
    target = dest or ROOT / ".build-cache" / "plantuml" / f"plantuml-{version}.jar"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not (target.exists() and _sha256_file(target) == pin["sha256"]):
        from urllib.request import urlopen

        url = pin["jar_url"].format(version=version)
        with urlopen(url, timeout=300) as response:  # noqa: S310 (https release URL from the manifest)
            data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != pin["sha256"]:
            raise ValueError(f"PlantUML {version} checksum mismatch: expected {pin['sha256']}, got {digest}")
        target.write_bytes(data)
    return target


def smoke_plantuml(output_dir: Path, examples_dir: Path | None = None) -> int:
    """Render the framework examples to output_dir with the pinned engine; fail on any error text."""
    examples_dir = examples_dir or PLANTUML_EXAMPLES_DIR
    env = os.environ.copy()
    engine_error = check_plantuml_engine(env)
    if engine_error:
        print(f"Configuration error: {engine_error}", file=sys.stderr)
        return 2
    env["PLANTUML_INCLUDE_PATH"] = ":".join(str(path) for path in PLANTUML_INCLUDE_DIRS if path.exists())
    examples = sorted(examples_dir.glob("*-example.puml"))
    if not examples:
        print(f"Configuration error: no *-example.puml under {examples_dir}", file=sys.stderr)
        return 2
    expected = [output_dir / output.name for example in examples for output in plantuml_output_paths(example, "svg")]
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = plantuml_render_command(plantuml_command_prefix(env), "svg", output_dir, None, [str(path) for path in examples])
    result = subprocess.run(cmd, cwd=str(examples_dir), env=env, check=False, capture_output=True, text=True)
    problems: list[str] = []
    if result.returncode != 0:
        problems.append(f"plantuml exited {result.returncode}: {result.stderr.strip().splitlines()[-1:] or result.stdout.strip()[-200:]}")
    clean = 0
    for output in expected:
        if not output.exists():
            problems.append(f"missing output {output.name}")
            continue
        phrase = svg_error_text(output)
        if phrase:
            problems.append(f"{output.name} contains {phrase!r}")
        else:
            clean += 1
    for problem in problems:
        print(f"PlantUML smoke: {problem}", file=sys.stderr)
    print(f"PlantUML smoke: {len(examples)} examples, {clean} clean outputs, {len(problems)} problems", file=sys.stderr)
    return 1 if problems else 0


def generated_image_paths(repo_root: Path, source_dir: str = "src", formats: Sequence[str] = PLANTUML_FORMATS) -> list[str]:
    """Tracked and untracked files matching <source_dir>/**/<fmt>/*.<fmt>, as repo-relative POSIX paths."""

    def git_paths(*args: str) -> list[str]:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z", *args, "--", source_dir],
            check=True,
            capture_output=True,
        )
        return [entry.decode("utf-8", errors="surrogateescape") for entry in result.stdout.split(b"\0") if entry]

    candidates = set(git_paths()) | set(git_paths("--others", "--exclude-standard"))
    selected = []
    for rel in candidates:
        parts = rel.split("/")
        if len(parts) >= 3 and parts[-2] in formats and parts[-1].lower().endswith(f".{parts[-2]}"):
            selected.append(rel)
    return sorted(selected)


def stage_generated_images(repo_root: Path, source_dir: str = "src", formats: Sequence[str] = PLANTUML_FORMATS) -> list[str]:
    """Stage additions, modifications and deletions of generated diagram images only.

    A literal `git add 'src/**/jpg/*.jpg'` aborts the whole add when one optional
    format has no files, so concrete NUL-separated paths are passed instead.
    Returns the staged entries as `<status>\t<path>` lines.
    """
    paths = generated_image_paths(repo_root, source_dir, formats)
    if paths:
        subprocess.run(
            ["git", "-C", str(repo_root), "add", "-A", "--pathspec-from-file=-", "--pathspec-file-nul"],
            input="\0".join(paths).encode("utf-8", errors="surrogateescape"),
            check=True,
        )
    staged = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--name-status", "-z", "--", source_dir],
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    entries = []
    it = iter(entry.decode("utf-8", errors="surrogateescape") for entry in staged if entry)
    for status in it:
        path = next(it, "")
        if status.startswith("R") or status.startswith("C"):
            path = next(it, path)
        entries.append(f"{status}\t{path}")
    return entries


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

    plan_parser = subparsers.add_parser("plan", help="Emit the affected-root set and shard matrix (no TeX required)")
    plan_parser.add_argument("--mode", choices=["changed", "full"], default="changed")
    plan_parser.add_argument("--base", dest="base_ref", default=None)
    plan_parser.add_argument("--head", dest="head_ref", default=None)
    plan_parser.add_argument("--max-shards", type=int, default=12)
    plan_parser.add_argument("--min-roots-per-shard", type=int, default=25)
    plan_parser.add_argument("--output", type=Path, default=None)
    plan_parser.add_argument("--emit", choices=["plan", "matrix", "summary"], default="summary")

    selection_parser = subparsers.add_parser("build-selection", help="Build an explicit list of roots (one shard)")
    selection_parser.add_argument("--plan", type=Path, required=True)
    selection_parser.add_argument("--shard-index", type=int, default=0)
    selection_parser.add_argument("--jobs", type=int, default=1)
    selection_parser.add_argument("--output-dir", type=Path, default=None)
    selection_parser.add_argument("--log-dir", type=Path, default=None)
    selection_parser.add_argument("--artifact-dir", type=Path, default=None)
    selection_parser.add_argument("--clean-output", action="store_true")
    selection_parser.add_argument("--mode-name", default="shard")

    verify_parser = subparsers.add_parser("verify-corpus", help="Validate published PDFs against the expected root manifest")
    verify_parser.add_argument("--pdf-dir", type=Path, required=True)
    verify_parser.add_argument("--plan", type=Path, required=True)
    verify_parser.add_argument("--no-prune", action="store_true")

    timings_parser = subparsers.add_parser("merge-timings", help="Merge shard timing reports into the persisted history")
    timings_parser.add_argument("inputs", nargs="*", type=Path)
    timings_parser.add_argument("--history", type=Path, default=TIMING_HISTORY_PATH)

    plan_outputs_parser = subparsers.add_parser("plan-outputs", help="Render plan data as GitHub Actions outputs or a summary table")
    plan_outputs_parser.add_argument("--plan", type=Path, required=True)
    plan_outputs_parser.add_argument("--markdown", action="store_true")

    check_manifest_parser = subparsers.add_parser("check-corpus-manifest", help="Decide whether an incremental publish is safe")
    check_manifest_parser.add_argument("--manifest", type=Path, required=True)
    check_manifest_parser.add_argument("--plan", type=Path, required=True)

    aggregate_parser = subparsers.add_parser("aggregate-shards", help="Merge shard results and validate the corpus")
    aggregate_parser.add_argument("--plan", type=Path, required=True)
    aggregate_parser.add_argument("--logs", type=Path, required=True)
    aggregate_parser.add_argument("--pdf-dir", type=Path, required=True)
    aggregate_parser.add_argument("--output", type=Path, required=True)
    aggregate_parser.add_argument("--manifest", type=Path, default=None)
    aggregate_parser.add_argument("--shard-result", default="success")
    aggregate_parser.add_argument("--require-complete-corpus", default="false")

    render_parser = subparsers.add_parser("render-plantuml")
    render_parser.add_argument("--source-dir", type=Path, default=None)
    render_parser.add_argument("--formats", nargs="*", default=["png", "svg"])
    render_parser.add_argument("--force", action="store_true", help="Re-render diagrams even when outputs are current")

    fetch_parser = subparsers.add_parser("fetch-plantuml", help="Download and checksum the pinned PlantUML jar; prints its path")
    fetch_parser.add_argument("--dest", type=Path, default=None)

    smoke_parser = subparsers.add_parser("smoke-plantuml", help="Render tooling/plantuml/*-example.puml and fail on any error text")
    smoke_parser.add_argument("--output-dir", type=Path, required=True)

    stage_parser = subparsers.add_parser("stage-plantuml-images", help="git add only generated png/svg/jpg diagram outputs")
    stage_parser.add_argument("--repo-root", type=Path, default=None)
    stage_parser.add_argument("--source-dir", default="src")

    raster_parser = subparsers.add_parser("collect-raster", help="Collect verified raster assets for artifact upload")
    raster_parser.add_argument("--source-dir", type=Path, default=SRC_DIR)
    raster_parser.add_argument("--output-dir", type=Path, required=True)
    raster_parser.add_argument("--manifest", type=Path, default=None)
    raster_parser.add_argument("--require-nonempty", action="store_true")

    stage_parser = subparsers.add_parser("stage-pages")
    stage_parser.add_argument("--pdf-dir", type=Path, required=True)
    stage_parser.add_argument("--image-dir", type=Path, default=None)
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

    if args.command == "plan":
        plan = plan_build(
            mode=args.mode,
            base_ref=args.base_ref,
            head_ref=args.head_ref,
            max_shards=args.max_shards,
            min_roots_per_shard=args.min_roots_per_shard,
            output_path=args.output,
        )
        if args.emit == "plan":
            print(json.dumps(plan, indent=2, sort_keys=True))
        elif args.emit == "matrix":
            print(json.dumps([{"index": shard["index"], "name": shard["name"], "count": shard["count"]} for shard in plan["shards"]], separators=(",", ":")))
        else:
            print(
                f"mode={plan['mode']} reason={plan['reason']} selected={plan['selected_roots']}"
                f"/{plan['total_roots']} shards={plan['shard_count']}"
                f" est_wall={plan['estimated_wall_seconds']}s"
            )
        return 0

    if args.command == "build-selection":
        plan = json.loads(_resolve_repo_path(args.plan).read_text(encoding="utf-8"))
        shards = plan.get("shards", [])
        selected = next((shard for shard in shards if shard["index"] == args.shard_index), None)
        if selected is None:
            print(f"::error::shard index {args.shard_index} is not present in the plan", file=sys.stderr)
            return 2
        roots = [ROOT / source for source in selected["roots"]]
        return build_roots(
            roots,
            jobs=args.jobs,
            output_dir=args.output_dir,
            log_dir=args.log_dir,
            artifact_dir=args.artifact_dir,
            clean_output=args.clean_output,
            mode=args.mode_name,
            base_revision=plan.get("base_ref", ""),
            head_revision=plan.get("head_ref", ""),
            shard_index=args.shard_index,
            shard_total=len(shards),
            skipped_count=plan.get("skipped_roots", 0),
        )

    if args.command == "plan-outputs":
        print(plan_outputs(args.plan, markdown=args.markdown))
        return 0

    if args.command == "check-corpus-manifest":
        return check_corpus_manifest(args.manifest, args.plan)

    if args.command == "aggregate-shards":
        return aggregate_shards(
            plan_path=args.plan,
            logs_dir=args.logs,
            pdf_dir=args.pdf_dir,
            output_dir=args.output,
            manifest_path=args.manifest,
            shard_result=args.shard_result,
            require_complete_corpus=str(args.require_complete_corpus).lower() == "true",
        )

    if args.command == "verify-corpus":
        return verify_corpus(args.pdf_dir, args.plan, prune=not args.no_prune)

    if args.command == "merge-timings":
        history_path = _resolve_repo_path(args.history)
        history = build_graph.load_timing_history(history_path)
        observed: dict[str, float] = {}
        for input_path in args.inputs:
            resolved = _resolve_repo_path(input_path)
            candidates = sorted(resolved.rglob("build-timings.json")) if resolved.is_dir() else [resolved]
            for candidate in candidates:
                try:
                    payload = json.loads(candidate.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                observed.update(payload.get("durations", {}))
        merged = build_graph.merge_timing_history(history, observed)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text(
            json.dumps({"durations": {key: round(value, 3) for key, value in sorted(merged.items())}}, indent=0, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Timing history: {len(merged)} roots ({len(observed)} updated this run)", file=sys.stderr)
        return 0

    if args.command == "stage-pages":
        stage_pages_site(args.pdf_dir, args.site_dir, args.image_dir)
        return 0

    if args.command == "render-plantuml":
        return render_plantuml(source_dir=args.source_dir, formats=args.formats, force=args.force)

    if args.command == "fetch-plantuml":
        try:
            print(fetch_plantuml(args.dest))
        except (OSError, ValueError) as exc:
            print(f"Configuration error: {exc}", file=sys.stderr)
            return 2
        return 0

    if args.command == "smoke-plantuml":
        return smoke_plantuml(args.output_dir)

    if args.command == "stage-plantuml-images":
        staged = stage_generated_images(args.repo_root or ROOT, args.source_dir)
        print(f"Staged {len(staged)} generated diagram file(s)", file=sys.stderr)
        for entry in staged:
            print(entry)
        return 0

    if args.command == "collect-raster":
        try:
            manifest = collect_raster_corpus(
                source_dir=args.source_dir,
                output_dir=args.output_dir,
                manifest_path=args.manifest,
                require_nonempty=args.require_nonempty,
            )
        except (OSError, ValueError) as exc:
            print(f"::error::{exc}", file=sys.stderr)
            return 1
        counts = manifest["counts"]
        print(
            f"Raster corpus: {manifest['total']} files "
            f"({counts['png']} png, {counts['jpg']} jpg, {counts['jpeg']} jpeg)",
            file=sys.stderr,
        )
        return 0

    if args.command == "clean":
        return clean()

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
