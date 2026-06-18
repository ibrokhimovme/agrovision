-- AgroVision — Monolith schema bootstrap (M4, Database Consolidation)
-- ADDITIVE ONLY: does not modify infrastructure/postgres/init.sql or any of the
-- 7 per-microservice databases it creates. This script targets the single
-- `agrovision` database (POSTGRES_DB in .env) and creates one schema per
-- monolith module, per migration_decisions.md MD-004.
--
-- Run manually against the `agrovision` database once a reachable Postgres
-- instance exists (see db_consolidation_design.md §5 for the verification
-- blocker recorded for this phase). NOT wired into any docker-entrypoint
-- init flow yet — that is M6 (Runtime Simplification) scope.

CREATE SCHEMA IF NOT EXISTS identity;
CREATE SCHEMA IF NOT EXISTS farm;
CREATE SCHEMA IF NOT EXISTS poultry;
CREATE SCHEMA IF NOT EXISTS inventory;
CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS notifications;
-- No schema for `gateway` or `reporting` — neither owns any tables (see
-- current_state_architecture_report.md §1/§4).

GRANT ALL ON SCHEMA identity TO agrovision;
GRANT ALL ON SCHEMA farm TO agrovision;
GRANT ALL ON SCHEMA poultry TO agrovision;
GRANT ALL ON SCHEMA inventory TO agrovision;
GRANT ALL ON SCHEMA finance TO agrovision;
GRANT ALL ON SCHEMA notifications TO agrovision;
