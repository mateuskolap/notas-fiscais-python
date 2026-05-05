from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.user_entity import UserModel
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserModel, session)

    async def find_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(
            self._base_query().where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
