from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.auth_actions import AuthActions
from src.actions.invoice_actions import InvoiceActions
from src.actions.nfce_actions import NfceActions
from src.actions.user_actions import UserActions
from src.entities.user_entity import UserEntity
from src.exceptions.base_exceptions import UnauthorizedException
from src.repositories.database import get_session
from src.repositories.establishment_repository import EstablishmentRepository
from src.repositories.invoice_item_repository import InvoiceItemRepository
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.services.nfce.extractor import NfceDataExtractor
from src.services.nfce.fetcher import NfcePageFetcher
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


async def get_nfce_actions() -> NfceActions:
    return NfceActions(NfcePageFetcher(), NfceDataExtractor())


NfceAct = Annotated[NfceActions, Depends(get_nfce_actions)]


async def get_establishment_repository(session: Session) -> EstablishmentRepository:
    return EstablishmentRepository(session)


EstablishmentRepo = Annotated[
    EstablishmentRepository, Depends(get_establishment_repository)
]


async def get_invoice_repository(session: Session) -> InvoiceRepository:
    return InvoiceRepository(session)


InvoiceRepo = Annotated[InvoiceRepository, Depends(get_invoice_repository)]


async def get_invoice_item_repository(session: Session) -> InvoiceItemRepository:
    return InvoiceItemRepository(session)


InvoiceItemRepo = Annotated[InvoiceItemRepository, Depends(get_invoice_item_repository)]


async def get_invoice_actions(
    nfce_actions: NfceAct,
    establishment_repo: EstablishmentRepo,
    invoice_repo: InvoiceRepo,
    invoice_item_repo: InvoiceItemRepo,
) -> InvoiceActions:
    return InvoiceActions(
        nfce_actions, establishment_repo, invoice_repo, invoice_item_repo
    )


InvoiceAct = Annotated[InvoiceActions, Depends(get_invoice_actions)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    repository: UserRepo,
) -> UserEntity:
    payload = decode_access_token(token, settings)
    user_id = int(payload['sub'])
    user = await repository.find_by_id(user_id)
    if not user:
        raise UnauthorizedException('User not found')
    return user


CurrentUser = Annotated[UserEntity, Depends(get_current_user)]
