from src.actions.base_actions import BaseActions
from src.entities.product_category_entity import ProductCategoryEntity
from src.repositories.product_category_repository import ProductCategoryRepository


class ProductCategoryActions(BaseActions[ProductCategoryEntity]):
    def __init__(self, repository: ProductCategoryRepository):
        super().__init__(repository, entity_name='ProductCategory')

    async def list_all_for_user(self, user_id: int) -> list[ProductCategoryEntity]:
        result = await self.repository.list_all_for_user(user_id)
        return list(result)
