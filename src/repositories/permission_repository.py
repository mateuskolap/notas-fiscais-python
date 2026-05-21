from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.permission_entity import PermissionEntity
from src.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[PermissionEntity], model=PermissionEntity):
    async def find_by_name(self, name: str) -> PermissionEntity | None:
        return await self.find_one_by(name=name)
