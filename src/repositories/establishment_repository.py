from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.establishment_entity import EstablishmentEntity
from src.repositories.base_repository import BaseRepository


class EstablishmentRepository(BaseRepository[EstablishmentEntity]):
    def __init__(self, session: AsyncSession):
        super().__init__(EstablishmentEntity, session)

    async def find_by_tin(self, business_tin: str) -> EstablishmentEntity | None:
        result = await self.session.execute(
            self._base_query().where(EstablishmentEntity.business_tin == business_tin)
        )
        return result.scalar_one_or_none()
