#!/usr/bin/env python3
"""Stage and install the separate 33-document C++ 2024 clause collection."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLLECTION = ROOT / "src/cornell-notes/programming/languages/cpp/cpp-2024"
MANIFEST = ROOT / "tooling/manifests/cpp-2024-top-level-intake.json"
STAGE = Path("/tmp/latex-docs-cpp-2024-top-level").resolve()

TITLES = {
    1: "Scope", 2: "Normative References", 3: "Terms and Definitions",
    4: "General Principles", 5: "Lexical Conventions", 6: "Basics",
    7: "Expressions", 8: "Statements", 9: "Declarations", 10: "Modules",
    11: "Classes", 12: "Overloading", 13: "Templates", 14: "Exception Handling",
    15: "Preprocessing Directives", 16: "Library Introduction",
    17: "Language Support Library", 18: "Concepts Library",
    19: "Diagnostics Library", 20: "Memory Management Library",
    21: "Metaprogramming Library", 22: "General Utilities Library",
    23: "Strings Library", 24: "Containers Library", 25: "Iterators Library",
    26: "Ranges Library", 27: "Algorithms Library", 28: "Numerics Library",
    29: "Time Library", 30: "Localization Library", 31: "Input Output Library",
    32: "Regular Expressions Library", 33: "Concurrency Support Library",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def structural_counts(text: str) -> dict[str, int]:
    return {
        "sections": len(re.findall(r"^\\section\{", text, re.M)),
        "subsections": len(re.findall(r"^\\subsection", text, re.M)),
        "cue_note_rows": len(re.findall(r"\\textbf\{[^{}]+\}.*?&", text)),
        "summary_boxes": len(re.findall(r"\\begin\{(?:summarybox|CornellReferenceSummaryBox)\}", text)),
        "checklist_items": len(re.findall(r"^\\item ", _between(text, "Programmer and Implementation Checklist", "Clause Synthesis"), re.M)),
        "self_test_questions": len(re.findall(r"^\\item ", _between(text, "Self-Test Questions", "Answer Key"), re.M)),
        "answer_key_items": len(re.findall(r"^\\item ", _between(text, "Answer Key", "Key-Term Recap"), re.M)),
        "key_term_rows": len(re.findall(r"^[^%\n]+&[^%\n]+\\\\", _between(text, "Key-Term Recap", "\\end{document}"), re.M)),
        "takeaways": len(re.findall(r"\\(?:takeaway|CornellTakeaway)\{", text)),
    }


def _between(text: str, start: str, end: str) -> str:
    start_index = text.find(start)
    if start_index < 0:
        return ""
    end_index = text.find(end, start_index + len(start))
    return text[start_index:] if end_index < 0 else text[start_index:end_index]


def source_records() -> list[dict[str, object]]:
    records = []
    seen: dict[int, Path] = {}
    for source in sorted(ROOT.glob("*.tex")):
        match = re.match(r"^(\d{2})-.+-cornell-notes(?: \(\d+\))?\.tex$", source.name)
        if not match:
            continue
        number = int(match.group(1))
        if number not in TITLES:
            continue
        if number in seen:
            raise RuntimeError(f"duplicate clause {number:02d}: {seen[number].name}, {source.name}")
        seen[number] = source
        title_slug = slug(TITLES[number])
        canonical_name = f"{number:02d}-{title_slug}-cornell-notes.tex"
        destination = COLLECTION / "clauses" / f"{number:02d}-{title_slug}" / canonical_name
        text = source.read_text(encoding="utf-8")
        records.append({
            "clause_number": number,
            "clause_title": TITLES[number],
            "source_path": source.relative_to(ROOT).as_posix(),
            "original_filename": source.name,
            "canonical_filename": canonical_name,
            "canonical_destination": destination.relative_to(ROOT).as_posix(),
            "source_sha256": digest(source),
            "source_bytes": source.stat().st_size,
            "source_lines": len(text.splitlines()),
            "source_counts": structural_counts(text),
            "transformed_sha256": "",
            "transformed_counts": {},
            "status": "inventoried",
        })
    missing = sorted(set(TITLES) - set(seen))
    if missing:
        raise RuntimeError(f"missing clause numbers: {', '.join(f'{n:02d}' for n in missing)}")
    return sorted(records, key=lambda record: int(record["clause_number"]))


def transform(text: str, number: int) -> str:
    begin = text.find(r"\begin{document}")
    end = text.rfind(r"\end{document}")
    if begin < 0 or end <= begin:
        raise RuntimeError(f"clause {number:02d}: malformed document markers")
    body = text[begin + len(r"\begin{document}"):end]
    body = re.sub(r"\s*\\maketitle\s*", "\n", body, count=1)
    body = body.replace(r"\thispagestyle{fancy}", "")
    replacements = {
        "orientation": "CornellReferenceOrientationBox",
        "summarybox": "CornellReferenceSummaryBox",
        "pitfallbox": "CornellReferencePitfallBox",
        "normativebox": "CornellReferenceNormativeBox",
        "ubbox": "CornellReferenceValidityBox",
        "checkbox": "CornellReferenceChecklistBox",
    }
    for old, new in replacements.items():
        body = body.replace(rf"\begin{{{old}}}", rf"\begin{{{new}}}")
        body = body.replace(rf"\end{{{old}}}", rf"\end{{{new}}}")
    body = body.replace(r"\clauseref", r"\CornellClauseRef")
    body = body.replace(r"\takeaway", r"\CornellTakeaway")
    for old, new in {
        "CueGray": "CornellReferenceCueGray", "LineGray": "CornellReferenceLineGray",
        "BlueBg": "CornellReferenceBlueBackground", "GreenBg": "CornellReferenceGreenBackground",
        "AmberBg": "CornellReferenceAmberBackground", "RedBg": "CornellReferenceRedBackground",
        "Navy": "CornellReferenceNavy", "Teal": "CornellReferenceTeal",
        "Green": "CornellReferenceGreen", "Amber": "CornellReferenceAmber",
        "Red": "CornellReferenceRed",
    }.items():
        body = re.sub(rf"(?<![A-Za-z]){old}(?![A-Za-z])", new, body)
    title = TITLES[number]
    label = f"Clause {number}: {title}"
    needspace = "\n\\usepackage{needspace}" if r"\Needspace" in body else ""
    header = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[technical-reference]{{cornell-notes}}{needspace}

\\title{{{label} - Cornell Notes}}
\\author{{}}
\\date{{}}
\\setDocTitle{{{label}}}
\\setDocSubtitle{{C++ 2024 Cornell Notes}}
\\setDocOwner{{C++ 2024 Cornell Notes}}
\\setDocAuthor{{}}
\\setDocDate{{}}
\\setCornellCollection{{C++ 2024 Cornell Notes}}
\\setCornellUnitType{{Clause}}
\\setCornellUnitNumber{{{number}}}
\\setCornellUnitTitle{{{title}}}
\\setCornellCompanionLabel{{C++ Technical Reference}}
\\hypersetup{{pdftitle={{{label} - Cornell Notes}},pdfsubject={{C++ technical study notes}},pdfauthor={{}}}}

\\begin{{document}}
\\maketitle
"""
    return header + body.strip() + "\n\\end{document}\n"


