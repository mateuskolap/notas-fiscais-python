from http import HTTPStatus

from fastapi import HTTPException

from src.dtos.user_dtos import UserCreate, UserRead, UserUpdate
from src.entities.user_entity import UserModel
from src.repositories.user_repository import UserRepository
from src.services.password_service import hash_password


async def list_users_action(repository: UserRepository) -> list[UserRead]:
    users = await repository.find_all()
    return [UserRead.model_validate(user) for user in users]


async def find_user_action(user_id: int, repository: UserRepository) -> UserRead:
    user = await repository.find_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    return UserRead.model_validate(user)


async def create_user_action(data: UserCreate, repository: UserRepository) -> UserRead:
    existing = await repository.find_by_email(data.email)

    if existing:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already registered',
        )

    user = UserModel(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
    )

    user = await repository.create(user)
    return UserRead.model_validate(user)


async def update_user_action(
    user_id: int, data: UserUpdate, repository: UserRepository
) -> UserRead:
    user = await repository.find_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    update_data = data.model_dump(exclude_unset=True)

    if 'email' in update_data and update_data['email'] != user.email:
        existing = await repository.find_by_email(update_data['email'])

        if existing:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already registered',
            )

    if 'password' in update_data:
        update_data['password'] = hash_password(update_data['password'])

    for field, value in update_data.items():
        setattr(user, field, value)

    user = await repository.update(user)
    return UserRead.model_validate(user)


async def delete_user_action(user_id: int, repository: UserRepository) -> None:
    user = await repository.find_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    await repository.delete(user)
