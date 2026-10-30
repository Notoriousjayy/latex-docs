"""In-memory disposable migration smoke check; no production data or connection."""
from pathlib import Path
import sqlite3
sql = (Path(__file__).parent / "sql/001_create_tasks.sql").read_text()
with sqlite3.connect(":memory:") as conn:
    conn.executescript(sql)
    conn.execute("INSERT INTO tasks(name) VALUES (?)", ("sample",))
    assert conn.execute("SELECT name,completed FROM tasks").fetchone() == ("sample", 0)
print("migration smoke check passed")
