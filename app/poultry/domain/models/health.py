"""
Poultry Health Domain Models — MVP
=====================================
ADR-003: All health models are batch-scoped in MVP.
No per-animal health records in MVP (individual tracking is Phase 3).

MVP models (active):
  VaccinationRecord    — batch-level vaccination event
  VaccinationSchedule  — age-based schedule template per species
  MedicationRecord     — medication/treatment event at batch level (MVP simplification)
  DailyHealthLog       — simplified daily health observation replacing DiseaseIncident for MVP

FUTURE RELEASE (schema preserved, not activated in MVP):
  DiseaseIncident      — formal disease case management with isolation workflow (Phase 2)
  TreatmentRecord      — linked to DiseaseIncident, deferred with it

SRS §5.7, §5.8, §5.9. BRD §6.1 items 7, 8. BP-06, BP-07.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


# ── MVP Enums ─────────────────────────────────────────────────────────────────

class VaccinationStatus(str, Enum):
    PLANNED = "planned"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    OVERDUE = "overdue"


# ── MVP Domain Models ─────────────────────────────────────────────────────────

class VaccinationRecord(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Batch-level vaccination event. MVP model.
    Always linked to a batch — individual bird vaccination is FUTURE RELEASE.
    SRS §5.7 (SF-07). BP-07: expired vaccines blocked; 95% on-time execution.
    """
    __tablename__ = "vaccination_records"

    batch_id: Mapped[UUID] = mapped_column(ForeignKey("batches.id"), nullable=False, index=True)
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    schedule_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    vaccine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vaccine_inventory_item_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    quantity_used: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[VaccinationStatus] = mapped_column(String(20), nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    vaccinated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    performed_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class VaccinationSchedule(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Age-based vaccination schedule template per species.
    Generates planned VaccinationRecords when a batch is created.
    SRS §5.7 (SF-07).
    """
    __tablename__ = "vaccination_schedules"

    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    species: Mapped[str] = mapped_column(String(20), nullable=False)
    vaccine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    day_of_age: Mapped[int] = mapped_column(Integer, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class MedicationRecord(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Medication/treatment event applied to a batch. MVP simplification.
    In MVP, medication is recorded directly without a disease incident case.
    The health observation that triggered it is captured in `reason` field.
    SRS §5.8, §5.9 (simplified for MVP). BP-06 health monitoring.

    FUTURE RELEASE: formal DiseaseIncident case management (Phase 2) with
    isolation workflow, biosecurity measures, and treatment plan tracking.
    """
    __tablename__ = "medication_records"

    batch_id: Mapped[UUID] = mapped_column(ForeignKey("batches.id"), nullable=False, index=True)
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    medicine_inventory_item_id: Mapped[UUID] = mapped_column(nullable=False)
    quantity_used: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    dosage_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    administered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    administered_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DailyHealthLog(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Daily health observation for a batch. MVP simplified health monitoring.
    Replaces the formal DiseaseIncident case management for MVP.
    Captures: any abnormal observations, temperature readings, abnormal behavior.
    SRS §5.8 (SF-08) — simplified. BP-06: every anomaly reviewed within 24h.

    FUTURE RELEASE: DiseaseIncident + TreatmentRecord case management (Phase 2).
    """
    __tablename__ = "daily_health_logs"

    batch_id: Mapped[UUID] = mapped_column(ForeignKey("batches.id"), nullable=False, index=True)
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    observation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    has_abnormality: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    observation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_taken: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)


# ── FUTURE RELEASE — Formal Disease Case Management (Phase 2, ADR-003) ────────
#
# DiseaseIncident and TreatmentRecord implement formal case-based health
# management with isolation workflows, biosecurity measures, and treatment plans.
# Preserved as skeletons. Activate in Phase 2 when operational readiness allows.
#
# See ADR-003 for rationale.

class DiseaseSeverity(str, Enum):
    """FUTURE RELEASE — used by DiseaseIncident (Phase 2)."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class _DiseaseIncident_FutureRelease(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    FUTURE RELEASE — Formal disease case. SF-08. Phase 2.
    Not active in MVP. Use DailyHealthLog + MedicationRecord instead.
    """
    __tablename__ = "disease_incidents_future"

    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    batch_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    diagnosis: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    severity: Mapped[DiseaseSeverity] = mapped_column(String(20), nullable=False)
    symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    detected_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    veterinarian_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    biosecurity_measures: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
