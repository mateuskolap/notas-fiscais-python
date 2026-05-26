import logging
import traceback
from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from src.exceptions.base_exceptions import AppException
from src.middleware import request_id_ctx

logger = logging.getLogger("app.exceptions")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        request_id = request_id_ctx.get()
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        path = request.url.path

        if exc.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.error(
                f"AppException {exc.error_code} on {request.method} {path} [Request ID: {request_id}]: {exc.message}\n"
                f"Details: {exc.details}\n"
                f"{''.join(traceback.format_exception(None, exc, exc.__traceback__))}"
            )
        else:
            logger.warning(
                f"AppException {exc.error_code} on {request.method} {path} [Request ID: {request_id}]: {exc.message} "
                f"(Status: {exc.status_code.value}, Details: {exc.details})"
            )

        content = {
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": timestamp,
                "path": path,
                "request_id": request_id,
            }
        }
        return JSONResponse(
            status_code=exc.status_code.value,
            content=content,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = request_id_ctx.get()
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        path = request.url.path

        # Format Pydantic field-level errors nicely
        fields = []
        for error in exc.errors():
            # For query/path/body params, location is a tuple (e.g. ('body', 'email'))
            # We want to present clean field paths by stripping standard prefixes
            loc_parts = error.get("loc", [])
            if len(loc_parts) > 1 and loc_parts[0] in {"body", "query", "path", "header"}:
                field_name = ".".join(str(loc) for loc in loc_parts[1:])
            else:
                field_name = ".".join(str(loc) for loc in loc_parts)

            fields.append({
                "field": field_name or "body",
                "message": error.get("msg", "Validation failed"),
                "type": error.get("type", "value_error")
            })

        details = {"fields": fields}

        # Log request validation errors as warnings
        logger.warning(
            f"Validation error on {request.method} {path} [Request ID: {request_id}]: {exc.errors()}"
        )

        content = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details,
                "timestamp": timestamp,
                "path": path,
                "request_id": request_id,
            }
        }
        return JSONResponse(
            status_code=422,
            content=content,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        request_id = request_id_ctx.get()
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        path = request.url.path

        # Map standard FastAPI/Starlette HTTPException status codes to machine-readable error codes
        code_map = {
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "RESOURCE_NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")

        logger.warning(
            f"HTTPException {code} ({exc.status_code}) on {request.method} {path} [Request ID: {request_id}]: {exc.detail}"
        )

        content = {
            "error": {
                "code": code,
                "message": str(exc.detail),
                "details": None,
                "timestamp": timestamp,
                "path": path,
                "request_id": request_id,
            }
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    @app.exception_handler(Exception)
    async def catch_all_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = request_id_ctx.get()
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        path = request.url.path

        # Always log unhandled exceptions with full stack trace as an error
        logger.error(
            f"Unhandled exception on {request.method} {path} [Request ID: {request_id}]: {exc}\n"
            f"{''.join(traceback.format_exception(None, exc, exc.__traceback__))}"
        )

        content = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected internal server error occurred",
                "details": None,
                "timestamp": timestamp,
                "path": path,
                "request_id": request_id,
            }
        }
        return JSONResponse(
            status_code=500,
            content=content,
        )
