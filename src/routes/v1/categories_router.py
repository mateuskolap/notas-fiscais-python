from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from src.dependencies import CurrentUser, ProductCategoryAct, require_permission
from src.dtos.category_dtos import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from src.enums.permission_enum import PermissionEnum

router = APIRouter(prefix='/categories', tags=['categories'])


@router.get(
    '',
    response_model=list[CategoryResponse],
    dependencies=[Depends(require_permission(PermissionEnum.PRODUCT_CATEGORIES_READ))],
)
async def list_categories(
    current_user: CurrentUser,
    actions: ProductCategoryAct,
):
    return await actions.list_all_for_user(current_user.id)


@router.get(
    '/{id}',
    response_model=CategoryResponse,
    dependencies=[Depends(require_permission(PermissionEnum.PRODUCT_CATEGORIES_READ))],
)
async def find_category(
    id: Annotated[int, Path(description='Category ID')],
    current_user: CurrentUser,
    actions: ProductCategoryAct,
    is_global: Annotated[
        bool, Query(description='Whether this is a global category')
    ] = False,
):
    return await actions.find_user_category(current_user.id, id, is_global)


@router.post(
    '',
    response_model=CategoryResponse,
    status_code=HTTPStatus.CREATED,
    dependencies=[
        Depends(require_permission(PermissionEnum.PRODUCT_CATEGORIES_MANAGE))
    ],
)
async def create_category(
    data: CategoryCreateRequest,
    current_user: CurrentUser,
    actions: ProductCategoryAct,
):
    return await actions.create_user_category(current_user.id, data)


@router.put(
    '/{id}',
    response_model=CategoryResponse,
    dependencies=[
        Depends(require_permission(PermissionEnum.PRODUCT_CATEGORIES_MANAGE))
    ],
)
async def update_category(
    id: Annotated[int, Path(description='Category ID')],
    data: CategoryUpdateRequest,
    current_user: CurrentUser,
    actions: ProductCategoryAct,
    is_global: Annotated[
        bool, Query(description='Whether this is a global category')
    ] = False,
):
    return await actions.update_user_category(current_user.id, id, is_global, data)


@router.delete(
    '/{id}',
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(require_permission(PermissionEnum.PRODUCT_CATEGORIES_MANAGE))
    ],
)
async def delete_category(
    id: Annotated[int, Path(description='Category ID')],
    current_user: CurrentUser,
    actions: ProductCategoryAct,
    is_global: Annotated[
        bool, Query(description='Whether this is a global category')
    ] = False,
):
    await actions.delete_user_category(current_user.id, id, is_global)
