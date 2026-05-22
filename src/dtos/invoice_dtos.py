from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import Query

from src.dtos.base_dtos import BaseFilterParams, BaseReadDTO


class EstablishmentResponse(BaseReadDTO):
    id: int
    name: str
    business_tin: str
    address: str | None


class InvoiceItemResponse(BaseReadDTO):
    id: int
    description: str
    code: str | None
    unit: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal


class InvoiceUserResponse(BaseReadDTO):
    id: int
    name: str
    email: str


class InvoiceResponse(BaseReadDTO):
    id: int
    establishment: EstablishmentResponse
    source_url: str
    total_value: Decimal
    discount_value: Decimal
    issued_at: datetime


class InvoiceDetailResponse(InvoiceResponse):
    user: InvoiceUserResponse


class InvoiceFilterParams(BaseFilterParams):
    establishment_id: Annotated[
        int | None, Query(description='Filter by establishment ID')
    ] = None
    establishment_name: Annotated[
        str | None, Query(description='Partial match on establishment name')
    ] = None
    min_value: Annotated[
        Decimal | None, Query(ge=0, description='Minimum total value')
    ] = None
    max_value: Annotated[
        Decimal | None, Query(ge=0, description='Maximum total value')
    ] = None
    issued_from: Annotated[
        date | None, Query(description='Issued on or after this date')
    ] = None
    issued_until: Annotated[
        date | None, Query(description='Issued on or before this date')
    ] = None

    order_by: Annotated[
        Literal['id', 'issued_at', 'total_value', 'created_at'] | None, Query()
    ] = 'issued_at'


class InvoiceItemFilterParams(BaseFilterParams):
    description: Annotated[
        str | None, Query(description='Partial match on item description')
    ] = None

    order_by: Annotated[
        Literal['id', 'description', 'quantity', 'total_price'] | None, Query()
    ] = 'id'
