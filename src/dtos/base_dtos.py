from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, ConfigDict


class BaseReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseWriteDTO(BaseModel):
    model_config = ConfigDict(extra='forbid')


class BaseFilterParams(BaseModel):
    model_config = ConfigDict(extra='forbid')

    order_by: Annotated[str | None, Query(description='Field to order by')] = None
    order_dir: Annotated[
        Literal['asc', 'desc'], Query(description='Order direction')
    ] = 'desc'
