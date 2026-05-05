from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base_entities import SoftDeleteMixin
from src.repositories.database import table_registry


@table_registry.mapped_as_dataclass()
class UserModel(SoftDeleteMixin):
    __tablename__ = 'users'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
