from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class UserRoleEntity(EntityMixin):
    __tablename__ = 'user_roles'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True
    )

    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)
