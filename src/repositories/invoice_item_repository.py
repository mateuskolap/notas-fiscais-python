from typing import Sequence

from src.dtos.invoice_dtos import InvoiceItemFilterParams
from src.entities.invoice_item_entity import InvoiceItemEntity
from src.repositories.base_repository import BaseRepository


class InvoiceItemRepository(BaseRepository[InvoiceItemEntity], model=InvoiceItemEntity):
    async def find_paginated_by_invoice(
        self,
        invoice_id: int,
        page: int = 1,
        per_page: int = 20,
        filters: InvoiceItemFilterParams | None = None,
    ) -> tuple[Sequence[InvoiceItemEntity], int]:
        query = self._base_query().where(InvoiceItemEntity.invoice_id == invoice_id)
        if filters:
            query = self._apply_filters(query, filters)
            query = self._apply_ordering(query, filters)
        return await self._paginate_query(query, page, per_page)

    def _apply_filters(self, query, filters: InvoiceItemFilterParams | None):
        if filters:
            if filters.description is not None:
                query = query.where(
                    InvoiceItemEntity.description.ilike(f'%{filters.description}%')
                )
        return query
