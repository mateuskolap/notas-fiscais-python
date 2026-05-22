from datetime import datetime
from decimal import Decimal

from src.dtos.base_dtos import BaseReadDTO


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
