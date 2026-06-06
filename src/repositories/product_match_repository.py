from typing import Sequence

from sqlalchemy import select

from src.entities.invoice_item_entity import InvoiceItemEntity
from src.entities.product_match_entity import ProductMatchEntity
from src.repositories.base_repository import BaseRepository


class ProductMatchRepository(
    BaseRepository[ProductMatchEntity], model=ProductMatchEntity
):
    async def find_by_invoice_item_id(self, item_id: int) -> ProductMatchEntity | None:
        return await self.find_one_by(invoice_item_id=item_id)

    async def find_unmatched_items(
        self, limit: int = 50
    ) -> Sequence[InvoiceItemEntity]:
        query = (
            select(InvoiceItemEntity)
            .outerjoin(
                ProductMatchEntity,
                InvoiceItemEntity.id == ProductMatchEntity.invoice_item_id,
            )
            .where(ProductMatchEntity.id.is_(None))
            .where(InvoiceItemEntity.is_manual.is_(False))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()
