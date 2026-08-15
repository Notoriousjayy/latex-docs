#!/usr/bin/env python3
"""Lightweight migration helpers for direct semantic style imports."""
from __future__ import annotations

import argparse
import subprocess
import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
LISTINGS_TOKENS = (
    "\\usepackage{listings}",
    "\\lstdefinestyle",
    "\\lstdefinelanguage",
    "\\lstset",
    "\\lstinputlisting",
    "\\lstinline",
    "\\lstnewenvironment",
    "\\begin{lstlisting}",
    "\\end{lstlisting}",
    "\\lstlisting",
)

SOURCE_EXTENSIONS = {
    ".tex",
    ".puml",
    ".md",
    ".bib",
    ".csv",
    ".png",
    ".svg",
    ".jpg",
    ".jpeg",
}

# Explicit allowlist for tool-required filenames that cannot be changed.
# Keep this list minimal and documented when used.
FILENAME_POLICY_EXCEPTIONS: tuple[str, ...] = (
    "src/cornell-notes/security/certifications/cissp/03-security-architecture-and-engineering-cornell-notes.tex",
    "src/cornell-notes/security/certifications/cissp/04-communication-and-network-security-cornell-notes.tex",
    "src/cornell-notes/security/certifications/cissp/05-identity-and-access-management-cornell-notes.tex",
    "src/cornell-notes/security/certifications/cissp/06-security-assessment-and-testing-cornell-notes.tex",
)
MAX_FILENAME_LENGTH = 50

LEGACY_PATH_EXCLUSIONS = (
    "src/architecture/cloud/architecture/cloud-architecture-diagram-library/advanced-cloud-architecture-plantuml/",
    "src/architecture/cloud/architecture/cloud-architecture-diagram-library/cloud-arch-plantuml/",
)

GENERIC_BASENAME_PATTERN = re.compile(r"^(main|plan|scope|section-\d+|diagram|how-to-use-this-template)\.[a-z0-9]+$")
KEBAB_BASENAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLANTUML_START_PATTERN = re.compile(
    r"@start(?:uml|mindmap|activity|flowchart|gantt|wbs|state|json|yaml|class|sequence|usecase|component|deployment|object|rect|command|graph)",
    re.IGNORECASE,
)
PLANTUML_DIRECT_STYLE_PATTERN = re.compile(r"!include(?:_once)?\s+.*tooling/styles/plantuml/.+\.iuml")
FORBIDDEN_PLANTUML_WRAPPER_FILES = {"appsec-style.puml"}
CORNELL_NOTES_PATH_PATTERN = re.compile(
    r"src/cornell-notes/(computer-science/(combinatorial-algorithms|computer-networks|operating-systems|string-algorithms)|electronics/electronic-circuits|security/certifications/cissp|mathematics/numerical-methods)/.+\.tex$"
)

SEMANTIC_STYLE_PACKAGES = {
    "business-admin",
    "cornell-notes",
    "financial",
    "hr",
    "legal",
    "personal-official",
    "technical",
    "technical-design-spec",
    "technical-implementation",
    "technical-installation",
    "technical-testing",
    "technical-user-manual",
}

MINTED_SHARED_HELPER_PATTERNS = (
    re.compile(r"\\newminted\[(?:yamlcode|bashcode|textcode)\]\{(?:yaml|bash|text)\}\{"),
    re.compile(r"\\newminted\{(?:yaml|bash|text)\}\{"),
)


