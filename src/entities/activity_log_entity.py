from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class ActivityLogEntity:
    __tablename__ = 'activity_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    subject_type: Mapped[str] = mapped_column(String(255), nullable=False)
    event: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    log_name: Mapped[str] = mapped_column(
        String(255), nullable=False, default='default'
    )
    subject_id: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    causer_type: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    causer_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None, index=True
    )
    old_properties: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=None
    )
    new_properties: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, init=False
    )
