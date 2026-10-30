from dataclasses import dataclass

@dataclass(frozen=True)
class Game:
    mode: str = "menu"
    health: int = 3

TRANSITIONS = {("menu", "start"): "playing", ("playing", "pause"): "paused",
               ("paused", "resume"): "playing", ("playing", "finish"): "won"}

def apply(state: Game, command: str) -> Game:
    target = TRANSITIONS.get((state.mode, command))
    if target is None:
        raise ValueError("invalid transition")
    return Game(target, state.health)

def test():
    s = apply(Game(), "start")
    assert s.mode == "playing" and s.health == 3
    try:
        apply(s, "resume")
        raise AssertionError("should reject")
    except ValueError:
        pass
    assert apply(apply(s, "pause"), "resume") == s

if __name__ == "__main__":
    test()
    print("fsm: ok")
