"""
Poultry Batch Domain Models — MVP
===================================
ADR-003: This service is focused on poultry batch management for MVP.
Species in scope: broiler, layer.

MVP models (active):
  Batch          — poultry flock group (partiya), managed through full lifecycle
  WeightSampling — periodic sample weight record for FCR/ADG calculation
  MortalityRecord — daily mortality count per batch

FUTURE RELEASE models (schema preserved, not activated):
  Animal         — individual bird/animal tracking (RFID, ear tags, genealogy)
                   Activated when individual traceability is required (Phase 3+)
  AnimalStatus   — individual status state machine (Phase 3+)

Domain rules (MVP):
  - All poultry is managed as batches (partiya). No per-bird tracking.
  - Batch status transitions: quarantine → active → closed. No skip.
  - Quarantine minimum: 7–14 days for poultry (BP-03).
  - Mortality is always recorded at batch level with a daily count.
  - Weight is sampled (subset of flock), not per-bird measurement.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


# ── MVP Enums ─────────────────────────────────────────────────────────────────

class PoultrySpecies(str, Enum):
    """MVP poultry species. Cattle/sheep/goat → FUTURE RELEASE (ADR-003)."""
    BROILER = "broiler"
    LAYER = "layer"


class BatchStatus(str, Enum):
    QUARANTINE = "quarantine"
    ACTIVE = "active"
    CLOSED = "closed"


class BatchCloseReason(str, Enum):
    SALE = "sale"
    SLAUGHTER = "slaughter"
    TRANSFER = "transfer"
    DISEASE = "disease"
    OTHER = "other"


# ── FUTURE RELEASE Enums (preserved, not used in MVP) ─────────────────────────

class Species(str, Enum):
    """Full species enum. CATTLE/SHEEP/GOAT deferred to Phase 3 (ADR-003)."""
    BROILER = "broiler"
    LAYER = "layer"
    CATTLE = "cattle"   # FUTURE RELEASE — ADR-003
    SHEEP = "sheep"     # FUTURE RELEASE — ADR-003
    GOAT = "goat"       # FUTURE RELEASE — ADR-003


class AnimalStatus(str, Enum):
    """Individual animal status. Not used in MVP — Animal model is Phase 3."""
    QUARANTINE = "quarantine"
    ACTIVE = "active"
    ISOLATED = "isolated"
    DECEASED = "deceased"
    SOLD = "sold"
    SLAUGHTERED = "slaughtered"


# ── MVP Domain Models ─────────────────────────────────────────────────────────

class Batch(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Poultry batch (partiya). Core MVP model.
    Manages a group of birds through their full production lifecycle.
    SRS §5.3 (SF-03), BRD §6.1 item 2. BP-01 through BP-15.

    Primary workflow: placement → [feed/water/vaccination/mortality daily] → close
    """
    __tablename__ = "batches"

    farm_id: Mapped[UUID] = mapped_column(ForeignKey("farms_ref.id"), nullable=False, index=True)
    section_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    species: Mapped[PoultrySpecies] = mapped_column(String(20), nullable=False)
    status: Mapped[BatchStatus] = mapped_column(String(20), nullable=False, default=BatchStatus.QUARANTINE)
    batch_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False)
    placement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quarantine_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    close_reason: Mapped[Optional[BatchCloseReason]] = mapped_column(String(20), nullable=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    chick_price_per_head: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    mortality_records: Mapped[list["MortalityRecord"]] = relationship(
        "MortalityRecord", back_populates="batch", cascade="all, delete-orphan"
    )
    weight_samplings: Mapped[list["WeightSampling"]] = relationship(
        "WeightSampling", back_populates="batch", cascade="all, delete-orphan"
    )

    def transition_to(self, new_status: BatchStatus) -> None:
        """Enforces valid batch state transitions. BP-03 quarantine rule."""
        VALID_TRANSITIONS = {
            BatchStatus.QUARANTINE: {BatchStatus.ACTIVE},
            BatchStatus.ACTIVE: {BatchStatus.CLOSED},
            BatchStatus.CLOSED: set(),
        }
        if new_status not in VALID_TRANSITIONS.get(self.status, set()):
            from shared.exceptions import InvalidStateTransitionError
            raise InvalidStateTransitionError("Batch", self.status.value, new_status.value)
        self.status = new_status

    @property
    def total_mortality(self) -> int:
        return sum(r.quantity for r in self.mortality_records)

    @property
    def survival_rate(self) -> Decimal:
        if self.initial_count == 0:
            return Decimal("0")
        return Decimal(str(round(self.current_count / self.initial_count * 100, 2)))


class WeightSampling(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Periodic weight sampling for a batch. MVP model (renamed from WeightRecord).
    Sampling: weigh a subset of birds, compute average. Not per-bird measurement.
    SRS §5.6 (SF-06). BRD §3.4 PG-01: FCR improvement goal.
    """
    __tablename__ = "weight_samplings"

    batch_id: Mapped[UUID] = mapped_column(ForeignKey("batches.id"), nullable=False, index=True)
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    average_weight_kg: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    total_sample_weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3), nullable=True)
    age_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    measured_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    batch: Mapped["Batch"] = relationship("Batch", back_populates="weight_samplings")


class MortalityRecord(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Daily mortality count for a batch. MVP model.
    Always batch-level — individual bird tracking is FUTURE RELEASE.
    SRS §5.18 (SF-18). BP-15: logged within 24h.
    BRD §3.4 PG-02: mortality rate reduction goal.
    """
    __tablename__ = "mortality_records"

    batch_id: Mapped[UUID] = mapped_column(ForeignKey("batches.id"), nullable=False, index=True)
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    cause_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cause_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    disposal_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    deceased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reported_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    batch: Mapped["Batch"] = relationship("Batch", back_populates="mortality_records")


class FarmRef(Base, UUIDPrimaryKeyMixin):
    """Read-only farm reference. Populated via FarmCreatedEvent consumer."""
    __tablename__ = "farms_ref"
    name: Mapped[str] = mapped_column(String(255), nullable=False)


# ── FUTURE RELEASE — Individual Animal Tracking (Phase 3, ADR-003) ────────────
#
# The Animal model below is preserved as a future-release skeleton.
# It is NOT registered with Alembic and NOT used in MVP endpoints.
# Activate when individual bird/livestock traceability is required.
#
# Deferred features:
#   - Per-animal health history
#   - RFID tag scanning
#   - Ear tag / physical tag number
#   - Genealogy and breeding records
#   - Individual weight tracking
#   - Cattle, sheep, goat management (SF-04, SF-05)
#   - Animal transfer workflows (BP-02 individual level)
#
# See ADR-003 for rationale.

class _Animal_FutureRelease(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    FUTURE RELEASE — Individual livestock animal.
    SF-04 (livestock management), SF-05 (animal registration).
    Not active in MVP. See ADR-003.
    """
    __tablename__ = "animals_future"  # separate table name avoids accidental activation

    farm_id: Mapped[UUID] = mapped_column(ForeignKey("farms_ref.id"), nullable=False, index=True)
    section_id: Mapped[UUID] = mapped_column(nullable=False)
    species: Mapped[Species] = mapped_column(String(20), nullable=False)
    status: Mapped[AnimalStatus] = mapped_column(String(20), nullable=False, default=AnimalStatus.QUARANTINE)
    tag_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    rfid_tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    breed: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    arrival_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __abstract__ = False  # set to True if you want Alembic to ignore this table
