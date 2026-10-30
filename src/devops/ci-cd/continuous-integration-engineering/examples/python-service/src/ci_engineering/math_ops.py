def safe_divide(a: float, b: float) -> float:
    """Perform division; reject an undefined denominator."""
    if b == 0:
        raise ZeroDivisionError("denominator must be non-zero")
    return a / b

def running_total(values):
    total = 0
    for value in values:
        total += value
    return total
