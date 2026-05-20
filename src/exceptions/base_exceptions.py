class AppException(Exception):
    """Base exception for application errors."""

    def __init__(self, detail: str):
        self.detail = detail


class NotFoundException(AppException):
    """Resource not found."""

    pass


class ConflictException(AppException):
    """Data conflict (e.g., duplicated unique key)."""

    pass


class UnauthorizedException(AppException):
    """Invalid credentials or missing authentication."""

    pass


class ForbiddenException(AppException):
    """Access to a resource that belongs to another user."""

    pass


class ValidationException(AppException):
    """Business rule validation failed."""

    pass


class NfceScrapingException(AppException):
    """Error while scraping NFC-e."""

    pass
