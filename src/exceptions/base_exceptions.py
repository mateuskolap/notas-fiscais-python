from http import HTTPStatus


class AppException(Exception):
    """Base exception for application errors."""

    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
    error_code: str = "APP_ERROR"

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        details: dict | None = None,
    ):
        self.message = message
        if error_code:
            self.error_code = error_code
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found."""

    status_code = HTTPStatus.NOT_FOUND
    error_code = "RESOURCE_NOT_FOUND"


class ConflictException(AppException):
    """Data conflict (e.g., duplicated unique key)."""

    status_code = HTTPStatus.CONFLICT
    error_code = "RESOURCE_CONFLICT"


class UnauthorizedException(AppException):
    """Invalid credentials or missing authentication."""

    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "UNAUTHORIZED"


class ForbiddenException(AppException):
    """Access to a resource that belongs to another user."""

    status_code = HTTPStatus.FORBIDDEN
    error_code = "FORBIDDEN"


class ValidationException(AppException):
    """Business rule validation failed."""

    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"


class ExternalServiceException(AppException):
    """Error communicating with an external service."""

    status_code = HTTPStatus.BAD_GATEWAY
    error_code = "EXTERNAL_SERVICE_ERROR"


class NfceScrapingException(ExternalServiceException):
    """Error while scraping NFC-e."""
