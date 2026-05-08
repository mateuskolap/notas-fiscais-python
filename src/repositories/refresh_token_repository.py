from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.refresh_token_entity import RefreshTokenModel
from src.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshTokenModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshTokenModel, session)

    async def find_valid_token(self, token: str) -> RefreshTokenModel | None:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            self
            ._base_query()
            .where(RefreshTokenModel.token == token)
            .where(RefreshTokenModel.revoked_at.is_(None))
            .where(RefreshTokenModel.expires_at > now)
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token: RefreshTokenModel) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            self
            ._base_query()
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.revoked_at.is_(None))
            .where(RefreshTokenModel.expires_at > now)
        )
        active_tokens = result.scalars().all()

        for token in active_tokens:
            token.revoked_at = now

        if active_tokens:
            await self.session.commit()
