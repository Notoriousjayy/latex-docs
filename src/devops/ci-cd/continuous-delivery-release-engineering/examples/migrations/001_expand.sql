-- Example SQLite additive migration (safe only for demonstration).
-- Keep original clients compatible during rollout.
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    total_cents INTEGER NOT NULL
);
ALTER TABLE orders ADD COLUMN customer_display_name TEXT;
