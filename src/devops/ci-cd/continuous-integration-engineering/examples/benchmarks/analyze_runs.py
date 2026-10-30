"""Offline benchmark summary; do not infer statistical significance from examples."""
import argparse, csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

def percentile(samples, percentage):
    if not samples: raise ValueError("no observations")
    values = sorted(samples)
    pos = (len(values) - 1) * percentage / 100
    lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)

def summarize(path):
    cohorts = defaultdict(list)
    statuses = defaultdict(lambda: defaultdict(int))
    with open(path, newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        required = {"run_id", "revision", "variant", "cache", "queue_seconds", "duration_seconds", "status"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("missing required run-data columns")
        for row in reader:
            key = (row["variant"], row["cache"])
            statuses[key][row["status"]] += 1
            if row["status"] == "success":
                duration = float(row["duration_seconds"])
                if not math.isfinite(duration) or duration < 0: raise ValueError("invalid duration")
                cohorts[key].append(duration)
    result = {}
    for key, counts in statuses.items():
        numbers = cohorts[key]
        result["/".join(key)] = {
          "successful_samples": len(numbers), "statuses": dict(counts),
          "median_seconds": statistics.median(numbers) if numbers else None,
          "p95_seconds": percentile(numbers, 95) if numbers else None,
          "note": "illustrative descriptive statistics; failed/cancelled runs excluded from duration summaries"
        }
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.csv_path), indent=2, sort_keys=True))
