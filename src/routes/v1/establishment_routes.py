from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

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
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_READ))],
)
async def list_establishments(
    actions: EstablishmentAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[EstablishmentFilterParams, Depends()],
):
    if filters.related_only:
        filters.user_id = current_user.id
    
    return await actions.list_paginated(pagination.page, pagination.per_page, filters)


@router.get(
    '/{establishment_id}',
    status_code=HTTPStatus.OK,
    response_model=EstablishmentRead,
    responses={404: {'model': ErrorResponse}},
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_READ))],
)
async def find_establishment(establishment_id: int, current_user: CurrentUser, actions: EstablishmentAct):
    return await actions.find(establishment_id)


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_model=EstablishmentRead,
    responses={409: {'model': ErrorResponse}},
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_CREATE))],
)
async def create_establishment(data: EstablishmentCreate, current_user: CurrentUser, actions: EstablishmentAct):
    return await actions.create(data)


@router.put(
    '/{establishment_id}',
    status_code=HTTPStatus.OK,
    response_model=EstablishmentRead,
    responses={
        404: {'model': ErrorResponse},
        409: {'model': ErrorResponse},
    },
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_UPDATE))],
)
async def update_establishment(
    establishment_id: int, data: EstablishmentUpdate, current_user: CurrentUser, actions: EstablishmentAct
):
    return await actions.update(establishment_id, data)


@router.delete(
    '/{establishment_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={404: {'model': ErrorResponse}},
    dependencies=[Depends(require_permission(PermissionEnum.ESTABLISHMENTS_DELETE))],
)
async def delete_establishment(establishment_id: int, current_user: CurrentUser, actions: EstablishmentAct):
    await actions.delete(establishment_id)
