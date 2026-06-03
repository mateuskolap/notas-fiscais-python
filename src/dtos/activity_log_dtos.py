from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.dtos.base_dtos import BaseFilterParams, BaseReadDTO


class ActivityLogRead(BaseReadDTO):
    id: int
    log_name: str
    description: str
    subject_type: str
    subject_id: int | None
    causer_type: str | None
    causer_id: int | None
    event: str
    old_properties: dict[str, Any] | None
    new_properties: dict[str, Any] | None
    created_at: datetime


class ActivityLogFilterParams(BaseFilterParams):
    model_config = ConfigDict(extra='forbid')

    subject_type: str | None = Field(default=None, description='Filter by entity type')
    subject_id: int | None = Field(default=None, description='Filter by entity ID')
    causer_id: int | None = Field(
        default=None, description='Filter by user who caused the action'
    )
    event: str | None = Field(
        default=None, description='Filter by event type (created, updated, deleted)'
    )
    date_from: datetime | None = Field(
        default=None, description='Filter logs from this date'
    )
    date_to: datetime | None = Field(
        default=None, description='Filter logs until this date'
    )


class ActivityLogSubjectParams(BaseModel):
    model_config = ConfigDict(extra='forbid')

    subject_type: str
    subject_id: int
