from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from src.dtos.base_dtos import BaseFilterParams, BaseReadDTO, BaseWriteDTO


class NormalizedProductResult(BaseModel):
    index: int
    normalized_name: str
    brand: str | None = None
    quantity_label: str | None = None
    variant: str | None = None
    unit_of_measure: str | None = None
    measure_value: Decimal | None = None
    category_slug: str | None = None
    confidence: Decimal


class CanonicalProductResponse(BaseReadDTO):
    id: int
    normalized_name: str
    brand: str | None
    quantity_label: str | None
    variant: str | None


class ProductSearchResultResponse(BaseReadDTO):
    product: CanonicalProductResponse
    avg_price: Decimal
    min_price: Decimal
    max_price: Decimal
    market_count: int


class MarketPriceResponse(BaseModel):
    market_name: str
    latest_price: Decimal
    latest_date: date


class PriceComparisonResponse(BaseReadDTO):
    product: CanonicalProductResponse
    markets: list[MarketPriceResponse]


class PricePointResponse(BaseModel):
    date: date
    price: Decimal
    market_name: str


class PriceHistoryResponse(BaseReadDTO):
    product: CanonicalProductResponse
    history: list[PricePointResponse]


class BasketMarketResponse(BaseModel):
    market_name: str
    total_price: Decimal
    available_items_count: int


class BasketComparisonResponse(BaseReadDTO):
    markets: list[BasketMarketResponse]


class ProductSearchParams(BaseFilterParams):
    query: str
    category_slug: str | None = None
    brand: str | None = None


class ProductOverrideRequest(BaseWriteDTO):
    custom_name: str | None = None
    custom_brand: str | None = None
    custom_category_id: int | None = None


class BasketComparisonRequest(BaseWriteDTO):
    product_ids: list[int]


class CheapestProductByMarketItem(BaseModel):
    establishment_id: int
    establishment_name: str
    product_id: int
    product_name: str
    product_brand: str | None
    min_price: Decimal
    purchase_date: date


class CheapestProductByMarketResponse(BaseReadDTO):
    items: list[CheapestProductByMarketItem]
    total: int
    page: int
    size: int
