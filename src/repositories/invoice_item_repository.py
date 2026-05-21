from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.invoice_item_entity import InvoiceItemEntity
from src.repositories.base_repository import BaseRepository


class InvoiceItemRepository(BaseRepository[InvoiceItemEntity], model=InvoiceItemEntity):
    async def find_paginated_by_invoice(
        self, invoice_id: int, page: int = 1, per_page: int = 20
    ) -> tuple[Sequence[InvoiceItemEntity], int]:
        query = self._base_query().where(InvoiceItemEntity.invoice_id == invoice_id)
        return await self._paginate_query(query, page, per_page)
