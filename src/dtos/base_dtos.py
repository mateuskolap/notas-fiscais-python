from typing import Literal

from pydantic import BaseModel, ConfigDict


class BaseReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseWriteDTO(BaseModel):
    model_config = ConfigDict(extra='forbid')


class BaseFilterParams(BaseModel):
    model_config = ConfigDict(extra='forbid')

    order_by: str | None = None
    order_dir: Literal['asc', 'desc'] = 'desc'
