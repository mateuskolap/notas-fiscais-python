from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies import CurrentUser, UserAct
from src.dtos.pagination_dtos import PaginatedResponse, PaginationParams
from src.dtos.response_dtos import ErrorResponse
from src.dtos.user_dtos import UserChangePassword, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    '',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[UserRead],
)
async def list_users(
    actions: UserAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
):
    return await actions.list_paginated(pagination.page, pagination.per_page)


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
    responses={404: {'model': ErrorResponse}},
)
async def find_user(user_id: int, current_user: CurrentUser, actions: UserAct):
    return await actions.find(user_id)


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_model=UserRead,
    responses={409: {'model': ErrorResponse}},
)
async def create_user(data: UserCreate, actions: UserAct):
    return await actions.create(data)


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
    responses={
        404: {'model': ErrorResponse},
        409: {'model': ErrorResponse},
    },
)
async def update_user(
    user_id: int, data: UserUpdate, current_user: CurrentUser, actions: UserAct
):
    return await actions.update(user_id, data)


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={404: {'model': ErrorResponse}},
)
async def delete_user(user_id: int, current_user: CurrentUser, actions: UserAct):
    await actions.delete(user_id)


@router.patch(
    '/{user_id}/password',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
    responses={
        404: {'model': ErrorResponse},
        401: {'model': ErrorResponse},
        422: {'model': ErrorResponse},
    },
)
async def reset_user_password(
    user_id: int, data: UserChangePassword, current_user: CurrentUser, actions: UserAct
):
    return await actions.change_password(user_id, data)
