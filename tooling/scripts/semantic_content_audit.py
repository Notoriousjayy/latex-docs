#!/usr/bin/env python3
"""Scan the COMPLETE source of every tracked LaTeX document for audit evidence.

This is a mechanical full-text inspection, NOT a substitute for content-level
semantic interpretation by an engineer. It never assigns unverified summaries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
MANIFEST = ROOT / "tooling/manifests/semantic-document-inventory.json"

HEADINGS = re.compile(r"\\(?:part|chapter|section|subsection)\*?\{([^{}\n]{1,220})\}")
DOC_TITLE = re.compile(r"\\(?:title|coverpage)\s*\{([^{}\n]{1,250})\}")
PDF_TITLE = re.compile(r"pdftitle\s*=\s*\{([^{}\n]{1,250})\}")
USES = re.compile(
    r"\\(?:input|include|includegraphics|addbibresource|bibliography|"
    r"lstinputlisting)\s*(?:\[[^\]\n]*\])?\s*\{([^{}\n]+)\}"
)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def extract(entry: dict) -> dict:
    path = ROOT / entry["path"]
    raw = path.read_bytes()  # Read the complete authored source, not an excerpt.
    body = raw.decode("utf-8", errors="replace")
    head = body.split(r"\begin{document}", 1)[0]
    titles = DOC_TITLE.findall(head) or PDF_TITLE.findall(head)
    headings = HEADINGS.findall(body)
    plain = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]\n]*\])?", " ", body)
    plain = re.sub(r"\s+", " ", plain).strip()
    terms = {
        "user_stories": bool(re.search(r"user.stor(?:y|ies)|story.card", plain, re.I)),
        "scorecards": bool(re.search(r"scorecard|scoring rubric", plain, re.I)),
        "workbooks": bool(re.search(r"\bworkbook\b", plain, re.I)),
        "templates": bool(re.search(r"\btemplate\b", plain, re.I)),
        "checklists": bool(re.search(r"\bchecklist\b", plain, re.I)),
    }
    return {
        "path": entry["path"],
        "git_blob_sha": git_blob_sha(raw),
        "bytes_scanned": len(raw),
        "documentclass": bool(re.search(r"\\documentclass(?:\[[^\]]*\])?\s*\{", head)),
        "title_candidates": titles[:3],
        "section_heading_count": len(headings),
        "sample_headings": headings[:12],
        "local_dependency_tokens": USES.findall(body),
        "terms_present": terms,
        "method": "complete_source_mechanical_scan_not_human_semantic_review",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Fail if canonical metadata paths/hashes differ from current sources")
    parser.add_argument("--output", type=Path,
                        help="Write complete-source evidence for subsequent semantic review")
    args = parser.parse_args()

    inventory = json.loads(MANIFEST.read_text(encoding="utf-8"))
    indexed = {item["path"]: item for item in inventory["sources"]}
    current = {p.relative_to(ROOT).as_posix() for p in SRC.rglob("*.tex")}
    if current != set(indexed):
        missing = sorted(current - set(indexed))
        stale = sorted(set(indexed) - current)
        print(json.dumps({"error": "inventory paths differ", "missing": missing[:20],
                          "stale": stale[:20]}, indent=2))
        return 1

    evidence = []
    mismatches = []
    for item in inventory["sources"]:
        entry = extract(item)
        evidence.append(entry)
        if entry["git_blob_sha"] != item["blob_sha"]:
            mismatches.append(item["path"])

    summary = {
        "files_scanned": len(evidence),
        "bytes_scanned": sum(e["bytes_scanned"] for e in evidence),
        "documentclass_files": sum(e["documentclass"] for e in evidence),
        "title_candidates_found": sum(bool(e["title_candidates"]) for e in evidence),
        "keyword_presence": dict(Counter(
            term for e in evidence for term, found in e["terms_present"].items() if found
        )),
        "hash_mismatches": mismatches[:30],
        "semantic_review_status": "mechanical_full_source_scan_only",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"summary": summary, "evidence": evidence},
                                          indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
