from src.dtos.establishment_dtos import EstablishmentFilterParams
from src.entities.establishment_entity import EstablishmentEntity
from src.entities.invoice_entity import InvoiceEntity
from src.repositories.base_repository import BaseRepository


class EstablishmentRepository(
    BaseRepository[EstablishmentEntity], model=EstablishmentEntity
):
    async def find_by_tin(self, business_tin: str) -> EstablishmentEntity | None:
        return await self.find_one_by(business_tin=business_tin)

    def _apply_filters(self, query, filters: EstablishmentFilterParams | None):
        if not filters:
            return query

        if filters.name:
            query = query.where(EstablishmentEntity.name.ilike(f'%{filters.name}%'))

        if filters.business_tin:
            query = query.where(
                EstablishmentEntity.business_tin.ilike(f'%{filters.business_tin}%')
            )

        if filters.related_only and filters.user_id is not None:
            query = query.where(
                EstablishmentEntity.invoices.any(
                    InvoiceEntity.user_id == filters.user_id
                )
            )

        return query
