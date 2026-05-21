from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.user_entity import UserEntity
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity], model=UserEntity):
    async def find_by_email(self, email: str) -> UserEntity | None:
        return await self.find_one_by(email=email)
