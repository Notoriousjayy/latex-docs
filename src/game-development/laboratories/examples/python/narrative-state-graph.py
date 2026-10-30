from dataclasses import dataclass

@dataclass(frozen=True)
class Story:
    clue: bool = False
    trusted: bool = False

def choose(state: Story, action: str) -> Story:
    if action == "investigate":
        return Story(True, state.trusted)
    if action == "confide" and state.clue:
        return Story(state.clue, True)
    raise ValueError("locked choice")

def ending(state: Story) -> str:
    return "alliance" if state.trusted else "isolation"

def test():
    s = Story()
    try:
        choose(s, "confide")
        raise AssertionError("locked option")
    except ValueError:
        pass
    assert ending(choose(choose(s, "investigate"), "confide")) == "alliance"

if __name__ == "__main__":
    test()
    print("narrative: ok")
