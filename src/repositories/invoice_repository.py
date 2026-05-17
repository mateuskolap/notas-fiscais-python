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
