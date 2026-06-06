from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.dependencies import CurrentUser, InvoiceAct, InvoiceCrudAct
from src.dtos.invoice_dtos import (
    InvoiceDetailResponse,
    InvoiceFilterParams,
    InvoiceItemFilterParams,
    InvoiceItemManualCreate,
    InvoiceItemManualUpdate,
    InvoiceItemResponse,
    InvoiceManualCreate,
    InvoiceManualUpdate,
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
    Extract invoice and item details from a valid HTTPS NFC-e portal URL (e.g. Parana's state portal),
    and persist it under the authenticated user.
    """
    return await actions.extract_and_persist(data.url, current_user)


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_model=InvoiceResponse,
    summary='Create a manual invoice',
)
async def create_manual_invoice(
    data: InvoiceManualCreate,
    crud_actions: InvoiceCrudAct,
    current_user: CurrentUser,
):
    return await crud_actions.create_manual_invoice(current_user.id, data)


@router.put(
    '/{invoice_id}',
    status_code=HTTPStatus.OK,
    response_model=InvoiceResponse,
    summary='Update a manual invoice',
)
async def update_manual_invoice(
    invoice_id: int,
    data: InvoiceManualUpdate,
    crud_actions: InvoiceCrudAct,
    current_user: CurrentUser,
):
    return await crud_actions.update_manual_invoice(current_user.id, invoice_id, data)


@router.delete(
    '/{invoice_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Delete an invoice',
)
async def delete_manual_invoice(
    invoice_id: int,
    crud_actions: InvoiceCrudAct,
    current_user: CurrentUser,
):
    await crud_actions.delete_manual_invoice(current_user.id, invoice_id)


@router.post(
    '/{invoice_id}/items',
    status_code=HTTPStatus.CREATED,
    response_model=InvoiceItemResponse,
    summary='Add an item to an invoice manually',
)
async def add_item_to_invoice(
    invoice_id: int,
    data: InvoiceItemManualCreate,
    crud_actions: InvoiceCrudAct,
    current_user: CurrentUser,
):
    return await crud_actions.add_item_to_invoice(current_user.id, invoice_id, data)


@router.put(
    '/{invoice_id}/items/{item_id}',
    status_code=HTTPStatus.OK,
    response_model=InvoiceItemResponse,
    summary='Update an invoice item manually',
)
async def update_invoice_item(
    invoice_id: int,
    item_id: int,
    data: InvoiceItemManualUpdate,
    crud_actions: InvoiceCrudAct,
    current_user: CurrentUser,
):
    return await crud_actions.update_invoice_item(
        current_user.id, invoice_id, item_id, data
    )


@router.delete(
    '/{invoice_id}/items/{item_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Delete an invoice item manually',
)
async def delete_invoice_item(
    invoice_id: int,
    item_id: int,
    crud_actions: InvoiceCrudAct,
    current_user: CurrentUser,
):
    await crud_actions.delete_invoice_item(current_user.id, invoice_id, item_id)
