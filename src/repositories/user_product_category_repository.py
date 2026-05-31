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
