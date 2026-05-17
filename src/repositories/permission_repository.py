from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.permission_entity import PermissionEntity
from src.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[PermissionEntity]):
    def __init__(self, session: AsyncSession):
        super().__init__(PermissionEntity, session)

    async def find_by_name(self, name: str) -> PermissionEntity | None:
        result = await self.session.execute(
            self._base_query().where(PermissionEntity.name == name)
        )
        return result.scalar_one_or_none()
