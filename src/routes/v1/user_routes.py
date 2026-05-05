from http import HTTPStatus

from fastapi import APIRouter

from src.actions.user_actions import (
    create_user_action,
    delete_user_action,
    find_user_action,
    list_users_action,
    update_user_action,
)
from src.dependencies import UserRepo
from src.dtos.user_dtos import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


@router.get('', status_code=HTTPStatus.OK, response_model=list[UserRead])
async def list_users(repository: UserRepo):
    return await list_users_action(repository)


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserRead)
async def find_user(user_id: int, repository: UserRepo):
    return await find_user_action(user_id, repository)


@router.post('', status_code=HTTPStatus.CREATED, response_model=UserRead)
async def create_user(data: UserCreate, repository: UserRepo):
    return await create_user_action(data, repository)


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserRead)
async def update_user(user_id: int, data: UserUpdate, repository: UserRepo):
    return await update_user_action(user_id, data, repository)


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(user_id: int, repository: UserRepo):
    await delete_user_action(user_id, repository)
