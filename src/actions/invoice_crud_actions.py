from src.dtos.invoice_dtos import (
    InvoiceItemManualCreate,
    InvoiceItemManualUpdate,
    InvoiceManualCreate,
    InvoiceManualUpdate,
)
from src.entities.invoice_entity import InvoiceEntity
from src.entities.invoice_item_entity import InvoiceItemEntity
from src.exceptions.base_exceptions import NotFoundException
from src.repositories.invoice_item_repository import InvoiceItemRepository
from src.repositories.invoice_repository import InvoiceRepository


class InvoiceCrudActions:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        invoice_item_repo: InvoiceItemRepository,
    ):
        self._invoice_repo = invoice_repo
        self._invoice_item_repo = invoice_item_repo

    async def _recalculate_invoice_totals(self, invoice_id: int) -> None:
        new_total = await self._invoice_item_repo.get_total_price_for_invoice(
            invoice_id
        )

        invoice = await self._invoice_repo.get(invoice_id)
        if not invoice:
            return

        invoice.total_value = new_total
        invoice.is_edited_manually = True
        invoice.discount_value = 0.0

        await self._invoice_repo.update(invoice_id, invoice)

    async def create_manual_invoice(
        self, user_id: int, data: InvoiceManualCreate
    ) -> InvoiceEntity:
        invoice = InvoiceEntity(
            user_id=user_id,
            establishment_id=data.establishment_id,
            source_url=None,
            total_value=data.total_value,
            discount_value=0.0,
            issued_at=data.issued_at,
            is_manual=True,
            is_edited_manually=True,
        )
        return await self._invoice_repo.create(invoice)

    async def update_manual_invoice(
        self, user_id: int, invoice_id: int, data: InvoiceManualUpdate
    ) -> InvoiceEntity:
        invoice = await self._invoice_repo.find_by_id_and_user(invoice_id, user_id)
        if not invoice:
            raise NotFoundException('Invoice not found.')

        if data.establishment_id is not None:
            invoice.establishment_id = data.establishment_id
        if data.issued_at is not None:
            invoice.issued_at = data.issued_at
        if data.total_value is not None:
            invoice.total_value = data.total_value

        return await self._invoice_repo.update(invoice_id, invoice)

    async def delete_manual_invoice(self, user_id: int, invoice_id: int) -> None:
        invoice = await self._invoice_repo.find_by_id_and_user(invoice_id, user_id)
        if not invoice:
            raise NotFoundException('Invoice not found.')

        await self._invoice_repo.delete(invoice)

    async def add_item_to_invoice(
        self, user_id: int, invoice_id: int, data: InvoiceItemManualCreate
    ) -> InvoiceItemEntity:
        invoice = await self._invoice_repo.find_by_id_and_user(invoice_id, user_id)
        if not invoice:
            raise NotFoundException('Invoice not found.')

        total_price = data.quantity * data.unit_price

        item = InvoiceItemEntity(
            invoice_id=invoice_id,
            description=data.description,
            code=data.code,
            unit=data.unit,
            quantity=data.quantity,
            unit_price=data.unit_price,
            total_price=total_price,
            is_manual=True,
        )
        created_item = await self._invoice_item_repo.create(item)

        await self._recalculate_invoice_totals(invoice_id)
        return created_item

    async def update_invoice_item(
        self, user_id: int, invoice_id: int, item_id: int, data: InvoiceItemManualUpdate
    ) -> InvoiceItemEntity:
        invoice = await self._invoice_repo.find_by_id_and_user(invoice_id, user_id)
        if not invoice:
            raise NotFoundException('Invoice not found.')

        item = await self._invoice_item_repo.get(item_id)
        if not item or item.invoice_id != invoice_id:
            raise NotFoundException('Invoice item not found.')

        if data.description is not None:
            item.description = data.description
        if data.code is not None:
            item.code = data.code
        if data.unit is not None:
            item.unit = data.unit

        if data.quantity is not None:
            item.quantity = data.quantity
        if data.unit_price is not None:
            item.unit_price = data.unit_price

        item.total_price = item.quantity * item.unit_price
        item.is_manual = True

        updated_item = await self._invoice_item_repo.update(item_id, item)
        await self._recalculate_invoice_totals(invoice_id)
        return updated_item

    async def delete_invoice_item(
        self, user_id: int, invoice_id: int, item_id: int
    ) -> None:
        invoice = await self._invoice_repo.find_by_id_and_user(invoice_id, user_id)
        if not invoice:
            raise NotFoundException('Invoice not found.')

        item = await self._invoice_item_repo.get(item_id)
        if not item or item.invoice_id != invoice_id:
            raise NotFoundException('Invoice item not found.')

        await self._invoice_item_repo.delete(item)
        await self._recalculate_invoice_totals(invoice_id)
