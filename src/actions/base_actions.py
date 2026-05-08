from typing import Generic, TypeVar

from src.dtos.pagination_dtos import PaginatedResponse
from src.exceptions.base_exceptions import NotFoundException
from src.repositories.base_repository import BaseRepository

T = TypeVar('T')


class BaseActions(Generic[T]):
    def __init__(self, repository: BaseRepository[T], entity_name: str = 'Entity'):
        self.repository = repository
        self._entity_name = entity_name

    async def _get_or_raise(self, id: int) -> T:
        entity = await self.repository.find_by_id(id)
        if not entity:
            raise NotFoundException(f'{self._entity_name} not found')
        return entity

    async def list_paginated(
        self, page: int = 1, per_page: int = 20
    ) -> PaginatedResponse[T]:
        items, total = await self.repository.find_paginated(page, per_page)
        return PaginatedResponse.create(
            items=list(items), total=total, page=page, per_page=per_page
        )

    async def find(self, id: int) -> T:
        return await self._get_or_raise(id)

    async def delete(self, id: int) -> None:
        entity = await self._get_or_raise(id)
        await self.repository.delete(entity)
