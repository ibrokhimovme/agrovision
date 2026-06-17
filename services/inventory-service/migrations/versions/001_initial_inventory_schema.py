"""Initial inventory schema: warehouses, stock_items, stock_batches, stock_movements.

Revision ID: 001
Revises:
Create Date: 2026-06-17 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── warehouses ────────────────────────────────────────────────────────────
    op.create_table(
        "warehouses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_warehouses_farm_id", "warehouses", ["farm_id"])

    # ── stock_items ───────────────────────────────────────────────────────────
    op.create_table(
        "stock_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("warehouse_id", UUID(as_uuid=True), sa.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("item_type", sa.String(20), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("current_quantity", sa.Numeric(15, 4), nullable=False, server_default="0"),
        sa.Column("minimum_quantity", sa.Numeric(15, 4), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.Numeric(15, 2), nullable=True),
        sa.Column("sku", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_stock_items_warehouse_id", "stock_items", ["warehouse_id"])
    op.create_index("ix_stock_items_item_type", "stock_items", ["item_type"])

    # ── stock_batches ─────────────────────────────────────────────────────────
    op.create_table(
        "stock_batches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("stock_item_id", UUID(as_uuid=True), sa.ForeignKey("stock_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("batch_number", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("remaining_quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(15, 2), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supplier_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_stock_batches_stock_item_id", "stock_batches", ["stock_item_id"])
    op.create_index("ix_stock_batches_expiry_date", "stock_batches", ["expiry_date"])

    # ── stock_movements ───────────────────────────────────────────────────────
    op.create_table(
        "stock_movements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("stock_item_id", UUID(as_uuid=True), sa.ForeignKey("stock_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("warehouse_id", UUID(as_uuid=True), nullable=False),
        sa.Column("movement_type", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("unit_cost", sa.Numeric(15, 2), nullable=True),
        sa.Column("purpose", sa.String(100), nullable=True),
        sa.Column("reference_id", UUID(as_uuid=True), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("moved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_stock_movements_stock_item_id", "stock_movements", ["stock_item_id"])
    op.create_index("ix_stock_movements_warehouse_id", "stock_movements", ["warehouse_id"])
    op.create_index("ix_stock_movements_moved_at", "stock_movements", ["moved_at"])


def downgrade() -> None:
    op.drop_table("stock_movements")
    op.drop_table("stock_batches")
    op.drop_table("stock_items")
    op.drop_table("warehouses")
