from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorDetail(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorDetail]
