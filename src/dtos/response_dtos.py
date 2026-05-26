from pydantic import BaseModel, ConfigDict


class FieldError(BaseModel):
    field: str
    message: str
    type: str


class ErrorDetails(BaseModel):
    fields: list[FieldError] | None = None
    model_config = ConfigDict(extra="allow")


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict | None = None
    timestamp: str
    path: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody
