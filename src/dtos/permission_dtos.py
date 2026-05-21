from datetime import datetime

from pydantic import BaseModel

from src.dtos.base_dtos import BaseReadDTO, BaseWriteDTO


class PermissionBase(BaseModel):
    name: str


class PermissionCreate(PermissionBase, BaseWriteDTO):
    pass


class Permission(PermissionBase):
    pass


class PermissionRead(Permission, BaseReadDTO):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
