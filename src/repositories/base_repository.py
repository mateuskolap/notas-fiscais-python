from typing import Generic, Sequence, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.base_entities import SoftDeleteEntityMixin

T = TypeVar('T')


class BaseRepository(Generic[T]):
    _model: type[T]

    def __init_subclass__(cls, model: type | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if model is not None:
            cls._model = model

    def __init__(self, session: AsyncSession):
        if not hasattr(self, "model") or getattr(self, "model", None) is None:
            self.model = getattr(self, "_model", None)
        self.session = session

    @property
    def _is_soft_deletable(self) -> bool:
        return issubclass(self.model, SoftDeleteEntityMixin)

    def _base_query(self):
        query = select(self.model)

        if self._is_soft_deletable:
            query = query.where(self.model.deleted_at.is_(None))  # type: ignore

        return query

    async def find_all(self) -> Sequence[T]:
        result = await self.session.execute(self._base_query())
        return result.scalars().unique().all()

    async def _paginate_query(
        self, query, page: int = 1, per_page: int = 20
    ) -> tuple[Sequence[T], int]:
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        offset = (page - 1) * per_page
        items = (
            (await self.session.execute(query.offset(offset).limit(per_page)))
            .scalars()
            .unique()
            .all()
        )
        return items, total

    async def find_paginated(
        self, page: int = 1, per_page: int = 20
    ) -> tuple[Sequence[T], int]:
        return await self._paginate_query(self._base_query(), page, per_page)

    async def find_one_by(self, **kwargs) -> T | None:
        query = self._base_query()
        for field, value in kwargs.items():
            column = getattr(self.model, field)
            query = query.where(column == value)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_all_by(self, **kwargs) -> Sequence[T]:
        query = self._base_query()
        for field, value in kwargs.items():
            column = getattr(self.model, field)
            query = query.where(column == value)
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def find_by_id(self, id: int) -> T | None:
        result = await self.session.execute(
            self._base_query().where(self.model.id == id)  # type: ignore
        )
        return result.unique().scalar_one_or_none()

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def create_bulk(self, entities: list[T]) -> list[T]:
        self.session.add_all(entities)
        await self.session.commit()
        for entity in entities:
            await self.session.refresh(entity)
        return entities

    async def update(self, entity: T) -> T:
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        if self._is_soft_deletable and isinstance(entity, SoftDeleteEntityMixin):
            entity.delete()
            await self.session.commit()
        else:
            await self.session.delete(entity)
            await self.session.commit()
