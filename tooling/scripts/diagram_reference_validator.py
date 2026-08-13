#!/usr/bin/env python3
"""Validate LaTeX diagram references against active PlantUML rename migrations."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
MIGRATION_MAP_PATH = Path("/tmp/migration-map.tsv")
GRAPHICS_EXTENSIONS = (".pdf", ".png", ".svg", ".jpg", ".jpeg", ".eps")
GRAPHICS_MACRO_PATTERN = re.compile(
    r"\\(?:includegraphics|safeincludegraphics)(?:\[[^\]]*\])?\{([^{}]+)\}",
    re.IGNORECASE,
)

# Fallback legacy patterns for known migration families when no runtime map is available.
FALLBACK_LEGACY_STEMS = {
    "index_specialized_cloud_architectures": "00-specialized-cloud-architectures-index",
    "direct_io_access": "01-direct-io-access",
    "direct_lun_access": "02-direct-lun-access",
    "dynamic_data_normalization": "03-dynamic-data-normalization",
    "elastic_network_capacity": "04-elastic-network-capacity",
    "cross_storage_device_vertical_tiering": "05-cross-storage-device-vertical-tiering",
    "intra_storage_device_vertical_data_tiering": "06-intra-storage-device-vertical-data-tiering",
    "load_balanced_virtual_switches": "07-load-balanced-virtual-switches",
    "multipath_resource_access": "08-multipath-resource-access",
    "persistent_virtual_network_configuration": "09-persistent-virtual-network-configuration",
    "redundant_physical_connection_virtual_servers": "10-redundant-physical-connection-virtual-servers",
    "storage_maintenance_window": "11-storage-maintenance-window",
    "edge_computing": "12-edge-computing",
    "fog_computing": "13-fog-computing",
    "virtual_data_abstraction": "14-virtual-data-abstraction",
    "metacloud": "15-metacloud",
    "federated_cloud_application": "16-federated-cloud-application",
    "specialized_cloud_architectures_puml": "specialized-cloud-architectures-puml",
}


def _read_migration_map() -> List[Tuple[str, str]]:
    if not MIGRATION_MAP_PATH.exists() or not MIGRATION_MAP_PATH.is_file():
        return []

    pairs: List[Tuple[str, str]] = []
    text = MIGRATION_MAP_PATH.read_text(encoding="utf-8", errors="ignore")
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part for part in re.split(r"\s{2,}|\t", line) if part]
        if len(parts) >= 2:
            old, new = parts[0].strip(), parts[-1].strip()
            if old != new:
                pairs.append((old, new))
    return pairs


def _read_git_renames() -> List[Tuple[str, str]]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-status", "--find-renames", "--", "src"],
            cwd=ROOT,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    pairs: List[Tuple[str, str]] = []
    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        # R100\told\tnew
        cols = line.split("\t")
        if len(cols) >= 3 and cols[0].startswith("R"):
            old, new = cols[-2].strip(), cols[-1].strip()
            if old != new:
                pairs.append((old, new))
    return pairs


def collect_rename_pairs() -> List[Tuple[str, str]]:
    pairs = _read_migration_map() + _read_git_renames()
    seen = set()
    deduped: List[Tuple[str, str]] = []
    for old, new in pairs:
        key = (old, new)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((old, new))
    return deduped


def _is_diagram_file(path: str) -> bool:
    return path.endswith((".puml", ".png", ".svg"))


def collect_legacy_mappings() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    rename_pairs = collect_rename_pairs()

    for old, new in rename_pairs:
        if not (_is_diagram_file(old) and _is_diagram_file(new)):
            continue

        mapping[old] = new

        old_path = Path(old)
        new_path = Path(new)
        if old_path.name != new_path.name:
            mapping[old_path.name] = new_path.name

        old_stem = old_path.stem
        new_stem = new_path.stem
        # Extensionless references are common in includegraphics; keep matching tight
        # to filename-like contexts during scan to avoid touching prose titles.
        if old_stem != new_stem and (
            "_" in old_stem
            or "vs." in old_stem
            or ".-" in old_stem
            or re.match(r"^\d{2}-", new_stem)
        ):
            mapping[old_stem] = new_stem

        if old_path.parent.as_posix() != new_path.parent.as_posix():
            mapping[old_path.parent.as_posix() + "/"] = new_path.parent.as_posix() + "/"

    if not mapping:
        mapping.update(FALLBACK_LEGACY_STEMS)

    return mapping


def _legacy_basename_pattern(old_stem: str) -> re.Pattern[str]:
    escaped = re.escape(old_stem)
    # Match only filename/path-like contexts, not natural language prose.
    return re.compile(rf"(?<![A-Za-z0-9-]){escaped}(?=(?:\.(?:puml|png|svg))|[/}}])")


def find_legacy_tex_references(tex_files: Sequence[Path], legacy_map: Dict[str, str]) -> List[str]:
    issues: List[str] = []
    for tex_file in tex_files:
        text = tex_file.read_text(encoding="utf-8", errors="ignore")
        rel = tex_file.relative_to(ROOT).as_posix()

        for old, new in legacy_map.items():
            if old in text:
                if old.endswith((".puml", ".png", ".svg")) or "/" in old:
                    issues.append(f"legacy-reference: {rel}: {old} -> {new}")
                else:
                    if _legacy_basename_pattern(old).search(text):
                        issues.append(f"legacy-reference: {rel}: {old} -> {new}")
    return issues


def _contains_latex_macro(path_text: str) -> bool:
    return "\\" in path_text or "{" in path_text or "}" in path_text


def _existing_case_insensitive_sibling(target: Path) -> bool:
    parent = target.parent
    if not parent.exists() or not parent.is_dir():
        return False
    expected = target.name.lower()
    return any(child.name.lower() == expected for child in parent.iterdir())


def _resolve_graphic_candidates(tex_file: Path, ref: str) -> List[Path]:
    ref_path = Path(ref)
    if ref_path.is_absolute():
        return [ref_path]

    base = tex_file.parent / ref
    if Path(ref).suffix:
        return [base]

    return [base.with_suffix(ext) for ext in GRAPHICS_EXTENSIONS]


def find_missing_or_case_mismatched_graphics(
    tex_files: Sequence[Path],
    rename_pairs: Sequence[Tuple[str, str]],
) -> List[str]:
    issues: List[str] = []

    watch_tokens = set()
    for old, new in rename_pairs:
        if not (_is_diagram_file(old) or _is_diagram_file(new)):
            continue
        for candidate in (old, new):
            p = Path(candidate)
            watch_tokens.add(p.stem)
            watch_tokens.add(p.name)
            watch_tokens.add(p.parent.as_posix())
    watch_tokens.update(FALLBACK_LEGACY_STEMS.keys())
    watch_tokens.update(FALLBACK_LEGACY_STEMS.values())

    for tex_file in tex_files:
        rel = tex_file.relative_to(ROOT).as_posix()
        text = tex_file.read_text(encoding="utf-8", errors="ignore")
        refs = GRAPHICS_MACRO_PATTERN.findall(text)

        for raw_ref in refs:
            ref = raw_ref.strip()
            if not ref or ref.startswith(("http://", "https://")):
                continue
            if "#" in ref:
                # Template placeholders like {#1} are not concrete file references.
                continue
            if _contains_latex_macro(ref):
                # Dynamic path; skip deterministic existence check.
                continue
            if not any(token and token in ref for token in watch_tokens):
                continue

            candidates = _resolve_graphic_candidates(tex_file, ref)
            existing = [c for c in candidates if c.exists() and c.is_file()]

            if not existing:
                case_mismatch = any(_existing_case_insensitive_sibling(c) for c in candidates)
                if case_mismatch:
                    issues.append(f"case-mismatch-graphic: {rel}: {ref}")
                else:
                    issues.append(f"missing-graphic: {rel}: {ref}")
                continue

            if Path(ref).suffix == "" and len(existing) > 1:
                names = ", ".join(sorted(p.suffix for p in existing))
                issues.append(f"ambiguous-extensionless-graphic: {rel}: {ref} ({names})")

    return issues


def find_unsynchronized_renamed_assets(rename_pairs: Sequence[Tuple[str, str]]) -> List[str]:
    issues: List[str] = []

    old_side = {old for old, _ in rename_pairs}
    try:
        proc = subprocess.run(
            ["git", "ls-files", "src"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        tracked_paths = set(proc.stdout.splitlines()) if proc.returncode == 0 else set()
    except FileNotFoundError:
        tracked_paths = set()

    png_svg_new_targets = {
        new
        for old, new in rename_pairs
        if old.endswith((".png", ".svg")) and new.endswith((".png", ".svg"))
    }

    for old, new in rename_pairs:
        if not (old.endswith(".puml") and new.endswith(".puml")):
            continue
        old_stem = Path(old).stem
        new_stem = Path(new).stem
        if old_stem == new_stem:
            continue

        # If the migration map/git diff records matching png/svg renames for the
        # same stem transformation, require those new targets to exist.
        for ext in (".png", ".svg"):
            mapped = [
                candidate
                for candidate in png_svg_new_targets
                if Path(candidate).suffix == ext and Path(candidate).stem == new_stem
            ]
            for candidate in mapped:
                # If a candidate was renamed again in the same worktree, do not
                # treat the intermediate target as missing.
                if candidate in old_side:
                    continue
                if tracked_paths and candidate not in tracked_paths:
                    continue
                path = ROOT / candidate
                if not path.exists() or not path.is_file():
                    issues.append(f"missing-synchronized-rendered-asset: {candidate} (from {new})")

    return issues


def validate_repo() -> int:
    tex_files = sorted(path for path in SRC_DIR.rglob("*.tex") if path.is_file())
    legacy_map = collect_legacy_mappings()
    rename_pairs = collect_rename_pairs()

    issues: List[str] = []
    issues.extend(find_legacy_tex_references(tex_files, legacy_map))
    issues.extend(find_missing_or_case_mismatched_graphics(tex_files, rename_pairs))
    issues.extend(find_unsynchronized_renamed_assets(rename_pairs))

    if issues:
        for issue in issues:
            print(issue)
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate migrated diagram references")
    parser.add_argument("--validate", action="store_true", help="Run repository validation checks")
    args = parser.parse_args()
    if args.validate:
        return validate_repo()
    return 0


if __name__ == "__main__":
    sys.exit(main())
