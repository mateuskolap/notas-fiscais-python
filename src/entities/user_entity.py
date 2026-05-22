from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base_entities import SoftDeleteEntityMixin
from src.entities.user_role_entity import UserRoleEntity
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class UserEntity(SoftDeleteEntityMixin):
    __tablename__ = 'users'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    roles: Mapped[list['RoleEntity']] = relationship(  # noqa: F821
        secondary=lambda: UserRoleEntity.__table__,
        back_populates='users',
        init=False,
        default_factory=list,
        lazy='noload',
    )

    @property
    def permissions(self) -> list['PermissionEntity']:  # noqa: F821
        perms = {}
        for role in self.roles:
            for p in role.permissions:
                perms[p.id] = p
        return list(perms.values())
