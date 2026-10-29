#!/usr/bin/env python3
"""Generate consistent multi-axis Markdown catalog pages from the evidence manifest.

Provisional classifications remain visible; no filename-derived category becomes
a claim of semantic review. Curated scorecard and secure-coding pages are retained.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tooling/manifests/semantic-document-inventory.json"

GROUPS = [
    ("by-domain", "Browse by Domain", "domain"),
    ("by-subject", "Browse by Subject", "primary_subject"),
    ("by-document-type", "Browse by Document Type", "primary_type"),
]
ARTIFACTS = [
    ("user-stories", "User Stories", "user-stories"),
    ("templates", "Reusable Templates", "template"),
    ("workbooks", "Workbooks and Exercises", "workbook"),
    ("checklists", "Checklists", "checklist"),
    ("technical-references", "Technical References", "technical-reference"),
    ("assessments", "Assessments", "assessment"),
    ("runbooks", "Operational Runbooks", "runbook"),
    ("study-guides", "Study Guides", "study-guide"),
    ("handbooks", "Handbooks", "handbook"),
    ("business-plans", "Business Plans", "business-plan"),
    ("architecture-documents", "Architecture Documents", "architecture-document"),
    ("source-fragments", "LaTeX Source Fragments", "latex-fragment"),
]
NOTE = (
    "**Provenance:** Reviewed entries have targeted content inspection; "
    "provisional type and subject labels are path-derived and should not be treated as verified. "
    "Links identify canonical source files."
)


def one(entry: dict) -> str:
    title = entry["title"].replace("[", r"\[").replace("]", r"\]")
    reviewed = "reviewed" if entry["review_status"] == "targeted-content-reviewed" else "provisional"
    suffix = " · non-standalone" if entry["primary_type"] == "latex-fragment" else ""
    return (
        f"- [{title}](../{entry['path']}) — {entry['primary_subject']} "
        f"· **{reviewed}**{suffix}\n"
    )


def group(sources: list[dict], key: str, title: str) -> str:
    out = f"# {title}\n\n{NOTE}\n\n"
    for label in sorted({entry[key] for entry in sources}):
        entries = sorted((e for e in sources if e[key] == label), key=lambda e: e["path"])
        out += f"## {label} ({len(entries)})\n\n{''.join(map(one, entries))}\n"
    return out


def artifact(sources: list[dict], title: str, kind: str) -> str:
    primary = sorted((e for e in sources if e["primary_type"] == kind), key=lambda e: e["path"])
    secondary = sorted(
        (e for e in sources if e["primary_type"] != kind
         and e["review_status"] == "targeted-content-reviewed"
         and kind in e["secondary_types"]),
        key=lambda e: e["path"]
    )
    out = f"# {title}\n\n{NOTE}\n\n## Primary {title.lower()} ({len(primary)})\n\n"
    out += "".join(map(one, primary)) if primary else "No primary sources currently classified in this category.\n"
    if secondary:
        out += (
            f"\n## Related reviewed sources with secondary {title.lower()} content "
            f"({len(secondary)})\n\n{''.join(map(one, secondary))}"
        )
    return out


def index(sources: list[dict], inventory: dict) -> str:
    counts = {slug: sum(e["primary_type"] == kind for e in sources) for slug, _, kind in ARTIFACTS}
    out = (
        "# Documentation Discovery Catalog\n\n"
        "Find documents by **domain**, **subject**, or **artifact type** without duplicating "
        "LaTeX sources. This catalog is generated from the content-review manifest.\n\n"
        "## Browse\n\n"
        "| Catalog | Number of primary sources |\n"
        "|---|---:|\n"
        f"| [By domain](by-domain.md) | {len(sources)} |\n"
        f"| [By subject](by-subject.md) | {len(sources)} |\n"
        f"| [By document type](by-document-type.md) | {len(sources)} |\n"
    )
    for slug, title, _ in ARTIFACTS:
        out += f"| [{title}]({slug}.md) | {counts[slug]} |\n"
    out += (
        "| [Scorecards and embedded evaluation tools](scorecards.md) | "
        "0 standalone verified; embedded examples listed |\n"
        "| [Secure coding by language](secure-coding.md) | Language-specific and cross-domain guidance |\n\n"
        "## Provenance and maintenance\n\n"
        + NOTE
        + f"\n\n**{inventory['reviewed_items']} of {inventory['document_count']}** LaTeX sources "
        + "have targeted semantic content review; "
        + f"**{inventory['document_count']-inventory['reviewed_items']}** remain provisional. "
        + "A reference that merely contains a checklist, workbook section, or scorecard "
        + "does not automatically have that primary type. Non-standalone LaTeX fragments "
        + "have their own classification and are not regular documents.\n\n"
        + "After modifying the inventory, regenerate the indexes with "
        + chr(96) + "python3 tooling/scripts/build_semantic_catalogs.py --write" + chr(96)
        + "; CI checks that the committed catalogs match the manifest. "
        + "Update the relevant domain README for substantive source relocations.\n"
    )
    return out


def render(inventory: dict) -> dict[str, str]:
    sources = inventory["sources"]
    result = {f"catalog/{slug}.md": group(sources, key, title)
              for slug, title, key in GROUPS}
    result.update({f"catalog/{slug}.md": artifact(sources, title, kind)
                   for slug, title, kind in ARTIFACTS})
    result["catalog/README.md"] = index(sources, inventory)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inventory = json.loads(MANIFEST.read_text(encoding="utf-8"))
    outputs = render(inventory)
    stale = []
    for relative, body in sorted(outputs.items()):
        path = ROOT / relative
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        elif not path.is_file() or path.read_text(encoding="utf-8") != body:
            stale.append(relative)
    if stale:
        print("Outdated semantic catalogs: " + ", ".join(stale))
        return 1
    print(f"Validated {len(outputs)} catalog pages from {len(inventory['sources'])} sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
