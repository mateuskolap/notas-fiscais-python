import asyncio
import sys
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry

from src.settings import settings

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore


engine = create_async_engine(settings.database_url)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


table_registry = registry()
