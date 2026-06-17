"""Add sale_records table. SF-17, BP-12.

Revision ID: 002
Revises: 001
Create Date: 2026-06-17 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sale_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("customer_phone", sa.String(20), nullable=True),
        sa.Column("head_count", sa.Integer, nullable=False),
        sa.Column("quantity_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column("price_per_kg_uzs", sa.Numeric(15, 2), nullable=False),
        sa.Column("total_revenue_uzs", sa.Numeric(15, 2), nullable=False),
        sa.Column("payment_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_sale_records_batch_id", "sale_records", ["batch_id"])
    op.create_index("ix_sale_records_farm_id", "sale_records", ["farm_id"])


def downgrade() -> None:
    op.drop_table("sale_records")
