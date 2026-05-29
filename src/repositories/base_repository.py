from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.base_dtos import BaseFilterParams
from src.entities.base_entities import EntityMixin, SoftDeleteEntityMixin


class BaseRepository[T: EntityMixin]:
    _model: type[T]
    model: type[T]

    def __init_subclass__(cls, model: type | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if model is not None:
            cls._model = model

    def __init__(self, session: AsyncSession):
        if not hasattr(self, 'model') or getattr(self, 'model', None) is None:
            model = getattr(self, '_model', None)
            if model is None:
                raise ValueError(
                    f'Repository {self.__class__.__name__} must have a model defined.'
                )
            self.model = model
        self.session = session

    @property
    def _is_soft_deletable(self) -> bool:
        return issubclass(self.model, SoftDeleteEntityMixin)

    def _base_query(self):
        return select(self.model)

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

    def _apply_ordering(self, query, filters: BaseFilterParams | None):
        if filters and filters.order_by:
            column = getattr(self.model, filters.order_by)
            if filters.order_dir == 'desc':
                column = column.desc()
            else:
                column = column.asc()
            query = query.order_by(column)
        return query

    def _apply_filters(self, query, filters: BaseFilterParams | None):
        """Hook to apply specific filters in child repositories."""
        return query

    async def find_paginated(
        self, page: int = 1, per_page: int = 20, filters: BaseFilterParams | None = None
    ) -> tuple[Sequence[T], int]:
        query = self._base_query()
        if filters:
            query = self._apply_filters(query, filters)
            query = self._apply_ordering(query, filters)
        return await self._paginate_query(query, page, per_page)

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
            self._base_query().where(self.model.id == id)
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
