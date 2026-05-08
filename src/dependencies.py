from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.auth_actions import AuthActions
from src.actions.user_actions import UserActions
from src.entities.user_entity import UserModel
from src.exceptions.base_exceptions import UnauthorizedException
from src.repositories.database import get_session
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.services.token_service import decode_access_token
from src.settings import settings

Session = Annotated[AsyncSession, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


async def get_user_repository(session: Session) -> UserRepository:
    return UserRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]


async def get_user_actions(repository: UserRepo) -> UserActions:
    return UserActions(repository)


UserAct = Annotated[UserActions, Depends(get_user_actions)]


async def get_refresh_token_repository(
    session: Session,
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


RefreshTokenRepo = Annotated[
    RefreshTokenRepository, Depends(get_refresh_token_repository)
]


async def get_auth_actions(
    user_repo: UserRepo, token_repo: RefreshTokenRepo
) -> AuthActions:
    return AuthActions(user_repo, token_repo)


AuthAct = Annotated[AuthActions, Depends(get_auth_actions)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    repository: UserRepo,
) -> UserModel:
    payload = decode_access_token(token, settings)
    user_id = int(payload['sub'])
    user = await repository.find_by_id(user_id)
    if not user:
        raise UnauthorizedException('User not found')
    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
