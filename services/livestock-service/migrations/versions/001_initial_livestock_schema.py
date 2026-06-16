"""Initial livestock schema: farms_ref, batches, weight_samplings, mortality_records.

Revision ID: 001
Revises:
Create Date: 2026-06-17 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── farms_ref ─────────────────────────────────────────────────────────────
    op.create_table(
        "farms_ref",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
    )

    # ── batches ───────────────────────────────────────────────────────────────
    op.create_table(
        "batches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("farm_id", UUID(as_uuid=True), sa.ForeignKey("farms_ref.id"), nullable=False),
        sa.Column("section_id", UUID(as_uuid=True), nullable=False),
        sa.Column("species", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="quarantine"),
        sa.Column("batch_code", sa.String(50), nullable=True),
        sa.Column("initial_count", sa.Integer, nullable=False),
        sa.Column("current_count", sa.Integer, nullable=False),
        sa.Column("placement_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quarantine_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("close_reason", sa.String(20), nullable=True),
        sa.Column("supplier_name", sa.String(255), nullable=True),
        sa.Column("chick_price_per_head", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_batches_farm_id", "batches", ["farm_id"])
    op.create_index("ix_batches_section_id", "batches", ["section_id"])
    op.create_index("ix_batches_batch_code", "batches", ["batch_code"])

    # ── weight_samplings ──────────────────────────────────────────────────────
    op.create_table(
        "weight_samplings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("sample_size", sa.Integer, nullable=False),
        sa.Column("average_weight_kg", sa.Numeric(8, 3), nullable=False),
        sa.Column("total_sample_weight_kg", sa.Numeric(12, 3), nullable=True),
        sa.Column("age_days", sa.Integer, nullable=True),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("measured_by", UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_weight_samplings_batch_id", "weight_samplings", ["batch_id"])
    op.create_index("ix_weight_samplings_farm_id", "weight_samplings", ["farm_id"])

    # ── mortality_records ─────────────────────────────────────────────────────
    op.create_table(
        "mortality_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("cause_category", sa.String(100), nullable=True),
        sa.Column("cause_description", sa.Text, nullable=True),
        sa.Column("disposal_method", sa.String(100), nullable=True),
        sa.Column("deceased_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reported_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_mortality_records_batch_id", "mortality_records", ["batch_id"])
    op.create_index("ix_mortality_records_farm_id", "mortality_records", ["farm_id"])

    # ── seed data ─────────────────────────────────────────────────────────────
    op.execute(
        "INSERT INTO farms_ref (id, name) VALUES "
        "('11111111-1111-1111-1111-111111111111', 'Test Ferma')"
    )


def downgrade() -> None:
    op.drop_table("mortality_records")
    op.drop_table("weight_samplings")
    op.drop_table("batches")
    op.drop_table("farms_ref")
