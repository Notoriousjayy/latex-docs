#!/usr/bin/env python3
"""Fail closed when the artifact or source identity is missing or mismatched."""
import argparse
import hashlib
import json
from pathlib import Path


def verify(package: Path, manifest_path: Path, revision: str):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    return all((manifest.get("sha256") == actual,
                manifest.get("source_revision") == revision,
                manifest.get("artifact") == package.name))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("package", type=Path)
    p.add_argument("manifest", type=Path)
    p.add_argument("--revision", required=True)
    a = p.parse_args()
    if not verify(a.package, a.manifest, a.revision):
        p.exit(2, "Artifact promotion DENIED: digest or source identity mismatch\n")
    print("Artifact identity verified")
