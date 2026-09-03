#!/usr/bin/env python3
"""Safely stage the Software Security Assessment Cornell-note migration."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COLLECTION = ROOT / "src/cornell-notes/security/application-security/software-security-assessment"
STAGE = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else Path("/tmp/software-security-assessment-stage").resolve()

TITLES = {
    1: "Software Vulnerability Fundamentals", 2: "Design Review",
    3: "Operational Review", 4: "Application Review Process",
    5: "Memory Corruption", 6: "C Language Issues",
    7: "Program Building Blocks", 8: "Strings and Metacharacters",
    9: "UNIX I: Privileges and Files", 10: "UNIX II: Processes",
    11: "Windows I: Objects and the File System", 12: "Windows II: Interprocess Communication",
    13: "Synchronization and State", 14: "Network Protocols", 15: "Firewalls",
    16: "Network Application Protocols", 17: "Web Applications", 18: "Web Technologies",
}
RANGES = {
    1: "pp. 3--23", 2: "pp. 25--66", 3: "pp. 67--89", 4: "pp. 91--164",
    5: "pp. 167--202", 6: "pp. 203--296", 7: "pp. 297--385", 8: "pp. 387--457",
    9: "pp. 459--557", 10: "pp. 559--624", 11: "pp. 625--684", 12: "pp. 685--754",
    13: "pp. 755--825", 14: "pp. 829--890", 15: "pp. 891--920", 16: "pp. 921--1005",
    17: "pp. 1007--1081", 18: "pp. 1083--1123",
}
GROUPS = {
    range(1, 5): "assessment-foundations", range(5, 9): "implementation-security",
    range(9, 14): "platform-security", range(14, 19): "network-and-web-security",
}
SECTIONS = ["Learning Objectives", "Cornell Cue-and-Notes", "Security-Review Checklist", "Chapter Synthesis", "Self-Test Questions", "Key-Term Recap", "One-Sentence Takeaway"]


def fail(message: str) -> None:
    raise SystemExit(f"migration gate failed: {message}")


def source_for(number: int) -> Path:
    matches = sorted(ROOT.glob(f"{number:02d}-*.tex"))
    if len(matches) != 1:
        fail(f"chapter {number} has {len(matches)} root matches: {matches}")
    return matches[0]


def audit(text: str, number: int) -> dict[str, object]:
    if len(re.findall(r"^\\documentclass", text, re.MULTILINE)) != 1:
        fail(f"chapter {number}: documentclass count")
    for marker in (r"\begin{document}", r"\end{document}"):
        if text.count(marker) != 1:
            fail(f"chapter {number}: {marker} count")
    canonical_title = rf"\\title{{Chapter {number}: {re.escape(TITLES[number])}}}"
    title_is_canonical = re.search(canonical_title, text) is not None
    title = re.search(r"\\title\{Chapter\s+(\d+):\s*(.*?)\\\\\[", text, re.DOTALL)
    if title_is_canonical:
        title = None
    if (not title and not title_is_canonical) or (title and (int(title.group(1)) != number or title.group(2).strip() != TITLES[number])):
        fail(f"chapter {number}: title mismatch")
    if f"Coverage range:}} {RANGES[number]}" not in text:
        fail(f"chapter {number}: coverage range mismatch")
    sections = re.findall(r"^\\section\{([^}]*)\}", text, re.MULTILINE)
    if sections != SECTIONS:
        fail(f"chapter {number}: section sequence {sections!r}")
    for marker in ("Answer Key", "Security-Review Checklist"):
        if marker not in text:
            fail(f"chapter {number}: missing {marker}")
    for env in ("document", "itemize", "enumerate", "longtable", "orientationbox", "summarybox", "historybox", "takeawaybox"):
        if text.count(rf"\begin{{{env}}}") != text.count(rf"\end{{{env}}}"):
            fail(f"chapter {number}: unbalanced {env}")
    checklist = text[text.index(r"\section{Security-Review Checklist}"):text.index(r"\section{Chapter Synthesis}")]
    checklist_items = len(re.findall(r"^\\checkbox\s+", checklist, re.MULTILINE))
    if checklist_items == 0 and r"\begin{CornellChecklist}" in checklist:
        checklist_items = len(re.findall(r"^\\item ", checklist, re.MULTILINE))
    if checklist_items == 0:
        fail(f"chapter {number}: empty checklist")
    return {
        "chapter": number, "title": TITLES[number], "coverage_range": RANGES[number],
        "sections": sections, "cue_note_rows": len(re.findall(r"^\\term\{", text, re.MULTILINE)),
        "checklist_items": checklist_items, "self_test_questions": len(re.findall(r"^\\item ", text[text.index(r"\section{Self-Test Questions}"):text.index(r"\section{Key-Term Recap}")], re.MULTILINE)),
        "answer_key_items": len(re.findall(r"^\\item ", text[text.index(r"\subsection*{Answer Key}"):text.index(r"\section{Key-Term Recap}")], re.MULTILINE)),
        "key_term_rows": len(re.findall(r"^\\textbf\{[^}]+\} &", text, re.MULTILINE)),
    }


def transform(text: str, number: int) -> str:
    audit(text, number)
    preamble, body = text.split(r"\begin{document}", 1)
    body = r"\begin{document}" + body
    checklist_start = body.index(r"\section{Security-Review Checklist}")
    checklist_end = body.index(r"\section{Chapter Synthesis}", checklist_start)
    lines = body[checklist_start:checklist_end].splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(r"\section{Security-Review Checklist}"):
            output.append(line)
            output.append(r"\begin{CornellChecklist}")
        elif line.startswith(r"\textbf{") and line.endswith(r"\\"):
            if index + 1 >= len(lines) or not lines[index + 1].startswith(r"\checkbox "):
                fail(f"chapter {number}: malformed checklist pair at line {index + 1}")
            output.append(r"\item \textbf{" + line[len(r"\textbf{"):-3] + "}")
            output.append(lines[index + 1].replace(r"\checkbox ", "", 1))
            index += 1
        elif line.startswith(r"\checkbox "):
            fail(f"chapter {number}: orphan checklist item at line {index + 1}")
        elif line == r"\section{Chapter Synthesis}":
            fail(f"chapter {number}: unexpected checklist boundary")
        else:
            output.append(line)
        index += 1
    if output[-1] != r"\end{CornellChecklist}":
        output.append(r"\end{CornellChecklist}")
    body = body[:checklist_start] + "\n".join(output) + "\n" + body[checklist_end:]
    body = body.replace(r"\begin{orientationbox}", r"\begin{CornellOverviewBox}{Review Orientation}").replace(r"\end{orientationbox}", r"\end{CornellOverviewBox}")
    body = body.replace(r"\begin{summarybox}", r"\begin{CornellSummaryBox}{Section Summary}").replace(r"\end{summarybox}", r"\end{CornellSummaryBox}")
    body = body.replace(r"\begin{historybox}", r"\begin{CornellLegacyBox}{Historical Context}").replace(r"\end{historybox}", r"\end{CornellLegacyBox}")
    body = body.replace(r"\begin{takeawaybox}", r"\begin{CornellExamBox}{One-Sentence Takeaway}").replace(r"\end{takeawaybox}", r"\end{CornellExamBox}")
    body = body.replace("SecNavy", "Navy").replace("SecBlue", "Accent").replace("SecTeal", "Teal").replace("SecGreen", "Teal").replace("SecAmber", "CornellExamAccent").replace("CueBg", "CornellCueBackground").replace("SoftBlue", "Soft").replace("SoftGreen", "CornellCueBackground").replace("SoftAmber", "CornellCueBackground").replace("RuleGray", "CardFrame").replace("TextGray", "Meta")
    body = body.replace(r"\thispagestyle{fancy}", "")
    header = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage{{cornell-notes}}
\\usepackage{{needspace}}

\\title{{Chapter {number}: {TITLES[number]}}}
\\author{{}}
\\date{{}}

\\setDocTitle{{Chapter {number}: {TITLES[number]}}}
\\setDocSubtitle{{Application Security Review}}
\\setCornellCollection{{Software Security Assessment}}
\\setCornellUnitType{{Chapter}}
\\setCornellUnitNumber{{{number}}}
\\setCornellUnitTitle{{{TITLES[number]}}}
\\setCornellCompanionLabel{{Study and audit reference}}
\\setCornellSourceRange{{{RANGES[number]}}}
"""
    result = header + body[body.index(r"\begin{document}"):]
    if r"\usepackage{listings}" in result or r"\lstset" in result:
        fail(f"chapter {number}: listings remains")
    return result


