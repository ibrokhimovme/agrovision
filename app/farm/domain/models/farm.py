"""
Farm domain models: farms, buildings, sections.
SRS §5.3 (Farm management). SF-02: farm management feature.
BRD §6.1 items 1, 3. SG-02: multi-farm management.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


class FarmType(str, Enum):
    POULTRY = "poultry"
    LIVESTOCK = "livestock"
    DAIRY = "dairy"
    MIXED = "mixed"


class SectionType(str, Enum):
    # EX-03 (Building & Section Simplification, execution-v2): QUARANTINE
    # removed per decision_log.md BMD-002 — quarantine workflows are removed
    # entirely, both as a batch status (EX-04) and as this place/type
    # concept. ISOLATION is explicitly retained (a narrower, distinct
    # sick-bird-isolation concept, not the mandatory new-arrival holding
    # period BMD-002 removed).
    PRODUCTION = "production"
    ISOLATION = "isolation"
    STORAGE = "storage"


class Farm(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    A farm entity. Top-level organizational unit.
    SG-02: system must support ≥5 farms and ≥10 warehouses.
    """
    __tablename__ = "farms"
    # M8 bug fix: identity.users.farm_id and poultry.batches.farm_id reference
    # this table cross-schema via ForeignKey("farm.farms.id") (MD-003). Without
    # this explicit schema, SQLAlchemy registers this Table under metadata key
    # "farms" (no prefix), so "farm.farms" never resolves — works fine for
    # read-only SELECTs (Postgres search_path handles those at the SQL level)
    # but raises NoReferencedTableError the moment any INSERT needs Python-side
    # FK dependency ordering. Found via M8 UAT testing (TC-04 batch creation).
    __table_args__ = {"schema": "farm"}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    farm_type: Mapped[FarmType] = mapped_column(String(20), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_user_id: Mapped[UUID] = mapped_column(nullable=False)
    # EX-01 (Account Foundation, execution-v2): Farm now belongs to an
    # Account (Account -> Farm -> Building -> Batch priority chain, per
    # decision_log.md BMD-001). Nullable for now and left alongside
    # owner_user_id rather than replacing it — backfilled for all existing
    # farms by infrastructure/postgres/migrations_v2/001_ex01_account_foundation.sql,
    # but making it NOT NULL and wiring it into create/update use cases is
    # EX-02 scope, not this phase's.
    account_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("identity.accounts.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    buildings: Mapped[list["Building"]] = relationship(
        "Building", back_populates="farm", cascade="all, delete-orphan"
    )


class Building(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Physical building within a farm.
    Examples: Poultry House 1, Feed Storage Building.
    """
    __tablename__ = "buildings"
    __table_args__ = {"schema": "farm"}

    farm_id: Mapped[UUID] = mapped_column(
        ForeignKey("farm.farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    farm: Mapped["Farm"] = relationship("Farm", back_populates="buildings")
    sections: Mapped[list["Section"]] = relationship(
        "Section", back_populates="building", cascade="all, delete-orphan"
    )


class Section(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Section within a building. Sections hold batches.
    """
    __tablename__ = "sections"
    __table_args__ = {"schema": "farm"}

    building_id: Mapped[UUID] = mapped_column(
        ForeignKey("farm.buildings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    section_type: Mapped[SectionType] = mapped_column(String(20), nullable=False)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    building: Mapped["Building"] = relationship("Building", back_populates="sections")