def classify_latex_style(path: Path) -> str:
    rel = str(path).lower()
    if CORNELL_NOTES_PATH_PATTERN.search(rel):
        return "cornell-notes"
    if "finance" in rel or "financial" in rel or ("cd" in rel and "certificate" in rel):
        return "financial"
    if "personal" in rel or "career" in rel or "gardening" in rel or "ebooks" in rel:
        return "personal-official"
    if "business-snapshot" in rel or "startup" in rel or "sba" in rel or "roadmap" in rel:
        return "business-admin"
    if "hr" in rel or "human" in rel or "people" in rel:
        return "hr"
    if "legal" in rel or "agreement" in rel or "contract" in rel:
        return "legal"
    if "business" in rel or "admin" in rel or "letterhead" in rel or "document-control" in rel or "governance" in rel:
        return "business-admin"
    if "security" in rel or "github" in rel or "codeql" in rel or "owasp" in rel or "appsec" in rel or "cis" in rel or "cissp" in rel or "gh-500" in rel or "trivy" in rel or "dependabot" in rel:
        return "technical-design-spec"
    if "implementation" in rel or "guide" in rel or "quickstart" in rel or "checklist" in rel or "deployment" in rel or "installation" in rel or "vault" in rel or "authentik" in rel or "suitecrm" in rel:
        return "technical-implementation"
    if "testing" in rel or "test" in rel:
        return "technical-testing"
    if "manual" in rel or "user" in rel or "how-to-use" in rel or "tutorial" in rel:
        return "technical-user-manual"
    return "technical"


def classify_plantuml_style(path: Path, text: str | None = None) -> str:
    content = (text or path.read_text(encoding="utf-8", errors="ignore")).lower()
    if "->" in content or "-->" in content:
        if "usecase" in content:
            return "tooling/styles/plantuml/behavioral/usecase-diagram-style.iuml"
        if re.search(r"(^|[^a-z0-9_])(start|stop|fork|if|else|endif|repeat|while|endwhile|switch|case|endswitch)\b", content):
            return "tooling/styles/plantuml/behavioral/activity-diagram-style.iuml"
        if re.search(r"(^|[^a-z0-9_])(participant|actor|alt|loop|note over|group|box)\b", content):
            return "tooling/styles/plantuml/interaction/sequence-diagram-style.iuml"
        return "tooling/styles/plantuml/interaction/sequence-diagram-style.iuml"
    if "class" in content and "interface" in content:
        return "tooling/styles/plantuml/structural/class-diagram-style.iuml"
    if "component" in content:
        return "tooling/styles/plantuml/structural/component-diagram-style.iuml"
    if "package" in content:
        return "tooling/styles/plantuml/structural/package-diagram-style.iuml"
    if "node" in content or "deployment" in content or "artifact" in content:
        return "tooling/styles/plantuml/structural/deployment-diagram-style.iuml"
    if "object" in content:
        return "tooling/styles/plantuml/structural/object-diagram-style.iuml"
    if "usecase" in content:
        return "tooling/styles/plantuml/behavioral/usecase-diagram-style.iuml"
    if re.search(r"(^|[^a-z0-9_])(start|stop|fork|if|else|endif|repeat|while|endwhile|switch|case|endswitch)\b", content):
        return "tooling/styles/plantuml/behavioral/activity-diagram-style.iuml"
    if "state" in content and ("=>" in content or "[*" in content):
        return "tooling/styles/plantuml/behavioral/statemachine-diagram-style.iuml"
    return "tooling/styles/plantuml/behavioral/activity-diagram-style.iuml"


def discover_latex_roots(src_root: Path | None = None) -> List[Path]:
    search_root = (src_root or SRC_DIR).resolve()
    if not search_root.exists():
        return []
    roots = []
    for path in sorted(search_root.rglob("*.tex")):
        if path.name.startswith(".") and path.name.endswith(".latex-build-wrapper.tex"):
            continue
        if path.is_file() and re.search(r"^\\documentclass", path.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE):
            roots.append(path.resolve())
    return roots


def strip_latex_comments(text: str) -> str:
    lines: List[str] = []
    for raw_line in text.splitlines():
        out: List[str] = []
        idx = 0
        while idx < len(raw_line):
            ch = raw_line[idx]
            if ch == "%":
                backslashes = 0
                j = idx - 1
                while j >= 0 and raw_line[j] == "\\":
                    backslashes += 1
                    j -= 1
                if backslashes % 2 == 0:
                    break
            out.append(ch)
            idx += 1
        lines.append("".join(out))
    return "\n".join(lines)


