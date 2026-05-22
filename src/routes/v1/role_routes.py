from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies import RoleAct, require_permission
from src.dtos.pagination_dtos import PaginatedResponse, PaginationParams
from src.dtos.response_dtos import ErrorResponse
from src.dtos.role_dtos import (
    RoleCreate,
    RoleRead,
    RoleReadSimple,
    RoleUpdate,
    SystemPermissionRead,
)
from src.entities.user_entity import UserEntity
from src.enums.permission_enum import PermissionEnum

router = APIRouter(prefix='/roles', tags=['roles'])


@router.get(
    '/permissions',
    status_code=HTTPStatus.OK,
    response_model=list[SystemPermissionRead],
)
async def list_permissions(
    user: Annotated[UserEntity, Depends(require_permission(PermissionEnum.ROLES_READ))],
):
    return [{'name': p.value} for p in PermissionEnum]


@router.get(
    '',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[RoleReadSimple],
)
async def list_roles(
    user: Annotated[UserEntity, Depends(require_permission(PermissionEnum.ROLES_READ))],
    actions: RoleAct,
    pagination: Annotated[PaginationParams, Depends()],
):
    return await actions.list_paginated(pagination.page, pagination.per_page)


@router.get(
    '/{role_id}',
    status_code=HTTPStatus.OK,
    response_model=RoleRead,
    responses={404: {'model': ErrorResponse}},
)
async def find_role(
    role_id: int,
    user: Annotated[UserEntity, Depends(require_permission(PermissionEnum.ROLES_READ))],
    actions: RoleAct,
):
    return await actions.find(role_id)


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_model=RoleReadSimple,
    responses={
        409: {'model': ErrorResponse},
        404: {'model': ErrorResponse},
    },
)
async def create_role(
    data: RoleCreate,
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_CREATE))
    ],
    actions: RoleAct,
):
    return await actions.create(data)


@router.put(
    '/{role_id}',
    status_code=HTTPStatus.OK,
    response_model=RoleReadSimple,
    responses={
        404: {'model': ErrorResponse},
        409: {'model': ErrorResponse},
    },
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_UPDATE))
    ],
    actions: RoleAct,
):
    return await actions.update(role_id, data)


@router.delete(
    '/{role_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={404: {'model': ErrorResponse}},
)
async def delete_role(
    role_id: int,
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_DELETE))
    ],
    actions: RoleAct,
):
    await actions.delete(role_id)
