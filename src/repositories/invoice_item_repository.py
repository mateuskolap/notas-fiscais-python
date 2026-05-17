from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.invoice_item_entity import InvoiceItemEntity
from src.repositories.base_repository import BaseRepository


class InvoiceItemRepository(BaseRepository[InvoiceItemEntity]):
    def __init__(self, session: AsyncSession):
        super().__init__(InvoiceItemEntity, session)

    async def create_bulk(
        self, items: list[InvoiceItemEntity]
    ) -> list[InvoiceItemEntity]:
        self.session.add_all(items)
        await self.session.commit()
        for item in items:
            await self.session.refresh(item)
        return items

    async def find_paginated_by_invoice(
        self, invoice_id: int, page: int = 1, per_page: int = 20
    ) -> tuple[Sequence[InvoiceItemEntity], int]:
        query = self._base_query().where(InvoiceItemEntity.invoice_id == invoice_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        offset = (page - 1) * per_page
        items = (
            (await self.session.execute(query.offset(offset).limit(per_page)))
            .scalars()
            .unique()
            .all()
        )

        return items, total