def validate(records: list[dict[str, object]]) -> None:
    destinations = [str(record["canonical_destination"]).lower() for record in records]
    if len(destinations) != len(set(destinations)):
        raise RuntimeError("canonical destination collision")
    previous_hashes: dict[str, str] = {}
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        previous_hashes = {record["canonical_destination"]: record["transformed_sha256"] for record in previous.get("records", [])}
    for record in records:
        filename = str(record["canonical_filename"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.tex", filename):
            raise RuntimeError(f"invalid canonical filename: {filename}")
        target = ROOT / str(record["canonical_destination"])
        old_hash = previous_hashes.get(str(record["canonical_destination"]))
        if target.exists() and digest(target) not in {record["transformed_sha256"], old_hash}:
            raise RuntimeError(f"refusing nonidentical destination: {target}")


def stage(records: list[dict[str, object]]) -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    for record in records:
        source = ROOT / str(record["source_path"])
        transformed = transform(source.read_text(encoding="utf-8"), int(record["clause_number"]))
        relative = Path(str(record["canonical_destination"])).relative_to(COLLECTION.relative_to(ROOT))
        target = STAGE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(transformed, encoding="utf-8")
        record["transformed_sha256"] = digest(target)
        record["transformed_counts"] = structural_counts(transformed)
        for key in record["source_counts"]:
            if record["transformed_counts"].get(key, 0) < record["source_counts"].get(key, 0):
                raise RuntimeError(f"clause {record['clause_number']:02d}: count decreased for {key}")
        record["status"] = "staged"


def write_manifest(records: list[dict[str, object]]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"collection": "cpp-2024-top-level", "expected_records": 33, "records": records}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def install(records: list[dict[str, object]]) -> None:
    previous_hashes: dict[str, str] = {}
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        previous_hashes = {record["canonical_destination"]: record["transformed_sha256"] for record in previous.get("records", [])}
    for record in records:
        target = ROOT / str(record["canonical_destination"])
        staged = STAGE / Path(str(record["canonical_destination"])).relative_to(COLLECTION.relative_to(ROOT))
        if target.exists():
            if digest(target) not in {record["transformed_sha256"], previous_hashes.get(str(record["canonical_destination"]))}:
                raise RuntimeError(f"refusing overwrite: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, target)
        if digest(target) != record["transformed_sha256"]:
            raise RuntimeError(f"installed hash mismatch: {target}")
        record["status"] = "installed"


def remove_sources() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = data["records"]
    if len(records) != 33 or {record["clause_number"] for record in records} != set(range(1, 34)):
        raise RuntimeError("manifest is not the complete 33-document collection")
    for record in records:
        source = ROOT / record["source_path"]
        target = ROOT / record["canonical_destination"]
        if record["status"] != "installed" or not source.exists() or digest(source) != record["source_sha256"]:
            raise RuntimeError(f"source changed or not installed: {source}")
        if not target.exists() or digest(target) != record["transformed_sha256"]:
            raise RuntimeError(f"canonical copy changed or missing: {target}")
    for record in records:
        (ROOT / record["source_path"]).unlink()
        record["status"] = "source_removed"
    write_manifest(records)


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--execute", action="store_true")
    modes.add_argument("--remove-sources", action="store_true")
    args = parser.parse_args()
    if args.remove_sources:
        remove_sources()
        print("removed 33 verified root sources")
        return 0
    records = source_records()
    stage(records)
    validate(records)
    if args.execute:
        install(records)
    write_manifest(records)
    print(json.dumps({"collection": "cpp-2024-top-level", "records": len(records), "status": "installed" if args.execute else "dry-run", "manifest": str(MANIFEST.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())