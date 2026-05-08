from typing import Generic, Sequence, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.base_entities import SoftDeleteMixin

T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    @property
    def _is_soft_deletable(self) -> bool:
        return issubclass(self.model, SoftDeleteMixin)

    def _base_query(self):
        query = select(self.model)

        if self._is_soft_deletable:
            query = query.where(self.model.deleted_at.is_(None))  # type: ignore

        return query

    async def find_all(self) -> Sequence[T]:
        result = await self.session.execute(self._base_query())
        return result.scalars().all()

    async def find_paginated(
        self, page: int = 1, per_page: int = 20
    ) -> tuple[Sequence[T], int]:
        query = self._base_query()

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        offset = (page - 1) * per_page
        items = (
            (await self.session.execute(query.offset(offset).limit(per_page)))
            .scalars()
            .all()
        )

        return items, total

    async def find_by_id(self, id: int) -> T | None:
        result = await self.session.execute(
            self._base_query().where(self.model.id == id)  # type: ignore
        )
        return result.scalar_one_or_none()

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        if self._is_soft_deletable and isinstance(entity, SoftDeleteMixin):
            entity.delete()
            await self.session.commit()
        else:
            await self.session.delete(entity)
            await self.session.commit()
