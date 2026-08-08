#!/usr/bin/env python3
"""Lightweight migration helpers for direct semantic style imports."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Sequence

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


def classify_latex_style(path: Path) -> str:
    rel = str(path).lower()
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
        if path.is_file() and re.search(r"^\\documentclass", path.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE):
            roots.append(path.resolve())
    return roots


def validate_repo() -> int:
    failures = 0
    for tex_path in discover_latex_roots():
        text = tex_path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\\usepackage\{style\}", text) or re.search(r"\\usepackage\{base\}", text):
            failures += 1
            print(f"wrapper-style: {tex_path.relative_to(ROOT)}")
        if not re.search(r"\\usepackage\{[A-Za-z0-9._-]+\}", text):
            failures += 1
            print(f"missing-style: {tex_path.relative_to(ROOT)}")
        if any(token in text for token in LISTINGS_TOKENS):
            failures += 1
            print(f"listings-token: {tex_path.relative_to(ROOT)}")
    for puml_path in sorted(SRC_DIR.rglob("*.puml")):
        text = puml_path.read_text(encoding="utf-8", errors="ignore")
        if puml_path.name.endswith("-style.puml") or "config" in puml_path.name.lower():
            continue
        if not re.search(r"@start(?:uml|mindmap|activity|flowchart|gantt|wbs|state|json|yaml|class|sequence|usecase|component|deployment|object|rect|command|graph)", text, re.IGNORECASE):
            continue
        if "appsec-style.puml" in text or "uml-base.iuml" in text or "uml-behavioral.iuml" in text or "uml-interaction.iuml" in text or "uml-structural.iuml" in text:
            failures += 1
            print(f"wrapper-style: {puml_path.relative_to(ROOT)}")
        if "!include " not in text:
            failures += 1
            print(f"missing-style: {puml_path.relative_to(ROOT)}")
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
