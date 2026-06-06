from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.entities.user_product_category_entity import UserProductCategoryEntity
from src.repositories.base_repository import BaseRepository


class UserProductCategoryRepository(
    BaseRepository[UserProductCategoryEntity], model=UserProductCategoryEntity
):
    def _base_query(self):
        return select(UserProductCategoryEntity).options(
            selectinload(UserProductCategoryEntity.category),
            selectinload(UserProductCategoryEntity.custom_children),
        )

    async def find_active_by_user(
        self, user_id: int
    ) -> Sequence[UserProductCategoryEntity]:
        query = self._base_query().where(
            UserProductCategoryEntity.user_id == user_id,
            UserProductCategoryEntity.is_active.is_(True),
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def find_by_user_and_id(
        self, user_id: int, category_id: int
    ) -> UserProductCategoryEntity | None:
        query = self._base_query().where(
            UserProductCategoryEntity.user_id == user_id,
            UserProductCategoryEntity.id == category_id,
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def find_by_user_and_slug(
        self, user_id: int, slug: str
    ) -> UserProductCategoryEntity | None:
        query = self._base_query().where(
            UserProductCategoryEntity.user_id == user_id,
            UserProductCategoryEntity.custom_slug == slug,
        )
        result = await self.session.execute(query)
        return result.scalars().first()
