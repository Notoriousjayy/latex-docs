#!/usr/bin/env python3
"""Resumable, collection-scoped migration for root Cornell-note intakes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "tooling" / "manifests" / "cornell-migration"
STAGE_ROOT = Path("/tmp/latex-docs-cornell-migration")
ISO_ROOT = ROOT / "src" / "cornell-notes" / "architecture" / "standards" / "iso-iec-ieee-42010-2022"
CPP_ROOT = ROOT / "src" / "cornell-notes" / "programming" / "languages" / "cpp" / "cpp-2024"
FIELDS = [
    "source_path", "source_filename", "source_sha256", "collection",
    "canonical_filename", "unit_type", "top_level_unit", "unit_identifier",
    "document_title", "topic_slug", "destination_path", "transformed_sha256",
    "classification_evidence", "status",
]
EXPECTED = {"iso": 115, "cpp": 2547}
COLLECTION_NAMES = {"iso": "iso-iec-ieee-42010-2022", "cpp": "cpp-2024"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value.lower()).strip("-")
    return value or "general"


def clean_filename(name: str) -> str:
    return re.sub(r" \([0-9]+\)(?=\.tex$)", "", name)


def iso_source(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")[:7000]
    return bool("CNavy" in text and "CLight" in text and "longtable" in text)


def parse_identity(path: Path, text: str) -> tuple[str, str, str, str, str]:
    name = clean_filename(path.name)
    stem = name.removesuffix(".tex").removesuffix("-cornell-notes")
    if stem.startswith("introduction"):
        return "Introduction", "introduction", "Introduction", "Introduction", "Introduction"
    annex = re.match(r"annex-([a-f])-(.+)$", stem, re.I)
    if annex:
        letter, rest = annex.groups()
        identifier_match = re.match(r"([0-9]+(?:-[0-9]+)*)-", rest)
        identifier = f"{letter.upper()}.{identifier_match.group(1).replace('-', '.') if identifier_match else ''}".rstrip(".")
        title = re.sub(r"^[0-9]+(?:-[0-9]+)*-", "", rest).replace("-", " ").strip().title()
        return "Annex", f"annex-{letter.lower()}", identifier, title, slug(f"annex-{letter}-{rest.split('-')[0]}")
    parts = stem.split("-")
    number_parts = []
    while parts and parts[0].isdigit():
        number_parts.append(parts.pop(0))
    identifier = ".".join(number_parts) if number_parts else stem
    title = " ".join(parts).replace("-", " ").strip().title()
    top = number_parts[0] if number_parts else "00"
    return "Clause", top, identifier, title, slug(f"{top}-{'-'.join(parts)}")


def classify(path: Path) -> tuple[str, str]:
    if iso_source(path):
        return "iso", "ISO-specific CNavy/CLight Cornell template"
    return "cpp", "collection remainder after ISO-specific template classification"


def extract_command_argument(text: str, command: str, start: int) -> tuple[int, str] | None:
    marker = text.find(command, start)
    if marker < 0:
        return None
    opening = text.find("{", marker + len(command))
    if opening < 0:
        return None
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index + 1, text[opening + 1:index]
    return None


def convert_iso(text: str, title: str, unit_type: str, identifier: str) -> str:
    marker = re.search(r"\\begin\{document\}", text)
    end_marker = re.search(r"\\end\{document\}", text)
    if not marker or not end_marker or end_marker.start() <= marker.end():
        raise ValueError("document body markers are malformed")
    body = text[marker.end():end_marker.start()]
    body = re.sub(r"^\s*\\maketitle\s*", "", body)
    overview = re.search(r"\\begin\{tcolorbox\}\[.*?\](.*?)\\end\{tcolorbox\}", body, re.S)
    overview_text = ""
    if overview:
        overview_text = overview.group(1)
        overview_text = re.sub(r"\\vspace\{[^}]*\}", "", overview_text)
        body = body[:overview.start()] + body[overview.end():]
    table = re.search(r"\\begin\{longtable\}.*?\\end\{longtable\}", body, re.S)
    rows = []
    if table:
        table_text = table.group(0)
        for match in re.finditer(r"\\textbf\{([^{}]+)\}\s*&\s*(.*?)\\\\\s*\\hline", table_text, re.S):
            cue = match.group(1).strip()
            notes = match.group(2).strip()
            notes = re.sub(r"\\hline|\\endfirsthead|\\endhead", "", notes).strip()
            if cue.lower() not in {"cue / question", "detailed notes"}:
                rows.append(f"\\CornellNoteRow{{{cue}}}{{{notes}}}")
        body = body[:table.start()] + "\n\\begin{CornellNotesTable}\n" + "\n".join(rows) + "\n\\end{CornellNotesTable}\n" + body[table.end():]
    body = re.sub(r"\\begin\{tcolorbox\}\[title=Summary,.*?\](.*?)\\end\{tcolorbox\}", r"\\begin{CornellSummaryBox}{Summary}\1\\end{CornellSummaryBox}", body, flags=re.S)
    unit_label = title if unit_type == "Introduction" else f"{unit_type} {identifier}: {title}"
    header = f"""\\documentclass[10pt,letterpaper]{{article}}
