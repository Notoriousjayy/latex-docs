-- E-commerce commercial price snapshot demonstration.
BEGIN;
CREATE SCHEMA IF NOT EXISTS edm;
DROP TABLE IF EXISTS edm.demo_order_line CASCADE;
DROP TABLE IF EXISTS edm.demo_order CASCADE;
DROP TABLE IF EXISTS edm.seller_offer CASCADE;
CREATE TABLE edm.seller_offer (
  offer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  seller_id bigint NOT NULL,
  product_code text NOT NULL,
  current_unit_price numeric(15,2) NOT NULL CHECK(current_unit_price >= 0),
  currency_code char(3) NOT NULL,
  UNIQUE(seller_id,product_code)
);
CREATE TABLE edm.demo_order (
  order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  buyer_id bigint NOT NULL,
  placed_at timestamptz NOT NULL DEFAULT now(),
  state text NOT NULL CHECK (state IN ('SUBMITTED','PAID','PARTIALLY_FULFILLED','FULFILLED','CANCELLED'))
);
CREATE TABLE edm.demo_order_line (
  order_line_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id bigint NOT NULL REFERENCES edm.demo_order(order_id),
  offer_id bigint NOT NULL REFERENCES edm.seller_offer(offer_id),
  agreed_unit_price numeric(15,2) NOT NULL CHECK(agreed_unit_price >= 0),
  agreed_currency char(3) NOT NULL,
  quantity integer NOT NULL CHECK(quantity > 0)
);
INSERT INTO edm.seller_offer(seller_id,product_code,current_unit_price,currency_code)
VALUES (12,'BOOK-001',19.99,'USD');
INSERT INTO edm.demo_order(buyer_id,state) VALUES (42,'SUBMITTED');
INSERT INTO edm.demo_order_line(order_id,offer_id,agreed_unit_price,agreed_currency,quantity)
SELECT 1,offer_id,current_unit_price,currency_code,2 FROM edm.seller_offer;
UPDATE edm.seller_offer SET current_unit_price=24.99 WHERE offer_id=1;
COMMIT;
-- The placed order remains at the contract-time unit price of 19.99.
SELECT o.order_id,l.agreed_unit_price,f.current_unit_price
FROM edm.demo_order o JOIN edm.demo_order_line l USING(order_id)
JOIN edm.seller_offer f USING(offer_id);
