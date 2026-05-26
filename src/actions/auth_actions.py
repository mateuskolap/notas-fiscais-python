from datetime import datetime, timedelta, timezone

from src.dtos.auth_dtos import TokenResponse
from src.entities.refresh_token_entity import RefreshTokenEntity
from src.exceptions.base_exceptions import UnauthorizedException
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.services.password_service import verify_password
from src.services.token_service import create_access_token, generate_refresh_token
from src.settings import settings


class AuthActions:
    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.find_by_email(email)
        if not user or not verify_password(password, user.password):
            raise UnauthorizedException(
                'Incorrect email or password',
                details={"email": email}
            )

        return await self._generate_tokens_for_user(user.id)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        token = await self.token_repo.find_valid_token(refresh_token)
        if not token:
            raise UnauthorizedException(
                'Invalid or expired refresh token',
                details={"reason": "token_not_found_or_revoked"}
            )

        await self.token_repo.revoke_token(token)

        return await self._generate_tokens_for_user(token.user_id)

    async def logout(self, refresh_token: str) -> None:
        token = await self.token_repo.find_valid_token(refresh_token)
        if token:
            await self.token_repo.revoke_token(token)

    async def _generate_tokens_for_user(self, user_id: int) -> TokenResponse:
        await self.token_repo.revoke_expired_user_tokens(user_id)

        access_token = create_access_token(user_id, settings)
        refresh_token_str = generate_refresh_token()

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        new_refresh_token = RefreshTokenEntity(
            token=refresh_token_str,
            user_id=user_id,
            expires_at=expires_at,
        )

        await self.token_repo.create(new_refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
        )
