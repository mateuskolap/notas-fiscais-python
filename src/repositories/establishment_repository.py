from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.establishment_entity import EstablishmentEntity
from src.repositories.base_repository import BaseRepository


class EstablishmentRepository(BaseRepository[EstablishmentEntity], model=EstablishmentEntity):
    async def find_by_tin(self, business_tin: str) -> EstablishmentEntity | None:
        return await self.find_one_by(business_tin=business_tin)
