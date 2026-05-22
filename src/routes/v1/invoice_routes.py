from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies import CurrentUser, InvoiceAct
from src.dtos.invoice_dtos import (
    InvoiceDetailResponse,
    InvoiceFilterParams,
    InvoiceItemFilterParams,
    InvoiceItemResponse,
    InvoiceResponse,
)
from src.dtos.nfce_dtos import ExtractInvoiceRequest
from src.dtos.pagination_dtos import PaginatedResponse, PaginationParams
from src.dtos.response_dtos import ErrorResponse

router = APIRouter(
    prefix='/invoices',
    tags=['invoices'],
)


@router.get(
    '',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[InvoiceResponse],
)
async def list_invoices(
    actions: InvoiceAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[InvoiceFilterParams, Depends()],
):
    return await actions.list_paginated_by_user(
        current_user.id, pagination.page, pagination.per_page, filters
    )


@router.get(
    '/{invoice_id}',
    status_code=HTTPStatus.OK,
    response_model=InvoiceDetailResponse,
    responses={404: {'model': ErrorResponse}},
)
async def find_invoice(
    invoice_id: int,
    actions: InvoiceAct,
    current_user: CurrentUser,
):
    return await actions.find_with_user_scoped(invoice_id, current_user.id)


@router.get(
    '/{invoice_id}/items',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[InvoiceItemResponse],
    responses={404: {'model': ErrorResponse}},
)
async def list_invoice_items(
    invoice_id: int,
    actions: InvoiceAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[InvoiceItemFilterParams, Depends()],
):
    return await actions.list_items_paginated(
        invoice_id, current_user.id, pagination.page, pagination.per_page, filters
    )


@router.post(
    '/extract',
    status_code=HTTPStatus.CREATED,
    response_model=InvoiceResponse,
    responses={
        400: {'model': ErrorResponse},
        409: {'model': ErrorResponse},
        502: {'model': ErrorResponse},
    },
)
async def extract_invoice(
    data: ExtractInvoiceRequest,
    actions: InvoiceAct,
    current_user: CurrentUser,
):
    return await actions.extract_and_persist(data.url, current_user)
