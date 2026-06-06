import logging
from decimal import Decimal

from src.actions.base_actions import BaseActions
from src.dtos.product_dtos import (
    CanonicalProductResponse,
    MarketPriceResponse,
    PriceComparisonResponse,
    PriceHistoryResponse,
    PricePointResponse,
    ProductSearchParams,
    ProductSearchResultResponse,
)
from src.entities.canonical_product_entity import CanonicalProductEntity
from src.exceptions.base_exceptions import NotFoundException
from src.repositories.canonical_product_repository import CanonicalProductRepository

logger = logging.getLogger(__name__)


class ProductSearchActions(BaseActions[CanonicalProductEntity]):
    def __init__(self, repository: CanonicalProductRepository):
        super().__init__(repository, entity_name='CanonicalProduct')

    async def search_products(
        self, user_id: int, params: ProductSearchParams
    ) -> list[ProductSearchResultResponse]:
        rows = await self.repository.search_normalized_products(
            user_id, params.query, params.brand
        )

        return [
            ProductSearchResultResponse(
                product=CanonicalProductResponse(
                    id=row.id,
                    normalized_name=row.name,
                    brand=row.brand,
                    quantity_label=row.quantity_label,
                    variant=row.variant,
                ),
                avg_price=Decimal(str(row.avg_price)),
                min_price=Decimal(str(row.min_price)),
                max_price=Decimal(str(row.max_price)),
                market_count=row.market_count,
            )
            for row in rows
        ]

    async def get_price_comparison(
        self, user_id: int, canonical_product_id: int
    ) -> PriceComparisonResponse:
        product_row = await self.repository.get_product_with_override(
            user_id, canonical_product_id
        )

        if not product_row:
            raise NotFoundException('Product not found')

        canonical, override = product_row

        name = (
            override.custom_name
            if override and override.custom_name
            else canonical.normalized_name
        )
        brand = (
            override.custom_brand
            if override and override.custom_brand
            else canonical.brand
        )

        rows = await self.repository.get_price_comparison_by_market(
            user_id, canonical_product_id
        )

        return PriceComparisonResponse(
            product=CanonicalProductResponse(
                id=canonical.id,
                normalized_name=name,
                brand=brand,
                quantity_label=canonical.quantity_label,
                variant=canonical.variant,
            ),
            markets=[
                MarketPriceResponse(
                    market_name=row.market_name,
                    latest_price=Decimal(str(row.unit_price)),
                    latest_date=row.issued_at.date(),
                )
                for row in rows
            ],
        )

    async def get_price_history(
        self, user_id: int, canonical_product_id: int
    ) -> PriceHistoryResponse:
        product_row = await self.repository.get_product_with_override(
            user_id, canonical_product_id
        )

        if not product_row:
            raise NotFoundException('Product not found')

        canonical, override = product_row
        name = (
            override.custom_name
            if override and override.custom_name
            else canonical.normalized_name
        )
        brand = (
            override.custom_brand
            if override and override.custom_brand
            else canonical.brand
        )

        rows = await self.repository.get_price_history(user_id, canonical_product_id)

        return PriceHistoryResponse(
            product=CanonicalProductResponse(
                id=canonical.id,
                normalized_name=name,
                brand=brand,
                quantity_label=canonical.quantity_label,
                variant=canonical.variant,
            ),
            history=[
                PricePointResponse(
                    date=row.issued_at.date(),
                    price=Decimal(str(row.unit_price)),
                    market_name=row.market_name,
                )
                for row in rows
            ],
        )
