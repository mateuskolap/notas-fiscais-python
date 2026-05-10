from http import HTTPStatus

from fastapi import APIRouter

from src.dtos.nfce_dtos import (
    NFCeParseRequest,
    NFCeResponse,
)
from src.services.nfce.nfce_service import parse_nfce

router = APIRouter(
    prefix='/nfce',
    tags=['nfce'],
)


@router.post(
    '/parse',
    status_code=HTTPStatus.OK,
    response_model=NFCeResponse,
)
async def parse_nfce_route(data: NFCeParseRequest):
    return await parse_nfce(data.url)