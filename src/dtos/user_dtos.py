from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.dtos.base_dtos import BaseReadDTO, BaseWriteDTO
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
