import argparse
import json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument("--require-rendered", action="store_true")
args = p.parse_args()
root = Path(__file__).resolve().parent.parent
errors = []
def check(value, message):
    if not value:
        errors.append(message)
parts = sorted(root.glob("part-*"))
check(len(parts) == 3, "expected three SADs")
for part in parts:
    m = json.loads((part / "models/architecture.json").read_text())
    groups = ("views", "modules", "components", "connectors", "staticImports",
              "interfaces", "allocations", "variability", "behaviors",
              "requirements", "risks", "decisions", "diagrams", "evidence")
    records = [x for k in groups for x in m[k]]
    ids = [x["id"] for x in records]
    known = set(ids)
    check(len(ids) == len(known), str(part) + ": duplicate id")
    for x in records:
        check(set(x.get("evidence", [])) <= known, x["id"] + ": evidence")
    ports = {p["id"] for c in m["components"] for p in c["ports"]}
    for x in m["connectors"]:
        check(x["from"] in known and x["to"] in known, x["id"] + ": endpoint")
        check({a["port"] for a in x["attachments"]} <= ports, x["id"] + ": attachment")
    for x in m["mappings"] + m["staticImports"]:
        check(x["from"] in known and x["to"] in known, "mapping endpoint")
    for x in m["interfaces"]:
        check(x["providerModule"] in known, x["id"] + ": provider")
    for x in m["diagrams"]:
        check(x["view"] in known and (part / x["source"]).is_file(), x["id"] + ": source/view")
        if args.require_rendered:
            png = part / x["png"]
            check(png.is_file() and (png.parent.parent / "svg" / (png.stem + ".svg")).is_file(),
                  x["id"] + ": missing render")
    print(m["id"], len(m["modules"]), "modules", len(m["connectors"]), "connectors")
print(json.dumps({"errors": errors, "semantic_review": "not established"}, indent=2))
raise SystemExit(bool(errors))
