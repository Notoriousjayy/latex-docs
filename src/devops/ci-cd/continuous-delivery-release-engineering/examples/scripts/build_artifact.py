#!/usr/bin/env python3
"""Build an identical-by-content ZIP and emit a digest manifest."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile


def build(source: Path, target: Path, revision: str):
    if not revision or revision == "UNKNOWN":
        raise ValueError("A source revision must be provided")
    source_bytes = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    info = zipfile.ZipInfo("function.py", date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    with zipfile.ZipFile(target, "w") as zf:
        zf.writestr(info, source_bytes)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = {"schema_version": 1, "source_revision": revision, "artifact": str(target.name),
                "sha256": digest, "size_bytes": target.stat().st_size}
    target.with_suffix(target.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--revision", required=True)
    p.add_argument("--source", default="examples/lambda/function.py")
    p.add_argument("--output", default="examples/lambda/function.zip")
    args = p.parse_args()
    print(json.dumps(build(Path(args.source), Path(args.output), args.revision), indent=2))
