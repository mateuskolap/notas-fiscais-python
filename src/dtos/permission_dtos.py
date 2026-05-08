from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    name: str


class PermissionCreate(PermissionBase):
    model_config = ConfigDict(extra='forbid')


class Permission(PermissionBase):
    pass


class PermissionRead(Permission):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
