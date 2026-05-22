from http import HTTPStatus


class AppException(Exception):
    """Base exception for application errors."""
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, detail: str):
        self.detail = detail


class NotFoundException(AppException):
    """Resource not found."""
    status_code = HTTPStatus.NOT_FOUND


class ConflictException(AppException):
    """Data conflict (e.g., duplicated unique key)."""
    status_code = HTTPStatus.CONFLICT


class UnauthorizedException(AppException):
    """Invalid credentials or missing authentication."""
    status_code = HTTPStatus.UNAUTHORIZED


class ForbiddenException(AppException):
    """Access to a resource that belongs to another user."""
    status_code = HTTPStatus.FORBIDDEN


class ValidationException(AppException):
    """Business rule validation failed."""
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY


class NfceScrapingException(AppException):
    """Error while scraping NFC-e."""
    status_code = HTTPStatus.BAD_GATEWAY
