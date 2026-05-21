from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base_entities import EntityMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class PermissionEntity(EntityMixin):
    __tablename__ = 'permissions'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
