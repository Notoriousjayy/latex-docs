-- Original PostgreSQL learning schema, not a production migration.
-- Run with psql -X -v ON_ERROR_STOP=1 -f 01-party-and-agreements.sql
BEGIN;
CREATE SCHEMA IF NOT EXISTS edm;
DROP TABLE IF EXISTS edm.agreement_participant CASCADE;
DROP TABLE IF EXISTS edm.agreement CASCADE;
DROP TABLE IF EXISTS edm.party_role CASCADE;
DROP TABLE IF EXISTS edm.party CASCADE;
CREATE TABLE edm.party (
  party_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  party_kind text NOT NULL CHECK (party_kind IN ('PERSON','ORGANIZATION')),
  display_name text NOT NULL CHECK (btrim(display_name) <> ''),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE edm.party_role (
  party_role_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  party_id bigint NOT NULL REFERENCES edm.party(party_id),
  role_code text NOT NULL,
  effective_from date NOT NULL,
  effective_to date,
  CHECK (effective_to IS NULL OR effective_to > effective_from),
  UNIQUE (party_id, role_code, effective_from)
);
CREATE TABLE edm.agreement (
  agreement_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  agreement_ref text NOT NULL UNIQUE,
  agreement_date date NOT NULL,
  status text NOT NULL CHECK (status IN ('DRAFT','SIGNED','TERMINATED'))
);
CREATE TABLE edm.agreement_participant (
  agreement_id bigint NOT NULL REFERENCES edm.agreement(agreement_id),
  party_role_id bigint NOT NULL REFERENCES edm.party_role(party_role_id),
  responsibility text NOT NULL,
  PRIMARY KEY (agreement_id, party_role_id, responsibility)
);
INSERT INTO edm.party(party_kind,display_name) VALUES
  ('ORGANIZATION','Example Supplier'),('PERSON','Example Customer');
INSERT INTO edm.party_role(party_id,role_code,effective_from)
SELECT party_id, CASE WHEN party_kind='ORGANIZATION' THEN 'SELLER' ELSE 'BUYER' END,
DATE '2026-01-01' FROM edm.party;
INSERT INTO edm.agreement(agreement_ref,agreement_date,status)
VALUES ('DEMO-AGR-001', DATE '2026-10-01','SIGNED');
INSERT INTO edm.agreement_participant(agreement_id,party_role_id,responsibility)
SELECT 1, party_role_id, role_code FROM edm.party_role;
COMMIT;
-- Overlapping effective periods are NOT prohibited by these row-local constraints.
-- An actual rule requires a separate exclusion/transaction design and concurrency tests.
