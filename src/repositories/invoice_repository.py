from typing import Sequence

from sqlalchemy.orm import selectinload

from src.dtos.invoice_dtos import InvoiceFilterParams
from src.entities.invoice_entity import InvoiceEntity
from src.repositories.base_repository import BaseRepository


class InvoiceRepository(BaseRepository[InvoiceEntity], model=InvoiceEntity):
    def _query(self):
        return InvoiceQueryBuilder(self)

    def _base_query(self):
        return (
            super()
            ._base_query()
            .options(
                selectinload(InvoiceEntity.establishment),
            )
        )

    async def find_by_url(self, url: str) -> InvoiceEntity | None:
        return await self._query().with_items().where_url(url).first()

    async def find_by_id_with_user(self, id: int) -> InvoiceEntity | None:
        return await self._query().with_user().where_id(id).first()

    async def find_paginated_by_user(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        filters: InvoiceFilterParams | None = None,
    ) -> tuple[Sequence[InvoiceEntity], int]:
        return await (
            self
            ._query()
            .where_user(user_id)
            .apply_filters(filters)
            .paginated(page, per_page)
        )

    async def find_by_id_and_user(self, id: int, user_id: int) -> InvoiceEntity | None:
        return await self._query().where_id(id).where_user(user_id).first()

    async def find_by_id_with_user_scoped(
        self, id: int, user_id: int
    ) -> InvoiceEntity | None:
        return await self._query().with_user().where_id(id).where_user(user_id).first()

    async def find_by_url_and_user(
        self, url: str, user_id: int
    ) -> InvoiceEntity | None:
        return await (
            self._query().with_items().where_url(url).where_user(user_id).first()
        )


class InvoiceQueryBuilder:
    def __init__(self, repo: InvoiceRepository):
        self._repo = repo
        self._query = repo._base_query()

    def with_items(self):
        self._query = self._query.options(selectinload(InvoiceEntity.items))
        return self

    def with_user(self):
        self._query = self._query.options(selectinload(InvoiceEntity.user))
        return self

    def where_id(self, id: int):
        self._query = self._query.where(InvoiceEntity.id == id)
        return self

    def where_url(self, url: str):
        self._query = self._query.where(InvoiceEntity.source_url == url)
        return self

    def where_user(self, user_id: int):
        self._query = self._query.where(InvoiceEntity.user_id == user_id)
        return self

    def apply_filters(self, filters: InvoiceFilterParams | None):
        if not filters:
            return self

        if filters.establishment_id is not None:
            self._query = self._query.where(
                InvoiceEntity.establishment_id == filters.establishment_id
            )

        if filters.establishment_name is not None:
            from src.entities.establishment_entity import EstablishmentEntity

            self._query = self._query.join(InvoiceEntity.establishment).where(
                EstablishmentEntity.name.ilike(f'%{filters.establishment_name}%')
            )

        if filters.min_value is not None:
            self._query = self._query.where(
                InvoiceEntity.total_value >= filters.min_value
            )

        if filters.max_value is not None:
            self._query = self._query.where(
                InvoiceEntity.total_value <= filters.max_value
            )

        if filters.issued_from is not None:
            self._query = self._query.where(
                InvoiceEntity.issued_at >= filters.issued_from
            )

        if filters.issued_until is not None:
            self._query = self._query.where(
                InvoiceEntity.issued_at <= filters.issued_until
            )

        self._query = self._repo._apply_ordering(self._query, filters)

        return self

    async def first(self) -> InvoiceEntity | None:
        result = await self._repo.session.execute(self._query)
        return result.unique().scalar_one_or_none()

    async def paginated(self, page: int, per_page: int):
        return await self._repo._paginate_query(self._query, page, per_page)
