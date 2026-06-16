from __future__ import annotations

import math
from typing import Sequence, TypeVar

from shared.contracts.api_standards import PaginatedResponse, PaginationMeta

T = TypeVar("T")


def paginate(
    items: Sequence[T],
    total_items: int,
    page: int,
    page_size: int,
) -> PaginatedResponse[T]:
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
    return PaginatedResponse(data=list(items), pagination=meta)
