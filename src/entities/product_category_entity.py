from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class ProductCategoryEntity(EntityMixin):
    __tablename__ = 'product_categories'
    __table_args__ = (UniqueConstraint('slug', 'parent_id'),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey('product_categories.id'), nullable=True, index=True, default=None
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @property
    def is_global(self) -> bool:
        return self.is_default

    parent: Mapped['ProductCategoryEntity | None'] = relationship(
        'ProductCategoryEntity',
        remote_side='ProductCategoryEntity.id',
        back_populates='children',
        init=False,
    )
    children: Mapped[list['ProductCategoryEntity']] = relationship(
        'ProductCategoryEntity',
        back_populates='parent',
        init=False,
        cascade='all, delete-orphan',
    )
