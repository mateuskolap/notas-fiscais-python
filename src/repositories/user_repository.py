from sqlalchemy.orm import selectinload

from src.entities.role_entity import RoleEntity
from src.entities.user_entity import UserEntity
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity], model=UserEntity):
    def _base_query(self):
        return super()._base_query().options(
            selectinload(UserEntity.roles).selectinload(RoleEntity.permissions)
        )

    async def find_by_email(self, email: str) -> UserEntity | None:
        return await self.find_one_by(email=email)
