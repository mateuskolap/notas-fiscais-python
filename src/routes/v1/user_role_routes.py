from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies import RoleAct, require_permission
from src.dtos.response_dtos import ErrorResponse
from src.dtos.role_dtos import AssignRoleRequest, RoleReadSimple
from src.entities.user_entity import UserEntity
from src.enums.permission_enum import PermissionEnum

router = APIRouter(prefix='/users/{user_id}/roles', tags=['user_roles'])


@router.put(
    '',
    status_code=HTTPStatus.OK,
    response_model=list[RoleReadSimple],
    responses={404: {'model': ErrorResponse}},
)
async def assign_user_roles(
    user_id: int,
    data: AssignRoleRequest,
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_ASSIGN))
    ],
    actions: RoleAct,
):
    return await actions.assign_roles_to_user(user_id, data.role_ids)
