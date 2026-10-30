-- Run after scripts 01--05, from psql with ON_ERROR_STOP=1.
-- Positive invariant queries; negative cases use transactional savepoints.
DO $$
BEGIN
 IF EXISTS (SELECT 1 FROM edm.party_role
  WHERE effective_to IS NOT NULL AND effective_to <= effective_from) THEN
   RAISE EXCEPTION 'Party role interval invariant failed';
 END IF;
 IF (SELECT COUNT(*) FROM edm.demo_order_line WHERE agreed_unit_price=19.99)<>1 THEN
   RAISE EXCEPTION 'Contract-time price snapshot was lost';
 END IF;
 IF EXISTS (SELECT journal_id FROM edm.ledger_posting
  GROUP BY journal_id HAVING SUM(signed_amount)<>0) THEN
   RAISE EXCEPTION 'Transfer has unbalanced postings';
 END IF;
END $$;
-- Demonstrate a rejected negative input without terminating the lab run.
DO $$
BEGIN
  BEGIN
    INSERT INTO edm.demo_order_line(order_id,offer_id,agreed_unit_price,agreed_currency,quantity)
    VALUES(1,1,2.00,'USD',-1);
    RAISE EXCEPTION 'Expected quantity check to reject the row';
  EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'Expected negative quantity rejected';
  END;
END $$;
SELECT 'All smoke assertions passed' AS result;
