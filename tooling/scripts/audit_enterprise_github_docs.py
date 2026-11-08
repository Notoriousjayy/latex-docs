#!/usr/bin/env python3
"""Read-only audit of integrated enterprise GitHub documentation sufficiency.

Checks source traceability and honest evidence statuses, not live GitHub
configuration, authority or compliance. No network I/O or security writes.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUFF = ROOT / ("src/security/github-advanced-security/code-scanning/"
               "enterprise-triage-governance/sufficiency")
MATRIX = SUFF / "requirements-matrix.csv"
REGISTER = SUFF / "document-register.csv"
DOMAINS = {
    "Enterprise governance", "Architecture", "Architecture discovery",
    "Platform engineering", "Application security", "Merge governance",
    "Dismissal governance", "Security assurance", "Operations",
    "Reliability", "Evidence and audit", "Reporting", "Delivery",
    "Personnel", "Maintenance",
}
EVIDENCE = {"unverified", "offline_test_only", "not_applicable"}
COVERAGE = {"covered", "partial", "missing"}


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def inspect() -> dict:
    requirements = load(MATRIX)
    documents = load(REGISTER)
    problems: list[str] = []
    seen_req = set()
    seen_doc = set()
    indexed_paths = set()
    for row in documents:
        did = row["document_id"]
        path = row["canonical_path"]
        if did in seen_doc:
            problems.append(f"duplicate document id: {did}")
        seen_doc.add(did)
        if path in indexed_paths:
            problems.append(f"duplicate canonical document path: {path}")
        indexed_paths.add(path)
        if not path.startswith(("src/", "tooling/")) or not (ROOT / path).is_file():
            problems.append(f"{did}: source absent or outside approved roots: {path}")
        if not row["owner_role_proposed"] or not row["reviewer_role_proposed"]:
            problems.append(f"{did}: owner or reviewer role missing")
        if row["source_status"].lower() in {"accepted", "signed", "deployed", "operational"}:
            problems.append(f"{did}: authorization cannot be inferred from docs")
    for row in requirements:
        rid = row["requirement_id"]
        if rid in seen_req:
            problems.append(f"duplicate requirement id: {rid}")
        seen_req.add(rid)
        if row["domain"] not in DOMAINS:
            problems.append(f"{rid}: invalid domain")
        if row["priority"] not in {"P0", "P1", "P2"}:
            problems.append(f"{rid}: invalid priority")
        if row["necessity"] not in {"necessary", "conditional", "supporting", "optional"}:
            problems.append(f"{rid}: invalid necessity")
        if row["coverage"] not in COVERAGE:
            problems.append(f"{rid}: invalid coverage")
        if row["operational_evidence"] not in EVIDENCE:
            problems.append(f"{rid}: unsupported evidence claim")
        if row["earliest_gate"] not in {"L1", "L2", "L3"}:
            problems.append(f"{rid}: invalid gate")
        if row.get("disposition") not in {"retain-and-verify", "revise-or-complete", "create"}:
            problems.append(f"{rid}: no governed disposition")
        for required_field in ("acceptance_criterion", "dependencies", "operational_risk_if_unmet",
                               "source_assessment_basis"):
            if not row.get(required_field):
                problems.append(f"{rid}: missing {required_field}")
        if not row["owner_role"] or not row["reviewer_role"] or not row["verification_id"]:
            problems.append(f"{rid}: missing review/test role or ID")
        paths = [p.strip() for p in row["canonical_document"].split(";")]
        if row["coverage"] != "missing" and not paths:
            problems.append(f"{rid}: no document for nonmissing coverage")
        for path in paths:
            if not path or path == "NONE":
                continue
            if path not in indexed_paths:
                problems.append(f"{rid}: canonical document not registered: {path}")
    for domain in sorted(DOMAINS - {r["domain"] for r in requirements}):
        problems.append(f"domain absent: {domain}")
    if len(documents) < 40:
        problems.append("document inventory incomplete: fewer than 40 artifacts")
    if len(requirements) < 60:
        problems.append("requirement inventory incomplete: fewer than 60 controls")
    if not any(d["source_status"] == "PROPOSED" for d in documents):
        problems.append("proposed decision records not declared")
    if not any(d["source_status"] == "NONAUTHORITATIVE_FOR_APPROVAL" for d in documents):
        problems.append("legacy unsafe dismissal guide not flagged")

    return {
        "assessment_kind": "repository_source_only_no_operational_authorization",
        "requirement_count": len(requirements),
        "document_count": len(documents),
        "domain_count": len({r["domain"] for r in requirements}),
        "priority_counts": dict(Counter(r["priority"] for r in requirements)),
        "design_coverage_counts": dict(Counter(r["coverage"] for r in requirements)),
        "p0_design_partial_or_missing": sorted(
            r["requirement_id"] for r in requirements
            if r["priority"] == "P0" and r["coverage"] != "covered"
        ),
        "operational_evidence_counts": dict(Counter(r["operational_evidence"] for r in requirements)),
        "readiness": {
            "L1": "provisional_unapproved",
            "L2": "not_evidenced",
            "L3": "not_evidenced",
        },
        "checks_pass": not problems,
        "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return nonzero on registry contract failures")
    args = parser.parse_args()
    report = inspect()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if args.check and report["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
