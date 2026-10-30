-- Demonstrates paired postings through one controlled function.
-- Application role must NOT be granted direct INSERT on journal/posting.
BEGIN;
CREATE SCHEMA IF NOT EXISTS edm;
DROP FUNCTION IF EXISTS edm.post_transfer(bigint,bigint,numeric,text);
DROP TABLE IF EXISTS edm.ledger_posting CASCADE;
DROP TABLE IF EXISTS edm.ledger_journal CASCADE;
DROP TABLE IF EXISTS edm.ledger_account CASCADE;
CREATE TABLE edm.ledger_account (
  account_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  account_ref text NOT NULL UNIQUE,
  currency_code char(3) NOT NULL,
  is_open boolean NOT NULL DEFAULT true
);
CREATE TABLE edm.ledger_journal (
  journal_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  external_transfer_ref text NOT NULL UNIQUE,
  recorded_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE edm.ledger_posting (
  posting_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  journal_id bigint NOT NULL REFERENCES edm.ledger_journal(journal_id),
  account_id bigint NOT NULL REFERENCES edm.ledger_account(account_id),
  signed_amount numeric(18,2) NOT NULL CHECK(signed_amount<>0)
);
CREATE FUNCTION edm.post_transfer(p_source bigint,p_target bigint,p_amount numeric,p_reference text)
RETURNS bigint LANGUAGE plpgsql AS $$
DECLARE v_journal bigint; v_source edm.ledger_account%ROWTYPE; v_target edm.ledger_account%ROWTYPE;
BEGIN
  IF p_source=p_target OR p_amount<=0 OR p_amount IS NULL THEN
    RAISE EXCEPTION 'Invalid transfer arguments';
  END IF;
  -- Lock accounts in deterministic order to reduce deadlock risk.
  PERFORM 1 FROM edm.ledger_account WHERE account_id IN(p_source,p_target)
    ORDER BY account_id FOR UPDATE;
  SELECT * INTO v_source FROM edm.ledger_account WHERE account_id=p_source;
  SELECT * INTO v_target FROM edm.ledger_account WHERE account_id=p_target;
  IF NOT FOUND OR v_source.account_id IS NULL OR NOT v_source.is_open
     OR NOT v_target.is_open OR v_source.currency_code<>v_target.currency_code THEN
    RAISE EXCEPTION 'Invalid account state or currency mismatch';
  END IF;
  INSERT INTO edm.ledger_journal(external_transfer_ref) VALUES(p_reference)
    RETURNING journal_id INTO v_journal;
  INSERT INTO edm.ledger_posting(journal_id,account_id,signed_amount)
  VALUES(v_journal,p_source,-p_amount),(v_journal,p_target,p_amount);
  RETURN v_journal;
END $$;
INSERT INTO edm.ledger_account(account_ref,currency_code) VALUES
 ('DEMO-CASH-A','USD'),('DEMO-CASH-B','USD');
SELECT edm.post_transfer(1,2,25.00,'TRANSFER-001');
COMMIT;
-- Caveat: this is a teaching implementation, NOT a complete financial ledger.
-- A production system must restrict arbitrary posting DML, guard immutable history,
-- enforce balances via a controlled posting protocol, and handle authorization,
-- reversals, idempotency, concurrency and multi-currency rules.
SELECT journal_id,SUM(signed_amount) AS net FROM edm.ledger_posting GROUP BY journal_id;
