from pydantic import BaseModel


class NFCeParseRequest(BaseModel):
    url: str


class NFCeStore(BaseModel):
    name: str


class NFCeItem(BaseModel):
    name: str
    code: str | None
    quantity: float | None
    unit: str | None
    unit_price: float | None
    total_price: float | None


class NFCeResponse(BaseModel):
    store: NFCeStore
    items: list[NFCeItem]
    total: float | None