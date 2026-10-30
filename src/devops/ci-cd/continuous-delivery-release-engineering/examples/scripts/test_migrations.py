"""Check the example additive migration and idempotent backfill."""
from pathlib import Path
import sqlite3
import unittest

SQL = Path(__file__).resolve().parent.parent / "migrations"

class MigrationTests(unittest.TestCase):
    def test_expand_backfill_compatible_old_reads(self):
        db = sqlite3.connect(":memory:")
        db.executescript((SQL / "001_expand.sql").read_text())
        db.execute("INSERT INTO orders (order_id, customer_name, total_cents) VALUES (1, 'Turing', 1200)")
        self.assertEqual(db.execute("SELECT customer_name FROM orders").fetchone()[0], 'Turing')
        for _ in range(2):
            db.executescript((SQL / "002_backfill.sql").read_text())
        self.assertEqual(db.execute("SELECT customer_display_name FROM orders").fetchone()[0], 'Turing')
        self.assertEqual(db.execute("SELECT COUNT(*) FROM orders WHERE customer_display_name IS NULL").fetchone()[0], 0)

if __name__ == "__main__":
    unittest.main()
