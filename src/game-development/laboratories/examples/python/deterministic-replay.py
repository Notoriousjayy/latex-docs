VALID = {"gain": 2, "spend": -1}

def replay(initial: int, commands: list[str]) -> int:
    score = initial
    for command in commands:
        if command not in VALID:
            raise ValueError("invalid command")
        candidate = score + VALID[command]
        if candidate < 0:
            raise ValueError("insufficient balance")
        score = candidate
    return score

def test():
    cmds = ["gain", "spend", "gain"]
    assert replay(0, cmds) == 3
    assert replay(0, cmds) == replay(0, cmds)
    try:
        replay(0, ["spend"])
        raise AssertionError("invalid negative balance")
    except ValueError:
        pass

if __name__ == "__main__":
    test()
    print("replay: ok")
