from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

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
    summary='Assign roles to a user',
    responses={
        400: {'model': ErrorResponse, 'description': 'Validation or bad request'},
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        403: {'model': ErrorResponse, 'description': 'Permission denied'},
        404: {'model': ErrorResponse, 'description': 'User or roles not found'},
    },
)
async def assign_user_roles(
    user_id: Annotated[
        int, Path(description='The unique identifier of the target user')
    ],
    data: AssignRoleRequest,
    user: Annotated[
        UserEntity, Depends(require_permission(PermissionEnum.ROLES_ASSIGN))
    ],
    actions: RoleAct,
):
    """
    Assign a list of roles to a specific user, overwriting any previously assigned roles.
    """
    return await actions.assign_roles_to_user(user_id, data.role_ids)