\\usepackage{{cornell-notes}}

\\title{{{unit_label}}}
\\author{{}}
\\date{{}}
\\setDocTitle{{{unit_label}}}
\\setDocSubtitle{{ISO/IEC/IEEE 42010:2022}}
\\setDocOwner{{ISO 42010 Cornell Notes}}
\\setDocDate{{\\today}}
\\setCornellCollection{{ISO/IEC/IEEE 42010:2022 Cornell Notes}}
\\setCornellUnitType{{{unit_type}}}
\\setCornellUnitNumber{{{identifier}}}
\\setCornellUnitTitle{{{title}}}
\\hypersetup{{pdftitle={{{unit_label}}},pdfsubject={{Cornell notes}},pdfauthor={{}}}}

\\begin{{document}}
\\maketitle
"""
    overview_block = f"\\begin{{CornellOverviewBox}}{{Overview}}\n{overview_text.strip()}\n\\end{{CornellOverviewBox}}\n" if overview_text.strip() else ""
    return header + overview_block + body.lstrip() + "\n\\end{document}\n"


def convert_cpp(text: str, title: str, unit_type: str, identifier: str) -> str:
    marker = re.search(r"\\begin\{document\}", text)
    end_marker = re.search(r"\\end\{document\}", text)
    if not marker or not end_marker or end_marker.start() <= marker.end():
        raise ValueError("document body markers are malformed")
    body = text[marker.end():end_marker.start()]
    table = re.search(r"\\begin\{longtable\}.*?\\end\{longtable\}", body, re.S)
    rows = []
    if table:
        table_text = table.group(0)
        for match in re.finditer(r"([^&\n]+?)\s*&\s*(.*?)\\\\(?:\[[^]]+\])?", table_text, re.S):
            cue = match.group(1).strip()
            notes = match.group(2).strip()
            if cue.startswith("\\textbf") or cue in {"\\toprule", "\\midrule", "\\bottomrule"}:
                continue
            cue = re.sub(r"\\textbf\{([^{}]+)\}", r"\1", cue)
            if cue and notes and cue not in {"Cue / Question", "Detailed Notes", "Detailed Notes (continued)"}:
                rows.append(f"\\CornellNoteRow{{{cue}}}{{{notes}}}")
        body = body[:table.start()] + "\n\\begin{CornellNotesTable}\n" + "\n".join(rows) + "\n\\end{CornellNotesTable}\n" + body[table.end():]
    position = 0
    replacements = []
    while True:
        result = extract_command_argument(body, "\\infobox", position)
        if result is None:
            break
        end, argument = result
        label = "Overview" if "Classification:" in argument else "Summary"
        content = argument
        content = re.sub(r"\{\\s*\\s*\\s*\\s*", "{", content)
        replacements.append((position, end, f"\\begin{{Cornell{'OverviewBox' if label == 'Overview' else 'SummaryBox'}}}{{{label}}}\n{content}\n\\end{{Cornell{'OverviewBox' if label == 'Overview' else 'SummaryBox'}}}"))
        position = end
    for start, end, replacement in reversed(replacements):
        body = body[:start] + replacement + body[end:]
    unit_label = title if unit_type == "Introduction" else f"{unit_type} {identifier}: {title}"
    header = f"""\\documentclass[10pt,letterpaper]{{article}}
