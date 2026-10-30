import heapq
import itertools

class EventQueue:
    def __init__(self):
        self.items = []
        self.sequence = itertools.count()

    def schedule(self, when: int, event: str):
        heapq.heappush(self.items, (when, next(self.sequence), event))

    def drain(self):
        out = []
        while self.items:
            out.append(heapq.heappop(self.items)[2])
        return out

def test():
    q = EventQueue()
    q.schedule(3, "A")
    q.schedule(1, "B")
    q.schedule(3, "C")
    assert q.drain() == ["B", "A", "C"]

if __name__ == "__main__":
    test()
    print("queue: ok")
