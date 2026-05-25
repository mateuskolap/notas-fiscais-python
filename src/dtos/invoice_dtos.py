from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

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
    establishment_id: int | None = None
    establishment_name: str | None = None
    min_value: Decimal | None = Field(default=None, ge=0)
    max_value: Decimal | None = Field(default=None, ge=0)
    issued_from: date | None = None
    issued_until: date | None = None
    order_by: Literal['id', 'issued_at', 'total_value', 'created_at'] | None = (
        'issued_at'
    )


class InvoiceItemFilterParams(BaseFilterParams):
    description: str | None = None
    order_by: Literal['id', 'description', 'quantity', 'total_price'] | None = 'id'
