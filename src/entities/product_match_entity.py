from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class ProductMatchEntity(EntityMixin):
    __tablename__ = 'product_matches'

    invoice_item_id: Mapped[int] = mapped_column(
        ForeignKey('invoice_items.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
    )
    canonical_product_id: Mapped[int] = mapped_column(
        ForeignKey('canonical_products.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    matched_by: Mapped[str] = mapped_column(String(20), nullable=False)

    invoice_item: Mapped['InvoiceItemEntity'] = relationship(  # noqa: F821
        back_populates='product_match', init=False
    )
    canonical_product: Mapped['CanonicalProductEntity'] = relationship(  # noqa: F821
        back_populates='matches', init=False
    )
