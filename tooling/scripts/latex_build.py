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
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, List, Sequence, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_graph  # noqa: E402  (local module, resolved via the path insert above)

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
LATEXMK = os.environ.get("LATEXMK", "latexmk")
TIMING_HISTORY_PATH = ROOT / "tooling" / "manifests" / "build-timings.json"

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


def stage_pages_site(pdf_dir: Path, site_dir: Path) -> List[Path]:
    pdf_dir = pdf_dir.resolve()
    site_dir = site_dir.resolve()
    site_pdf_dir = site_dir / "pdfs"

    if not pdf_dir.exists():
        raise FileNotFoundError(pdf_dir)

    reset_output_tree(site_dir)
    shutil.copytree(pdf_dir, site_pdf_dir, dirs_exist_ok=True)

    pdf_rel_paths = sorted(path.relative_to(site_pdf_dir) for path in site_pdf_dir.rglob("*.pdf") if path.is_file())

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

    def _emit_links(handle: Any, paths: list[Path], sort_by_chapter: bool = False) -> None:
        ordered = sorted(paths, key=_collection_path_key if sort_by_chapter else lambda path: (path.as_posix(),))
        handle.write("<ul>")
        for rel_path in ordered:
            rel_posix = rel_path.as_posix()
            escaped = html.escape(rel_posix)
            handle.write(f'<li><a href="pdfs/{escaped}">{escaped}</a></li>')
        handle.write("</ul>")

    index_path = site_dir / "index.html"
    with index_path.open("w", encoding="utf-8") as handle:
        handle.write("<!doctype html><html><body><h1>LaTeX PDFs</h1>")

        if cornell_paths:
            handle.write("<h2>Cornell Notes</h2>")

            string_paths = [path for path in cornell_paths if path.parts[:3] == ("cornell-notes", "computer-science", "string-algorithms")]
            combinatorial_paths = [path for path in cornell_paths if path.parts[:3] == ("cornell-notes", "computer-science", "combinatorial-algorithms")]
            network_paths = [path for path in cornell_paths if path.parts[:3] == ("cornell-notes", "computer-science", "computer-networks")]
            operating_system_paths = [path for path in cornell_paths if path.parts[:3] == ("cornell-notes", "computer-science", "operating-systems")]
            elec_paths = [path for path in cornell_paths if path.parts[:3] == ("cornell-notes", "electronics", "electronic-circuits")]
            math_paths = [path for path in cornell_paths if path.parts[:3] == ("cornell-notes", "mathematics", "numerical-methods")]
            sec_paths = [path for path in cornell_paths if path.parts[:4] == ("cornell-notes", "security", "certifications", "cissp")]
            iso_paths = [path for path in cornell_paths if path.parts[:4] == ("cornell-notes", "architecture", "standards", "iso-iec-ieee-42010-2022")]
            cpp_paths = [path for path in cornell_paths if path.parts[:5] == ("cornell-notes", "programming", "languages", "cpp", "cpp-2024")]
            computer_science_paths = string_paths + combinatorial_paths + network_paths + operating_system_paths
            other_cornell = [path for path in cornell_paths if path not in computer_science_paths and path not in elec_paths and path not in math_paths and path not in sec_paths and path not in iso_paths and path not in cpp_paths]

            def _emit_new_collection(heading: str, paths: list[Path]) -> None:
                if not paths:
                    return
                handle.write(f"<h3>{html.escape(heading)}</h3>")
                grouped: dict[str, list[Path]] = {}
                for path in paths:
                    if path.parts[4] == "introduction":
                        grouped.setdefault("Introduction", []).append(path)
                    else:
                        section = path.parts[4].title()
                        topic = path.parts[5] if len(path.parts) > 6 else "(uncategorized)"
                        grouped.setdefault(section, [])
                        grouped.setdefault(f"{section}: {topic}", []).append(path)
                for label in ("Introduction", "Clauses", "Annexes"):
                    matching = [key for key in grouped if key == label or key.startswith(label + ":")]
                    if not matching:
                        continue
                    handle.write(f"<h4>{label}</h4>")
                    for key in sorted(matching, key=lambda value: (0, value) if value == label else (1, value)):
                        if key != label:
                            handle.write(f"<h5>{html.escape(key.split(': ', 1)[1])}</h5>")
                        _emit_links(handle, grouped[key], sort_by_chapter=True)

            _emit_new_collection("Architecture: ISO/IEC/IEEE 42010:2022", iso_paths)
            _emit_new_collection("Programming: C++ 2024", cpp_paths)

            if computer_science_paths:
                handle.write("<h3>Computer Science</h3>")
                if string_paths:
                    handle.write("<h4>String Algorithms</h4>")
                    _emit_links(handle, string_paths, sort_by_chapter=True)

                for label, collection_paths, topic_order in (
                    ("Combinatorial Algorithms", combinatorial_paths, ["subset-generation", "compositions", "permutations", "integer-partitions", "set-partitions", "general-frameworks", "young-tableaux", "sorting", "array-reindexing", "graph-algorithms", "polynomial-algorithms", "matrix-and-array-algorithms", "partially-ordered-sets", "backtracking", "tree-algorithms"]),
                    ("Computer Networks", network_paths, ["foundations", "physical-layer", "data-link-layer", "medium-access-control", "network-layer", "transport-layer", "application-layer", "network-security", "reference-material"]),
                    ("Operating Systems", operating_system_paths, ["foundations", "processes-and-threads", "memory-management", "file-systems", "input-output", "deadlocks", "virtualization-and-cloud", "multiple-processor-systems", "security", "case-studies", "operating-system-design", "reference-material"]),
                ):
                    if not collection_paths:
                        continue
                    handle.write(f"<h4>{label}</h4>")
                    handle.write("<h5>Chapter index</h5>")
                    _emit_links(handle, collection_paths, sort_by_chapter=True)
                    grouped: dict[str, list[Path]] = {}
                    for path in collection_paths:
                        topic = path.parts[3] if len(path.parts) > 4 else "(uncategorized)"
                        grouped.setdefault(topic, []).append(path)
                    for topic in topic_order:
                        if topic in grouped:
                            handle.write(f"<h5>{html.escape(topic)}</h5>")
                            _emit_links(handle, grouped.pop(topic), sort_by_chapter=True)
                    for topic in sorted(grouped):
                        handle.write(f"<h5>{html.escape(topic)}</h5>")
                        _emit_links(handle, grouped[topic], sort_by_chapter=True)

            if elec_paths:
                handle.write("<h3>Electronics</h3><h4>Electronic Circuits</h4>")
                grouped: dict[str, list[Path]] = {}
                for path in elec_paths:
                    topic = path.parts[3] if len(path.parts) > 4 else "(uncategorized)"
                    grouped.setdefault(topic, []).append(path)

                topic_order = [
                    "foundations",
                    "semiconductor-devices",
                    "analog-circuits",
                    "power-electronics",
                    "digital-logic-and-interfaces",
                    "mixed-signal-systems",
                    "embedded-systems",
                ]
                ordered_topics = [topic for topic in topic_order if topic in grouped]
                ordered_topics.extend(topic for topic in sorted(grouped) if topic not in ordered_topics)

                for topic in ordered_topics:
                    handle.write(f"<h5>{html.escape(topic)}</h5>")
                    _emit_links(handle, grouped[topic], sort_by_chapter=True)

            if math_paths:
                handle.write("<h3>Mathematics</h3><h4>Numerical Methods</h4>")
                grouped = {}
                for path in math_paths:
                    topic = path.parts[3] if len(path.parts) > 4 else "(uncategorized)"
                    grouped.setdefault(topic, []).append(path)

                topic_order = [
                    "foundations",
                    "linear-algebra",
                    "interpolation-integration-and-functions",
                    "randomization-and-ordering",
                    "root-finding-and-optimization",
                    "fourier-and-spectral-methods",
                    "statistics-modeling-and-inference",
                    "differential-and-integral-equations",
                    "computational-geometry",
                    "general-algorithms",
                ]
                ordered_topics = [topic for topic in topic_order if topic in grouped]
                ordered_topics.extend(topic for topic in sorted(grouped) if topic not in ordered_topics)

                for topic in ordered_topics:
                    handle.write(f"<h5>{html.escape(topic)}</h5>")
                    _emit_links(handle, grouped[topic], sort_by_chapter=True)

            if sec_paths:
                handle.write("<h3>Security</h3><h4>CISSP</h4>")
                _emit_links(handle, sec_paths, sort_by_chapter=True)

            if other_cornell:
                handle.write("<h3>Other Cornell Notes</h3>")
                _emit_links(handle, other_cornell)

        if non_cornell_paths:
            handle.write("<h2>Other PDFs</h2>")
            _emit_links(handle, non_cornell_paths)

        handle.write("</body></html>")

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


