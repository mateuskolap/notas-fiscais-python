from datetime import datetime
from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, EmailStr

from src.dtos.base_dtos import BaseFilterParams, BaseReadDTO, BaseWriteDTO
from src.dtos.role_dtos import PermissionRead, RoleReadSimple
from src.dtos.validators import PasswordStr


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase, BaseWriteDTO):
    password: PasswordStr


class UserUpdate(BaseWriteDTO):
    name: str | None = None
    email: EmailStr | None = None
    password: PasswordStr | None = None


class User(UserBase):
    pass


class UserReadBase(User, BaseReadDTO):
    id: int
    created_at: datetime
    updated_at: datetime


class UserRead(UserReadBase):
    roles: list[RoleReadSimple]


class UserMeRead(UserReadBase):
    permissions: list[PermissionRead]


class UserChangePassword(BaseWriteDTO):
    password: PasswordStr
    new_password: PasswordStr
    new_password_confirm: PasswordStr


class UserFilterParams(BaseFilterParams):
    name: Annotated[str | None, Query(description='Partial match on user name')] = None
    email: Annotated[str | None, Query(description='Partial match on user email')] = (
        None
    )

    order_by: Annotated[
        Literal['id', 'name', 'email', 'created_at'] | None, Query()
    ] = 'id'
