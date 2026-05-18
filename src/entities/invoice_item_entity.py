from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import SoftDeleteEntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class InvoiceItemEntity(SoftDeleteEntityMixin):
    __tablename__ = 'invoice_items'

    invoice_id: Mapped[int] = mapped_column(ForeignKey('invoices.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    invoice: Mapped['InvoiceEntity'] = relationship(  # noqa: F821
        back_populates='items', init=False
    )
