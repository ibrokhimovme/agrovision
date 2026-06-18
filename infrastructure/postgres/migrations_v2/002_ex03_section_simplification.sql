-- AgroVision — execution-v2 / EX-03 (Building & Section Simplification)
-- Removes the quarantine SectionType and its one existing demo-data row,
-- per .project-governance/execution-v2/decision_log.md BMD-002 (quarantine
-- workflows removed entirely, including the place/type concept, not just
-- the batch-status concept handled separately in EX-04).
--
-- Pre-verified before writing this script (2026-06-18): exactly one
-- section row exists with section_type='quarantine' (id
-- cccccccc-0003-0000-0000-000000000005, "Karantin bo'limi", inside building
-- "Karantin bloki" id cccccccc-0003-0000-0000-000000000002), and zero
-- poultry.batches rows reference that section_id — safe to delete outright
-- rather than needing a more careful re-typing/data-preservation migration.
--
-- No CHECK constraint enforces section_type values at the database level
-- (validation is Python/Pydantic-only, via SectionType), so no ALTER TABLE
-- ... DROP CONSTRAINT is needed here — removing QUARANTINE from the Python
-- enum (already done in app/farm/domain/models/farm.py) is what prevents
-- new quarantine-typed sections going forward.
--
-- Run manually against the `agrovision` database:
--   docker exec -i agrovision-postgres-1 psql -U agrovision -d agrovision \
--     < infrastructure/postgres/migrations_v2/002_ex03_section_simplification.sql
--
-- Idempotent: safe to run more than once.

BEGIN;

-- Defensive re-check at apply time: abort if any batch has ever been placed
-- in a quarantine-typed section, rather than blindly deleting data that
-- might matter. (DO block since plain SQL can't conditionally raise.)
DO $$
DECLARE
    batch_count INTEGER;
BEGIN
    SELECT count(*) INTO batch_count
    FROM poultry.batches b
    JOIN farm.sections s ON s.id = b.section_id
    WHERE s.section_type = 'quarantine';

    IF batch_count > 0 THEN
        RAISE EXCEPTION 'EX-03 migration aborted: % batch(es) reference a quarantine-typed section. Resolve manually before re-running.', batch_count;
    END IF;
END $$;

-- Delete the quarantine section, then its now-empty parent building.
DELETE FROM farm.sections WHERE section_type = 'quarantine';
DELETE FROM farm.buildings
WHERE id = 'cccccccc-0003-0000-0000-000000000002'
  AND NOT EXISTS (SELECT 1 FROM farm.sections WHERE building_id = farm.buildings.id);

COMMIT;

-- Verification queries (run manually after applying):
--   SELECT count(*) FROM farm.sections WHERE section_type = 'quarantine'; -- expect 0
--   SELECT id, name FROM farm.buildings WHERE name ILIKE '%karantin%';    -- expect 0 rows
