from src.actions.base_actions import BaseActions
from src.dtos.user_dtos import UserChangePassword, UserCreate, UserUpdate
from src.entities.user_entity import UserModel
from src.exceptions.base_exceptions import (
    ConflictException,
    UnauthorizedException,
    ValidationException,
)
from src.repositories.user_repository import UserRepository
from src.services.password_service import hash_password, verify_password


class UserActions(BaseActions[UserModel]):
    def __init__(self, repository: UserRepository):
        super().__init__(repository, entity_name='User')
        self.repository = repository

    async def create(self, data: UserCreate) -> UserModel:
        existing = await self.repository.find_by_email(data.email)
        if existing:
            raise ConflictException('Email already registered')

        user = UserModel(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
        )

        return await self.repository.create(user)

    async def update(self, user_id: int, data: UserUpdate) -> UserModel:
        user = await self._get_or_raise(user_id)

        update_data = data.model_dump(exclude_unset=True)

        if 'email' in update_data and update_data['email'] != user.email:
            existing = await self.repository.find_by_email(update_data['email'])
            if existing:
                raise ConflictException('Email already registered')

        if 'password' in update_data:
            update_data['password'] = hash_password(update_data['password'])

        for field, value in update_data.items():
            setattr(user, field, value)

        return await self.repository.update(user)

    async def change_password(
        self, user_id: int, data: UserChangePassword
    ) -> UserModel:
        user = await self._get_or_raise(user_id)

        if not verify_password(data.password, user.password):
            raise UnauthorizedException('Incorrect password')

        if data.new_password != data.new_password_confirm:
            raise ValidationException('New password and confirmation do not match')

        if data.new_password == data.password:
            raise ValidationException(
                'New password must be different from the current password'
            )

        user.password = hash_password(data.new_password)

        return await self.repository.update(user)
