from typing import Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

from src.entities.product_category_entity import ProductCategoryEntity
from src.entities.user_product_category_entity import UserProductCategoryEntity
from src.repositories.base_repository import BaseRepository


class ProductCategoryRepository(
    BaseRepository[ProductCategoryEntity], model=ProductCategoryEntity
):
    def _base_query(self):
        return select(ProductCategoryEntity).options(
            selectinload(ProductCategoryEntity.children)
        )

    async def find_root_categories(self) -> Sequence[ProductCategoryEntity]:
        query = (
            self
            ._base_query()
            .where(ProductCategoryEntity.parent_id.is_(None))
            .order_by(ProductCategoryEntity.position.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def list_all_for_user(self, user_id: int) -> Sequence[ProductCategoryEntity]:
        query = (
            select(ProductCategoryEntity)
            .outerjoin(
                UserProductCategoryEntity,
                and_(
                    UserProductCategoryEntity.category_id == ProductCategoryEntity.id,
                    UserProductCategoryEntity.user_id == user_id,
                ),
            )
            .where(
                or_(
                    ProductCategoryEntity.is_default,
                    UserProductCategoryEntity.id.isnot(None),
                )
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_by_slug(
        self, slug: str, parent_id: int | None
    ) -> ProductCategoryEntity | None:
        return await self.find_one_by(slug=slug, parent_id=parent_id)

    async def find_tree(self) -> Sequence[ProductCategoryEntity]:
        return await self.find_root_categories()
