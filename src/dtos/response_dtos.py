from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response for OpenAPI docs."""

    detail: str


class ValidationErrorDetail(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Standard validation error response for OpenAPI docs."""

    detail: list[ValidationErrorDetail]
