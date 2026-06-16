"""Initial farm schema: farms, buildings, sections.

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
    # ── farms ─────────────────────────────────────────────────────────────────
    op.create_table(
        "farms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("farm_type", sa.String(20), nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("owner_user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )

    # ── buildings ─────────────────────────────────────────────────────────────
    op.create_table(
        "buildings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("farm_id", UUID(as_uuid=True), sa.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("capacity", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_buildings_farm_id", "buildings", ["farm_id"])

    # ── sections ──────────────────────────────────────────────────────────────
    op.create_table(
        "sections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("building_id", UUID(as_uuid=True), sa.ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("section_type", sa.String(20), nullable=False),
        sa.Column("capacity", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_sections_building_id", "sections", ["building_id"])
    op.create_index("ix_sections_farm_id", "sections", ["farm_id"])

    # ── seed data ─────────────────────────────────────────────────────────────
    op.execute(
        "INSERT INTO farms (id, name, farm_type, owner_user_id, is_active) VALUES "
        "('11111111-1111-1111-1111-111111111111', 'Test Ferma', 'poultry', "
        "'00000000-0000-0000-0000-000000000000', true)"
    )
    op.execute(
        "INSERT INTO buildings (id, farm_id, name, capacity) VALUES "
        "('22222222-2222-2222-2222-222222222222', "
        "'11111111-1111-1111-1111-111111111111', 'Bino 1', 5000)"
    )
    op.execute(
        "INSERT INTO sections (id, building_id, farm_id, name, section_type, capacity, is_active) VALUES "
        "('33333333-3333-3333-3333-333333333333', "
        "'22222222-2222-2222-2222-222222222222', "
        "'11111111-1111-1111-1111-111111111111', "
        "E'Bo''lim 1', 'production', 5000, true)"
    )


def downgrade() -> None:
    op.drop_table("sections")
    op.drop_table("buildings")
    op.drop_table("farms")
