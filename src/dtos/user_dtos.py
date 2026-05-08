from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from src.dtos.validators import PasswordStr


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    model_config = ConfigDict(extra='forbid')

    password: PasswordStr


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str | None = None
    email: EmailStr | None = None
    password: PasswordStr | None = None


class User(UserBase):
    pass


class UserRead(User):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class UserChangePassword(BaseModel):
    model_config = ConfigDict(extra='forbid')

    password: PasswordStr
    new_password: PasswordStr
    new_password_confirm: PasswordStr
