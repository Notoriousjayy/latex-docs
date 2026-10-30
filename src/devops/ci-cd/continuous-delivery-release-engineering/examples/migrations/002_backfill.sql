-- Idempotent backfill, validate counts before later contraction.
UPDATE orders SET customer_display_name = customer_name
WHERE customer_display_name IS NULL;
SELECT COUNT(*) AS missing_display_names FROM orders WHERE customer_display_name IS NULL;
