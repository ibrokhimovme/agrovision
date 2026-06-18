# AgroVision — M4 Database Consolidation Design

**Status:** Design + low-risk scaffolding complete. Live data migration NOT executed in this pass — see §5 (Verification Blocker).

## 1. Target Shape

- One Postgres **database**: `agrovision` (already the default in `.env`'s `POSTGRES_DB=agrovision` — the consolidated DB name was effectively pre-chosen before this migration started).
- One Postgres **schema** per module that currently owns a database: `identity`, `farm`, `poultry`, `inventory`, `finance`, `notifications`. (`gateway` and `reporting` own no tables today and need no schema.)
- Each module's existing SQLAlchemy models are unchanged — they don't hardcode a schema, so routing them into the correct schema is done via the connection's `search_path`, not by editing model code.
- Each module keeps tracking its own migration state via Alembic's `version_table_schema` parameter, pointed at that module's schema (e.g. `identity.alembic_version`). Existing migration scripts are copied unmodified (per MD-004).

## 2. Schema Bootstrap

New file `infrastructure/postgres/init_monolith.sql` (additive — does **not** modify or replace the existing `infrastructure/postgres/init.sql`, which remains exactly as-is for the still-running `services/*` microservices):

```sql
CREATE SCHEMA IF NOT EXISTS identity;
CREATE SCHEMA IF NOT EXISTS farm;
CREATE SCHEMA IF NOT EXISTS poultry;
CREATE SCHEMA IF NOT EXISTS inventory;
CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS notifications;
GRANT ALL ON SCHEMA identity, farm, poultry, inventory, finance, notifications TO agrovision;
```

This only needs to run once against the `agrovision` database. It does not touch `identity_db`, `farm_db`, `livestock_db`, `inventory_db`, `finance_db`, `notification_db`, or `reporting_db` — those remain intact and in use by `services/*` until M7.

## 3. Consolidated Settings

`app/core/config.py` (new — monolith-level settings, separate from each module's own `app/<module>/core/config.py`, which is left unchanged and unused once the monolith is wired in M5/M6):

- Single `DATABASE_URL` pointing at `agrovision` (not a per-module DB).
- Single `REDIS_URL`, single `JWT_SECRET_KEY`/`JWT_ALGORITHM` (the gateway's, since it's the only one that mattered — see audit §7).
- No `RABBITMQ_URL` (MD-002: dropped).
- Each module's repository/session code still asks for "a DATABASE_URL" the same way it always did; the only change needed when modules are actually wired (M5/M6) is to set the connection's `search_path` to the owning module's schema before queries run. That wiring is **not** done yet — it belongs to M5 (API Consolidation), since it requires the modules to actually be mounted and exercised together.

## 4. `farms_ref` Resolution (MD-003)

Exact steps for when this is executed against a reachable database (M5/M6 timeframe, or earlier if DB access becomes available before then):

1. Confirm (again, via live query, not just code inspection) that `identity.farms_ref` and `poultry.farms_ref` contain zero rows or only stale/orphaned rows — expected, since no consumer ever populated them (confirmed via static audit; must be re-confirmed live before deleting anything, per the Deletion Gate).
2. Alembic revision in `identity` schema: `ALTER TABLE users DROP CONSTRAINT <fk>; ALTER TABLE users ADD CONSTRAINT users_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES farm.farms(id);`
3. Alembic revision in `poultry` schema: same pattern for `batches.farm_id` → `farm.farms.id`.
4. Drop `identity.farms_ref` and `poultry.farms_ref` only after step 2/3 are applied and verified (FK now resolves correctly, application code paths exercised — see Deletion Gate in `migration_verification.md`).

## 5. Verification Blocker (must be cleared before M4 is marked fully complete)

This session has **no reachable Postgres / Docker daemon** (`docker info` → permission denied on `/var/run/docker.sock`). This means:
- `infrastructure/postgres/init_monolith.sql` has not been run against any database.
- No data has been copied from the 7 existing per-service databases into the new schemas.
- The `farms_ref` → `farm.farms` FK repoint (§4) has not been executed.
- No row-count or FK-integrity verification (MIG-M4-05) has been performed.

**This is recorded as a blocker, not silently skipped.** The next session/agent with Docker/DB access must:
1. Run `init_monolith.sql` against the `agrovision` database.
2. For each module, run its existing Alembic migrations with `version_table_schema` and `search_path` set to that module's schema (no migration file content changes needed per MD-004).
3. Copy data from each of the 7 existing databases into the matching schema (`pg_dump`/`pg_restore` with `--schema`, or `INSERT INTO ... SELECT FROM dblink`/`postgres_fdw`, depending on whether source and target can be reached from the same session).
4. Execute and verify the `farms_ref` FK repoint (§4).
5. Run row-count parity checks: `SELECT count(*) FROM <old_db>.<table>` vs `SELECT count(*) FROM agrovision.<schema>.<table>` for every table, and FK-integrity checks (`SELECT count(*) FROM poultry.batches WHERE farm_id NOT IN (SELECT id FROM farm.farms)` must be 0).
6. Record the results in `migration_verification.md`'s log before M4 is marked VERIFIED_COMPLETE.

Until then, M4's status is **IN_PROGRESS** (design + schema bootstrap + consolidated config done; data migration blocked).
