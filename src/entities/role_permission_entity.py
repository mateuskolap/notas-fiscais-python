from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class RolePermissionEntity(EntityMixin):
    __tablename__ = 'role_permissions'

    role_id: Mapped[int] = mapped_column(
        ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, index=True
    )

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
