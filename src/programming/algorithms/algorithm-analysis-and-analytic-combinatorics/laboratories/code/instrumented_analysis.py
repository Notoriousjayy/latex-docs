"""Original educational algorithms with explicit operation-count conventions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Measurement:
    values: tuple[int, ...]
    comparisons: int
    shifts: int = 0


def merge_sort(values: Sequence[int]) -> Measurement:
    """Stable sort; comparisons count actual element-versus-element tests."""
    arr = list(values)
    temp = arr.copy()
    comparisons = 0

    def sort(lo: int, hi: int) -> None:
        nonlocal comparisons
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        sort(lo, mid)
        sort(mid, hi)
        i, j, k = lo, mid, lo
        while i < mid and j < hi:
            comparisons += 1
            if arr[i] <= arr[j]:
                temp[k] = arr[i]; i += 1
            else:
                temp[k] = arr[j]; j += 1
            k += 1
        while i < mid:
            temp[k] = arr[i]; i += 1; k += 1
        while j < hi:
            temp[k] = arr[j]; j += 1; k += 1
        arr[lo:hi] = temp[lo:hi]

    sort(0, len(arr))
    return Measurement(tuple(arr), comparisons)


def quick_sort_first_pivot(values: Sequence[int]) -> Measurement:
    """Partition uses n-1 comparisons against the pivot, including duplicates."""
    comparisons = 0
    def rec(xs: list[int]) -> list[int]:
        nonlocal comparisons
        if len(xs) <= 1:
            return xs
        pivot = xs[0]
        low, high = [], []
        for x in xs[1:]:
            comparisons += 1
            if x < pivot:
                low.append(x)
            else:
                high.append(x)
        return rec(low) + [pivot] + rec(high)
    return Measurement(tuple(rec(list(values))), comparisons)


def insertion_sort(values: Sequence[int]) -> Measurement:
    """Shifts are array-element moves caused by inversions; compare count differs."""
    arr = list(values)
    comparisons = shifts = 0
    for i in range(1, len(arr)):
        key, j = arr[i], i-1
        while j >= 0:
            comparisons += 1
            if arr[j] <= key:
                break
            arr[j+1] = arr[j]
            shifts += 1
            j -= 1
        arr[j+1] = key
    return Measurement(tuple(arr), comparisons, shifts)


def count_inversions(values: Sequence[int]) -> int:
    return sum(values[i] > values[j]
               for i in range(len(values)) for j in range(i+1, len(values)))


def harmonic(n: int) -> float:
    return sum(1.0/k for k in range(1, n+1))


def expected_quick_comparisons(n: int) -> float:
    if n < 0:
        raise ValueError("n must be nonnegative")
    return 2*(n+1)*harmonic(n) - 4*n if n else 0.0
