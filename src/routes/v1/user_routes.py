from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.dependencies import CurrentUser, UserAct
from src.dtos.pagination_dtos import PaginatedResponse, PaginationParams
from src.dtos.response_dtos import ErrorResponse
from src.dtos.user_dtos import (
    UserChangePassword,
    UserCreate,
    UserFilterParams,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    '',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[UserRead],
    summary='List all users',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
    },
)
async def list_users(
    actions: UserAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[UserFilterParams, Depends()],
):
    """
    Retrieve a paginated list of all users registered in the system.

    Supports filtering by name and email, and custom sorting.
    """
    return await actions.list_paginated(pagination.page, pagination.per_page, filters)


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
    summary='Get user by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'User not found'},
    },
)
async def find_user(
    user_id: Annotated[int, Path(description='The unique identifier of the user')],
    current_user: CurrentUser,
    actions: UserAct,
):
    """
    Retrieve details of a specific user by their ID, including their assigned roles.
    """
    return await actions.find(user_id)


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_model=UserRead,
    summary='Register a new user',
    responses={
        400: {'model': ErrorResponse, 'description': 'Validation or bad request'},
        409: {
            'model': ErrorResponse,
            'description': 'User with this email already exists',
        },
    },
)
async def create_user(data: UserCreate, actions: UserAct):
    """
    Register a new user account.

    This endpoint does not require authentication and is open for public registration.
    """
    return await actions.create(data)


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
    summary='Update user by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'User not found'},
        409: {
            'model': ErrorResponse,
            'description': 'Email is already taken by another user',
        },
    },
)
async def update_user(
    user_id: Annotated[int, Path(description='The unique identifier of the user')],
    data: UserUpdate,
    current_user: CurrentUser,
    actions: UserAct,
):
    """
    Update details (name, email, password) of an existing user by their ID.
    """
    return await actions.update(user_id, data)


@router.patch(
    '/me',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
    summary='Update current user profile',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        409: {
            'model': ErrorResponse,
            'description': 'Email is already taken by another user',
        },
    },
)
async def update_current_user(
    data: UserUpdate,
    current_user: CurrentUser,
    actions: UserAct,
):
    """
    Update the profile information of the currently authenticated user.
    """
    return await actions.update(current_user.id, data)


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Delete user by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'User not found'},
    },
)
async def delete_user(
    user_id: Annotated[int, Path(description='The unique identifier of the user')],
    current_user: CurrentUser,
    actions: UserAct,
):
    """
    Permanently delete a user account from the system by their ID.
    """
    await actions.delete(user_id)


@router.patch(
    '/{user_id}/password',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
    summary='Change user password',
    responses={
        401: {
            'model': ErrorResponse,
            'description': 'Missing token or invalid current password',
        },
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'User not found'},
        422: {'description': 'New password validation failed'},
    },
)
async def reset_user_password(
    user_id: Annotated[int, Path(description='The unique identifier of the user')],
    data: UserChangePassword,
    current_user: CurrentUser,
    actions: UserAct,
):
    """
    Change a user's password.

    Requires validating the current password and confirming the new password.
    """
    return await actions.change_password(user_id, data)
