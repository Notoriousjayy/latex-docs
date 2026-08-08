#!/usr/bin/env python3
"""Canonical build helpers for the latex-docs repository."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Sequence, Set

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
LATEXMK = os.environ.get("LATEXMK", "latexmk")


def discover_roots(src_root: Path | None = None) -> List[Path]:
    search_root = (src_root or SRC_DIR).resolve()
    if not search_root.exists():
        return []

    roots: List[Path] = []
    for path in sorted(search_root.rglob("*.tex")):
        if path.is_file() and contains_documentclass(path):
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
        return ":".join(entries) + (":" + current if current else "")
    return current


def _resolve_package_path(package_name: str) -> Path | None:
    candidates = [
        ROOT / "tooling" / "latex" / f"{package_name}.sty",
        ROOT / "tooling" / "styles" / "latex" / f"{package_name}.sty",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def _collect_dependencies(path: Path) -> Set[Path]:
    deps: Set[Path] = set()
    if not path.exists():
        return deps

    text = path.read_text(encoding="utf-8", errors="ignore")
    base_dir = path.parent

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
                deps.update(_collect_dependencies(candidate))
                break

    for match in re.finditer(r"\\usepackage\{([^}]+)\}", text):
        package_name = match.group(1)
        package_path = _resolve_package_path(package_name)
        if package_path is not None:
            deps.add(package_path)

    return deps


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


def build_root(tex_path: Path, output_dir: Path | None = None, log_dir: Path | None = None, artifact_dir: Path | None = None) -> int:
    tex_path = tex_path.resolve()
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

    base_cmd = [LATEXMK, "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-shell-escape", "-synctex=1"]
    engine = _detect_engine(tex_path)
    if engine == "lualatex":
        base_cmd.extend(["-pdflatex=lualatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-shell-escape", "%O", "%S"])
    elif engine == "xelatex":
        base_cmd.extend(["-pdflatex=xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-shell-escape", "%O", "%S"])

    if output_dir is not None:
        build_dir = output_dir / tex_path.relative_to(SRC_DIR).parent / stem
        build_dir.mkdir(parents=True, exist_ok=True)
        base_cmd.extend([f"-outdir={build_dir}"])
    else:
        build_dir = work_dir

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)

    cmd = [*base_cmd, tex_path.name]
    stdout_path = None
    stderr_path = None
    if log_dir is not None:
        stdout_path = log_dir / f"{stem}.build.stdout.txt"
        stderr_path = log_dir / f"{stem}.build.stderr.txt"

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

    if artifact_dir is not None:
        rel_dir = tex_path.relative_to(SRC_DIR).parent
        dest_dir = artifact_dir / rel_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = build_dir / f"{stem}.pdf"
        if pdf_path.exists():
            shutil.copy2(pdf_path, dest_dir / f"{stem}.pdf")

    return result.returncode


def build_roots(tex_paths: Sequence[Path], jobs: int = 1, output_dir: Path | None = None, log_dir: Path | None = None, artifact_dir: Path | None = None) -> int:
    if jobs <= 1:
        failures = 0
        for tex_path in tex_paths:
            if build_root(tex_path, output_dir=output_dir, log_dir=log_dir, artifact_dir=artifact_dir) != 0:
                failures += 1
        return failures

    failures = 0
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
        futures = [executor.submit(build_root, tex_path, output_dir, log_dir, artifact_dir) for tex_path in tex_paths]
        for future in futures:
            if future.result() != 0:
                failures += 1
    return failures


def build_changed(base_ref: str | None = None, jobs: int = 1) -> int:
    try:
        if base_ref is None:
            target = "HEAD~1"
            changed = subprocess.check_output(["git", "diff", "--name-only", target, "HEAD"], cwd=str(ROOT), text=True)
        else:
            changed = subprocess.check_output(["git", "diff", "--name-only", base_ref], cwd=str(ROOT), text=True)
    except subprocess.CalledProcessError:
        return 1

    tex_changes = [line.strip() for line in changed.splitlines() if line.endswith(".tex")]
    roots = discover_roots()
    affected = []
    for changed_path in tex_changes:
        path = (ROOT / changed_path).resolve()
        if path.exists() and path.suffix == ".tex":
            affected.extend(determine_affected_roots(roots, path))
    unique_roots = sorted({path.resolve() for path in affected})
    return build_roots(unique_roots, jobs=jobs)


def clean() -> int:
    for tex_path in discover_roots():
        work_dir = tex_path.parent
        subprocess.run([LATEXMK, "-c", tex_path.name], cwd=str(work_dir), check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 0


def main() -> int:
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

    category_parser = subparsers.add_parser("build-category")
    category_parser.add_argument("category")
    category_parser.add_argument("--jobs", type=int, default=1)
    category_parser.add_argument("--output-dir", type=Path, default=None)
    category_parser.add_argument("--log-dir", type=Path, default=None)
    category_parser.add_argument("--artifact-dir", type=Path, default=None)

    changed_parser = subparsers.add_parser("build-changed")
    changed_parser.add_argument("--base", default=None)
    changed_parser.add_argument("--jobs", type=int, default=1)

    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("--jobs", type=int, default=1)

    args = parser.parse_args()

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
        return build_roots(discover_roots(), jobs=jobs, output_dir=args.output_dir, log_dir=args.log_dir, artifact_dir=args.artifact_dir)

    if args.command == "build-category":
        roots = [root for root in discover_roots() if root.is_relative_to(SRC_DIR / args.category)]
        return build_roots(roots, jobs=args.jobs, output_dir=args.output_dir, log_dir=args.log_dir, artifact_dir=args.artifact_dir)

    if args.command == "build-changed":
        return build_changed(base_ref=args.base, jobs=args.jobs)

    if args.command == "clean":
        return clean()

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
