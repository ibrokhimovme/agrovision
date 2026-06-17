"""
Building sub-resource endpoints: sections. SRS §5.3, SF-02.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.farm_dtos import CreateSectionRequest, SectionResponse
from app.application.use_cases.list_sections import ListSectionsUseCase
from app.application.use_cases.create_section import CreateSectionUseCase
from app.infrastructure.database.repositories.farm_repository_impl import SQLAlchemyFarmRepository
from app.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/{building_id}/sections", response_model=APIResponse[list[SectionResponse]])
async def list_sections(
    building_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyFarmRepository(db)
    use_case = ListSectionsUseCase(repo)
    sections = await use_case.execute(building_id)
    return APIResponse(data=[SectionResponse.model_validate(s) for s in sections])


@router.post("/{building_id}/sections", response_model=APIResponse[SectionResponse], status_code=201)
async def create_section(
    building_id: UUID,
    body: CreateSectionRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyFarmRepository(db)
    use_case = CreateSectionUseCase(repo)
    section = await use_case.execute(building_id, body)
    return APIResponse(data=SectionResponse.model_validate(section))
