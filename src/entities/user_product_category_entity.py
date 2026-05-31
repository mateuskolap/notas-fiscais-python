from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class UserProductCategoryEntity(EntityMixin):
    __tablename__ = 'user_product_categories'
    __table_args__ = (
        UniqueConstraint('user_id', 'category_id', name='uq_user_category'),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey('product_categories.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        default=None,
    )
    custom_name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    custom_slug: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    custom_parent_id: Mapped[int | None] = mapped_column(
        ForeignKey('user_product_categories.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        default=None,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped['UserEntity'] = relationship(init=False)  # noqa: F821
    category: Mapped['ProductCategoryEntity | None'] = relationship(init=False)  # noqa: F821
    custom_parent: Mapped['UserProductCategoryEntity | None'] = relationship(
        'UserProductCategoryEntity',
        remote_side='UserProductCategoryEntity.id',
        back_populates='custom_children',
        init=False,
    )
    custom_children: Mapped[list['UserProductCategoryEntity']] = relationship(
        'UserProductCategoryEntity',
        back_populates='custom_parent',
        init=False,
        cascade='all, delete-orphan',
    )
