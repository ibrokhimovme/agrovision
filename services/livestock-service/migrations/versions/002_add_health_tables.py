"""Add vaccination and health tables: vaccination_records, vaccination_schedules, medication_records, daily_health_logs.

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
    # ── vaccination_schedules ─────────────────────────────────────────────────
    op.create_table(
        "vaccination_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("species", sa.String(20), nullable=False),
        sa.Column("vaccine_name", sa.String(255), nullable=False),
        sa.Column("day_of_age", sa.Integer, nullable=False),
        sa.Column("is_mandatory", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_vaccination_schedules_farm_id", "vaccination_schedules", ["farm_id"])
    op.create_index("ix_vaccination_schedules_species", "vaccination_schedules", ["species"])

    # ── vaccination_records ───────────────────────────────────────────────────
    op.create_table(
        "vaccination_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("schedule_id", UUID(as_uuid=True), nullable=True),
        sa.Column("vaccine_name", sa.String(255), nullable=False),
        sa.Column("vaccine_inventory_item_id", UUID(as_uuid=True), nullable=False),
        sa.Column("quantity_used", sa.Numeric(10, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vaccinated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("performed_by", UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_vaccination_records_batch_id", "vaccination_records", ["batch_id"])
    op.create_index("ix_vaccination_records_farm_id", "vaccination_records", ["farm_id"])

    # ── medication_records ────────────────────────────────────────────────────
    op.create_table(
        "medication_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("medicine_name", sa.String(255), nullable=False),
        sa.Column("medicine_inventory_item_id", UUID(as_uuid=True), nullable=False),
        sa.Column("quantity_used", sa.Numeric(10, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("dosage_notes", sa.Text, nullable=True),
        sa.Column("administered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("administered_by", UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_medication_records_batch_id", "medication_records", ["batch_id"])
    op.create_index("ix_medication_records_farm_id", "medication_records", ["farm_id"])

    # ── daily_health_logs ─────────────────────────────────────────────────────
    op.create_table(
        "daily_health_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("observation_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("has_abnormality", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("observation_notes", sa.Text, nullable=True),
        sa.Column("action_taken", sa.Text, nullable=True),
        sa.Column("recorded_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_daily_health_logs_batch_id", "daily_health_logs", ["batch_id"])
    op.create_index("ix_daily_health_logs_farm_id", "daily_health_logs", ["farm_id"])


def downgrade() -> None:
    op.drop_table("daily_health_logs")
    op.drop_table("medication_records")
    op.drop_table("vaccination_records")
    op.drop_table("vaccination_schedules")
