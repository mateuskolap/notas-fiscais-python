from typing import Sequence

from src.entities.permission_entity import PermissionEntity
from src.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[PermissionEntity], model=PermissionEntity):
    async def find_by_name(self, name: str) -> PermissionEntity | None:
        return await self.find_one_by(name=name)

    async def find_by_names(self, names: list[str]) -> Sequence[PermissionEntity]:
        result = await self.session.execute(
            self._base_query().where(PermissionEntity.name.in_(names))
        )
        return result.scalars().all()
