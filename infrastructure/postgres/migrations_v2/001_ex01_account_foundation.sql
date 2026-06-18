-- AgroVision — execution-v2 / EX-01 (Account Foundation)
-- Introduces the `Account` entity above Farm in the priority chain:
-- Account -> Farm -> Building -> Batch (see
-- .project-governance/execution-v2/decision_log.md BMD-001).
--
-- ADDITIVE ONLY: does not modify infrastructure/postgres/init.sql or
-- init_monolith.sql. Targets the single `agrovision` database, schemas
-- `identity` and `farm` (already created by init_monolith.sql).
--
-- Alembic is not wired up for the monolith yet (migration_decisions.md
-- MD-008) — this script continues the same manual-apply convention used by
-- init_monolith.sql (M4) rather than introducing Alembic as an incidental
-- side effect of this phase (T-EX01-02: decision recorded in
-- project_state.md — direct schema bootstrap continues; full Alembic
-- wiring remains a separately tracked, not-yet-scoped item).
--
-- Run manually against the `agrovision` database:
--   docker exec -i agrovision-postgres-1 psql -U agrovision -d agrovision \
--     < infrastructure/postgres/migrations_v2/001_ex01_account_foundation.sql
--
-- Idempotent: safe to run more than once (IF NOT EXISTS / ON CONFLICT guards
-- throughout).

BEGIN;

-- 1. Create the accounts table.
CREATE TABLE IF NOT EXISTS identity.accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_user_id UUID NOT NULL REFERENCES identity.users(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    updated_by UUID
);

-- 2. Backfill: one Account per distinct existing farm owner, so every
--    pre-existing Farm has a real Account to attach to (no orphaned farms).
INSERT INTO identity.accounts (id, name, owner_user_id, is_active, created_at, updated_at)
SELECT gen_random_uuid(),
       u.full_name || ' — Account',
       f.owner_user_id,
       true,
       now(),
       now()
FROM (SELECT DISTINCT owner_user_id FROM farm.farms) f
JOIN identity.users u ON u.id = f.owner_user_id
WHERE NOT EXISTS (
    SELECT 1 FROM identity.accounts a WHERE a.owner_user_id = f.owner_user_id
);

-- 3. Add Farm.account_id (nullable for now — EX-02 makes it mandatory and
--    wires it into the create/update use cases; this migration only adds
--    the column and backfills existing rows).
ALTER TABLE farm.farms ADD COLUMN IF NOT EXISTS account_id UUID REFERENCES identity.accounts(id);

UPDATE farm.farms f
SET account_id = a.id
FROM identity.accounts a
WHERE a.owner_user_id = f.owner_user_id
  AND f.account_id IS NULL;

-- 4. Add User.account_id (nullable — a platform super-admin has none).
ALTER TABLE identity.users ADD COLUMN IF NOT EXISTS account_id UUID REFERENCES identity.accounts(id);

-- 4a. Owner users get their own account.
UPDATE identity.users u
SET account_id = a.id
FROM identity.accounts a
WHERE a.owner_user_id = u.id
  AND u.account_id IS NULL;

-- 4b. Staff users (non-owner, scoped to a farm) inherit their farm's account.
UPDATE identity.users u
SET account_id = f.account_id
FROM farm.farms f
WHERE u.farm_id = f.id
  AND u.account_id IS NULL
  AND f.account_id IS NOT NULL;

COMMIT;

-- Verification queries (run manually after applying, not part of the
-- transaction above):
--   SELECT count(*) FROM farm.farms WHERE account_id IS NULL;          -- expect 0
--   SELECT count(*) FROM identity.users WHERE farm_id IS NOT NULL AND account_id IS NULL; -- expect 0
--   SELECT count(*) FROM identity.accounts;                            -- expect >= 1
