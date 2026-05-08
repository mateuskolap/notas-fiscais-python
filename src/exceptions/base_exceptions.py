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


class ValidationException(AppException):
    """Business rule validation failed."""

    pass
