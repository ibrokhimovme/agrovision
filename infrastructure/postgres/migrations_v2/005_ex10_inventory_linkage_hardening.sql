-- AgroVision — execution-v2 / EX-10 (Inventory Linkage Hardening)
-- Adds real FK constraints for the three bare-UUID references identified
-- in the Business Revision Report §11 footnote, per
-- .project-governance/execution-v2/decision_log.md BMD-014:
--   inventory.warehouses.farm_id          -> farm.farms.id
--   inventory.stock_movements.warehouse_id -> inventory.warehouses.id
--   poultry.feed_consumptions.feed_inventory_item_id -> inventory.stock_items.id
--
-- Pre-verified before writing this script (2026-06-18), live `agrovision`
-- database: zero orphaned rows across all three (warehouses with no
-- matching farm, stock_movements with no matching warehouse, and
-- feed_consumptions with a non-null feed_inventory_item_id with no
-- matching stock item) — safe to add the constraints directly, no cleanup
-- pass needed first.
--
-- Run manually against the `agrovision` database:
--   docker exec -i agrovision-postgres-1 psql -U agrovision -d agrovision \
--     < infrastructure/postgres/migrations_v2/005_ex10_inventory_linkage_hardening.sql
--
-- Idempotent: safe to run more than once.

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_warehouses_farm_id'
    ) THEN
        ALTER TABLE inventory.warehouses
            ADD CONSTRAINT fk_warehouses_farm_id FOREIGN KEY (farm_id) REFERENCES farm.farms(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_stock_movements_warehouse_id'
    ) THEN
        ALTER TABLE inventory.stock_movements
            ADD CONSTRAINT fk_stock_movements_warehouse_id FOREIGN KEY (warehouse_id) REFERENCES inventory.warehouses(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_feed_consumptions_feed_inventory_item_id'
    ) THEN
        ALTER TABLE poultry.feed_consumptions
            ADD CONSTRAINT fk_feed_consumptions_feed_inventory_item_id FOREIGN KEY (feed_inventory_item_id) REFERENCES inventory.stock_items(id);
    END IF;
END $$;

COMMIT;

-- Verification queries (run manually after applying):
--   \d inventory.warehouses        -- expect fk_warehouses_farm_id listed
--   \d inventory.stock_movements   -- expect fk_stock_movements_warehouse_id listed
--   \d poultry.feed_consumptions   -- expect fk_feed_consumptions_feed_inventory_item_id listed
