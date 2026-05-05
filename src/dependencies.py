from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.database import get_session
from src.repositories.user_repository import UserRepository

Session = Annotated[AsyncSession, Depends(get_session)]


async def get_user_repository(session: Session) -> UserRepository:
    return UserRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
