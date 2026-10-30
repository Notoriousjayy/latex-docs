from dataclasses import dataclass

@dataclass
class Wallet:
    balance: int
    cap: int = 20

    def spend(self, amount: int) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True

    def earn(self, amount: int) -> bool:
        if amount <= 0 or amount > self.cap - self.balance:
            return False
        self.balance += amount
        return True

def test():
    w = Wallet(10)
    assert not w.spend(11) and w.balance == 10
    assert w.spend(6) and w.balance == 4
    assert not w.earn(19) and w.balance == 4
    assert w.earn(3) and w.balance == 7

if __name__ == "__main__":
    test()
    print("economy: ok")
