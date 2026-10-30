"""Original, intentionally readable reference implementations for the laboratories.

These are educational baselines, not copies of any algorithms printed in TAOCP.
Use standard libraries for production unless their preconditions and risk are reviewed.
"""
from __future__ import annotations
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from random import Random


class RingBuffer:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._items: list[object | None] = [None] * capacity
        self._head = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def enqueue(self, item: object) -> None:
        if self._size == len(self._items):
            raise OverflowError("ring buffer is full")
        pos = (self._head + self._size) % len(self._items)
        self._items[pos] = item
        self._size += 1

    def dequeue(self) -> object:
        if not self._size:
            raise IndexError("ring buffer is empty")
        item = self._items[self._head]
        self._items[self._head] = None
        self._head = (self._head + 1) % len(self._items)
        self._size -= 1
        return item


def euclid_gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcg(seed: int, a: int, c: int, modulus: int, count: int) -> list[int]:
    """Expose all state transitions; NOT suitable for secrets or cryptography."""
    if modulus <= 0 or count < 0 or a < 0 or c < 0:
        raise ValueError("invalid generator parameters")
    state = seed % modulus
    result = []
    for _ in range(count):
        state = (a * state + c) % modulus
        result.append(state)
    return result


def fisher_yates(items: Sequence[int], rng: Random) -> list[int]:
    result = list(items)
    for i in range(len(result) - 1, 0, -1):
        j = rng.randrange(i + 1)
        result[i], result[j] = result[j], result[i]
    return result


@dataclass(frozen=True)
class Record:
    key: int
    ordinal: int


def insertion_sort(records: Sequence[Record]) -> list[Record]:
    result = list(records)
    for i in range(1, len(result)):
        current = result[i]
        j = i
        while j > 0 and result[j - 1].key > current.key:
            result[j] = result[j - 1]
            j -= 1
        result[j] = current
    return result


def stable_merge_sort(records: Sequence[Record]) -> list[Record]:
    arr = list(records)
    if len(arr) < 2:
        return arr
    midpoint = len(arr) // 2
    left = stable_merge_sort(arr[:midpoint])
    right = stable_merge_sort(arr[midpoint:])
    result: list[Record] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i].key <= right[j].key:  # equality preserves stability
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result


def lower_bound(values: Sequence[int], target: int) -> int:
    lo, hi = 0, len(values)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def combinations(n: int, k: int) -> Iterator[tuple[int, ...]]:
    if n < 0 or k < 0 or k > n:
        return
    selection = list(range(k))
    while True:
        yield tuple(selection)
        i = k - 1
        while i >= 0 and selection[i] == n - k + i:
            i -= 1
        if i < 0:
            return
        selection[i] += 1
        for j in range(i + 1, k):
            selection[j] = selection[j - 1] + 1


def permutations(items: Sequence[int]) -> Iterator[tuple[int, ...]]:
    """Index-based enumeration; distinct input elements give unique permutations."""
    indices = list(range(len(items)))
    while True:
        yield tuple(items[i] for i in indices)
        p = len(indices) - 2
        while p >= 0 and indices[p] >= indices[p + 1]:
            p -= 1
        if p < 0:
            return
        q = len(indices) - 1
        while indices[q] <= indices[p]:
            q -= 1
        indices[p], indices[q] = indices[q], indices[p]
        indices[p + 1:] = reversed(indices[p + 1:])


def n_queens(n: int) -> int:
    if n < 0:
        raise ValueError("n must be nonnegative")
    occupied_col: set[int] = set()
    diag_up: set[int] = set()
    diag_down: set[int] = set()
    def search(row: int) -> int:
        if row == n:
            return 1
        count = 0
        for col in range(n):
            a, b = row - col, row + col
            if col in occupied_col or a in diag_up or b in diag_down:
                continue
            occupied_col.add(col); diag_up.add(a); diag_down.add(b)
            count += search(row + 1)
            occupied_col.remove(col); diag_up.remove(a); diag_down.remove(b)
        return count
    return search(0)


def exact_cover(primary: set[str], options: Sequence[set[str]]) -> list[tuple[int, ...]]:
    """Return index tuples; each primary item must be covered exactly once.

    An option must use at least one primary item. Secondary/colored
    constraints from Volume 4B are deliberately outside this baseline.
    """
    if any(not option or not option <= primary for option in options):
        raise ValueError("all options must be nonempty subsets of primary")
    solutions: list[tuple[int, ...]] = []
    def visit(uncovered: set[str], selected: tuple[int, ...], available: tuple[int, ...]) -> None:
        if not uncovered:
            solutions.append(selected)
            return
        candidates_by_item = {
            item: [i for i in available if item in options[i]]
            for item in uncovered
        }
        item = min(sorted(uncovered), key=lambda key: len(candidates_by_item[key]))
        for index in candidates_by_item[item]:
            chosen = options[index]
            remaining = tuple(
                i for i in available if i != index and not (options[i] & chosen)
            )
            visit(uncovered - chosen, selected + (index,), remaining)
    visit(set(primary), (), tuple(range(len(options))))
    return solutions


CNF = Sequence[Sequence[int]]

def cnf_satisfied(clauses: CNF, assignment: dict[int, bool]) -> bool:
    return all(any(assignment.get(abs(literal), False) == (literal > 0)
                       and abs(literal) in assignment for literal in clause)
               for clause in clauses)


def dpll(clauses: CNF) -> dict[int, bool] | None:
    """A small educational DPLL solver with unit propagation.

    Positive integer denotes the variable; negative integer its negation.
    An empty clause is unsatisfiable. An empty CNF is satisfiable.
    """
    formula = tuple(tuple(int(lit) for lit in clause) for clause in clauses)
    if any(lit == 0 for clause in formula for lit in clause):
        raise ValueError("variable identifiers must be nonzero")

    def simplify(cnf: tuple[tuple[int, ...], ...], var: int, value: bool):
        sat_lit = var if value else -var
        unsat_lit = -sat_lit
        return tuple(tuple(lit for lit in clause if lit != unsat_lit)
                     for clause in cnf if sat_lit not in clause)

    def search(cnf: tuple[tuple[int, ...], ...], assigned: dict[int, bool]):
        while True:
            if not cnf:
                return assigned
            if any(not clause for clause in cnf):
                return None
            unit = next((clause[0] for clause in cnf if len(clause) == 1), None)
            if unit is None:
                break
            var, value = abs(unit), unit > 0
            if var in assigned and assigned[var] != value:
                return None
            assigned = {**assigned, var: value}
            cnf = simplify(cnf, var, value)
        chosen = min(abs(literal) for clause in cnf for literal in clause)
        for value in (True, False):
            solution = search(simplify(cnf, chosen, value), {**assigned, chosen: value})
            if solution is not None:
                return solution
        return None
    return search(formula, {})
