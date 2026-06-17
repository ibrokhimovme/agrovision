"""add mortality_records table

Revision ID: 004
Revises: 003
Create Date: 2026-06-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mortality_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("cause_category", sa.String(100), nullable=True),
        sa.Column("cause_description", sa.Text, nullable=True),
        sa.Column("disposal_method", sa.String(100), nullable=True),
        sa.Column("deceased_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reported_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_mortality_records_batch_id", "mortality_records", ["batch_id"])
    op.create_index("ix_mortality_records_farm_id", "mortality_records", ["farm_id"])
    op.create_index("ix_mortality_records_deceased_at", "mortality_records", ["deceased_at"])


def downgrade() -> None:
    op.drop_index("ix_mortality_records_deceased_at", table_name="mortality_records")
    op.drop_index("ix_mortality_records_farm_id", table_name="mortality_records")
    op.drop_index("ix_mortality_records_batch_id", table_name="mortality_records")
    op.drop_table("mortality_records")
