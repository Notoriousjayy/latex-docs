#!/usr/bin/env python3
"""Machine-readable inventory of every first-party PlantUML diagram.

One row per renderable source (and one per @startuml block) covering the fields
the architecture-description index needs: stable diagram ID, source and output
names, collection, purpose, actual model kind (derived from the leaf style the
diagram includes and the C4 level where applicable), primary style entry point,
transitive includes and configuration, output matrix, consuming documents,
subject kind and validation status from the last render result.

Discovery boundary: `.puml` files under src/ and tooling/plantuml (framework
examples). Include-only fragments and configuration files are listed with
kind "fragment"/"config" and excluded from render counts. Test fixtures are
created in temporary directories by the test suite and never live in the
tree; there are no vendored third-party diagram sources (the C4 library is
consumed from the pinned jar's stdlib).

Usage:
    python3 tooling/scripts/plantuml_inventory.py --json out.json --csv out.csv --markdown out.md
    python3 tooling/scripts/plantuml_inventory.py --check   # exit 1 on collisions/unstyled sources
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latex_build  # noqa: E402

ROOT = latex_build.ROOT
SRC = ROOT / "src"
EXAMPLES = ROOT / "tooling" / "plantuml"
ROOTS = (SRC, EXAMPLES)

LEAF_RE = re.compile(r"tooling/styles/plantuml/(structural|behavioral|interaction|c4)/([a-z0-9-]+)-diagram-style\.iuml$")
TITLE_RE = re.compile(r"^title\s+(.+)$", re.M)
HEADER_RE = re.compile(r"^'\s*(Diagram|Type|Owns|Status|Subject|Model kind|Purpose|Message|Section)\s*:\s*(.+)$", re.M)
DIAGRAM_MACRO_RE = re.compile(r"\\diagram(?:\[[^\]]*\])?\{([^{}]+)\}")
GRAPHICS_RE = re.compile(r"\\(?:safe)?includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}", re.I)
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")

# Leaf style -> (model kind label, notation, governing specification)
MODEL_KINDS = {
    "structural/class": ("UML class diagram", "UML 2.5.1 cl. 11 (Classifiers, StructuredClassifiers)"),
    "structural/object": ("UML object (instance) diagram", "UML 2.5.1 cl. 11.3, Annex A"),
    "structural/component": ("UML component diagram", "UML 2.5.1 cl. 11.6 (Components)"),
    "structural/deployment": ("UML deployment diagram", "UML 2.5.1 cl. 19 (Deployments)"),
    "structural/package": ("UML package diagram", "UML 2.5.1 cl. 12.2 (Packages)"),
    "structural/composite-structure": ("UML composite structure diagram", "UML 2.5.1 cl. 11.2-11.4"),
    "structural/profile": ("UML profile diagram", "UML 2.5.1 cl. 12.3 (Profiles)"),
    "behavioral/activity": ("UML activity diagram", "UML 2.5.1 cl. 15 (Activities), 16 (Actions)"),
    "behavioral/statemachine": ("UML state machine diagram", "UML 2.5.1 cl. 14 (StateMachines)"),
    "behavioral/usecase": ("UML use case diagram", "UML 2.5.1 cl. 18 (UseCases)"),
    "interaction/sequence": ("UML sequence diagram", "UML 2.5.1 cl. 17 (Interactions)"),
    "interaction/communication": ("UML communication diagram", "UML 2.5.1 cl. 17.9"),
    "interaction/timing": ("UML timing diagram", "UML 2.5.1 cl. 17.10"),
    "interaction/interaction-overview": ("UML interaction overview diagram", "UML 2.5.1 cl. 17.11"),
    "c4/context": ("C4 system context / landscape view", "C4 model: system context diagram"),
    "c4/container": ("C4 container view", "C4 model: container diagram"),
    "c4/component": ("C4 component view", "C4 model: component diagram"),
    "c4/dynamic": ("C4 dynamic view", "C4 model: dynamic diagram"),
    "c4/deployment": ("C4 deployment view", "C4 model: deployment diagram"),
}

# Collection -> (subject kind, viewpoint id) per src/architecture/readme.md (AD index).
COLLECTION_RULES = (
    ("src/architecture/views-and-beyond/", "reference pattern (Views and Beyond style catalogue)", "VP-STYLE-CATALOG"),
    ("src/architecture/cloud/", "reference pattern (cloud architecture library)", "VP-CLOUD-PATTERN"),
    ("src/architecture/diagrams/", "teaching example", "VP-SOFTWARE-STRUCTURE"),
    ("src/architecture/enterprise/", "proposed design (reference integration/operating model)", "VP-ENTERPRISE-INTEGRATION"),
    ("src/devops/platform/", "reference deployment (vendor-documented)", "VP-PLATFORM-DEPLOYMENT"),
    ("src/devops/ci-cd/", "reference process", "VP-DELIVERY-PROCESS"),
    ("src/security/application-security/processes/", "operational process (teaching/reference)", "VP-SECURITY-PROCESS"),
    ("src/security/", "teaching example (security)", "VP-SECURITY-TEACHING"),
    ("tooling/plantuml/", "framework example (fixture)", "VP-FRAMEWORK-EXAMPLE"),
)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _collection(path: Path) -> str:
    parts = path.relative_to(ROOT).parts
    if parts[0] == "tooling":
        return "tooling/plantuml"
    if len(parts) > 3 and parts[1] == "architecture" and parts[2] == "views-and-beyond":
        return "/".join(parts[:6])
    return "/".join(parts[:3])


def _subject(rel: str) -> tuple[str, str]:
    for prefix, kind, viewpoint in COLLECTION_RULES:
        if rel.startswith(prefix):
            return kind, viewpoint
    return "unclassified", "VP-UNSPECIFIED"


def _consumers() -> dict[Path, set[str]]:
    outputs: dict[Path, Path] = {}
    for root in ROOTS:
        for source in root.rglob("*.puml"):
            for fmt in latex_build.PLANTUML_FORMATS:
                for out in (source.parent / fmt).glob(f"*.{fmt}") if (source.parent / fmt).is_dir() else []:
                    outputs.setdefault(out.resolve(), source)
    # Prefer the source whose block names produce the output.
    for root in ROOTS:
        for source in root.rglob("*.puml"):
            try:
                text = source.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for fmt in latex_build.PLANTUML_FORMATS:
                for out in latex_build.plantuml_output_paths(source, fmt, text):
                    if out.exists():
                        outputs[out.resolve()] = source
    consumers: dict[Path, set[str]] = defaultdict(set)
    for doc in list(SRC.rglob("*.tex")) + list(SRC.rglob("*.md")):
        try:
            text = doc.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        refs = [r.strip() for r in GRAPHICS_RE.findall(text)] + [r for r in MD_IMAGE_RE.findall(text)]
        if "\\diagram}" in text or "\\newcommand{\\diagram}" in text:
            refs += [f"png/{n.strip()}.png" for n in DIAGRAM_MACRO_RE.findall(text)]
        for ref in refs:
            if "\\" in ref or "#" in ref or ref.startswith("http"):
                continue
            base = doc.parent / ref
            candidates = [base] if Path(ref).suffix else [base.with_suffix(ext) for ext in (".png", ".svg", ".jpg", ".pdf")]
            for candidate in candidates:
                hit = outputs.get(candidate.resolve())
                if hit is not None:
                    consumers[hit].add(_rel(doc))
    return consumers


def build_inventory(render_result: Path | None = None) -> dict:
    consumers = _consumers()
    render_status: dict[str, dict] = {}
    if render_result and render_result.is_file():
        data = json.loads(render_result.read_text(encoding="utf-8"))
        render_status = {d["source"]: d for d in data.get("diagrams", [])}
    lowered_config = {n.lower() for n in latex_build.PLANTUML_CONFIG_NAMES}
    rows: list[dict] = []
    seen: set[Path] = set()
    for root in ROOTS:
        for source in sorted(root.rglob("*.puml")):
            if source in seen or not source.is_file():
                continue
            seen.add(source)
            rel = _rel(source)
            text = source.read_text(encoding="utf-8", errors="ignore")
            if source.name.lower() in lowered_config:
                rows.append({"id": rel, "source": rel, "kind": "config", "collection": _collection(source)})
                continue
            names = latex_build._plantuml_output_names(source, text)
            if not names:
                rows.append({"id": rel, "source": rel, "kind": "fragment", "collection": _collection(source)})
                continue
            includes = sorted(_rel(p) for p in latex_build.plantuml_includes(source, text))
            leaf = next((m for inc in includes for m in [LEAF_RE.search(inc)] if m), None)
            leaf_key = f"{leaf.group(1)}/{leaf.group(2)}" if leaf else ""
            model_kind, governing = MODEL_KINDS.get(leaf_key, ("unstyled", ""))
            c4_level = leaf.group(2) if leaf and leaf.group(1) == "c4" else ""
            headers = {k.lower(): v.strip() for k, v in HEADER_RE.findall(text)}
            title = TITLE_RE.search(text)
            subject_kind, viewpoint = _subject(rel)
            status = render_status.get(rel, {})
            config = latex_build.plantuml_config_for(source)
            outputs = {
                fmt: [
                    {"path": _rel(p), "exists": p.exists()}
                    for p in latex_build.plantuml_output_paths(source, fmt, text)
                ]
                for fmt in latex_build.PLANTUML_FORMATS
            }
            for index, name in enumerate(names):
                rows.append(
                    {
                        "id": f"{rel}#{name}",
                        "source": rel,
                        "block": name,
                        "block_index": index,
                        "kind": "diagram",
                        "collection": _collection(source),
                        "title": (title.group(1).replace("\\n", " ").strip() if title else headers.get("diagram", "")),
                        "purpose": headers.get("owns") or headers.get("purpose") or headers.get("message") or "",
                        "declared_type": headers.get("type", ""),
                        "subject_kind": subject_kind,
                        "declared_status": headers.get("status", ""),
                        "viewpoint": viewpoint,
                        "model_kind": model_kind,
                        "governing_specification": governing,
                        "c4_level": c4_level,
                        "primary_style": f"tooling/styles/plantuml/{leaf_key}-diagram-style.iuml" if leaf else "",
                        "includes": includes,
                        "config": _rel(config) if config else "",
                        "outputs": {fmt: entries[index] for fmt, entries in outputs.items() if index < len(entries)},
                        "required_formats": ["png", "svg"] + (["jpg"] if outputs["jpg"][index]["exists"] else []),
                        "consumers": sorted(consumers.get(source, set())),
                        "render_status": status.get("status", "unknown"),
                        "render_formats": status.get("formats", {}),
                        "migration_action": "converted-to-c4" if c4_level else ("migrated-to-house-tokens" if source.is_relative_to(SRC) else "framework-example"),
                    }
                )
    diagrams = [r for r in rows if r["kind"] == "diagram"]
    collisions = [
        f"{d}: {n} produced by {', '.join(sorted(s))}"
        for (d, n), s in _collisions(diagrams).items()
        if len(s) > 1
    ]
    summary = {
        "files": len(rows) - sum(1 for r in rows if r.get("block_index", 0) > 0),
        "config_files": sum(1 for r in rows if r["kind"] == "config"),
        "fragments": sum(1 for r in rows if r["kind"] == "fragment"),
        "diagram_sources": len({r["source"] for r in diagrams}),
        "diagram_blocks": len(diagrams),
        "by_model_kind": dict(Counter(r["model_kind"] for r in diagrams).most_common()),
        "by_collection": dict(Counter(r["collection"] for r in diagrams).most_common()),
        "by_subject_kind": dict(Counter(r["subject_kind"] for r in diagrams).most_common()),
        "with_consumers": sum(1 for r in diagrams if r["consumers"]),
        "unstyled": [r["id"] for r in diagrams if r["model_kind"] == "unstyled"],
        "output_collisions": collisions,
        "missing_required_outputs": [
            f"{r['id']}:{fmt}" for r in diagrams for fmt in r["required_formats"] if not r["outputs"][fmt]["exists"]
        ],
        "render_status": dict(Counter(r["render_status"] for r in diagrams)),
    }
    return {"summary": summary, "rows": rows}


def _collisions(diagrams: list[dict]) -> dict[tuple[str, str], set[str]]:
    by_output: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in diagrams:
        by_output[(str(Path(row["source"]).parent), row["block"])].add(row["source"])
    return by_output


def write_markdown(inventory: dict, path: Path) -> None:
    s = inventory["summary"]
    lines = [
        "# PlantUML diagram inventory",
        "",
        "Generated by `tooling/scripts/plantuml_inventory.py`; regenerate rather than edit.",
        "",
        f"- Files: {s['files']} (config {s['config_files']}, include-only fragments {s['fragments']})",
        f"- Diagram sources / blocks: {s['diagram_sources']} / {s['diagram_blocks']}",
        f"- Sources with a document consumer: {s['with_consumers']}",
        f"- Output-name collisions: {len(s['output_collisions'])}; missing required outputs: {len(s['missing_required_outputs'])}",
        "",
        "## By model kind",
        "",
        "| Model kind | Diagrams |",
        "| --- | --- |",
        *[f"| {k} | {v} |" for k, v in s["by_model_kind"].items()],
        "",
        "## By subject kind",
        "",
        "| Subject kind | Diagrams |",
        "| --- | --- |",
        *[f"| {k} | {v} |" for k, v in s["by_subject_kind"].items()],
        "",
        "## Diagrams",
        "",
        "| ID | Viewpoint | Model kind | C4 | Subject | Style entry point | Formats | Consumers | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in inventory["rows"]:
        if r["kind"] != "diagram":
            continue
        fmts = "/".join(f for f in latex_build.PLANTUML_FORMATS if r["outputs"].get(f, {}).get("exists"))
        style = Path(r["primary_style"]).name.replace("-diagram-style.iuml", "") if r["primary_style"] else "-"
        lines.append(
            f"| {r['id']} | {r['viewpoint']} | {r['model_kind']} | {r['c4_level'] or '-'} | {r['subject_kind']} | "
            f"{style} | {fmts} | {len(r['consumers'])} | {r['render_status']} |"
        )
    lines += ["", "## Non-diagram files", "", "| Path | Kind |", "| --- | --- |"]
    lines += [f"| {r['source']} | {r['kind']} |" for r in inventory["rows"] if r["kind"] != "diagram"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--render-result", type=Path, default=latex_build.PLANTUML_RESULT_DEFAULT)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--check", action="store_true", help="exit 1 on collisions, unstyled or missing required outputs")
    args = parser.parse_args(argv)
    inventory = build_inventory(args.render_result)
    summary = inventory["summary"]
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        fields = ["id", "source", "block", "kind", "collection", "title", "viewpoint", "model_kind", "c4_level",
                  "subject_kind", "primary_style", "config", "required_formats", "consumers", "render_status", "migration_action"]
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in inventory["rows"]:
                out = dict(row)
                for key in ("required_formats", "consumers"):
                    if isinstance(out.get(key), list):
                        out[key] = " ".join(out[key])
                writer.writerow(out)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(inventory, args.markdown)
    print(json.dumps({k: v for k, v in summary.items() if not isinstance(v, (list, dict))}), file=sys.stderr)
    problems = summary["unstyled"] + summary["output_collisions"] + summary["missing_required_outputs"]
    if problems:
        for problem in problems:
            print(f"inventory: {problem}", file=sys.stderr)
    return 1 if (args.check and problems) else 0


if __name__ == "__main__":
    raise SystemExit(main())
