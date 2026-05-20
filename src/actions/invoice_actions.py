from src.actions.base_actions import BaseActions
from src.actions.nfce_actions import NfceActions
from src.dtos.pagination_dtos import PaginatedResponse
from src.entities.establishment_entity import EstablishmentEntity
from src.entities.invoice_entity import InvoiceEntity
from src.entities.invoice_item_entity import InvoiceItemEntity
from src.entities.user_entity import UserEntity
from src.exceptions.base_exceptions import ConflictException, NotFoundException
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
    ):
        super().__init__(invoice_repo, entity_name='Invoice')
        self.nfce_actions = nfce_actions
        self.establishment_repo = establishment_repo
        self.invoice_repo = invoice_repo
        self.invoice_item_repo = invoice_item_repo

    async def list_paginated_by_user(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> PaginatedResponse[InvoiceEntity]:
        items, total = await self.invoice_repo.find_paginated_by_user(
            user_id, page, per_page
        )
        return PaginatedResponse.create(
            items=list(items), total=total, page=page, per_page=per_page
        )

    async def find_with_user_scoped(self, id: int, user_id: int) -> InvoiceEntity:
        entity = await self.invoice_repo.find_by_id_with_user_scoped(id, user_id)
        if not entity:
            raise NotFoundException(f'{self._entity_name} not found')
        return entity

    async def list_items_paginated(
        self, invoice_id: int, user_id: int, page: int = 1, per_page: int = 20
    ) -> PaginatedResponse[InvoiceItemEntity]:
        # Validate invoice exists and belongs to user
        invoice = await self.invoice_repo.find_by_id_and_user(invoice_id, user_id)
        if not invoice:
            raise NotFoundException(f'{self._entity_name} not found')
        items, total = await self.invoice_item_repo.find_paginated_by_invoice(
            invoice_id, page, per_page
        )
        return PaginatedResponse.create(
            items=list(items), total=total, page=page, per_page=per_page
        )

    async def extract_and_persist(self, url: str, user: UserEntity) -> InvoiceEntity:
        existing_invoice = await self.invoice_repo.find_by_url_and_user(url, user.id)
        if existing_invoice:
            raise ConflictException(
                'NFC-e already extracted and registered in the system.'
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

        items_to_create = [
            InvoiceItemEntity(
                invoice_id=invoice.id,
                description=item.description.upper(),
                code=item.code,
                unit=item.unit,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            for item in parsed.items
        ]

        await self.invoice_item_repo.create_bulk(items_to_create)

        return await self.invoice_repo.find_by_id(invoice.id)  # type: ignore
