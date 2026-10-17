#!/usr/bin/env python3
"""Idempotently integrate the eight 2026-10-17 CCoE planning sources."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = Path("src/architecture/governance/ccoe/planning")
MANIFEST_PATH = Path("tooling/manifests/ccoe-planning-intake-2026-10-17.json")
DOCUMENTS = [
    ("2.32", "Risk Register", "2.32 Risk Register.tex", "2-32-risk-register.tex"),
    ("2.33", "Probability and Impact Assessment", "2.33 Probability and Impact Assessment.tex", "2-33-probability-and-impact-assessment.tex"),
    ("2.34", "Probability and Impact Matrix", "2.34 Probability and Impact Matrix.tex", "2-34-probability-and-impact-matrix.tex"),
    ("2.35", "Risk Data Sheet", "2.35 Risk Data Sheet.tex", "2-35-risk-data-sheet.tex"),
    ("2.36", "Procurement Management Plan", "2.36 Procurement Management Plan.tex", "2-36-procurement-management-plan.tex"),
    ("2.37", "Source Selection Criteria", "2.37 Source Selection Criteria.tex", "2-37-source-selection-criteria.tex"),
    ("2.38", "Stakeholder Management Plan", "2.38 Stakeholder Management Plan.tex", "2-38-stakeholder-management-plan.tex"),
    ("2.39", "Change Management Plan", "2.39 Change Management Plan.tex", "2-39-change-management-plan.tex"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {"integration": "CCoE planning intake 2026-10-17", "documents": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def integrate(*, apply: bool, cleanup: bool, record_build: bool) -> int:
    manifest_path = ROOT / MANIFEST_PATH
    manifest = load_manifest(manifest_path)
    recorded = {item["document_id"]: item for item in manifest["documents"]}
    documents = []
    errors = []

    for document_id, title, source_name, target_name in DOCUMENTS:
        source = ROOT / source_name
        target = ROOT / DESTINATION / target_name
        previous = recorded.get(document_id)

        if source.exists():
            original_hash = sha256(source)
        elif previous:
            original_hash = previous["original_sha256"]
        else:
            errors.append(f"Missing source and no prior record: {source_name}")
            continue

        if target.exists():
            target_hash = sha256(target)
            if previous and target_hash == previous["integrated_sha256"]:
                pass
            elif record_build and previous and source.exists() and original_hash == previous["original_sha256"]:
                pass
            elif source.exists() and target_hash == original_hash:
                pass
            else:
                errors.append(f"Refusing to overwrite/reconcile different content: {target.relative_to(ROOT)}")
                continue
        elif source.exists() and apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            target_hash = sha256(target)
        elif source.exists():
            target_hash = original_hash
        else:
            errors.append(f"Missing integrated target: {target.relative_to(ROOT)}")
            continue

        if previous and target.exists() and target_hash != previous["integrated_sha256"] and not record_build:
            errors.append(f"Integrated target changed since manifest record: {target.relative_to(ROOT)}")
            continue

        pdf = ROOT / "public/pdfs/architecture/governance/ccoe/planning" / target.with_suffix(".pdf").name
        if record_build and (not pdf.is_file() or pdf.stat().st_size == 0):
            errors.append(f"Missing or empty compiled PDF: {pdf.relative_to(ROOT)}")
            continue

        transformation = "Copied to the canonical planning path and added descriptive PDF title metadata."
        if document_id == "2.38":
            transformation += " Added a page-break guard for the communication table and expanded related-artifact guidance."
        document = {
            "document_id": document_id,
            "document_title": title,
            "original_filename": source_name,
            "original_sha256": original_hash,
            "canonical_destination": target.relative_to(ROOT).as_posix(),
            "integrated_sha256": target_hash,
            "transformation_summary": transformation,
            "duplicate_reconciliation": "No equivalent canonical document found; target was absent before intake.",
            "compilation_status": "success" if record_build else (previous.get("compilation_status", "pending") if previous else "pending"),
            "final_source_disposition": previous.get("final_source_disposition", "retained pending successful compilation") if previous else "retained pending successful compilation",
        }
        documents.append(document)

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    manifest["documents"] = documents
    if apply or record_build:
        save_manifest(manifest_path, manifest)
        action = "Recorded successful builds for" if record_build else "Integrated/verified"
        print(f"{action} {len(documents)} documents; manifest: {MANIFEST_PATH}")
    else:
        print(f"Validated {len(documents)} source-to-destination mappings.")

    if cleanup:
        if not apply:
            print("--cleanup requires --apply", file=sys.stderr)
            return 2
        if any(item["compilation_status"] != "success" for item in documents):
            print("Refusing cleanup: every document must have compilation_status=success.", file=sys.stderr)
            return 1
        for item in documents:
            source = ROOT / item["original_filename"]
            target = ROOT / item["canonical_destination"]
            if not target.exists() or sha256(target) != item["integrated_sha256"]:
                print(f"Refusing cleanup: target hash mismatch: {item['canonical_destination']}", file=sys.stderr)
                return 1
            if source.exists():
                if sha256(source) != item["original_sha256"]:
                    print(f"Refusing cleanup: source hash mismatch: {item['original_filename']}", file=sys.stderr)
                    return 1
                source.unlink()
            item["final_source_disposition"] = "removed after canonical target and successful PDF compilation were verified"
        save_manifest(manifest_path, manifest)
        print("Removed verified root staging sources.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="copy sources and write the provenance manifest")
    parser.add_argument("--record-build", action="store_true", help="record hashes and successful PDFs after the canonical builds")
    parser.add_argument("--cleanup", action="store_true", help="remove original sources after successful verified builds (requires --apply)")
    args = parser.parse_args()
    if args.record_build and (args.apply or args.cleanup):
        parser.error("--record-build cannot be combined with --apply or --cleanup")
    return integrate(apply=args.apply, cleanup=args.cleanup, record_build=args.record_build)


if __name__ == "__main__":
    raise SystemExit(main())
