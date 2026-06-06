from typing import Any, Sequence

from sqlalchemy import Row, and_, desc, func, select
from sqlalchemy.orm import aliased

from src.entities.canonical_product_entity import CanonicalProductEntity
from src.entities.establishment_entity import EstablishmentEntity
from src.entities.invoice_entity import InvoiceEntity
from src.entities.invoice_item_entity import InvoiceItemEntity
from src.entities.product_match_entity import ProductMatchEntity
from src.entities.user_product_override_entity import UserProductOverrideEntity
from src.repositories.base_repository import BaseRepository


class CanonicalProductRepository(
    BaseRepository[CanonicalProductEntity], model=CanonicalProductEntity
):
    async def find_by_fingerprint(
        self, fingerprint: str
    ) -> CanonicalProductEntity | None:
        return await self.find_one_by(fingerprint=fingerprint)

    async def find_by_fingerprints(
        self, fingerprints: list[str]
    ) -> Sequence[CanonicalProductEntity]:
        query = self._base_query().where(
            CanonicalProductEntity.fingerprint.in_(fingerprints)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def search_normalized_products(
        self, user_id: int, query_text: str | None, brand: str | None
    ) -> Sequence[Row[Any]]:
        Override = aliased(UserProductOverrideEntity)
        Match = aliased(ProductMatchEntity)
        Item = aliased(InvoiceItemEntity)
        Invoice = aliased(InvoiceEntity)
        Canonical = aliased(CanonicalProductEntity)

        effective_name = func.coalesce(Override.custom_name, Canonical.normalized_name)
        effective_brand = func.coalesce(Override.custom_brand, Canonical.brand)

        query = (
            select(
                Canonical.id,
                effective_name.label('name'),
                effective_brand.label('brand'),
                Canonical.quantity_label,
                Canonical.variant,
                func.avg(Item.unit_price).label('avg_price'),
                func.min(Item.unit_price).label('min_price'),
                func.max(Item.unit_price).label('max_price'),
                func.count(func.distinct(Invoice.establishment_id)).label(
                    'market_count'
                ),
            )
            .select_from(Canonical)
            .join(Match, Match.canonical_product_id == Canonical.id)
            .join(Item, Item.id == Match.invoice_item_id)
            .join(Invoice, Invoice.id == Item.invoice_id)
            .outerjoin(
                Override,
                and_(
                    Override.canonical_product_id == Canonical.id,
                    Override.user_id == user_id,
                ),
            )
            .where(Invoice.user_id == user_id)
        )

        if query_text:
            query = query.where(effective_name.ilike(f'%{query_text}%'))

        if brand:
            query = query.where(effective_brand.ilike(f'%{brand}%'))

        query = query.group_by(
            Canonical.id,
            effective_name,
            effective_brand,
            Canonical.quantity_label,
            Canonical.variant,
        ).limit(50)

        result = await self.session.execute(query)
        return result.all()

    async def get_product_with_override(
        self, user_id: int, canonical_product_id: int
    ) -> Row[Any] | None:
        Override = aliased(UserProductOverrideEntity)
        Canonical = aliased(CanonicalProductEntity)

        product_query = (
            select(Canonical, Override)
            .outerjoin(
                Override,
                and_(
                    Override.canonical_product_id == Canonical.id,
                    Override.user_id == user_id,
                ),
            )
            .where(Canonical.id == canonical_product_id)
        )

        product_res = await self.session.execute(product_query)
        return product_res.first()

    async def get_price_comparison_by_market(
        self, user_id: int, canonical_product_id: int
    ) -> Sequence[Row[Any]]:
        Match = aliased(ProductMatchEntity)
        Item = aliased(InvoiceItemEntity)
        Invoice = aliased(InvoiceEntity)
        Establishment = aliased(EstablishmentEntity)

        subq = (
            select(
                Establishment.name.label('market_name'),
                Item.unit_price,
                Invoice.issued_at,
                func
                .row_number()
                .over(
                    partition_by=Establishment.id,
                    order_by=desc(Invoice.issued_at),
                )
                .label('rn'),
            )
            .select_from(Match)
            .join(Item, Item.id == Match.invoice_item_id)
            .join(Invoice, Invoice.id == Item.invoice_id)
            .join(Establishment, Establishment.id == Invoice.establishment_id)
            .where(
                and_(
                    Match.canonical_product_id == canonical_product_id,
                    Invoice.user_id == user_id,
                )
            )
            .subquery()
        )

        query = (
            select(subq.c.market_name, subq.c.unit_price, subq.c.issued_at)
            .where(subq.c.rn == 1)
            .order_by(subq.c.unit_price)
        )

        result = await self.session.execute(query)
        return result.all()

    async def get_price_history(
        self, user_id: int, canonical_product_id: int
    ) -> Sequence[Row[Any]]:
        Match = aliased(ProductMatchEntity)
        Item = aliased(InvoiceItemEntity)
        Invoice = aliased(InvoiceEntity)
        Establishment = aliased(EstablishmentEntity)

        query = (
            select(
                Invoice.issued_at,
                Item.unit_price,
                Establishment.name.label('market_name'),
            )
            .select_from(Match)
            .join(Item, Item.id == Match.invoice_item_id)
            .join(Invoice, Invoice.id == Item.invoice_id)
            .join(Establishment, Establishment.id == Invoice.establishment_id)
            .where(
                and_(
                    Match.canonical_product_id == canonical_product_id,
                    Invoice.user_id == user_id,
                )
            )
            .order_by(Invoice.issued_at)
        )

        result = await self.session.execute(query)
        return result.all()
