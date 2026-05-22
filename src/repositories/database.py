import asyncio
import sys
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry

from src.settings import settings
from src.entities.base_entities import SoftDeleteEntityMixin
from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    if execute_state.is_select and not execute_state.is_column_load:
        if not execute_state.execution_options.get("include_deleted", False):
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    SoftDeleteEntityMixin,
                    lambda cls: cls.deleted_at.is_(None),
                    include_aliases=True
                )
            )

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore


engine = create_async_engine(settings.database_url)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


table_registry = registry()
