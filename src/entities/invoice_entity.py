from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import SoftDeleteEntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class InvoiceEntity(SoftDeleteEntityMixin):
    __tablename__ = 'invoices'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False, index=True
    )
    establishment_id: Mapped[int] = mapped_column(
        ForeignKey('establishments.id'), nullable=False, index=True
    )
    source_url: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, index=True
    )
    total_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    establishment: Mapped['EstablishmentEntity'] = relationship(  # noqa: F821
        back_populates='invoices', init=False, lazy='joined'
    )
    user: Mapped['UserEntity'] = relationship(  # noqa: F821
        init=False, lazy='noload'
    )
    items: Mapped[list['InvoiceItemEntity']] = relationship(  # noqa: F821
        back_populates='invoice', init=False, default_factory=list, lazy='noload'
    )
