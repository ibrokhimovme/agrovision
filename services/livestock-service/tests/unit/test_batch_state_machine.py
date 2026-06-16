"""
Unit tests for the Batch state machine (transition_to).
Tests domain logic only — no DB, no HTTP.
"""
from __future__ import annotations

import pytest

from app.domain.models.animal import Batch, BatchStatus, PoultrySpecies
from shared.exceptions import InvalidStateTransitionError


def _make_batch(status: BatchStatus) -> Batch:
    b = Batch()
    b.status = status
    b.mortality_records = []
    b.weight_samplings = []
    b.initial_count = 1000
    b.current_count = 1000
    return b


def test_quarantine_to_active_ok():
    batch = _make_batch(BatchStatus.QUARANTINE)
    batch.transition_to(BatchStatus.ACTIVE)
    assert batch.status == BatchStatus.ACTIVE


def test_active_to_closed_ok():
    batch = _make_batch(BatchStatus.ACTIVE)
    batch.transition_to(BatchStatus.CLOSED)
    assert batch.status == BatchStatus.CLOSED


def test_quarantine_to_closed_raises():
    batch = _make_batch(BatchStatus.QUARANTINE)
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        batch.transition_to(BatchStatus.CLOSED)
    assert "quarantine" in exc_info.value.message
    assert "closed" in exc_info.value.message


def test_closed_to_active_raises():
    batch = _make_batch(BatchStatus.CLOSED)
    with pytest.raises(InvalidStateTransitionError):
        batch.transition_to(BatchStatus.ACTIVE)


def test_active_to_quarantine_raises():
    batch = _make_batch(BatchStatus.ACTIVE)
    with pytest.raises(InvalidStateTransitionError):
        batch.transition_to(BatchStatus.QUARANTINE)
