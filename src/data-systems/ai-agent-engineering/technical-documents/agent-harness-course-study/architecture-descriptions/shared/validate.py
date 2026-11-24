"""Validate architecture model references without executing upstream code."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--require-rendered", action="store_true")
args = parser.parse_args()
errors = []
all_elements = {}
def require(ok, msg):
    if not ok:
        errors.append(msg)
dirs = sorted(ROOT.glob("part-*"))
require(len(dirs) == 3, "Expected three independent ADs")
for part in dirs:
    model = json.loads((part / "models/architecture.json").read_text())
    with (part / "evidence/repository-evidence.csv").open(newline="") as fp:
        evidence = list(csv.DictReader(fp))
    fields = ("stakeholders", "perspectives", "concerns", "aspects",
              "viewpoints", "views", "viewComponents", "elements", "risks", "decisions")
    ids = [e["id"] for k in fields for e in model[k]] + [e["id"] for e in evidence]
    known = set(ids)
    require(len(ids) == len(known), f"{part.name}: duplicate AD element IDs")
    methods = {r["id"] for r in model["correspondenceMethods"]}
    for e in evidence:
        require(e["commit"] == model["baseline"], e["id"] + ": baseline mismatch")
    for row in model["correspondences"]:
        require(row["from"] in known and row["to"] in known and row["ad"] == model["id"]
                and row["method"] in methods, f"{part.name}: invalid correspondence {row}")
    for row in model["relationships"]:
        require(row["from"] in known and row["to"] in known, row["id"] + ": dangling relationship")
    for e in model["elements"]:
        require(e["parent"] is None or e["parent"] in known, e["id"] + ": invalid parent")
        require(set(e["evidence"]) <= known, e["id"] + ": evidence")
    for c in model["concerns"]:
        require(bool(c["stakeholders"]) and any(v["concern"] == c["id"] for v in model["viewpoints"])
                and any(c["id"] in v["concerns"] for v in model["views"]), c["id"] + ": coverage")
    for v in model["viewpoints"]:
        require(any(x["viewpoint"] == v["id"] for x in model["views"]), v["id"] + ": no view")
    for d in model["viewComponents"]:
        if "source" in d:
            require((part / d["source"]).is_file(), d["id"] + ": missing source")
            require(set(d["elements"] + d["evidence"]) <= known, d["id"] + ": invalid reference")
            if args.require_rendered:
                png = part / d["png"]
                svg = png.parent.parent / "svg" / (png.stem + ".svg")
                require(png.is_file() and svg.is_file(), d["id"] + ": missing PNG or SVG")
    all_elements[model["id"]] = {e["id"] for e in model["elements"]}
    print(part.name, len(model["correspondences"]), "local correspondences")
for row in json.loads((ROOT / "shared/cross-ad-correspondences.json").read_text()):
    require(row["from"] in all_elements.get(row["fromAD"], set())
            and row["to"] in all_elements.get(row["toAD"], set()), row["id"])
print(json.dumps({"errors": errors, "semantic_review": "not assessed"}, indent=2))
raise SystemExit(bool(errors))
