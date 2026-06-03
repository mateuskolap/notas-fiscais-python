from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.base_dtos import BaseFilterParams
from src.entities.base_entities import SoftDeleteEntityMixin

T = TypeVar('T')

_DEFAULT_EXCLUDED_FIELDS = frozenset({
    'password',
    'deleted_at',
    'created_at',
    'updated_at',
})


class BaseRepository(Generic[T]):
    _model: type[T]
    _loggable: bool = True
    _log_excluded_fields: set[str] = set()

    def __init_subclass__(cls, model: type | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if model is not None:
            cls._model = model

    def __init__(self, session: AsyncSession):
        if not hasattr(self, 'model') or getattr(self, 'model', None) is None:
            self.model = getattr(self, '_model', None)
        self.session = session

    @property
    def _is_soft_deletable(self) -> bool:
        return issubclass(self.model, SoftDeleteEntityMixin)

    @property
    def _excluded_fields(self) -> frozenset[str]:
        return _DEFAULT_EXCLUDED_FIELDS | frozenset(self._log_excluded_fields)

    def _base_query(self):
        return select(self.model)

    # ──────────────────────────────────────────────
    # Activity Log helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Convert non-JSON-serializable types to JSON-safe values."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='replace')
        return value

    def _get_entity_properties(
        self, entity: T, *, use_committed: bool = False
    ) -> dict[str, Any]:
        """Extract loggable properties from an entity.

        When use_committed=True, returns the values that were last committed
        to the database (before pending changes).
        """
        mapper = inspect(type(entity))
        excluded = self._excluded_fields
        properties: dict[str, Any] = {}

        for col in mapper.columns:
            key = col.key
            if key in excluded:
                continue

            if use_committed:
                state = inspect(entity)
                committed = state.committed_state
                if key in committed:
                    properties[key] = self._serialize_value(committed[key])
                else:
                    properties[key] = self._serialize_value(getattr(entity, key))
            else:
                properties[key] = self._serialize_value(getattr(entity, key))

        return properties

    @staticmethod
    def _compute_diff(
        old: dict[str, Any] | None, new: dict[str, Any] | None
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """Compute only the changed fields between old and new states."""
        if old is None or new is None:
            return old, new

        diff_old: dict[str, Any] = {}
        diff_new: dict[str, Any] = {}

        all_keys = set(old.keys()) | set(new.keys())
        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                diff_old[key] = old_val
                diff_new[key] = new_val

        if not diff_old and not diff_new:
            return None, None

        return diff_old, diff_new

    async def _log_activity(
        self,
        event: str,
        entity: T,
        *,
        old_properties: dict[str, Any] | None = None,
        new_properties: dict[str, Any] | None = None,
    ) -> None:
        """Record an activity log entry for the given entity change."""
        if not self._loggable:
            return

        from src.entities.activity_log_entity import ActivityLogEntity
        from src.middleware import current_user_ctx

        entity_type = type(entity).__name__
        entity_id = getattr(entity, 'id', None)
        causer_id = current_user_ctx.get(None)

        description = f'{event} {entity_type}'
        if entity_id is not None:
            description += f' #{entity_id}'

        log = ActivityLogEntity(
            log_name='default',
            description=description,
            subject_type=entity_type,
            subject_id=entity_id,
            causer_type='UserEntity' if causer_id else None,
            causer_id=causer_id,
            event=event,
            old_properties=old_properties,
            new_properties=new_properties,
        )
        self.session.add(log)
        await self.session.flush()

    # ──────────────────────────────────────────────
    # Query methods (unchanged)
    # ──────────────────────────────────────────────

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
            self._base_query().where(self.model.id == id)  # type: ignore
        )
        return result.unique().scalar_one_or_none()

    # ──────────────────────────────────────────────
    # Mutating methods (with activity logging)
    # ──────────────────────────────────────────────

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        await self._log_activity(
            'created', entity, new_properties=self._get_entity_properties(entity)
        )
        await self.session.commit()
        return entity

    async def create_bulk(self, entities: list[T]) -> list[T]:
        self.session.add_all(entities)
        await self.session.commit()
        for entity in entities:
            await self.session.refresh(entity)
            await self._log_activity(
                'created', entity, new_properties=self._get_entity_properties(entity)
            )
        await self.session.commit()
        return entities

    async def update(self, entity: T) -> T:
        old_properties = self._get_entity_properties(entity, use_committed=True)
        await self.session.commit()
        await self.session.refresh(entity)
        new_properties = self._get_entity_properties(entity)
        diff_old, diff_new = self._compute_diff(old_properties, new_properties)
        if diff_old or diff_new:
            await self._log_activity(
                'updated', entity, old_properties=diff_old, new_properties=diff_new
            )
            await self.session.commit()
        return entity

    async def delete(self, entity: T) -> None:
        old_properties = self._get_entity_properties(entity)
        if self._is_soft_deletable and isinstance(entity, SoftDeleteEntityMixin):
            entity.delete()
            await self.session.commit()
        else:
            await self.session.delete(entity)
            await self.session.commit()
        await self._log_activity('deleted', entity, old_properties=old_properties)
        await self.session.commit()
