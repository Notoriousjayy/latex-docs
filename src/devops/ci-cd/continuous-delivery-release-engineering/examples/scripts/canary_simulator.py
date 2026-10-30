#!/usr/bin/env python3
"""Deterministic rehearsal only: no AWS calls or real traffic shifting."""
import argparse
import json


def assess(steps, measured, max_errors=0.02, min_requests=100):
    audit = []
    for percent, observation in zip(steps, measured):
        requests = observation["requests"]
        rate = observation["errors"] / requests if requests else 1.0
        status = "ABORT" if requests < min_requests or rate > max_errors else "PROMOTE"
        audit.append({"traffic_percent": percent, "requests": requests,
                      "error_rate": round(rate, 4), "decision": status})
        if status == "ABORT":
            break
    return audit

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inject-failure", action="store_true")
    opts = parser.parse_args()
    readings = [{"requests": 200, "errors": 1}, {"requests": 400, "errors": 1},
                {"requests": 600, "errors": 1}]
    if opts.inject_failure:
        readings[1]["errors"] = 32
    print(json.dumps(assess([10, 50, 100], readings), indent=2))
