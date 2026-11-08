"""Synthetic evaluation metrics only; do not infer production benefits."""
from __future__ import annotations
import statistics
from typing import Iterable


def percentile(values: list[float], percentile_value: float) -> float | None:
    if not values:
        return None
    if not 0 <= percentile_value <= 100:
        raise ValueError("invalid percentile")
    s = sorted(values)
    k = (len(s) - 1) * percentile_value / 100
    i = int(k)
    return round(s[i] + (s[min(i+1, len(s)-1)] - s[i]) * (k-i), 3)


def summary(wait_minutes: Iterable[float], eligible_prs: int,
            blocked_prs: int, sampled_dismissals: int,
            erroneous_dismissals: int) -> dict:
    waits = list(wait_minutes)
    if any(x < 0 for x in waits):
        raise ValueError("negative wait")
    if not 0 <= blocked_prs <= eligible_prs:
        raise ValueError("invalid PR denominator")
    if not 0 <= erroneous_dismissals <= sampled_dismissals:
        raise ValueError("invalid dismissal sample")
    return {
        "n_waits": len(waits),
        "wait_median_minutes": round(statistics.median(waits), 3) if waits else None,
        "wait_p95_minutes": percentile(waits, 95),
        "blocked_pr_rate": round(blocked_prs / eligible_prs, 6) if eligible_prs else None,
        "incorrect_dismissal_sample_rate":
            round(erroneous_dismissals / sampled_dismissals, 6) if sampled_dismissals else None,
        "caveat": "Unadjusted observation only; no causal claim or production evidence",
    }