def main() -> None:
    if STAGE.exists():
        fail(f"staging path already exists: {STAGE}")
    STAGE.mkdir(parents=True)
    inventory = []
    for number in range(1, 19):
        source = source_for(number)
        text = source.read_text(encoding="utf-8")
        record = audit(text, number)
        record.update({"source_filename": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "source_bytes": source.stat().st_size, "source_lines": text.count("\n") + 1})
        group = next(group for numbers, group in GROUPS.items() if number in numbers)
        destination = Path(group) / f"{number:02d}-{TITLES[number].lower().replace('unix i: ', 'unix-').replace('unix ii: ', 'unix-').replace('windows i: ', 'windows-').replace('windows ii: ', 'windows-').replace(' ', '-').replace(':', '').replace('---', '-').replace('--', '-')}-cornell-notes.tex"
        destination = {1: Path(group) / "01-vulnerability-fundamentals-cornell-notes.tex", 8: Path(group) / "08-strings-metacharacters-cornell-notes.tex", 9: Path(group) / "09-unix-privileges-files-cornell-notes.tex", 10: Path(group) / "10-unix-processes-cornell-notes.tex", 11: Path(group) / "11-windows-objects-filesystem-cornell-notes.tex", 12: Path(group) / "12-windows-ipc-cornell-notes.tex", 13: Path(group) / "13-synchronization-state-cornell-notes.tex", 16: Path(group) / "16-network-app-protocols-cornell-notes.tex"}.get(number, destination)
        output = transform(text, number)
        out = STAGE / destination
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
        final_record = audit(output, number)
        if any(final_record[key] < record[key] for key in ("cue_note_rows", "checklist_items", "self_test_questions", "answer_key_items", "key_term_rows")):
            fail(f"chapter {number}: content count decreased")
        record.update({"canonical_destination": str(COLLECTION / destination), "final_counts": final_record})
        inventory.append(record)
    (STAGE / "migration-inventory.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(f"STAGED MIGRATION PASS: {len(inventory)} documents at {STAGE}")


if __name__ == "__main__":
    main()