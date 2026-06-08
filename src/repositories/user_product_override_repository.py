from sqlalchemy import select

from src.entities.user_product_override_entity import UserProductOverrideEntity
from src.repositories.base_repository import BaseRepository


class UserProductOverrideRepository(
    BaseRepository[UserProductOverrideEntity], model=UserProductOverrideEntity
):
    async def find_by_user_and_product(
        self, user_id: int, product_id: int
    ) -> UserProductOverrideEntity | None:
        return await self.find_one_by(user_id=user_id, canonical_product_id=product_id)

    async def find_by_user_and_product_with_deleted(
        self, user_id: int, product_id: int
    ) -> UserProductOverrideEntity | None:
        query = (
            select(UserProductOverrideEntity)
            .where(
                UserProductOverrideEntity.user_id == user_id,
                UserProductOverrideEntity.canonical_product_id == product_id,
            )
            .execution_options(include_deleted=True)
        )
        res = await self.session.execute(query)
        return res.unique().scalar_one_or_none()
