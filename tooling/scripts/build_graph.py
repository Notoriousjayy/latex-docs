#!/usr/bin/env python3
"""Dependency graph, fingerprinting and shard planning for latex-docs.

This module is deliberately free of any TeX dependency so that the CI planning
job can run on a bare runner without installing a TeX distribution.

Responsibilities:

* discover standalone LaTeX roots and their transitive dependencies;
* build a reverse dependency index (dependency -> dependent roots);
* derive a deterministic per-root build fingerprint;
* translate a set of changed repository paths into the affected root set;
* pack roots into weighted shards for the GitHub Actions build matrix.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Set

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"

# Bumped whenever the build configuration changes in a way that can alter the
# rendered PDF of every document. Participates in every root fingerprint.
BUILD_CONFIG_VERSION = "2"

STYLE_DIRS = (
    Path("tooling/latex"),
    Path("tooling/styles/latex"),
)

# Changing any of these invalidates every root: they define the toolchain, the
# compilation contract or the shared house style resolution rules.
GLOBAL_DEPENDENCY_FILES = {
    "latexmkrc",
    ".latexmkrc",
    "Makefile",
}

GLOBAL_DEPENDENCY_PREFIXES = (
    "tooling/scripts/",
    ".github/actions/",
    ".github/workflows/_build-latex.yml",
)

SOURCE_SUFFIXES = {".tex", ".sty", ".cls", ".bib", ".bbx", ".cbx", ".lbx", ".def"}
ASSET_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg", ".pdf", ".eps", ".csv", ".dat", ".txt", ".json"}

_INPUT_PATTERN = re.compile(r"\\(?:input|include|subfile|subfileinclude)\s*\{([^}]+)\}")
_GRAPHICS_PATTERN = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
_INPUT_MINTED_PATTERN = re.compile(r"\\inputminted\s*(?:\[[^\]]*\])?\s*\{[^}]*\}\s*\{([^}]+)\}")
_BIB_PATTERN = re.compile(r"\\(?:addbibresource|bibliography)\s*\{([^}]+)\}")
_PACKAGE_PATTERN = re.compile(r"\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
_DOCUMENTCLASS_PATTERN = re.compile(r"^\s*\\documentclass", re.MULTILINE)
_GRAPHICSPATH_PATTERN = re.compile(r"\\graphicspath\s*\{((?:\s*\{[^}]*\}\s*)+)\}")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def is_generated_wrapper(path: Path) -> bool:
    return path.name.startswith(".") and path.name.endswith(".latex-build-wrapper.tex")


def contains_documentclass(path: Path) -> bool:
    return bool(_DOCUMENTCLASS_PATTERN.search(_read_text(path)))


def discover_roots(src_root: Path | None = None) -> List[Path]:
    """Return every standalone LaTeX root, sorted deterministically."""
    search_root = (src_root or SRC_DIR).resolve()
    if not search_root.exists():
        return []
    return [
        path.resolve()
        for path in sorted(search_root.rglob("*.tex"))
        if path.is_file() and not is_generated_wrapper(path) and contains_documentclass(path)
    ]


def _resolve_style(package_name: str) -> Path | None:
    for style_dir in STYLE_DIRS:
        candidate = ROOT / style_dir / f"{package_name}.sty"
        if candidate.is_file():
            return candidate.resolve()
        candidate = ROOT / style_dir / f"{package_name}.cls"
        if candidate.is_file():
            return candidate.resolve()
    return None


def _candidate_paths(base_dirs: Sequence[Path], name: str, suffixes: Sequence[str]) -> Iterable[Path]:
    name = name.strip()
    if not name:
        return
    for base in base_dirs:
        yield (base / name)
        for suffix in suffixes:
            yield (base / f"{name}{suffix}")


def _first_existing(candidates: Iterable[Path]) -> Path | None:
    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate.resolve()
        except OSError:
            continue
    return None


def direct_dependencies(path: Path) -> Set[Path]:
    """Return files directly referenced by ``path`` that live in this repository."""
    resolved = path.resolve()
    text = _read_text(resolved)
    if not text:
        return set()

    base_dir = resolved.parent
    deps: Set[Path] = set()

    graphics_dirs = [base_dir]
    graphicspath = _GRAPHICSPATH_PATTERN.search(text)
    if graphicspath:
        for entry in re.findall(r"\{([^}]*)\}", graphicspath.group(1)):
            entry = entry.strip()
            if entry:
                graphics_dirs.append((base_dir / entry))

    for match in _INPUT_PATTERN.finditer(text):
        found = _first_existing(_candidate_paths([base_dir, ROOT], match.group(1), [".tex", ".sty"]))
        if found is not None:
            deps.add(found)

    for match in _INPUT_MINTED_PATTERN.finditer(text):
        found = _first_existing(_candidate_paths([base_dir], match.group(1), []))
        if found is not None:
            deps.add(found)

    for match in _BIB_PATTERN.finditer(text):
        for name in match.group(1).split(","):
            found = _first_existing(_candidate_paths([base_dir, ROOT / "src"], name, [".bib"]))
            if found is not None:
                deps.add(found)

    for match in _GRAPHICS_PATTERN.finditer(text):
        name = match.group(1)
        if "#" in name:  # macro argument, not a literal path
            continue
        found = _first_existing(
            _candidate_paths(graphics_dirs, name, [".png", ".pdf", ".svg", ".jpg", ".jpeg", ".eps"])
        )
        if found is not None:
            deps.add(found)

    for match in _PACKAGE_PATTERN.finditer(text):
        for package_name in match.group(1).split(","):
            style = _resolve_style(package_name.strip())
            if style is not None:
                deps.add(style)

    return {dep for dep in deps if dep != resolved and dep.is_relative_to(ROOT)}


def transitive_dependencies(path: Path, cache: Dict[Path, Set[Path]] | None = None) -> Set[Path]:
    """Return the transitive in-repository dependency closure of ``path``."""
    memo: Dict[Path, Set[Path]] = cache if cache is not None else {}
    resolved = path.resolve()

    stack = [resolved]
    seen: Set[Path] = {resolved}
    closure: Set[Path] = set()
    while stack:
        current = stack.pop()
        if current in memo:
            direct = memo[current]
        else:
            direct = direct_dependencies(current)
            memo[current] = direct
        for dep in direct:
            closure.add(dep)
            if dep not in seen and dep.suffix.lower() in SOURCE_SUFFIXES:
                seen.add(dep)
                stack.append(dep)
    return closure


@dataclass
class RootRecord:
    """Everything the planner knows about one standalone LaTeX root."""

    source: str
    pdf: str
    category: str
    dependencies: List[str] = field(default_factory=list)
    fingerprint: str = ""
    weight: float = 0.0


@dataclass
class DependencyGraph:
    roots: List[RootRecord]
    reverse: Dict[str, List[str]]

    def root_sources(self) -> List[str]:
        return [record.source for record in self.roots]

    def by_source(self) -> Dict[str, RootRecord]:
        return {record.source: record for record in self.roots}


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
    except OSError:
        return "missing"
    return digest.hexdigest()


def expected_pdf_path(source: str) -> str:
    """Map a repo-relative root source path to its published PDF path."""
    rel = Path(source)
    try:
        rel = rel.relative_to("src")
    except ValueError:
        rel = Path(rel.name)
    return rel.with_suffix(".pdf").as_posix()


def _category(source: str) -> str:
    parts = Path(source).parts
    if len(parts) >= 2 and parts[0] == "src":
        return parts[1]
    return "(root)"


def build_graph(
    roots: Sequence[Path] | None = None,
    *,
    toolchain_version: str = "",
    weights: Mapping[str, float] | None = None,
    default_weight: float = 2.5,
) -> DependencyGraph:
    """Compute the dependency graph, fingerprints and weights for all roots."""
    root_paths = list(roots) if roots is not None else discover_roots()
    dep_cache: Dict[Path, Set[Path]] = {}
    hash_cache: Dict[Path, str] = {}

    def cached_hash(path: Path) -> str:
        if path not in hash_cache:
            hash_cache[path] = _hash_file(path)
        return hash_cache[path]

    prefix = hashlib.sha256(
        f"{BUILD_CONFIG_VERSION}\0{toolchain_version}".encode("utf-8")
    ).hexdigest()

    records: List[RootRecord] = []
    reverse: Dict[str, Set[str]] = {}

    for root_path in root_paths:
        source = _rel(root_path)
        deps = sorted(_rel(dep) for dep in transitive_dependencies(root_path, dep_cache))

        digest = hashlib.sha256()
        digest.update(prefix.encode("utf-8"))
        for rel_path in [source, *deps]:
            digest.update(rel_path.encode("utf-8"))
            digest.update(b"\0")
            digest.update(cached_hash(ROOT / rel_path).encode("utf-8"))
            digest.update(b"\0")

        weight = default_weight
        if weights and source in weights:
            weight = max(0.05, float(weights[source]))

        records.append(
            RootRecord(
                source=source,
                pdf=expected_pdf_path(source),
                category=_category(source),
                dependencies=deps,
                fingerprint=digest.hexdigest(),
                weight=weight,
            )
        )

        for dep in deps:
            reverse.setdefault(dep, set()).add(source)

    return DependencyGraph(
        roots=records,
        reverse={dep: sorted(sources) for dep, sources in sorted(reverse.items())},
    )


def is_global_change(changed_path: str) -> bool:
    """Whether a changed path forces every root to be considered affected."""
    normalized = changed_path.strip().replace("\\", "/").lstrip("./")
    if not normalized:
        return False
    if normalized in GLOBAL_DEPENDENCY_FILES:
        return True
    return normalized.startswith(GLOBAL_DEPENDENCY_PREFIXES)


def _directory_fallback(graph: DependencyGraph, path: str) -> Set[str]:
    """Select every root under the nearest ancestor directory containing roots.

    Documents reference generated assets through wrapper macros such as
    ``\\safeincludegraphics{png/#2.png}``, whose argument is not a literal path,
    so static parsing cannot always attribute an asset to a root. Rather than
    silently skipping the change (which would publish a stale PDF) or rebuilding
    everything (which would destroy incrementality), bound the blast radius to
    the nearest enclosing directory subtree that actually contains roots.
    """
    directory = Path(path).parent
    while True:
        prefix = directory.as_posix()
        if prefix in {"", "."}:
            return set()
        matches = {source for source in graph.root_sources() if source.startswith(prefix + "/")}
        if matches:
            return matches
        if directory.parent == directory:
            return set()
        directory = directory.parent


def select_affected(
    graph: DependencyGraph,
    changed_paths: Sequence[str],
) -> tuple[List[str], str]:
    """Translate changed repository paths into the affected root set.

    Returns ``(sorted_root_sources, reason)`` where ``reason`` is ``"global"``
    when a foundation change forced a full selection, otherwise ``"incremental"``.

    Correctness rule: when in doubt, include.
    """
    normalized = [path.strip().replace("\\", "/").lstrip("./") for path in changed_paths]
    normalized = [path for path in normalized if path]

    if any(is_global_change(path) for path in normalized):
        return graph.root_sources(), "global"

    root_set = set(graph.root_sources())
    affected: Set[str] = set()
    for path in normalized:
        if path in root_set:
            affected.add(path)
            continue

        dependents = graph.reverse.get(path)
        if dependents:
            affected.update(dependents)
            continue

        suffix = Path(path).suffix.lower()
        if suffix in ASSET_SUFFIXES or suffix in {".puml", ".iuml"}:
            # A generated//referenced asset we could not attribute statically.
            affected.update(_directory_fallback(graph, path))

    return sorted(affected), "incremental"


def plan_shards(
    records: Sequence[RootRecord],
    shard_count: int,
    *,
    min_roots_per_shard: int = 1,
) -> List[List[RootRecord]]:
    """Distribute roots across shards using longest-processing-time-first.

    LPT gives a makespan within 4/3 of optimal, which matters here because
    document build times are strongly bimodal (tiny notes vs. heavy minted
    documents); naive count-based sharding produces long-tail shards.
    """
    if not records:
        return []

    usable = max(1, min(int(shard_count), max(1, len(records) // max(1, min_roots_per_shard))))
    buckets: List[List[RootRecord]] = [[] for _ in range(usable)]
    loads = [0.0] * usable

    for record in sorted(records, key=lambda item: (-item.weight, item.source)):
        target = min(range(usable), key=lambda index: (loads[index], index))
        buckets[target].append(record)
        loads[target] += record.weight

    return [bucket for bucket in buckets if bucket]


def load_timing_history(path: Path) -> Dict[str, float]:
    """Load persisted per-root build durations, tolerating a missing/corrupt file."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    durations = payload.get("durations", payload)
    if not isinstance(durations, dict):
        return {}
    result: Dict[str, float] = {}
    for source, value in durations.items():
        try:
            result[str(source)] = float(value)
        except (TypeError, ValueError):
            continue
    return result


def merge_timing_history(
    existing: Mapping[str, float],
    observed: Mapping[str, float],
    *,
    smoothing: float = 0.5,
) -> Dict[str, float]:
    """Exponentially smooth new observations into the persisted timing history."""
    merged = dict(existing)
    for source, duration in observed.items():
        try:
            value = float(duration)
        except (TypeError, ValueError):
            continue
        if value <= 0:
            continue
        previous = merged.get(source)
        merged[source] = value if previous is None else (smoothing * value + (1 - smoothing) * previous)
    return merged


def toolchain_version() -> str:
    """Identify the compiling toolchain for fingerprinting and cache keys."""
    explicit = os.environ.get("LATEX_TOOLCHAIN_VERSION")
    if explicit:
        return explicit
    return "unpinned"
