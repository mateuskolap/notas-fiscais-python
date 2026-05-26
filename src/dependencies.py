from typing import Annotated, Type, TypeVar

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.auth_actions import AuthActions
from src.actions.establishment_actions import EstablishmentActions
from src.actions.invoice_actions import InvoiceActions
from src.actions.nfce_actions import NfceActions
from src.actions.role_actions import RoleActions
from src.actions.user_actions import UserActions
from src.entities.user_entity import UserEntity
from src.enums.permission_enum import PermissionEnum
from src.exceptions.base_exceptions import ForbiddenException, UnauthorizedException
from src.repositories.database import get_session
from src.repositories.establishment_repository import EstablishmentRepository
from src.repositories.invoice_item_repository import InvoiceItemRepository
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.permission_repository import PermissionRepository
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.services.nfce.extractor import NfceExtractorFactory
from src.services.nfce.fetcher import NfcePageFetcher
from src.services.token_service import decode_access_token
from src.settings import settings

Session = Annotated[AsyncSession, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


T = TypeVar('T')


def _repository_dependency(repo_class: Type[T]):
    async def _get_repository(session: Session) -> T:
        return repo_class(session)

    _get_repository.__name__ = f'get_{repo_class.__name__.lower()}'
    return _get_repository


UserRepo = Annotated[UserRepository, Depends(_repository_dependency(UserRepository))]


async def get_user_actions(repository: UserRepo) -> UserActions:
    return UserActions(repository)


UserAct = Annotated[UserActions, Depends(get_user_actions)]

RefreshTokenRepo = Annotated[
    RefreshTokenRepository, Depends(_repository_dependency(RefreshTokenRepository))
]


async def get_auth_actions(
    user_repo: UserRepo, token_repo: RefreshTokenRepo
) -> AuthActions:
    return AuthActions(user_repo, token_repo)


AuthAct = Annotated[AuthActions, Depends(get_auth_actions)]


async def get_nfce_actions() -> NfceActions:
    return NfceActions(NfcePageFetcher(), NfceExtractorFactory())


NfceAct = Annotated[NfceActions, Depends(get_nfce_actions)]


EstablishmentRepo = Annotated[
    EstablishmentRepository,
    Depends(_repository_dependency(EstablishmentRepository)),
]

InvoiceRepo = Annotated[
    InvoiceRepository, Depends(_repository_dependency(InvoiceRepository))
]
InvoiceRepo = Annotated[
    InvoiceRepository, Depends(_repository_dependency(InvoiceRepository))
]

InvoiceItemRepo = Annotated[
    InvoiceItemRepository, Depends(_repository_dependency(InvoiceItemRepository))
]
InvoiceItemRepo = Annotated[
    InvoiceItemRepository, Depends(_repository_dependency(InvoiceItemRepository))
]


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
        raise UnauthorizedException('User not found', details={"user_id": user_id})
    return user


CurrentUser = Annotated[UserEntity, Depends(get_current_user)]


RoleRepo = Annotated[RoleRepository, Depends(_repository_dependency(RoleRepository))]
PermissionRepo = Annotated[
    PermissionRepository, Depends(_repository_dependency(PermissionRepository))
]


async def get_role_actions(
    repository: RoleRepo,
    permission_repo: PermissionRepo,
    user_repo: UserRepo,
) -> RoleActions:
    return RoleActions(repository, permission_repo, user_repo)


RoleAct = Annotated[RoleActions, Depends(get_role_actions)]


def require_permission(permission: PermissionEnum):
    async def dependency(
        current_user: CurrentUser,
        role_actions: RoleAct,
    ) -> UserEntity:
        user_perms = await role_actions.get_user_permissions(current_user.id)
        if permission.value not in user_perms:
            raise ForbiddenException('Permission denied', details={"required_permission": permission.value})
        return current_user

    return dependency


async def get_establishment_actions(
    repository: EstablishmentRepo,
) -> EstablishmentActions:
    return EstablishmentActions(repository)


EstablishmentAct = Annotated[EstablishmentActions, Depends(get_establishment_actions)]
