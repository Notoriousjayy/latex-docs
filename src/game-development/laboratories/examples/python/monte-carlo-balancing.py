import random
import math

def estimate(p: float, n: int, seed: int):
    assert 0 <= p <= 1 and n > 0
    rng = random.Random(seed)
    successes = sum(rng.random() < p for _ in range(n))
    rate = successes / n
    stderr = math.sqrt(rate * (1 - rate) / n)
    return rate, stderr

def test():
    assert estimate(0, 100, 17) == (0, 0)
    assert estimate(1, 100, 17) == (1, 0)
    assert estimate(.4, 1000, 17) == estimate(.4, 1000, 17)

if __name__ == "__main__":
    test()
    print("MC rate and SE:", estimate(.45, 10000, 17))