\\usepackage{{cornell-notes}}

\\title{{{unit_label}}}
\\author{{}}
\\date{{}}
\\setDocTitle{{{unit_label}}}
\\setDocSubtitle{{C++ 2024}}
\\setDocOwner{{C++ 2024 Cornell Notes}}
\\setDocDate{{\\today}}
\\setCornellCollection{{C++ 2024 Cornell Notes}}
\\setCornellUnitType{{{unit_type}}}
\\setCornellUnitNumber{{{identifier}}}
\\setCornellUnitTitle{{{title}}}
\\hypersetup{{pdftitle={{{unit_label}}},pdfsubject={{Cornell notes}},pdfauthor={{}}}}

\\begin{{document}}
\\maketitle
"""
    return header + body.lstrip() + "\n\\end{document}\n"


def inventory(collection: str) -> list[dict[str, str]]:
    records = []
    sources = sorted(ROOT.glob("*.tex"))
    if collection == "iso":
        selected = [p for p in sources if iso_source(p)]
    elif collection == "cpp":
        selected = [p for p in sources if not iso_source(p)]
    else:
        selected = sources
    for source in selected:
        coll, evidence = classify(source)
        if coll != collection:
            continue
        text = source.read_text(encoding="utf-8", errors="ignore")
        unit_type, top, identifier, title, topic = parse_identity(source, text)
        filename = clean_filename(source.name)
        if unit_type == "Introduction":
            relative = Path("introduction") / filename
        elif unit_type == "Annex":
            relative = Path("annexes") / topic / filename
        else:
            relative = Path("clauses") / topic / filename
        destination = (ISO_ROOT if collection == "iso" else CPP_ROOT) / relative
        records.append({
            "source_path": source.relative_to(ROOT).as_posix(),
            "source_filename": source.name,
            "source_sha256": sha256(source),
            "collection": collection,
            "canonical_filename": filename,
            "unit_type": unit_type,
            "top_level_unit": top,
            "unit_identifier": identifier,
            "document_title": title,
            "topic_slug": topic,
            "destination_path": destination.relative_to(ROOT).as_posix(),
            "transformed_sha256": "",
            "classification_evidence": evidence,
            "status": "inventoried",
        })
    return records


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def validate_records(records: list[dict[str, str]], expected: int) -> None:
    if len(records) != expected:
        raise RuntimeError(f"expected {expected} records, found {len(records)}")
    sources = [r["source_path"] for r in records]
    destinations = [r["destination_path"].lower() for r in records]
    if len(set(sources)) != len(sources):
        raise RuntimeError("duplicate physical source paths")
    if len(set(destinations)) != len(destinations):
        groups = defaultdict(list)
        for record in records:
            groups[record["destination_path"].lower()].append(record["source_path"])
        raise RuntimeError(f"destination collision: {next(v for v in groups.values() if len(v) > 1)}")
    for record in records:
        if "(" in record["canonical_filename"] or ")" in record["canonical_filename"]:
            raise RuntimeError(f"upload suffix in destination filename: {record['source_path']}")


def stage(records: list[dict[str, str]], collection: str) -> None:
    stage_root = STAGE_ROOT / collection
    if stage_root.exists():
        shutil.rmtree(stage_root)
    for record in records:
        source = ROOT / record["source_path"]
        text = source.read_text(encoding="utf-8", errors="ignore")
        converter = convert_iso if collection == "iso" else convert_cpp
        transformed = converter(text, record["document_title"], record["unit_type"], record["unit_identifier"])
        target = stage_root / Path(record["destination_path"]).relative_to((ISO_ROOT if collection == "iso" else CPP_ROOT).relative_to(ROOT))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(transformed, encoding="utf-8")
        record["transformed_sha256"] = sha256(target)
        record["status"] = "transformed"


def static_verify(records: list[dict[str, str]], collection: str) -> None:
    stage_root = STAGE_ROOT / collection
    base = ISO_ROOT if collection == "iso" else CPP_ROOT
    for record in records:
        target = stage_root / Path(record["destination_path"]).relative_to(base.relative_to(ROOT))
        text = target.read_text(encoding="utf-8", errors="ignore")
        checks = [
            (len(re.findall(r"^\\documentclass", text, re.M)) == 1, "documentclass"),
            (len(re.findall(r"\\title\s*\{([^{}]+)\}", text)) == 1, "title"),
            (text.count("\\maketitle") == 1, "maketitle"),
            (text.count("\\begin{document}") == 1, "begin document"),
            (text.count("\\end{document}") == 1, "end document"),
            ("\\usepackage{cornell-notes}" in text, "cornell package"),
            ("\\begin{titlepage}" not in text, "titlepage"),
            ("\\makecornelltitle" not in text, "legacy title"),
        ]
        failed = [name for ok, name in checks if not ok]
        if failed:
            raise RuntimeError(f"static validation failed for {record['source_path']}: {', '.join(failed)}")
        record["status"] = "static_verified"


def install(records: list[dict[str, str]], collection: str) -> None:
    base = ISO_ROOT if collection == "iso" else CPP_ROOT
    stage_root = STAGE_ROOT / collection
    for record in records:
        target = ROOT / record["destination_path"]
        staged = stage_root / Path(record["destination_path"]).relative_to(base.relative_to(ROOT))
        if target.exists():
            if sha256(target) != record["transformed_sha256"]:
                raise RuntimeError(f"refusing overwrite: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(staged, target)
        if sha256(target) != record["transformed_sha256"]:
            raise RuntimeError(f"installed hash mismatch: {target}")
        record["status"] = "installed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", choices=["iso", "cpp", "all"], required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--remove-sources", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    if not (args.dry_run or args.execute or args.verify or args.remove_sources):
        parser.error("choose --dry-run, --execute, --verify, or --remove-sources")
    collections = ["iso", "cpp"] if args.collection == "all" else [args.collection]
    summaries = {}
    for collection in collections:
        records = inventory(collection)
        if args.remove_sources:
            manifest_path = STATE_DIR / "iso-42010-intake.csv" if collection == "iso" else STATE_DIR / "cpp-2024-intake.csv"
            if not manifest_path.exists():
                raise RuntimeError(f"cannot remove sources without manifest: {manifest_path}")
            with manifest_path.open(newline="", encoding="utf-8") as handle:
                records = list(csv.DictReader(handle))
            validate_records(records, EXPECTED[collection])
            for record in records:
                source = ROOT / record["source_path"]
                target = ROOT / record["destination_path"]
                if record["status"] != "installed":
                    raise RuntimeError(f"source is not installed: {record['source_path']}")
                if not source.exists() or sha256(source) != record["source_sha256"]:
                    raise RuntimeError(f"source changed or missing: {record['source_path']}")
                if not target.exists() or sha256(target) != record["transformed_sha256"]:
                    raise RuntimeError(f"canonical copy is missing or changed: {record['destination_path']}")
            for record in records:
                (ROOT / record["source_path"]).unlink()
                record["status"] = "source_removed"
            write_csv(manifest_path, records)
            summaries[collection] = {"status": "source_removed", "records": len(records), "csv": str(manifest_path.relative_to(ROOT))}
            continue
        validate_records(records, EXPECTED[collection])
        csv_path = STATE_DIR / f"{collection}-42010-intake.csv" if collection == "iso" else STATE_DIR / f"{collection}-2024-intake.csv"
        write_csv(csv_path, records)
        if args.dry_run:
            summaries[collection] = {"status": "dry-run", "records": len(records), "csv": str(csv_path.relative_to(ROOT))}
            continue
        stage(records, collection)
        static_verify(records, collection)
        if args.execute:
            install(records, collection)
        write_csv(csv_path, records)
        summaries[collection] = {"status": "installed" if args.execute else "staged", "records": len(records), "csv": str(csv_path.relative_to(ROOT))}
    atomic_json(STATE_DIR / "migration-state.json", {"collections": summaries, "stage_root": str(STAGE_ROOT)})
    print(json.dumps(summaries, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"migration error: {exc}", file=sys.stderr)
        raise SystemExit(1)
