"""Write raw per-repetition CSV; run input construction outside timed regions."""
from __future__ import annotations
import argparse
import csv
import random
import sys
import time
from pathlib import Path
from instrumented_analysis import merge_sort, quick_sort_first_pivot, insertion_sort

ALGORITHMS = {"merge": merge_sort, "quick": quick_sort_first_pivot,
              "insert": insertion_sort}


def run(algorithm: str, sizes: list[int], repeats: int, seed: int, path: Path) -> None:
    if algorithm not in ALGORITHMS or repeats < 1 or any(n < 0 for n in sizes):
        raise ValueError("invalid algorithm, sizes or repetitions")
    fn = ALGORITHMS[algorithm]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "algorithm", "language", "input_model", "n", "seed", "repeat",
            "comparisons", "shifts", "elapsed_ns", "correct"])
        writer.writeheader()
        cases = [(n, r) for n in sizes for r in range(repeats)]
        random.Random(seed).shuffle(cases)
        for n, repeat in cases:
            case_seed = seed + n * 1000003 + repeat
            data = list(range(n))
            random.Random(case_seed).shuffle(data)
            start = time.perf_counter_ns()
            result = fn(data)
            elapsed = time.perf_counter_ns() - start
            correct = result.values == tuple(sorted(data))
            writer.writerow(dict(algorithm=algorithm, language="Python",
                    input_model="uniform_permutation", n=n, seed=case_seed,
                    repeat=repeat, comparisons=result.comparisons,
                    shifts=result.shifts, elapsed_ns=elapsed, correct=correct))
            if not correct:
                raise AssertionError("output incorrect: failure row preserved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", choices=list(ALGORITHMS), default="merge")
    parser.add_argument("--sizes", type=int, nargs="+", default=[32, 64, 128, 256])
    parser.add_argument("--repeats", type=int, default=15)
    parser.add_argument("--seed", type=int, default=71)
    parser.add_argument("--output", type=Path, default=Path("results.csv"))
    args = parser.parse_args()
    run(args.algorithm, args.sizes, args.repeats, args.seed, args.output)
    print(f"Wrote {args.output}")
