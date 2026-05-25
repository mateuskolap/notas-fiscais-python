from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.dependencies import CurrentUser, EstablishmentAct, require_permission
from src.dtos.establishment_dtos import (
    EstablishmentCreate,
    EstablishmentFilterParams,
    EstablishmentRead,
    EstablishmentUpdate,
)
from src.dtos.pagination_dtos import PaginatedResponse, PaginationParams
from src.dtos.response_dtos import ErrorResponse
from src.enums.permission_enum import PermissionEnum

router = APIRouter(prefix='/establishments', tags=['establishments'])


@router.get(
    '',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[EstablishmentRead],
    summary='List all establishments',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
    },
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_READ))],
)
async def list_establishments(
    actions: EstablishmentAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[EstablishmentFilterParams, Depends()],
):
    """
    Retrieve a paginated list of all establishments registered in the system.

    Supports filtering by name, CNPJ, and scoping to establishments related
    to the current user.
    """
    if filters.related_only:
        filters.user_id = current_user.id

    return await actions.list_paginated(pagination.page, pagination.per_page, filters)


@router.get(
    '/{establishment_id}',
    status_code=HTTPStatus.OK,
    response_model=EstablishmentRead,
    summary='Get establishment by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'Establishment not found'},
    },
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_READ))],
)
async def find_establishment(
    establishment_id: Annotated[
        int, Path(description='The unique identifier of the establishment')
    ],
    current_user: CurrentUser,
    actions: EstablishmentAct,
):
    """
    Retrieve details of a specific establishment by its ID.
    """
    return await actions.find(establishment_id)


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_model=EstablishmentRead,
    summary='Create a new establishment',
    responses={
        400: {'model': ErrorResponse, 'description': 'Validation or bad request'},
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        409: {
            'model': ErrorResponse,
            'description': 'Establishment with this CNPJ already exists',
        },
    },
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_CREATE))],
)
async def create_establishment(
    data: EstablishmentCreate,
    current_user: CurrentUser,
    actions: EstablishmentAct,
):
    """
    Register a new establishment in the system.
    """
    return await actions.create(data)


@router.put(
    '/{establishment_id}',
    status_code=HTTPStatus.OK,
    response_model=EstablishmentRead,
    summary='Update establishment by ID',
    responses={
        400: {'model': ErrorResponse, 'description': 'Validation or bad request'},
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'Establishment not found'},
        409: {
            'model': ErrorResponse,
            'description': 'Establishment CNPJ conflict with another establishment',
        },
    },
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_UPDATE))],
)
async def update_establishment(
    establishment_id: Annotated[
        int, Path(description='The unique identifier of the establishment')
    ],
    data: EstablishmentUpdate,
    current_user: CurrentUser,
    actions: EstablishmentAct,
):
    """
    Update details (name, CNPJ, address) of an existing establishment by its ID.
    """
    return await actions.update(establishment_id, data)


@router.delete(
    '/{establishment_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Delete establishment by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'Establishment not found'},
    },
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_DELETE))],
)
async def delete_establishment(
    establishment_id: Annotated[
        int, Path(description='The unique identifier of the establishment')
    ],
    current_user: CurrentUser,
    actions: EstablishmentAct,
):
    """
    Delete an existing establishment from the system by its ID.
    """
    await actions.delete(establishment_id)
