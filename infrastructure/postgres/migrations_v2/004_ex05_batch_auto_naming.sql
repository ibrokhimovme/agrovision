-- AgroVision — execution-v2 / EX-05 (Batch Auto Naming)
-- Makes poultry.batches.batch_code mandatory and enforces per-farm
-- uniqueness at the database level, per
-- .project-governance/execution-v2/decision_log.md BMD-012 (farm-prefixed
-- sequential naming convention, fully automatic, no manual override,
-- finalized with the business owner on 2026-06-18).
--
-- Pre-verified before writing this script (2026-06-18), live `agrovision`
-- database: all 4 existing poultry.batches rows already have a non-null
-- batch_code, and all 4 are already unique within their (single) farm —
-- no backfill or dedup pass is needed before adding the constraints.
--
-- Run manually against the `agrovision` database:
--   docker exec -i agrovision-postgres-1 psql -U agrovision -d agrovision \
--     < infrastructure/postgres/migrations_v2/004_ex05_batch_auto_naming.sql
--
-- Idempotent: safe to run more than once (constraint adds are guarded).

BEGIN;

ALTER TABLE poultry.batches ALTER COLUMN batch_code SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_batches_farm_id_batch_code'
    ) THEN
        ALTER TABLE poultry.batches
            ADD CONSTRAINT uq_batches_farm_id_batch_code UNIQUE (farm_id, batch_code);
    END IF;
END $$;

COMMIT;

-- Verification queries (run manually after applying):
--   SELECT count(*) FROM poultry.batches WHERE batch_code IS NULL; -- expect 0
--   \d poultry.batches -- expect "uq_batches_farm_id_batch_code" UNIQUE constraint listed
