"""
Account domain model.

Introduced by the Business Model Revision (execution-v2, EX-01 — Account
Foundation). Account is the new top-level ownership entity in the priority
chain: Account -> Farm -> Building -> Batch.
See .project-governance/execution-v2/decision_log.md BMD-001.

Schema is explicitly declared (unlike the other identity models) because
Farm (schema "farm") needs to reference this table cross-schema via
ForeignKey("identity.accounts.id") — without an explicit schema here, that
FK string would not resolve in SQLAlchemy's metadata, the same class of bug
recorded in migration_decisions.md / project_state.md CL-030 (M8) for
farm.farms.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


class Account(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Top-level ownership entity. One Account may own multiple Farms.
    owner_user_id identifies the user who administers this account.
    """
    __tablename__ = "accounts"
    __table_args__ = {"schema": "identity"}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Bare "users.id" (not "identity.users.id"): the User model does not
    # declare an explicit schema, so its metadata key is the unqualified
    # "users" — matching that exactly, per the same lesson as the docstring
    # above.
    owner_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
