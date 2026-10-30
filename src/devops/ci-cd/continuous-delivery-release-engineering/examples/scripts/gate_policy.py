#!/usr/bin/env python3
"""Minimal security gate example. All findings labeled blocking deny promotion."""
import json
import sys
from pathlib import Path


def gate(findings):
    blocking = [f for f in findings if f.get("disposition", "block") == "block"]
    return not blocking, blocking

if __name__ == "__main__":
    findings = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    ok, blocking = gate(findings)
    print(json.dumps({"allowed": ok, "blocking_findings": blocking}, indent=2))
    sys.exit(0 if ok else 2)
