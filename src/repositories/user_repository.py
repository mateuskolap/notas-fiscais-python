from sqlalchemy.orm import selectinload

from src.dtos.user_dtos import UserFilterParams
from src.entities.role_entity import RoleEntity
from src.entities.user_entity import UserEntity
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity], model=UserEntity):
    def _base_query(self):
        return (
            super()
            ._base_query()
            .options(
                selectinload(UserEntity.roles).selectinload(RoleEntity.permissions)
            )
        )

    async def find_by_email(self, email: str) -> UserEntity | None:
        return await self.find_one_by(email=email)

    async def find_by_email_with_deleted(self, email: str) -> UserEntity | None:
        query = (
            self
            ._base_query()
            .where(UserEntity.email == email)
            .execution_options(include_deleted=True)
        )
        res = await self.session.execute(query)
        return res.unique().scalar_one_or_none()

    def _apply_filters(self, query, filters: UserFilterParams | None):
        if filters:
            if filters.name is not None:
                query = query.where(UserEntity.name.ilike(f'%{filters.name}%'))
            if filters.email is not None:
                query = query.where(UserEntity.email.ilike(f'%{filters.email}%'))
        return query
