-- AgroVision — execution-v2 / EX-04 (Batch Lifecycle Simplification)
-- Collapses poultry.batches.status from {quarantine, active, closed} to
-- {active, completed}, per .project-governance/execution-v2/decision_log.md
-- BMD-002 (quarantine removed entirely) and BMD-003 (CLOSED renamed to
-- COMPLETED). Also drops the now-unused quarantine_end_date column.
--
-- Pre-verified before writing this script (2026-06-18), live `agrovision`
-- database: 4 rows in poultry.batches —
--   1 'closed'     (B-2026-001, close_reason='sale')
--   2 'quarantine'  (B-2026-06, UAT-TEST-01 — pre-existing test/UAT data,
--                    not created by this initiative)
--   1 'active'      (B-2026-06-10)
-- No row has close_reason='slaughter' — safe to drop that enum value with
-- no data rewrite needed. No CHECK constraint enforces status/close_reason
-- at the database level (validation is Python/Pydantic-only via BatchStatus
-- /BatchCloseReason), consistent with the EX-03 precedent for section_type.
--
-- Status mapping applied: quarantine -> active (the only non-terminal state
-- left), closed -> completed (BMD-003 rename, same terminal meaning).
--
-- Run manually against the `agrovision` database:
--   docker exec -i agrovision-postgres-1 psql -U agrovision -d agrovision \
--     < infrastructure/postgres/migrations_v2/003_ex04_batch_lifecycle_simplification.sql
--
-- Idempotent: safe to run more than once.

BEGIN;

UPDATE poultry.batches SET status = 'active' WHERE status = 'quarantine';
UPDATE poultry.batches SET status = 'completed' WHERE status = 'closed';

ALTER TABLE poultry.batches ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE poultry.batches DROP COLUMN IF EXISTS quarantine_end_date;

COMMIT;

-- Verification queries (run manually after applying):
--   SELECT DISTINCT status FROM poultry.batches; -- expect only 'active'/'completed'
--   SELECT column_name FROM information_schema.columns
--     WHERE table_schema='poultry' AND table_name='batches'
--     AND column_name='quarantine_end_date'; -- expect 0 rows
