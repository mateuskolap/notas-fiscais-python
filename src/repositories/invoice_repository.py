from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.entities.invoice_entity import InvoiceEntity
from src.repositories.base_repository import BaseRepository


class InvoiceRepository(BaseRepository[InvoiceEntity]):
    def __init__(self, session: AsyncSession):
        super().__init__(InvoiceEntity, session)

    def _base_query(self):
        return (
            super()
            ._base_query()
            .options(
                selectinload(InvoiceEntity.establishment),
            )
        )

    async def find_by_url(self, url: str) -> InvoiceEntity | None:
        result = await self.session.execute(
            self
            ._base_query()
            .options(selectinload(InvoiceEntity.items))
            .where(InvoiceEntity.source_url == url)
        )
        return result.unique().scalar_one_or_none()

    async def find_by_id_with_user(self, id: int) -> InvoiceEntity | None:
        result = await self.session.execute(
            self
            ._base_query()
            .options(selectinload(InvoiceEntity.user))
            .where(InvoiceEntity.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def find_paginated_by_user(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> tuple[Sequence[InvoiceEntity], int]:
        query = self._base_query().where(InvoiceEntity.user_id == user_id)

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

    async def find_by_id_and_user(self, id: int, user_id: int) -> InvoiceEntity | None:
        result = await self.session.execute(
            self
            ._base_query()
            .where(InvoiceEntity.id == id)
            .where(InvoiceEntity.user_id == user_id)
        )
        return result.unique().scalar_one_or_none()

    async def find_by_id_with_user_scoped(
        self, id: int, user_id: int
    ) -> InvoiceEntity | None:
        result = await self.session.execute(
            self
            ._base_query()
            .options(selectinload(InvoiceEntity.user))
            .where(InvoiceEntity.id == id)
            .where(InvoiceEntity.user_id == user_id)
        )
        return result.unique().scalar_one_or_none()

    async def find_by_url_and_user(
        self, url: str, user_id: int
    ) -> InvoiceEntity | None:
        result = await self.session.execute(
            self
            ._base_query()
            .options(selectinload(InvoiceEntity.items))
            .where(InvoiceEntity.source_url == url)
            .where(InvoiceEntity.user_id == user_id)
        )
        return result.unique().scalar_one_or_none()
