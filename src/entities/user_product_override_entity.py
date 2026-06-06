from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import SoftDeleteEntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class UserProductOverrideEntity(SoftDeleteEntityMixin):
    __tablename__ = 'user_product_overrides'
    __table_args__ = (
        UniqueConstraint('user_id', 'canonical_product_id', name='uq_user_override'),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    canonical_product_id: Mapped[int] = mapped_column(
        ForeignKey('canonical_products.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    custom_category_id: Mapped[int | None] = mapped_column(
        ForeignKey('product_categories.id', ondelete='SET NULL'),
        nullable=True,
        default=None,
    )
    custom_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    custom_brand: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )

    user: Mapped['UserEntity'] = relationship(init=False)  # noqa: F821
    canonical_product: Mapped['CanonicalProductEntity'] = relationship(init=False)  # noqa: F821
    custom_category: Mapped['ProductCategoryEntity | None'] = relationship(init=False)  # noqa: F821
