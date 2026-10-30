from dataclasses import dataclass

@dataclass
class Challenge:
    level: int = 3
    minimum: int = 1
    maximum: int = 5

    def observe(self, recent_success_rate: float):
        if not 0 <= recent_success_rate <= 1:
            raise ValueError("invalid rate")
        if recent_success_rate > .8:
            self.level = min(self.maximum, self.level + 1)
        elif recent_success_rate < .2:
            self.level = max(self.minimum, self.level - 1)

def test():
    d = Challenge()
    for _ in range(20): d.observe(1)
    assert d.level == 5
    for _ in range(20): d.observe(0)
    assert d.level == 1
    d.observe(.5)
    assert d.level == 1

if __name__ == "__main__":
    test()
    print("challenge: ok")
