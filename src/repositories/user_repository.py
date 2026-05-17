from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.user_entity import UserEntity
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserEntity, session)

    async def find_by_email(self, email: str) -> UserEntity | None:
        result = await self.session.execute(
            self._base_query().where(UserEntity.email == email)
        )
        return result.scalar_one_or_none()
