from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions.base_exceptions import (
    AppException,
    ConflictException,
    ForbiddenException,
    NfceScrapingException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundException)
    async def not_found_handler(
        request: Request, exc: NotFoundException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={'detail': exc.detail},
        )

    @app.exception_handler(ConflictException)
    async def conflict_handler(
        request: Request, exc: ConflictException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content={'detail': exc.detail},
        )

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_handler(
        request: Request, exc: UnauthorizedException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={'detail': exc.detail},
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_handler(
        request: Request, exc: ForbiddenException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.FORBIDDEN,
            content={'detail': exc.detail},
        )

    @app.exception_handler(ValidationException)
    async def validation_handler(
        request: Request, exc: ValidationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content={'detail': exc.detail},
        )

    @app.exception_handler(NfceScrapingException)
    async def nfce_scraping_handler(
        request: Request, exc: NfceScrapingException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.BAD_GATEWAY,
            content={'detail': exc.detail},
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={'detail': exc.detail},
        )
