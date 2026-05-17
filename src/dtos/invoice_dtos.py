from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EstablishmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    business_tin: str
    address: str | None


class InvoiceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    description: str
    code: str | None
    unit: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal


class InvoiceUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class InvoiceListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    establishment: EstablishmentResponse
    source_url: str
    total_value: Decimal
    discount_value: Decimal
    issued_at: datetime


class InvoiceDetailResponse(InvoiceListResponse):
    user: InvoiceUserResponse


class InvoiceResponse(InvoiceListResponse):
    items: list[InvoiceItemResponse]
