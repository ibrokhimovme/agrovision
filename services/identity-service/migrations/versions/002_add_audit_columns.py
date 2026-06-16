"""Add created_by and updated_by audit columns to users and roles

Revision ID: 002
Revises: 001
Create Date: 2026-06-17

AuditMixin in shared/models/base.py defines created_by and updated_by but
migration 001 omitted them. This migration adds the missing columns.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ('roles', 'users'):
        op.add_column(table, sa.Column(
            'created_by',
            UUID(as_uuid=True),
            nullable=True,
        ))
        op.add_column(table, sa.Column(
            'updated_by',
            UUID(as_uuid=True),
            nullable=True,
        ))


def downgrade() -> None:
    for table in ('roles', 'users'):
        op.drop_column(table, 'updated_by')
        op.drop_column(table, 'created_by')
