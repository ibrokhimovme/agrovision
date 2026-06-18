from __future__ import annotations

import re

from app.poultry.application.dtos.batch_dtos import CreateBatchRequest
from app.poultry.domain.models.animal import Batch, BatchStatus
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository

_NON_ALNUM = re.compile(r"[^A-Z0-9]")


def _derive_farm_code(farm_name: str | None) -> str:
    """First word of the farm name, uppercased, alnum-only, capped at 12
    chars. Falls back to 'FARM' if the name yields nothing usable (e.g.
    farm not found, or a name with no latin/digit characters)."""
    if not farm_name:
        return "FARM"
    first_word = farm_name.strip().split(" ", 1)[0]
    code = _NON_ALNUM.sub("", first_word.upper())
    return code[:12] or "FARM"


class CreateBatchUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(self, req: CreateBatchRequest) -> Batch:
        # EX-05 (Batch Auto Naming, execution-v2): batch_code is always
        # server-generated — {FARM_CODE}-{YEAR}-{SEQ}, sequence per farm per
        # year, zero-padded to 3 digits — per decision_log.md BMD-012. No
        # client-supplied code is accepted (CreateBatchRequest has no
        # batch_code field).
        farm_name = await self._repo.get_farm_name(req.farm_id)
        farm_code = _derive_farm_code(farm_name)
        year = req.placement_date.year
        prefix = f"{farm_code}-{year}-"
        seq = await self._repo.count_batches_with_code_prefix(req.farm_id, prefix) + 1
        batch_code = f"{prefix}{seq:03d}"

        batch = Batch()
        batch.farm_id = req.farm_id
        batch.section_id = req.section_id
        batch.species = req.species
        # EX-04 (execution-v2): a new batch starts ACTIVE directly — no
        # quarantine intermediate stage (decision_log.md BMD-002/BMD-003).
        batch.status = BatchStatus.ACTIVE
        batch.batch_code = batch_code
        batch.initial_count = req.initial_count
        batch.current_count = req.initial_count
        batch.placement_date = req.placement_date
        batch.supplier_name = req.supplier_name
        batch.chick_price_per_head = req.chick_price_per_head
        batch.notes = req.notes

        return await self._repo.create(batch)
