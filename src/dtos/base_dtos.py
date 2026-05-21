from pydantic import BaseModel, ConfigDict


class BaseReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseWriteDTO(BaseModel):
    model_config = ConfigDict(extra='forbid')
