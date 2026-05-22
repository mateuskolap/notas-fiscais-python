from datetime import datetime, timezone

from src.entities.refresh_token_entity import RefreshTokenEntity
from src.repositories.base_repository import BaseRepository


class RefreshTokenRepository(
    BaseRepository[RefreshTokenEntity], model=RefreshTokenEntity
):
    async def find_valid_token(self, token: str) -> RefreshTokenEntity | None:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            self
            ._base_query()
            .where(RefreshTokenEntity.token == token)
            .where(RefreshTokenEntity.revoked_at.is_(None))
            .where(RefreshTokenEntity.expires_at > now)
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token: RefreshTokenEntity) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            self
            ._base_query()
            .where(RefreshTokenEntity.user_id == user_id)
            .where(RefreshTokenEntity.revoked_at.is_(None))
            .where(RefreshTokenEntity.expires_at > now)
        )
        active_tokens = result.scalars().all()

        for token in active_tokens:
            token.revoked_at = now

        if active_tokens:
            await self.session.commit()

    async def revoke_expired_user_tokens(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            self
            ._base_query()
            .where(RefreshTokenEntity.user_id == user_id)
            .where(RefreshTokenEntity.revoked_at.is_(None))
            .where(RefreshTokenEntity.expires_at <= now)
        )
        expired_tokens = result.scalars().all()

        for token in expired_tokens:
            token.revoked_at = now

        if expired_tokens:
            await self.session.commit()
