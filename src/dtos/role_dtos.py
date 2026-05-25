from datetime import datetime
from typing import Literal

from src.dtos.base_dtos import BaseFilterParams, BaseReadDTO, BaseWriteDTO
from src.enums.permission_enum import PermissionEnum


class RoleCreate(BaseWriteDTO):
    name: str
    description: str | None = None
    permissions: list[PermissionEnum]


class RoleUpdate(BaseWriteDTO):
    name: str | None = None
    description: str | None = None
    permissions: list[PermissionEnum] | None = None


class PermissionRead(BaseReadDTO):
    id: int
    name: str


class SystemPermissionRead(BaseReadDTO):
    name: str


class RoleReadSimple(BaseReadDTO):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class RoleRead(RoleReadSimple):
    permissions: list[PermissionRead]


class AssignRoleRequest(BaseWriteDTO):
    role_ids: list[int]


class RoleFilterParams(BaseFilterParams):
    name: str | None = None
    order_by: Literal['id', 'name', 'created_at'] | None = 'id'
