from datetime import datetime

from sqlalchemy import DateTime, Integer, event, func
from sqlalchemy.orm import Mapped, Session, mapped_column, with_loader_criteria

from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class EntityMixin:
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, init=False
    )


@table_registry.mapped_as_dataclass()
class SoftDeleteEntityMixin(EntityMixin):
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


@event.listens_for(Session, 'do_orm_execute')
def _add_filtering_criteria(execute_state):
    if execute_state.is_select and not execute_state.is_column_load:
        if not execute_state.execution_options.get('include_deleted', False):
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    SoftDeleteEntityMixin,
                    lambda cls: cls.deleted_at.is_(None),
                    include_aliases=True,
                )
            )
