import math

from pydantic import BaseModel, ConfigDict, Field


class PaginationParams(BaseModel):
    model_config = ConfigDict(extra='forbid')

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PaginatedResponse[T](BaseModel):
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
