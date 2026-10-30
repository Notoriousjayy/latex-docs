ALLOWED = {"session_id", "event", "time_ms"}
EVENTS = {"start", "move", "finish", "hint"}

def collect(opt_in: bool, record: dict, store: list) -> bool:
    if not opt_in:
        return False
    if (set(record) != ALLOWED or record["event"] not in EVENTS
            or not isinstance(record["time_ms"], int)
            or not isinstance(record["session_id"], str)):
        return False
    store.append(dict(record))
    return True

def test():
    items = []
    rec = {"session_id": "s1", "event": "move", "time_ms": 12}
    assert not collect(False, rec, items) and not items
    assert collect(True, rec, items) and len(items) == 1
    assert not collect(True, {**rec, "email": "private"}, items)
    items.clear()  # Retention/deletion hook for a local demo.
    assert not items

if __name__ == "__main__":
    test()
    print("telemetry: ok")
