#!/usr/bin/env python3
"""Reject legacy JPEG files and missing/invalid PNG/SVG outputs for every renderable block."""
from __future__ import annotations

import argparse
from pathlib import Path
from tooling.scripts import latex_build


def verify(roots: list[Path]) -> list[str]:
    issues = []
    seen = {}
    for root in roots:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg"}:
                issues.append(f"Legacy JPEG prohibited: {path}")
        for source in sorted(root.rglob("*.puml")):
            text = source.read_text(encoding="utf-8", errors="replace")
            names = latex_build._plantuml_output_names(source, text)
            for name in names:
                for fmt, valid in (("png", latex_build._png_is_valid), ("svg", latex_build._svg_is_valid)):
                    target = source.parent / fmt / (name + "." + fmt)
                    if target in seen:
                        issues.append(f"Output collision: {target} ({seen[target]}, {source})")
                    seen[target] = source
                    if not target.is_file() or not valid(target):
                        issues.append(f"Missing or invalid {fmt.upper()}: {target} ({source})")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append")
    args = parser.parse_args()
    issues = verify(args.root or [latex_build.SRC_DIR, latex_build.ROOT / "tooling" / "plantuml"])
    for issue in issues:
        print(issue)
    if not issues:
        print("All renderable PlantUML blocks have valid PNG/SVG pairs; no legacy JPEG files.")
    return bool(issues)


if __name__ == "__main__":
    raise SystemExit(main())
