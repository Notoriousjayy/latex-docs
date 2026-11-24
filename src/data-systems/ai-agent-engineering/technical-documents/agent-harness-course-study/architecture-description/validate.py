"""Structural validation of the draft AD; does not certify semantics."""
import csv
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
m = json.loads((ROOT / "models/architecture.json").read_text())
with (ROOT / "evidence/repository-evidence.csv").open(newline="") as f:
    evidence = {r["id"] for r in csv.DictReader(f)}
errors = []
def require(ok, message):
    if not ok:
        errors.append(message)
def ids(key):
    records = m[key]
    result = {r["id"] for r in records}
    require(len(result) == len(records), f"duplicate ids in {key}")
    return result
st, pe, co, asp, vp, vi, vc, el, methods = [
    ids(k) for k in ("stakeholders", "perspectives", "concerns", "aspects",
                     "viewpoints", "views", "viewComponents", "elements",
                     "correspondenceMethods")]
known = st | pe | co | asp | vp | vi | vc | el | evidence
for c in m["concerns"]:
    require(bool(c["stakeholders"]) and set(c["stakeholders"]) <= st, c["id"])
    require(any(c["id"] in v["concerns"] for v in m["viewpoints"]), c["id"]+" viewpoint")
    require(any(c["id"] in v["concerns"] for v in m["views"]), c["id"]+" view")
for p in m["perspectives"]:
    require(set(p["stakeholders"]) <= st and set(p["concerns"]) <= co, p["id"])
    require(any(p["id"] in v["perspectives"] for v in m["views"]), p["id"]+" view")
for a in m["aspects"]:
    require(bool(a["concerns"]) and set(a["concerns"]) <= co, a["id"])
    require(any(a["id"] in v["aspects"] for v in m["views"]), a["id"]+" view")
for v in m["viewpoints"]:
    require(any(x["viewpoint"] == v["id"] for x in m["views"]), v["id"])
for v in m["views"]:
    require(v["viewpoint"] in vp and bool(v["components"]) and set(v["components"]) <= vc, v["id"])
for c in m["viewComponents"]:
    require(c["view"] in vi, c["id"]+" view")
    if "source" in c:
        require((ROOT / c["source"]).is_file(), c["id"]+" source")
        require(set(c["evidence"]) <= evidence and set(c["elements"]) <= el, c["id"]+" trace")
for e in m["elements"]:
    require(e["parent"] is None or e["parent"] in el, e["id"]+" parent")
    require(set(e["evidence"]) <= evidence, e["id"]+" evidence")
for c in m["correspondences"]:
    require(c["from"] in known and c["to"] in known and c["method"] in methods and c["ad"] == m["ad"], str(c))
print(json.dumps({"structural_errors": errors, "diagram_sources": sum("source" in x for x in m["viewComponents"]),
                  "semantic_review": "not assessed", "render": "not assessed"}, indent=2))
raise SystemExit(bool(errors))
