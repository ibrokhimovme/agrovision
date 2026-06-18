"""
Poultry Batch Domain Models
=============================
ADR-003: This service is focused on poultry batch management.
Species in scope: broiler, layer.

Models:
  Batch          — poultry flock group (partiya), managed through full lifecycle
  WeightSampling — periodic sample weight record for FCR/ADG calculation
  MortalityRecord — daily mortality count per batch

Domain rules:
  - All poultry is managed as batches (partiya). No per-bird tracking.
  - Batch status: active → completed. No skip, no reopening.
  - Mortality is always recorded at batch level with a daily count.
  - Weight is sampled (subset of flock), not per-bird measurement.

EX-04 (Batch Lifecycle Simplification, execution-v2): quarantine, slaughter,
RFID, and individual-bird tracking were removed entirely — not deferred to
a future release — per decision_log.md BMD-002/BMD-003/BMD-004. The
previously-preserved FUTURE RELEASE `_Animal_FutureRelease`/`AnimalStatus`/
`Species` (multi-species) skeletons were deleted along with them: ADR-003's
original assumption that individual-animal tracking might be activated in a
later phase is explicitly overridden by BMD-004, not merely left dormant.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


# ── Enums ─────────────────────────────────────────────────────────────────────

class PoultrySpecies(str, Enum):
    """Poultry species. Cattle/sheep/goat permanently out of scope (BMD-004)."""
    BROILER = "broiler"
    LAYER = "layer"


class BatchStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class BatchCloseReason(str, Enum):
    SALE = "sale"
    TRANSFER = "transfer"
    DISEASE = "disease"
    OTHER = "other"


# ── Domain Models ───────────────────────────────────────────────────────────

class Batch(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Poultry batch (partiya).
    Manages a group of birds through their full production lifecycle.
    SRS §5.3 (SF-03), BRD §6.1 item 2.

    Primary workflow: placement (ACTIVE) → [feed/mortality/weight daily] → close (COMPLETED)
    """
    __tablename__ = "batches"

    # M5: was ForeignKey("farms_ref.id") — see app/identity/domain/models/user.py
    # for the identical MD-003 rationale. Repointed at farm.farms directly.
    farm_id: Mapped[UUID] = mapped_column(ForeignKey("farm.farms.id"), nullable=False, index=True)
    section_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    species: Mapped[PoultrySpecies] = mapped_column(String(20), nullable=False)
    status: Mapped[BatchStatus] = mapped_column(String(20), nullable=False, default=BatchStatus.ACTIVE)
    # EX-05 (Batch Auto Naming, execution-v2): batch_code is mandatory and
    # always server-generated (farm-prefixed sequential convention, decided
    # with the business owner — see decision_log.md BMD-012). Uniqueness is
    # enforced per-farm at the database level (migration 004), not just here.
    batch_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False)
    placement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    close_reason: Mapped[Optional[BatchCloseReason]] = mapped_column(String(20), nullable=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    chick_price_per_head: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # EX-16 (Archive System, execution-v2): additive-only, never a deletion
    # path (decision_log.md BMD-007/BMD-018). status stays COMPLETED when
    # archived — this is an orthogonal visibility flag, not a new status.
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    mortality_records: Mapped[list["MortalityRecord"]] = relationship(
        "MortalityRecord", back_populates="batch", cascade="all, delete-orphan"
    )
    weight_samplings: Mapped[list["WeightSampling"]] = relationship(
        "WeightSampling", back_populates="batch", cascade="all, delete-orphan"
    )

    def transition_to(self, new_status: BatchStatus) -> None:
        """Enforces valid batch state transitions (EX-04: ACTIVE -> COMPLETED only)."""
        VALID_TRANSITIONS = {
            BatchStatus.ACTIVE: {BatchStatus.COMPLETED},
            BatchStatus.COMPLETED: set(),
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

    def archive(self, archived_by: UUID) -> None:
        """EX-16 (execution-v2): manual-only archiving, restricted to COMPLETED
        batches per the archive policy (decision_log.md BMD-018)."""
        from shared.exceptions import BusinessRuleViolationError
        if self.status != BatchStatus.COMPLETED:
            raise BusinessRuleViolationError(
                "BATCH_ARCHIVE_REQUIRES_COMPLETED",
                "Only a COMPLETED batch can be archived.",
            )
        if self.is_archived:
            raise BusinessRuleViolationError(
                "BATCH_ALREADY_ARCHIVED",
                "This batch is already archived.",
            )
        self.is_archived = True
        self.archived_at = datetime.now(timezone.utc)
        self.archived_by = archived_by

    def unarchive(self) -> None:
        from shared.exceptions import BusinessRuleViolationError
        if not self.is_archived:
            raise BusinessRuleViolationError(
                "BATCH_NOT_ARCHIVED",
                "This batch is not archived.",
            )
        self.is_archived = False
        self.archived_at = None
        self.archived_by = None


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

# EX-04 (execution-v2): the former "FUTURE RELEASE — Individual Animal
# Tracking" skeleton (_Animal_FutureRelease, AnimalStatus, Species,
# RFID/tag-number fields) was removed entirely per decision_log.md BMD-004
# — permanently out of scope, not deferred. It was never Alembic-registered
# or used by any live endpoint (table "animals_future" was never created in
# any database), so removing it has no data-migration implication.
