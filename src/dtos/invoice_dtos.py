from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

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
    is_manual: bool


class InvoiceUserResponse(BaseReadDTO):
    id: int
    name: str
    email: str


class InvoiceResponse(BaseReadDTO):
    id: int
    establishment: EstablishmentResponse | None
    source_url: str | None
    total_value: Decimal
    discount_value: Decimal
    issued_at: datetime
    is_manual: bool
    is_edited_manually: bool


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


class InvoiceManualCreate(BaseModel):
    establishment_id: int | None = Field(default=None, description='Establishment ID')
    issued_at: datetime = Field(..., description='Invoice emission date')
    total_value: Decimal = Field(
        default=Decimal('0.0'),
        ge=0,
        description='Invoice total value (will be updated if items are added)',
    )


class InvoiceManualUpdate(BaseModel):
    establishment_id: int | None = Field(default=None)
    issued_at: datetime | None = Field(default=None)
    total_value: Decimal | None = Field(default=None, ge=0)


class InvoiceItemManualCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=20)
    code: str | None = Field(default=None, max_length=50)


class InvoiceItemManualUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=500)
    quantity: Decimal | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    code: str | None = Field(default=None, max_length=50)
