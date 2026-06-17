"""Add feed_consumptions table.

Revision ID: 003
Revises: 002
Create Date: 2026-06-17 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feed_consumptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("feed_date", sa.Date, nullable=False),
        sa.Column("feed_type", sa.String(50), nullable=True),
        sa.Column("quantity_kg", sa.Numeric(10, 3), nullable=False),
        sa.Column("water_liters", sa.Numeric(10, 3), nullable=True),
        sa.Column("age_days", sa.Integer, nullable=True),
        sa.Column("feed_inventory_item_id", UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_feed_consumptions_batch_id", "feed_consumptions", ["batch_id"])
    op.create_index("ix_feed_consumptions_farm_id", "feed_consumptions", ["farm_id"])
    op.create_index("ix_feed_consumptions_feed_date", "feed_consumptions", ["feed_date"])


def downgrade() -> None:
    op.drop_table("feed_consumptions")
