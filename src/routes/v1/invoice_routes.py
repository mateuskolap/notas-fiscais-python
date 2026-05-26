from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

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
    summary='List all invoices',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def list_invoices(
    actions: InvoiceAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[InvoiceFilterParams, Depends()],
):
    """
    Retrieve a paginated list of all invoices scoped/belonging to the current user.

    Supports filtering by establishment ID, establishment name, total value limits,
    issued date ranges, and custom sorting.
    """
    return await actions.list_paginated_by_user(
        current_user.id, pagination.page, pagination.per_page, filters
    )


@router.get(
    '/{invoice_id}',
    status_code=HTTPStatus.OK,
    response_model=InvoiceDetailResponse,
    summary='Get invoice by ID',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        404: {'model': ErrorResponse, 'description': 'Invoice not found'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def find_invoice(
    invoice_id: Annotated[
        int, Path(description='The unique identifier of the invoice')
    ],
    actions: InvoiceAct,
    current_user: CurrentUser,
):
    """
    Retrieve detailed information for a single invoice by its ID, scoped to the current user.
    """
    return await actions.find_with_user_scoped(invoice_id, current_user.id)


@router.get(
    '/{invoice_id}/items',
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[InvoiceItemResponse],
    summary='List items of an invoice',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        404: {'model': ErrorResponse, 'description': 'Invoice not found'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def list_invoice_items(
    invoice_id: Annotated[
        int, Path(description='The unique identifier of the invoice')
    ],
    actions: InvoiceAct,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[InvoiceItemFilterParams, Depends()],
):
    """
    Retrieve a paginated list of items associated with a specific invoice.

    Supports partial match filtering on the item description.
    """
    return await actions.list_items_paginated(
        invoice_id, current_user.id, pagination.page, pagination.per_page, filters
    )


@router.post(
    '/extract',
    status_code=HTTPStatus.CREATED,
    response_model=InvoiceResponse,
    summary='Extract invoice from NFC-e URL',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
        409: {
            'model': ErrorResponse,
            'description': 'Invoice has already been registered',
        },
        422: {'model': ErrorResponse, 'description': 'Validation error or invalid URL'},
        502: {
            'model': ErrorResponse,
            'description': 'State portal returned an error during extraction',
        },
    },
)
async def extract_invoice(
    data: ExtractInvoiceRequest,
    actions: InvoiceAct,
    current_user: CurrentUser,
):
    """
    Extract invoice and item details from a valid HTTPS NFC-e portal URL (e.g. Paraná's state portal),
    and persist it under the authenticated user.
    """
    return await actions.extract_and_persist(data.url, current_user)
