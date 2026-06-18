-- AgroVision — execution-v2 / EX-11 (Finance Improvements)
-- Adds supplier debt, customer debt, and partial-payment tracking, per
-- .project-governance/execution-v2/decision_log.md BMD-015 (business-owner
-- scope: track supplier debt, customer debt, partial payments, outstanding
-- balances, debtor/creditor summary — explicitly NOT budgeting/forecasting/
-- advanced accounting).
--
-- Pre-verified before writing this script (2026-06-18), live `agrovision`
-- database: 14 expenses (none with a supplier_id, since the column is new),
-- 2 sale_records (1 'paid' totaling 329,280,000 UZS, 1 'pending' totaling
-- 8,750,000 UZS) — backfill assumes existing 'paid' expenses/sales were
-- already fully settled (amount_paid = amount/total_revenue_uzs), and
-- existing 'pending' sales had nothing paid yet (amount_paid = 0). This
-- preserves the pre-EX-11 assumption that expenses are settled immediately
-- unless a supplier debt is explicitly declared going forward.
--
-- Run manually against the `agrovision` database:
--   docker exec -i agrovision-postgres-1 psql -U agrovision -d agrovision \
--     < infrastructure/postgres/migrations_v2/006_ex11_finance_debt_tracking.sql
--
-- Idempotent: safe to run more than once.

BEGIN;

CREATE TABLE IF NOT EXISTS finance.suppliers (
    id UUID PRIMARY KEY,
    farm_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    updated_by UUID
);
CREATE INDEX IF NOT EXISTS ix_suppliers_farm_id ON finance.suppliers (farm_id);

ALTER TABLE finance.expenses ADD COLUMN IF NOT EXISTS supplier_id UUID;
ALTER TABLE finance.expenses ADD COLUMN IF NOT EXISTS amount_paid NUMERIC(15, 2);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_expenses_supplier_id'
    ) THEN
        ALTER TABLE finance.expenses
            ADD CONSTRAINT fk_expenses_supplier_id FOREIGN KEY (supplier_id) REFERENCES finance.suppliers(id);
    END IF;
END $$;

UPDATE finance.expenses SET amount_paid = amount WHERE amount_paid IS NULL;
ALTER TABLE finance.expenses ALTER COLUMN amount_paid SET NOT NULL;
ALTER TABLE finance.expenses ALTER COLUMN amount_paid SET DEFAULT 0;
CREATE INDEX IF NOT EXISTS ix_expenses_supplier_id ON finance.expenses (supplier_id);

ALTER TABLE finance.sale_records ADD COLUMN IF NOT EXISTS amount_paid NUMERIC(15, 2);
UPDATE finance.sale_records
    SET amount_paid = CASE WHEN payment_status = 'paid' THEN total_revenue_uzs ELSE 0 END
    WHERE amount_paid IS NULL;
ALTER TABLE finance.sale_records ALTER COLUMN amount_paid SET NOT NULL;
ALTER TABLE finance.sale_records ALTER COLUMN amount_paid SET DEFAULT 0;

COMMIT;

-- Verification queries (run manually after applying):
--   \d finance.suppliers          -- expect the new table
--   \d finance.expenses           -- expect supplier_id, amount_paid (not null)
--   \d finance.sale_records       -- expect amount_paid (not null)
--   SELECT count(*) FROM finance.expenses WHERE amount_paid IS NULL;      -- expect 0
--   SELECT count(*) FROM finance.sale_records WHERE amount_paid IS NULL; -- expect 0
