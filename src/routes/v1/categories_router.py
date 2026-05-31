from typing import Annotated

from fastapi import APIRouter, Depends

from src.actions.product_category_actions import ProductCategoryActions
from src.dependencies import CurrentUser, ProductCategoryRepo
from src.dtos.category_dtos import CategoryResponse

router = APIRouter(prefix='/categories', tags=['categories'])


def get_category_actions(repo: ProductCategoryRepo) -> ProductCategoryActions:
    return ProductCategoryActions(repo)


CategoryActionsDep = Annotated[ProductCategoryActions, Depends(get_category_actions)]


@router.get('', response_model=list[CategoryResponse])
async def list_categories(
    current_user: CurrentUser,
    actions: CategoryActionsDep,
):
    return await actions.list_all_for_user(current_user.id)
