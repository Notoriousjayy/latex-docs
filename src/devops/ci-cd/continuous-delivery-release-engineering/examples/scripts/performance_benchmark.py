#!/usr/bin/env python3
"""Local synthetic benchmark for percentiles; not production latency evidence."""
import argparse
import json
import math
import random


def percentile(numbers, p):
    ordered = sorted(numbers)
    if not ordered:
        raise ValueError("samples required")
    return ordered[min(len(ordered)-1, max(0, math.ceil(len(ordered)*p)-1))]

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--samples", type=int, default=1000)
    a.add_argument("--regress", action="store_true")
    opts = a.parse_args()
    if opts.samples < 1:
        a.error("samples must be positive")
    r = random.Random(17)
    timings = [max(1, r.gauss(130, 20)) * (2 if opts.regress else 1) for _ in range(opts.samples)]
    result = {"samples": opts.samples, "p50_ms": round(percentile(timings, .5), 2),
              "p95_ms": round(percentile(timings, .95), 2),
              "p99_ms": round(percentile(timings, .99), 2),
              "benchmark_kind": "synthetic_local_model_not_http"}
    print(json.dumps(result, indent=2))
