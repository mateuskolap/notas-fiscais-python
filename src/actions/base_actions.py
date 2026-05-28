from typing import Awaitable, Callable, Generic, Sequence, TypeVar

from src.dtos.pagination_dtos import PaginatedResponse
from src.exceptions.base_exceptions import NotFoundException
from src.repositories.base_repository import BaseRepository

T = TypeVar('T')


class BaseActions(Generic[T]):
    def __init__(self, repository: BaseRepository[T], entity_name: str = 'Entity'):
        self.repository = repository
        self._entity_name = entity_name

    async def _get_or_raise(
        self,
        id: int | None = None,
        *,
        finder: Callable | None = None,
        message: str | None = None,
        resource_name: str | None = None,
    ) -> T:
        if finder:
            entity = await finder()
        elif id is not None:
            entity = await self.repository.find_by_id(id)
        else:
            raise ValueError('Either id or finder must be provided')

        if not entity:
            res_name = resource_name or self._entity_name
            details = {'resource': res_name}
            if id is not None:
                details['id'] = id
            raise NotFoundException(
                message or f'{res_name} not found',
                details=details,
            )
        return entity

    async def _paginated_query(
        self,
        finder: Callable[..., Awaitable[tuple[Sequence, int]]],
        page: int,
        per_page: int,
        **finder_kwargs,
    ) -> PaginatedResponse[T]:
        items, total = await finder(page=page, per_page=per_page, **finder_kwargs)
        return PaginatedResponse.create(
            items=list(items), total=total, page=page, per_page=per_page
        )

    async def list_paginated(
        self, page: int = 1, per_page: int = 20, filters=None
    ) -> PaginatedResponse[T]:
        return await self._paginated_query(
            self.repository.find_paginated, page, per_page, filters=filters
        )

    async def find(self, id: int) -> T:
        return await self._get_or_raise(id)

    async def delete(self, id: int) -> None:
        entity = await self._get_or_raise(id)
        await self.repository.delete(entity)
