def discount(cents: int, percent: int) -> int:
    """Return discounted price, rounded down to a whole cent."""
    if type(cents) is not int or type(percent) is not int:
        raise ValueError("integer inputs required")
    if cents < 0 or not 0 <= percent <= 100:
        raise ValueError("invalid amount or percentage")
    return cents * (100 - percent) // 100
