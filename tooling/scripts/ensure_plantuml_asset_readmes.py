#!/usr/bin/env python3
"""Safely create or update README files for staged PlantUML image folders.

Only explicitly staged images are considered; curated README files are never
overwritten. The generated indexes satisfy the source-directory navigation
contract used by LaTeX CI and GitHub Pages.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from urllib.parse import quote

MARKER = "<!-- Managed by tooling/scripts/ensure_plantuml_asset_readmes.py -->"
FORMAT_EXT = {
    "png": {".png"},
    "svg": {".svg"},
    "jpg": {".jpg", ".jpeg"},
    "jpeg": {".jpg", ".jpeg"},
}


def ensure_index(image: Path, root: Path) -> Path | None:
    root = root.resolve()
    image = (root / image).resolve() if not image.is_absolute() else image.resolve()
    if not image.is_relative_to(root) or not image.is_file():
        return None
    folder = image.parent
    suffixes = FORMAT_EXT.get(folder.name.lower())
    if not suffixes or image.suffix.lower() not in suffixes:
        return None
    if image.relative_to(root).parts[0] not in {"src", "tooling"}:
        return None
    readme = folder / "README.md"
    if (folder / "readme.md").exists():
        return None
    if readme.exists() and MARKER not in readme.read_text(encoding="utf-8"):
        return None
    assets = sorted(
        (p for p in folder.iterdir()
         if p.is_file() and p.suffix.lower() in suffixes),
        key=lambda p: p.name,
    )
    if not assets:
        return None
    label = folder.name.upper()
    rows = "\n".join(
        "| [" + chr(96) + p.name + chr(96) + "](" + quote(p.name) +
        ") | Rendered " + label + " |"
        for p in assets
    )
    content = (
        "# " + label + " assets\n\n" + MARKER + "\n\n"
        "Rendered PlantUML assets, not independently authored documents. "
        "The adjacent diagram sources remain authoritative.\n\n"
        "## Files\n\n| File | Type |\n|---|---|\n" + rows + "\n\n"
        "## Navigation\n\nSee the [diagram source index](../README.md).\n\n"
        "## Maintenance\n\nRegenerate using the pinned PlantUML renderer. "
        "The render workflow updates this index when images change.\n"
    )
    if readme.exists() and readme.read_text(encoding="utf-8") == content:
        return None
    readme.write_text(content, encoding="utf-8")
    return readme


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-staged", action="store_true", required=True)
    parser.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    diff = subprocess.run(
        ["git", "-C", str(root), "diff", "--cached", "--name-only",
         "--diff-filter=AM", "-z", "--", "src", "tooling/plantuml"],
        check=True, capture_output=True,
    )
    images = [
        root / name.decode("utf-8")
        for name in diff.stdout.split(b"\x00") if name
    ]
    changed = sorted(set(filter(None, (ensure_index(p, root) for p in images))))
    if args.stage and changed:
        subprocess.run(
            ["git", "-C", str(root), "add", "--",
             *[str(p.relative_to(root)) for p in changed]],
            check=True,
        )
    print("PlantUML asset index files updated:", len(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
