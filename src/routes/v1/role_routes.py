from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.dependencies import RoleAct, require_permission
from src.dtos.pagination_dtos import PaginatedResponse, PaginationParams
from src.dtos.response_dtos import ErrorResponse
from src.dtos.role_dtos import (
    RoleCreate,
    RoleFilterParams,
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
    summary='List all system permissions',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
    },
)
async def list_permissions(
    user: Annotated[UserEntity, Depends(require_permission(PermissionEnum.ROLES_READ))],
):
    """
    Retrieve all available system permissions defined in the application's permission enum.
    """
    return [{'name': p.value} for p in PermissionEnum]


@router.get(
    '',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[RoleReadSimple],
    summary='List all roles',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def list_roles(
    user: Annotated[UserEntity, Depends(require_permission(PermissionEnum.ROLES_READ))],
    actions: RoleAct,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[RoleFilterParams, Depends()],
):
    """
    Retrieve a paginated list of defined user roles.

    Supports filtering by name and custom sorting.
    """
    return await actions.list_paginated(pagination.page, pagination.per_page, filters)


@router.get(
    '/{role_id}',
    status_code=HTTPStatus.OK,
    response_model=RoleRead,
    summary='Get role by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'Role not found'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def find_role(
    role_id: Annotated[int, Path(description='The unique identifier of the role')],
    user: Annotated[UserEntity, Depends(require_permission(PermissionEnum.ROLES_READ))],
    actions: RoleAct,
):
    """
    Retrieve details of a specific role by its ID, including all assigned permissions.
    """
    return await actions.find(role_id)


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_model=RoleReadSimple,
    summary='Create a new role',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'Permissions not found'},
        409: {'model': ErrorResponse, 'description': 'Role name already exists'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def create_role(
    data: RoleCreate,
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_CREATE))
    ],
    actions: RoleAct,
):
    """
    Create a new custom role with a specific list of system permissions.
    """
    return await actions.create(data)


@router.put(
    '/{role_id}',
    status_code=HTTPStatus.OK,
    response_model=RoleReadSimple,
    summary='Update role by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'Role or permissions not found'},
        409: {'model': ErrorResponse, 'description': 'Role name already taken'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def update_role(
    role_id: Annotated[int, Path(description='The unique identifier of the role')],
    data: RoleUpdate,
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_UPDATE))
    ],
    actions: RoleAct,
):
    """
    Update details (name, description, list of permissions) of an existing role by its ID.
    """
    return await actions.update(role_id, data)


@router.delete(
    '/{role_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Delete role by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'Role not found'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def delete_role(
    role_id: Annotated[int, Path(description='The unique identifier of the role')],
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_DELETE))
    ],
    actions: RoleAct,
):
    """
    Delete a user role by its ID.
    """
    await actions.delete(role_id)
