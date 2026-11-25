import json
import sys
from statistics import mean
with open(sys.argv[1]) as f:
    records = [json.loads(line) for line in f if line.strip()]
n = len(records)
passed = sum(r['verified'] is True for r in records)
complete_cost = all(r.get('cost') is not None for r in records)
print(json.dumps({'tasks':n,'verified':passed,'completion_rate':passed/n if n else None,
 'mean_review_minutes':mean(r['review_minutes'] for r in records) if n else None,
 'cost_per_verified_task':sum(r['cost'] for r in records)/passed if passed and complete_cost else None}, indent=2))
