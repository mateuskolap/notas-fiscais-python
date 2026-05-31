from pydantic import ConfigDict

from src.dtos.base_dtos import BaseReadDTO, BaseWriteDTO


class CategoryResponse(BaseReadDTO):
    id: int
    name: str
    slug: str
    parent_id: int | None = None
    is_global: bool = True
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class CategoryCreateRequest(BaseWriteDTO):
    name: str
    parent_id: int | None = None


class CategoryUpdateRequest(BaseWriteDTO):
    name: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None
