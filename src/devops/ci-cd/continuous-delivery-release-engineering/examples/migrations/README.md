# Example database migrations

SQLite additive expand, repeatable backfill and intentionally unimplemented contraction. Not for production datasets.

## Inventory

- [`001_expand.sql`](001_expand.sql)
- [`002_backfill.sql`](002_backfill.sql)
- [`003_contract_REVIEW_ONLY.sql`](003_contract_REVIEW_ONLY.sql)

## Use

See the parent `examples/README.md` for safety prerequisites. Do not copy secrets, Terraform plans, or IAM session credentials into this repository.
