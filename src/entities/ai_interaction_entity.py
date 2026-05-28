from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base_entities import EntityMixin
from src.enums.ai_enum import AiInteractionStatusEnum, AiProviderEnum, AiTaskTypeEnum
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class AiInteractionEntity(EntityMixin):
    __tablename__ = 'ai_interactions'

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'), nullable=True, index=True, default=None
    )
    provider: Mapped[AiProviderEnum] = mapped_column(
        Enum(AiProviderEnum, native_enum=False, length=100), nullable=False, index=True
    )
    task_type: Mapped[AiTaskTypeEnum] = mapped_column(
        Enum(AiTaskTypeEnum, native_enum=False, length=100), nullable=False, index=True
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    input_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )
    output_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )
    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), nullable=True, default=None
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )
    status: Mapped[AiInteractionStatusEnum] = mapped_column(
        Enum(AiInteractionStatusEnum, native_enum=False, length=20),
        nullable=False,
        default=AiInteractionStatusEnum.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
