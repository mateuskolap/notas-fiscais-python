from typing import Annotated

from fastapi import APIRouter, Query, status

from src.dependencies import CurrentUser, ProductNormAct, ProductSearchAct
from src.dtos.product_dtos import (
    CheapestProductByMarketResponse,
    PriceComparisonResponse,
    PriceHistoryResponse,
    ProductOverrideRequest,
    ProductSearchParams,
    ProductSearchResultResponse,
)

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/search', response_model=list[ProductSearchResultResponse])
async def search_products(
    current_user: CurrentUser,
    search_actions: ProductSearchAct,
    query: Annotated[str, Query()] = '',
    category_slug: Annotated[str | None, Query()] = None,
    brand: Annotated[str | None, Query()] = None,
):
    params = ProductSearchParams(query=query, category_slug=category_slug, brand=brand)
    return await search_actions.search_products(current_user.id, params)


@router.get('/cheapest-by-market', response_model=CheapestProductByMarketResponse)
async def search_cheapest_product_by_market(
    current_user: CurrentUser,
    search_actions: ProductSearchAct,
    query: Annotated[
        str, Query(..., min_length=2, description='Product search term (e.g., Ketchup)')
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await search_actions.search_cheapest_by_market(
        user_id=current_user.id, query_text=query, page=page, size=size
    )


@router.get('/{product_id}/price-comparison', response_model=PriceComparisonResponse)
async def get_price_comparison(
    product_id: int,
    current_user: CurrentUser,
    search_actions: ProductSearchAct,
):
    return await search_actions.get_price_comparison(current_user.id, product_id)


@router.get('/{product_id}/price-history', response_model=PriceHistoryResponse)
async def get_price_history(
    product_id: int,
    current_user: CurrentUser,
    search_actions: ProductSearchAct,
):
    return await search_actions.get_price_history(current_user.id, product_id)


@router.post('/{product_id}/override', status_code=status.HTTP_201_CREATED)
async def apply_product_override(
    product_id: int,
    data: ProductOverrideRequest,
    current_user: CurrentUser,
    norm_actions: ProductNormAct,
):
    override = await norm_actions.apply_user_override(current_user.id, product_id, data)
    return {'status': 'success', 'override_id': override.id}


@router.delete('/{product_id}/override', status_code=status.HTTP_204_NO_CONTENT)
async def remove_product_override(
    product_id: int,
    current_user: CurrentUser,
    norm_actions: ProductNormAct,
):
    await norm_actions.remove_user_override(current_user.id, product_id)
