from src.actions.base_actions import BaseActions
from src.actions.nfce_actions import NfceActions
from src.actions.product_normalization_actions import ProductNormalizationActions
from src.dtos.invoice_dtos import InvoiceFilterParams, InvoiceItemFilterParams
from src.dtos.pagination_dtos import PaginatedResponse
from src.entities.establishment_entity import EstablishmentEntity
from src.entities.invoice_entity import InvoiceEntity
from src.entities.invoice_item_entity import InvoiceItemEntity
from src.entities.user_entity import UserEntity
from src.exceptions.base_exceptions import ConflictException
from src.mappers import EntityMapper
from src.repositories.establishment_repository import EstablishmentRepository
from src.repositories.invoice_item_repository import InvoiceItemRepository
from src.repositories.invoice_repository import InvoiceRepository


class InvoiceActions(BaseActions[InvoiceEntity]):
    def __init__(
        self,
        nfce_actions: NfceActions,
        establishment_repo: EstablishmentRepository,
        invoice_repo: InvoiceRepository,
        invoice_item_repo: InvoiceItemRepository,
        product_normalization_actions: ProductNormalizationActions,
    ):
        super().__init__(invoice_repo, entity_name='Invoice')
        self.nfce_actions = nfce_actions
        self.establishment_repo = establishment_repo
        self.invoice_repo = invoice_repo
        self.invoice_item_repo = invoice_item_repo
        self.product_normalization_actions = product_normalization_actions

    async def list_paginated_by_user(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        filters: InvoiceFilterParams | None = None,
    ) -> PaginatedResponse[InvoiceEntity]:
        return await self._paginated_query(
            self.invoice_repo.find_paginated_by_user,
            page,
            per_page,
            user_id=user_id,
            filters=filters,
        )

    async def find_with_user_scoped(self, id: int, user_id: int) -> InvoiceEntity:
        return await self._get_or_raise(
            id=id,
            finder=lambda: self.invoice_repo.find_by_id_with_user_scoped(id, user_id),
            resource_name='Invoice',
        )

    async def list_items_paginated(
        self,
        invoice_id: int,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        filters: InvoiceItemFilterParams | None = None,
    ) -> PaginatedResponse[InvoiceItemEntity]:
        await self._get_or_raise(
            id=invoice_id,
            finder=lambda: self.invoice_repo.find_by_id_and_user(invoice_id, user_id),
            resource_name='Invoice',
        )
        return await self._paginated_query(
            self.invoice_item_repo.find_paginated_by_invoice,
            page,
            per_page,
            invoice_id=invoice_id,
            filters=filters,
        )

    async def extract_and_persist(self, url: str, user: UserEntity) -> InvoiceEntity:
        existing_invoice = await self.invoice_repo.find_by_url_and_user(url, user.id)
        if existing_invoice:
            raise ConflictException(
                'NFC-e already extracted and registered in the system.',
                details={'field': 'source_url', 'value': url},
            )

        parsed = await self.nfce_actions.parse(url)

        establishment = await self.establishment_repo.find_by_tin(
            parsed.establishment.business_tin
        )
        if not establishment:
            establishment = await self.establishment_repo.create(
                EstablishmentEntity(
                    name=parsed.establishment.name,
                    business_tin=parsed.establishment.business_tin,
                    address=parsed.establishment.address,
                )
            )

        invoice = await self.invoice_repo.create(
            InvoiceEntity(
                user_id=user.id,
                establishment_id=establishment.id,
                source_url=url,
                total_value=parsed.total_value,
                discount_value=parsed.discount_value,
                issued_at=parsed.issued_at,
            )
        )

        items_to_create = EntityMapper.to_entities(
            parsed.items,
            InvoiceItemEntity,
            description_transform=lambda d: d.upper(),
            invoice_id=invoice.id,
        )

        await self.invoice_item_repo.create_bulk(items_to_create)

        await self.product_normalization_actions.match_or_enqueue(items_to_create)

        return await self.invoice_repo.find_by_id(invoice.id)  # type: ignore
