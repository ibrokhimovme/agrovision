"""
User domain model skeleton.
Implements SRS §5.1 (Authentication) and §5.2 (Users and Permissions).
Hybrid RBAC: user has roles (role templates) + individual permissions.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, String, ForeignKey, Table, Column, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


# Association table: users ↔ roles (many-to-many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Platform user. Belongs to a farm (or is a super-admin with no farm).
    BRD §5 — stakeholder roles: Farm Owner, Director, Manager, Vet, Accountant,
    Warehouse Manager, Sales, Worker, Inspector, Auditor.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # M5: was ForeignKey("farms_ref.id") against a denormalized local copy of
    # farm data (never kept in sync — no consumer ever populated it). M4
    # consolidated identity and farm into the same `agrovision` database and
    # repointed this FK directly at farm.farms; the farms_ref table was
    # dropped (see migration_decisions.md MD-003). The FarmRef model class
    # that used to live here was removed for the same reason.
    farm_id: Mapped[UUID | None] = mapped_column(ForeignKey("farm.farms.id"), nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=user_roles, back_populates="users", lazy="selectin"
    )
    individual_permissions: Mapped[list["IndividualPermission"]] = relationship(
        "IndividualPermission", back_populates="user", cascade="all, delete-orphan"
    )

    def has_permission(self, module: str, action: str) -> bool:
        for role in self.roles:
            if role.has_permission(module, action):
                return True
        for perm in self.individual_permissions:
            if perm.module == module and perm.action == action and perm.granted:
                return True
        return False


class Role(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Role template. Predefined roles per SRS §5.2.
    Examples: farm_owner, farm_director, farm_manager, veterinarian,
    accountant, warehouse_manager, sales_personnel, farm_worker.
    """
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles"
    )
    permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )

    def has_permission(self, module: str, action: str) -> bool:
        return any(p.module == module and p.action == action for p in self.permissions)


class RolePermission(Base, UUIDPrimaryKeyMixin):
    """Permission granted to a role template."""
    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # read|create|update|delete|approve

    role: Mapped["Role"] = relationship("Role", back_populates="permissions")


class IndividualPermission(Base, UUIDPrimaryKeyMixin):
    """
    Per-user individual permission override.
    SRS §5.2 / §5.26: hybrid RBAC — role template + individual grants.
    Effective permissions = union of all role permissions + individual grants.
    """
    __tablename__ = "individual_permissions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="individual_permissions")
