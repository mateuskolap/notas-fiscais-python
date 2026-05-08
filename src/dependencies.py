from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.user_actions import UserActions
from src.repositories.database import get_session
from src.repositories.user_repository import UserRepository

Session = Annotated[AsyncSession, Depends(get_session)]


async def get_user_repository(session: Session) -> UserRepository:
    return UserRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]


async def get_user_actions(repository: UserRepo) -> UserActions:
    return UserActions(repository)


UserAct = Annotated[UserActions, Depends(get_user_actions)]
