from datetime import datetime
from decimal import Decimal
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator

ALLOWED_DOMAINS = ['fazenda.pr.gov.br']


class ExtractInvoiceRequest(BaseModel):
    url: str

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)

        if parsed.scheme != 'https':
            raise ValueError('The URL must use HTTPS')

        host = parsed.hostname or ''
        if not any(host == d or host.endswith(f'.{d}') for d in ALLOWED_DOMAINS):
            raise ValueError('Unauthorized domain')

        return v


class ParsedEstablishment(BaseModel):
    name: str
    business_tin: str
    address: str


class ParsedInvoiceItem(BaseModel):
    description: str
    code: str | None
    quantity: Decimal
    unit: str
    unit_price: Decimal
    total_price: Decimal


class ParsedInvoice(BaseModel):
    establishment: ParsedEstablishment
    issued_at: datetime
    total_value: Decimal
    discount_value: Decimal
    items: list[ParsedInvoiceItem]