def _plantuml_is_current(source: Path, config: Path | None, outputs: Sequence[Path]) -> bool:
    """Whether every rendered output is newer than the diagram and its config."""
    try:
        newest_input = source.stat().st_mtime
        if config is not None:
            newest_input = max(newest_input, config.stat().st_mtime)
        return all(output.exists() and output.stat().st_mtime >= newest_input for output in outputs)
    except OSError:
        return False


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
    their source and config are skipped, and the rest are rendered in batches
    that share a single JVM start.
    """
    search_root = (source_dir or SRC_DIR).resolve()
    if not search_root.exists():
        return 0

    config_names = ["plantuml-config.puml", "config.puml"]
    lowered_config_names = {name.lower() for name in config_names}
    formats = list(formats or ["png", "svg"])

    include_paths = [ROOT / "tooling" / "plantuml", ROOT / "tooling" / "styles" / "plantuml"]
    env = os.environ.copy()
    env["PLANTUML_INCLUDE_PATH"] = ":".join(str(path) for path in include_paths if path.exists())

    # Batch key: (working directory, config, format). PlantUML resolves a
    # relative -o against each input file's own directory, and every batched
    # file shares a directory here, so outputs stay co-located with sources.
    batches: dict[tuple[Path, str, str], list[str]] = {}
    diagram_count = 0
    skipped = 0

    for path in sorted(search_root.rglob("*.puml")):
        if not path.is_file() or path.name.lower() in lowered_config_names:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "@startuml" not in text:
            continue

        diagram_count += 1
        config_path = _plantuml_config_for(path, config_names)

        for fmt in formats:
            output_path = path.parent / fmt / f"{path.stem}.{fmt}"
            if not force and _plantuml_is_current(path, config_path, [output_path]):
                skipped += 1
                continue
            output_path.parent.mkdir(parents=True, exist_ok=True)
            key = (path.parent, str(config_path) if config_path else "", fmt)
            batches.setdefault(key, []).append(path.name)

    failures = 0
    rendered = 0
    for (work_dir, config, fmt), names in sorted(batches.items(), key=lambda item: str(item[0])):
        cmd = ["plantuml", f"-t{fmt}", "-o", fmt]
        if config:
            cmd.extend(["-config", config])
        cmd.extend(names)
        result = subprocess.run(
            cmd,
            cwd=str(work_dir),
            env=env,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            failures += 1
            detail = (result.stderr or b"").decode("utf-8", errors="ignore").strip().splitlines()
            print(
                f"PlantUML failed in {work_dir} ({fmt}): {detail[-1] if detail else 'unknown error'}",
                file=sys.stderr,
            )
        else:
            rendered += len(names)

    print(
        f"PlantUML: {diagram_count} diagrams, {rendered} rendered, {skipped} already current, "
        f"{len(batches)} JVM invocations, {failures} failed batches",
        file=sys.stderr,
    )
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
        stage_pages_site(args.pdf_dir, args.site_dir)
        return 0

    if args.command == "render-plantuml":
        return render_plantuml(source_dir=args.source_dir, formats=args.formats, force=args.force)

    if args.command == "clean":
        return clean()

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
