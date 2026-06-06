from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class CanonicalProductEntity(EntityMixin):
    __tablename__ = 'canonical_products'

    # Required Fields
    raw_description: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('product_categories.id'), nullable=False, index=True
    )
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    fingerprint: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )

    # Optional Fields
    brand: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, default=None
    )
    quantity_label: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=None
    )
    variant: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    unit_of_measure: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default=None
    )
    measure_value: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), nullable=True, default=None
    )
    ai_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)

    category: Mapped['ProductCategoryEntity'] = relationship(init=False)  # noqa: F821
    matches: Mapped[list['ProductMatchEntity']] = relationship(  # noqa: F821
        back_populates='canonical_product', init=False
    )
