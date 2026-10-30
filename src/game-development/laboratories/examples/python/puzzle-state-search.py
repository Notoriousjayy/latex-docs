from collections import deque

def shortest_path(start, goal, blocked=frozenset(), width=3):
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        cell, path = queue.popleft()
        if cell == goal:
            return path
        x, y = cell
        for nxt in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)):
            if (0 <= nxt[0] < width and 0 <= nxt[1] < width
                    and nxt not in blocked and nxt not in seen):
                seen.add(nxt)
                queue.append((nxt, path + [nxt]))
    return None

def test():
    p = shortest_path((0, 0), (2, 2), {(1, 1)})
    assert p[0] == (0, 0) and p[-1] == (2, 2) and len(p) == 5
    assert shortest_path((0, 0), (2, 2), {(0, 1), (1, 0)}) is None

if __name__ == "__main__":
    test()
    print("puzzle: ok")
