from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.permission_entity import PermissionModel
from src.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[PermissionModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(PermissionModel, session)

    async def find_by_name(self, name: str) -> PermissionModel | None:
        result = await self.session.execute(
            self._base_query().where(PermissionModel.name == name)
        )
        return result.scalar_one_or_none()
