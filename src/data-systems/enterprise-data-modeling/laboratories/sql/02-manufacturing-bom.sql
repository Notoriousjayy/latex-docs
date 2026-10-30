-- Original manufacturing BOM lab. Re-running resets these demo tables only.
BEGIN;
CREATE SCHEMA IF NOT EXISTS edm;
DROP TABLE IF EXISTS edm.material_consumption CASCADE;
DROP TABLE IF EXISTS edm.production_run CASCADE;
DROP TABLE IF EXISTS edm.bom_line CASCADE;
DROP TABLE IF EXISTS edm.part_revision CASCADE;
DROP TABLE IF EXISTS edm.part CASCADE;
CREATE TABLE edm.part (
  part_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  part_code text NOT NULL UNIQUE,
  part_name text NOT NULL
);
CREATE TABLE edm.part_revision (
  part_revision_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  part_id bigint NOT NULL REFERENCES edm.part(part_id),
  revision_code text NOT NULL,
  released_at date,
  UNIQUE(part_id, revision_code)
);
CREATE TABLE edm.bom_line (
  parent_revision_id bigint NOT NULL REFERENCES edm.part_revision(part_revision_id),
  component_revision_id bigint NOT NULL REFERENCES edm.part_revision(part_revision_id),
  quantity_per numeric(14,4) NOT NULL CHECK (quantity_per > 0),
  effective_from date NOT NULL,
  effective_to date,
  PRIMARY KEY (parent_revision_id, component_revision_id, effective_from),
  CHECK (parent_revision_id <> component_revision_id),
  CHECK (effective_to IS NULL OR effective_to > effective_from)
);
CREATE TABLE edm.production_run (
  production_run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  work_order_ref text NOT NULL UNIQUE,
  produced_revision_id bigint NOT NULL REFERENCES edm.part_revision(part_revision_id),
  started_at timestamptz NOT NULL,
  completed_at timestamptz,
  CHECK (completed_at IS NULL OR completed_at >= started_at)
);
CREATE TABLE edm.material_consumption (
  production_run_id bigint NOT NULL REFERENCES edm.production_run(production_run_id),
  component_revision_id bigint NOT NULL REFERENCES edm.part_revision(part_revision_id),
  lot_code text NOT NULL,
  quantity_used numeric(14,4) NOT NULL CHECK(quantity_used > 0),
  PRIMARY KEY (production_run_id, component_revision_id, lot_code)
);
INSERT INTO edm.part(part_code,part_name)
VALUES ('A-100','Assembly'),('C-200','Component');
INSERT INTO edm.part_revision(part_id,revision_code,released_at)
VALUES (1,'R1','2026-01-10'),(2,'R1','2026-01-02');
INSERT INTO edm.bom_line(parent_revision_id,component_revision_id,quantity_per,effective_from)
VALUES(1,2,2.0,'2026-01-10');
COMMIT;
-- True graph-cycle prevention and interval overlap exclusion need additional logic.
