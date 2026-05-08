import math
from typing import Annotated, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class PaginationParams(BaseModel):
    model_config = ConfigDict(extra='forbid')

    page: Annotated[int, Query(ge=1, description='Page number')] = 1
    per_page: Annotated[int, Query(ge=1, le=100, description='Items per page')] = 20


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, per_page: int
    ) -> 'PaginatedResponse[T]':
        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )
