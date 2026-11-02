"""Finite two-run noninterference demonstration; not a formal proof."""
from collections.abc import Callable, Iterable


def safe_public_output(high_secret: int, low_value: int) -> int:
    del high_secret
    return low_value * 2


def deliberately_leaky_output(high_secret: int, low_value: int) -> int:
    return low_value * 2 + (high_secret & 1)


def find_low_observation_differences(
    program: Callable[[int, int], int],
    high_values: Iterable[int],
    low_values: Iterable[int],
) -> list[tuple[int, int, int]]:
    highs = list(high_values)
    violations = []
    for low in low_values:
        if not highs:
            continue
        reference = program(highs[0], low)
        for high in highs[1:]:
            if program(high, low) != reference:
                violations.append((low, highs[0], high))
    return violations
