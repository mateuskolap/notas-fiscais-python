from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.dtos.base_dtos import BaseFilterParams, BaseReadDTO, BaseWriteDTO


class EstablishmentBase(BaseModel):
    name: str = Field(..., max_length=255)
    business_tin: str | None = Field(default=None, max_length=20)
    address: str | None = None


class EstablishmentCreate(EstablishmentBase, BaseWriteDTO):
    pass


class EstablishmentUpdate(BaseWriteDTO):
    name: str | None = Field(None, max_length=255)
    business_tin: str | None = Field(None, max_length=20)
    address: str | None = None


class EstablishmentRead(EstablishmentBase, BaseReadDTO):
    id: int
    created_at: datetime
    updated_at: datetime
    is_manual: bool


class EstablishmentFilterParams(BaseFilterParams):
    name: str | None = None
    business_tin: str | None = None
    related_only: bool = False
    user_id: int | None = None
    order_by: Literal['id', 'name', 'business_tin', 'created_at'] | None = 'id'
