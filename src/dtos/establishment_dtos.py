from datetime import datetime
from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, Field

from src.dtos.base_dtos import BaseFilterParams, BaseReadDTO, BaseWriteDTO


class EstablishmentBase(BaseModel):
    name: str = Field(..., max_length=255)
    business_tin: str = Field(
        ..., max_length=20, description='CNPJ of the establishment'
    )
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


class EstablishmentFilterParams(BaseFilterParams):
    name: Annotated[
        str | None, Query(description='Partial match on establishment name')
    ] = None
    business_tin: Annotated[
        str | None, Query(description='Exact or partial match on CNPJ')
    ] = None
    related_only: Annotated[
        bool,
        Query(
            description='If true, return only establishments with invoices related to the current user'
        ),
    ] = False

    user_id: int | None = None

    order_by: Annotated[
        Literal['id', 'name', 'business_tin', 'created_at'] | None, Query()
    ] = 'id'
