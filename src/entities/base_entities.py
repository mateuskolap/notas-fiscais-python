from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class ModelMixin:
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, init=False
    )


@table_registry.mapped_as_dataclass()
class SoftDeleteMixin(ModelMixin):
    __abstract__ = True

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, init=False, default=None
    )

    def delete(self):
        self.deleted_at = datetime.now()

    def restore(self):
        self.deleted_at = None

    @property
    def is_deleted(self):
        return self.deleted_at is not None
