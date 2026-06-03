from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.dependencies import ActivityLogAct, CurrentUser
from src.dtos.activity_log_dtos import (
    ActivityLogFilterParams,
    ActivityLogRead,
)
from src.dtos.pagination_dtos import PaginatedResponse, PaginationParams
from src.dtos.response_dtos import ErrorResponse

router = APIRouter(prefix='/activity-logs', tags=['activity-logs'])


@router.get(
    '',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[ActivityLogRead],
    summary='List activity logs',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def list_activity_logs(
    actions: ActivityLogAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[ActivityLogFilterParams, Depends()],
):
    """
    Retrieve a paginated list of activity logs.

    Supports filtering by subject_type, subject_id, causer_id, event,
    and date range.
    """
    return await actions.list_paginated(pagination.page, pagination.per_page, filters)


@router.get(
    '/{log_id}',
    status_code=HTTPStatus.OK,
    response_model=ActivityLogRead,
    summary='Get activity log by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        404: {'model': ErrorResponse, 'description': 'Activity log not found'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def find_activity_log(
    log_id: Annotated[
        int, Path(description='The unique identifier of the activity log')
    ],
    current_user: CurrentUser,
    actions: ActivityLogAct,
):
    """
    Retrieve details of a specific activity log entry by its ID.
    """
    return await actions.find(log_id)
