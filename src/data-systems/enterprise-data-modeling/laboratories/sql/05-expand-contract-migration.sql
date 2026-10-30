-- Educational expand/backfill example; never contract live columns blindly.
BEGIN;
CREATE SCHEMA IF NOT EXISTS edm;
DROP TABLE IF EXISTS edm.customer_profile CASCADE;
CREATE TABLE edm.customer_profile (
  customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name text NOT NULL
);
INSERT INTO edm.customer_profile(full_name) VALUES ('Ada Example'),('Grace Example');
ALTER TABLE edm.customer_profile ADD COLUMN given_name text;
ALTER TABLE edm.customer_profile ADD COLUMN family_name text;
-- Placeholder backfill logic is deliberately simplified for known demo fixtures.
UPDATE edm.customer_profile SET
  given_name=split_part(full_name,' ',1),
  family_name=substring(full_name from strpos(full_name,' ')+1)
WHERE strpos(full_name,' ')>0 AND given_name IS NULL;
COMMIT;
SELECT COUNT(*) AS remaining FROM edm.customer_profile
WHERE given_name IS NULL OR family_name IS NULL;
-- Do not DROP full_name until every existing reader and writer has migrated.
-- Real names are not safely parsed by splitting on one space.
