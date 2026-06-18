-- AgroVision — execution-v2 / EX-16 (Archive System)
-- Adds manual-only batch archiving, per .project-governance/execution-v2/
-- decision_log.md BMD-018 (business-owner archive policy: manual trigger
-- only; Account Owner / Farm Director authority; batch status stays
-- COMPLETED; archived batches hidden from default Dashboard/Farm views but
-- remain fully visible/filterable in Reports; no data deletion, no audit
-- history removal; no automatic/scheduled archiving, no retention policy).
--
-- Additive-only: this migration adds nullable/defaulted columns. No
-- existing column, row, or table is altered or removed.
--
-- Run manually against the `agrovision` database:
--   docker exec -i agrovision-postgres-1 psql -U agrovision -d agrovision \
--     < infrastructure/postgres/migrations_v2/007_ex16_archive_system.sql
--
-- Idempotent: safe to run more than once.

BEGIN;

ALTER TABLE poultry.batches ADD COLUMN IF NOT EXISTS is_archived BOOLEAN;
ALTER TABLE poultry.batches ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;
ALTER TABLE poultry.batches ADD COLUMN IF NOT EXISTS archived_by UUID;

UPDATE poultry.batches SET is_archived = false WHERE is_archived IS NULL;
ALTER TABLE poultry.batches ALTER COLUMN is_archived SET NOT NULL;
ALTER TABLE poultry.batches ALTER COLUMN is_archived SET DEFAULT false;
CREATE INDEX IF NOT EXISTS ix_batches_is_archived ON poultry.batches (is_archived);

COMMIT;

-- Verification queries (run manually after applying):
--   \d poultry.batches                                                  -- expect is_archived (not null), archived_at, archived_by
--   SELECT count(*) FROM poultry.batches WHERE is_archived IS NULL;     -- expect 0
--   SELECT count(*) FROM poultry.batches WHERE is_archived = true;      -- expect 0 (nothing archived yet)
