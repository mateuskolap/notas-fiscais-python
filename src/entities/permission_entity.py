from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from entities.base_entities import ModelMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class PermissionModel(ModelMixin):
    __tablename__ = 'permissions'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
