from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class RefreshTokenEntity(EntityMixin):
    __tablename__ = 'refresh_tokens'

    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, init=False, default=None
    )
