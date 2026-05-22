from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import EntityMixin
from src.entities.role_permission_entity import RolePermissionEntity
from src.entities.user_role_entity import UserRoleEntity
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class RoleEntity(EntityMixin):
    __tablename__ = 'roles'

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )

    permissions: Mapped[list['PermissionEntity']] = relationship(  # noqa: F821
        secondary=lambda: RolePermissionEntity.__table__,
        init=False,
        default_factory=list,
        lazy='noload',
    )
    users: Mapped[list['UserEntity']] = relationship(  # noqa: F821
        secondary=lambda: UserRoleEntity.__table__,
        back_populates='roles',
        init=False,
        default_factory=list,
        lazy='noload',
    )
