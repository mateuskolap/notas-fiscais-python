from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base_entities import EntityMixin
from src.enums.permission_enum import PermissionEnum
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class PermissionEntity(EntityMixin):
    __tablename__ = 'permissions'

    name: Mapped[PermissionEnum] = mapped_column(
        Enum(PermissionEnum, native_enum=False, length=255), nullable=False
    )
