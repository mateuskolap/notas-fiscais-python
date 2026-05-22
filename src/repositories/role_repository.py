from sqlalchemy.orm import selectinload

from src.entities.role_entity import RoleEntity
from src.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[RoleEntity], model=RoleEntity):
    async def find_by_name(self, name: str) -> RoleEntity | None:
        return await self.find_one_by(name=name)

    async def find_by_id_with_permissions(self, id: int) -> RoleEntity | None:
        result = await self.session.execute(
            self
            ._base_query()
            .options(selectinload(RoleEntity.permissions))
            .where(RoleEntity.id == id)
        )
        return result.unique().scalar_one_or_none()