def latex_usepackages(text: str) -> List[str]:
    packages: List[str] = []
    for match in re.finditer(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", text):
        for package in match.group(1).split(","):
            normalized = package.strip()
            if normalized:
                packages.append(normalized)
    return packages


def _command_args(text: str, command: str) -> List[str]:
    pattern = re.compile(rf"\\{re.escape(command)}\s*\{{([^{{}}]*)\}}", re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(text)]


def find_unbalanced_setminted_lines(text: str) -> List[int]:
    lines: List[int] = []
    start = 0
    marker = r"\setminted{"

    while True:
        idx = text.find(marker, start)
        if idx == -1:
            break

        line_number = text.count("\n", 0, idx) + 1
        cursor = idx + len(marker)
        depth = 1
        balanced = False

        while cursor < len(text):
            char = text[cursor]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    balanced = True
                    break
            cursor += 1

        if not balanced:
            lines.append(line_number)
            break

        start = cursor + 1

    return lines


def find_malformed_mintinline_lines(text: str) -> List[int]:
    """Detect the broken \\mintinline"lang"code" shorthand.

    minted's \\mintinline always takes its language as a brace-delimited
    argument (\\mintinline{lang}{code}); a bare double-quote delimiter is a
    leftover migration artifact that pygmentize rejects (\"no lexer for alias
    '\"' found\") and which corrupts fvextra's Verbatim scanning downstream,
    surfacing as an unrelated "Missing end for environment Verbatim" error.
    """
    lines: List[int] = []
    for match in re.finditer(r'\\mintinline"[^"]*"', text):
        lines.append(text.count("\n", 0, match.start()) + 1)
    return lines


def _tracked_src_files() -> List[Path]:
    """Return existing tracked files under src/ in repo-relative form."""
    try:
        output = subprocess.check_output(["git", "ls-files", "src"], cwd=ROOT, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    files: List[Path] = []
    for line in output.splitlines():
        rel = line.strip()
        if not rel:
            continue
        path = ROOT / rel
        if path.exists() and path.is_file():
            files.append(path)
    return files


def _is_excluded_from_path_checks(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in LEGACY_PATH_EXCLUSIONS)


def filename_policy_violations(path: Path) -> List[str]:
    """Return filename-policy violations for a tracked src file."""
    rel = path.relative_to(ROOT).as_posix()
    if rel in FILENAME_POLICY_EXCEPTIONS:
        return []

    name = path.name
    base = path.stem
    violations: List[str] = []

    if len(name) > MAX_FILENAME_LENGTH:
        violations.append("filename-too-long")
    if any(ch.isupper() for ch in name):
        violations.append("uppercase-filename")
    if "_" in name:
        violations.append("underscore-filename")
    if " " in name:
        violations.append("space-in-filename")
    if ".tex.tex" in name or re.search(r"\.[a-z0-9]+\.[a-z0-9]+$", name):
        violations.append("duplicate-extension")
    if not KEBAB_BASENAME_PATTERN.fullmatch(base):
        violations.append("non-kebab-filename")
    if GENERIC_BASENAME_PATTERN.fullmatch(name.lower()):
        violations.append("generic-basename")

    return violations


def _validate_naming(files: Sequence[Path]) -> int:
    failures = 0
    seen_lower: Dict[str, str] = {}

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        lower_rel = rel.lower()
        if lower_rel in seen_lower and seen_lower[lower_rel] != rel:
            failures += 1
            print(f"case-collision: {seen_lower[lower_rel]} :: {rel}")
        else:
            seen_lower[lower_rel] = rel

        suffix = path.suffix.lower()
        if suffix and suffix not in SOURCE_EXTENSIONS:
            continue

        for violation in filename_policy_violations(path):
            failures += 1
            print(f"{violation}: {rel}")

        if _is_excluded_from_path_checks(rel):
            continue

        for part in path.relative_to(SRC_DIR).parts:
            if part in {"readme.md", "git-workflow.md"}:
                continue
            if "." in part:
                base, ext = part.rsplit(".", 1)
                if not KEBAB_BASENAME_PATTERN.fullmatch(base):
                    failures += 1
                    print(f"non-kebab-path: {rel}")
                    break
                if not re.fullmatch(r"[a-z0-9]+", ext):
                    failures += 1
                    print(f"invalid-extension: {rel}")
                    break
            else:
                if not KEBAB_BASENAME_PATTERN.fullmatch(part):
                    failures += 1
                    print(f"non-kebab-path: {rel}")
                    break

    return failures


def validate_repo() -> int:
    failures = 0

    tracked_files = _tracked_src_files()
    failures += _validate_naming(tracked_files)

    for tex_path in discover_latex_roots():
        text = tex_path.read_text(encoding="utf-8", errors="ignore")
        active_text = strip_latex_comments(text)
        rel = tex_path.relative_to(ROOT).as_posix()

        for line in find_unbalanced_setminted_lines(active_text):
            failures += 1
            print(f"unbalanced-setminted: {rel}:{line}")

        for line in find_malformed_mintinline_lines(active_text):
            failures += 1
            print(f"malformed-mintinline-shorthand: {rel}:{line}")

        for pattern in MINTED_SHARED_HELPER_PATTERNS:
            for match in pattern.finditer(active_text):
                failures += 1
                line = active_text.count("\n", 0, match.start()) + 1
                print(f"duplicate-shared-minted-helper: {rel}:{line}")

        if re.search(r"\\usepackage\{(?:style|base)\}", active_text):
            failures += 1
            print(f"forbidden-direct-style-import: {rel}")

        is_cornell_root = (
            rel.startswith("src/cornell-notes/electronics/electronic-circuits/")
            or rel.startswith("src/cornell-notes/security/certifications/cissp/")
            or rel.startswith("src/cornell-notes/mathematics/numerical-methods/")
            or rel == "src/architecture/style-system/examples/cornell-notes-study-sheet.tex"
        )
        uses_cornell_notes = bool(re.search(r"\\usepackage(?:\[[^\]]*\])?\{[^}]*\bcornell-notes\b[^}]*\}", active_text))

        if is_cornell_root and not uses_cornell_notes:
            failures += 1
            print(f"invalid-cornell-import: {rel}")

        if is_cornell_root:
            if not uses_cornell_notes:
                failures += 1
                print(f"invalid-cornell-import: {rel}")

            packages = latex_usepackages(active_text)
            semantic_packages = [name for name in packages if name in SEMANTIC_STYLE_PACKAGES]
            if semantic_packages != ["cornell-notes"]:
                failures += 1
                print(f"invalid-cornell-semantic-style-set: {rel}")

            title_values = _command_args(active_text, "title")
            if not title_values:
                failures += 1
                print(f"missing-cornell-title-command: {rel}")
            elif all(value == "" for value in title_values):
                failures += 1
                print(f"empty-cornell-title-command: {rel}")

            maketitle_count = len(re.findall(r"\\maketitle\b", active_text))
            if maketitle_count == 0:
                failures += 1
                print(f"missing-cornell-maketitle: {rel}")
            elif maketitle_count > 1:
                failures += 1
                print(f"multiple-cornell-maketitle: {rel}")

            if re.search(r"\\makecornelltitle\b", active_text):
                failures += 1
                print(f"legacy-cornell-title-command: {rel}")

            if re.search(r"\\begin\s*\{titlepage\}|\\end\s*\{titlepage\}", active_text):
                failures += 1
                print(f"manual-titlepage-in-cornell-doc: {rel}")

        if any(token in active_text for token in LISTINGS_TOKENS):
            failures += 1
            print(f"listings-token: {rel}")

    for puml_path in sorted(path for path in tracked_files if path.suffix.lower() == ".puml"):
        rel = puml_path.relative_to(ROOT).as_posix()
        text = puml_path.read_text(encoding="utf-8", errors="ignore")
        lower_name = puml_path.name.lower()
        if lower_name in FORBIDDEN_PLANTUML_WRAPPER_FILES:
            failures += 1
            print(f"wrapper-style-file: {rel}")
            continue
        if "config" in lower_name:
            continue
        if not PLANTUML_START_PATTERN.search(text):
            continue

        if "@enduml" not in text.lower():
            failures += 1
            print(f"missing-enduml: {rel}")

        if "appsec-style.puml" in text:
            failures += 1
            print(f"wrapper-style-include: {rel}")

        if not PLANTUML_DIRECT_STYLE_PATTERN.search(text):
            failures += 1
            print(f"missing-direct-style: {rel}")

    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate direct semantic style imports")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.validate:
        return validate_repo()
    return 0


if __name__ == "__main__":
    sys.exit(main())
