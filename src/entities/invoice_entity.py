from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import SoftDeleteEntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class InvoiceEntity(SoftDeleteEntityMixin):
    __tablename__ = 'invoices'
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'source_url', name='uq_invoices_user_id_source_url'
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False, index=True
    )
    total_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    establishment_id: Mapped[int | None] = mapped_column(
        ForeignKey('establishments.id'), nullable=True, index=True, default=None
    )
    source_url: Mapped[str | None] = mapped_column(
        Text, nullable=True, index=True, default=None
    )
    is_manual: Mapped[bool] = mapped_column(default=False, server_default='false')
    is_edited_manually: Mapped[bool] = mapped_column(
        default=False, server_default='false'
    )

    establishment: Mapped[Optional['EstablishmentEntity']] = relationship(  # noqa: F821
        back_populates='invoices', init=False, lazy='joined'
    )
    user: Mapped['UserEntity'] = relationship(  # noqa: F821
        init=False, lazy='noload'
    )
    items: Mapped[list['InvoiceItemEntity']] = relationship(  # noqa: F821
        back_populates='invoice', init=False, default_factory=list, lazy='noload'
    )
