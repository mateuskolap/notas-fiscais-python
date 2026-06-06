from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import SoftDeleteEntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class EstablishmentEntity(SoftDeleteEntityMixin):
    __tablename__ = 'establishments'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_tin: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, index=True, default=None
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    is_manual: Mapped[bool] = mapped_column(default=False, server_default='false')

    invoices: Mapped[list['InvoiceEntity']] = relationship(  # noqa: F821
        back_populates='establishment', init=False, default_factory=list
    )
