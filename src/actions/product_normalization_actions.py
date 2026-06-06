import hashlib
import logging
import re
import unicodedata

from src.dtos.product_dtos import ProductOverrideRequest
from src.entities.canonical_product_entity import CanonicalProductEntity
from src.entities.invoice_item_entity import InvoiceItemEntity
from src.entities.product_match_entity import ProductMatchEntity
from src.entities.user_product_override_entity import UserProductOverrideEntity
from src.enums.product_match_method_enum import ProductMatchMethodEnum
from src.repositories.canonical_product_repository import CanonicalProductRepository
from src.repositories.product_category_repository import ProductCategoryRepository
from src.repositories.product_match_repository import ProductMatchRepository
from src.repositories.user_product_override_repository import (
    UserProductOverrideRepository,
)
from src.services.ai.product_normalization_service import ProductNormalizationService

logger = logging.getLogger(__name__)


def generate_fingerprint(description: str) -> str:
    cleaned = (
        unicodedata
        .normalize('NFKD', description)
        .encode('ASCII', 'ignore')
        .decode('ASCII')
    )
    cleaned = cleaned.upper().strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return hashlib.sha256(cleaned.encode()).hexdigest()


class ProductNormalizationActions:
    def __init__(
        self,
        match_repository: ProductMatchRepository,
        canonical_repository: CanonicalProductRepository,
        category_repository: ProductCategoryRepository,
        override_repository: UserProductOverrideRepository,
        normalization_service: ProductNormalizationService,
    ):
        self._match_repository = match_repository
        self._canonical_repository = canonical_repository
        self._category_repository = category_repository
        self._override_repository = override_repository
        self._normalization_service = normalization_service

    async def match_or_enqueue(self, invoice_items: list[InvoiceItemEntity]) -> None:
        if not invoice_items:
            return

        fingerprints = [
            generate_fingerprint(item.description) for item in invoice_items
        ]
        canonical_products = await self._canonical_repository.find_by_fingerprints(
            fingerprints
        )
        canonical_map = {p.fingerprint: p for p in canonical_products}

        matches_to_create = []
        for item in invoice_items:
            fp = generate_fingerprint(item.description)
            if fp in canonical_map:
                matches_to_create.append(
                    ProductMatchEntity(
                        invoice_item_id=item.id,
                        canonical_product_id=canonical_map[fp].id,
                        matched_by=ProductMatchMethodEnum.CACHE,
                    )
                )

        if matches_to_create:
            await self._match_repository.create_bulk(matches_to_create)

    async def normalize_unmatched_products(self, batch_size: int = 15) -> int:  # noqa: PLR0912, PLR0914
        unmatched_items = await self._match_repository.find_unmatched_items(
            limit=batch_size * 2
        )
        if not unmatched_items:
            return 0

        logger.info(
            f'Found {len(unmatched_items)} unmatched items to check for normalization.'
        )

        items_to_normalize = []
        fingerprints_to_check = []
        seen_fingerprints = set()

        for item in unmatched_items:
            fp = generate_fingerprint(item.description)
            if fp not in seen_fingerprints:
                seen_fingerprints.add(fp)
                fingerprints_to_check.append((fp, item))

        fps = [item[0] for item in fingerprints_to_check]
        existing_canonicals = await self._canonical_repository.find_by_fingerprints(fps)
        existing_fps = {p.fingerprint for p in existing_canonicals}

        for fp, item in fingerprints_to_check:
            if fp not in existing_fps:
                items_to_normalize.append(item)
                if len(items_to_normalize) >= batch_size:
                    break

        if not items_to_normalize:
            logger.info('No new unique items require AI normalization in this batch.')
            return 0

        unique_fingerprints = [
            generate_fingerprint(item.description) for item in items_to_normalize
        ]
        descriptions_to_normalize = [item.description for item in items_to_normalize]

        logger.info(
            f'Normalizing batch of {len(descriptions_to_normalize)} unique products with Gemini...'
        )
        normalized_results = await self._normalization_service.normalize_batch(
            descriptions_to_normalize
        )

        logger.info(f'AI processing returned {len(normalized_results)} results.')

        root_categories = await self._category_repository.find_root_categories()
        fallback_category_id = root_categories[0].id if root_categories else None

        created_count = 0
        for result in normalized_results:
            logger.info(
                f'Processing normalized result: {result.model_dump(mode="json") if hasattr(result, "model_dump") else result}'
            )
            if result.index < 0 or result.index >= len(unique_fingerprints):
                logger.error(f'Invalid index {result.index} returned from AI.')
                continue

            fp = unique_fingerprints[result.index]
            raw_desc = descriptions_to_normalize[result.index]

            category = None
            if result.category_slug:
                category = await self._category_repository.find_one_by(
                    slug=result.category_slug
                )

            category_id = category.id if category else fallback_category_id

            if category_id is None:
                logger.warning(f'No category found for {result.category_slug}')
                continue

            existing = await self._canonical_repository.find_by_fingerprint(fp)
            if not existing:
                canonical = CanonicalProductEntity(
                    raw_description=raw_desc,
                    normalized_name=result.normalized_name,
                    brand=result.brand,
                    quantity_label=result.quantity_label,
                    variant=result.variant,
                    unit_of_measure=result.unit_of_measure,
                    measure_value=result.measure_value,
                    category_id=category_id,
                    confidence_score=result.confidence,
                    fingerprint=fp,
                    ai_metadata=result.model_dump(mode='json')
                    if hasattr(result, 'model_dump')
                    else {},
                )
                await self._canonical_repository.create(canonical)
                created_count += 1
            else:
                logger.info(
                    f'Canonical product for fingerprint {fp} already exists, skipping creation.'
                )

        logger.info(
            f'AI normalization batch completed. Created {created_count} canonical products.'
        )
        return created_count

    async def match_unmatched_items(self, batch_size: int = 100) -> int:
        unmatched_items = await self._match_repository.find_unmatched_items(
            limit=batch_size
        )
        if not unmatched_items:
            return 0

        logger.info(
            f'Found {len(unmatched_items)} unmatched items to match with existing database catalog.'
        )

        fingerprints = [
            generate_fingerprint(item.description) for item in unmatched_items
        ]
        canonical_products = await self._canonical_repository.find_by_fingerprints(
            fingerprints
        )
        canonical_map = {p.fingerprint: p for p in canonical_products}

        matches_to_create = []
        for item in unmatched_items:
            fp = generate_fingerprint(item.description)
            if fp in canonical_map:
                matches_to_create.append(
                    ProductMatchEntity(
                        invoice_item_id=item.id,
                        canonical_product_id=canonical_map[fp].id,
                        matched_by=ProductMatchMethodEnum.AI,
                    )
                )

        if matches_to_create:
            logger.info(f'Creating {len(matches_to_create)} product matches.')
            await self._match_repository.create_bulk(matches_to_create)

        return len(matches_to_create)

    async def apply_user_override(
        self, user_id: int, canonical_product_id: int, data: ProductOverrideRequest
    ) -> UserProductOverrideEntity:
        override = await self._override_repository.find_by_user_and_product(
            user_id, canonical_product_id
        )

        if not override:
            override = UserProductOverrideEntity(
                user_id=user_id,
                canonical_product_id=canonical_product_id,
                custom_name=data.custom_name,
                custom_brand=data.custom_brand,
                custom_category_id=data.custom_category_id,
            )
            return await self._override_repository.create(override)
        else:
            if data.custom_name is not None:
                override.custom_name = data.custom_name
            if data.custom_brand is not None:
                override.custom_brand = data.custom_brand
            if data.custom_category_id is not None:
                override.custom_category_id = data.custom_category_id

            return await self._override_repository.update(override)

    async def remove_user_override(
        self, user_id: int, canonical_product_id: int
    ) -> None:
        override = await self._override_repository.find_by_user_and_product(
            user_id, canonical_product_id
        )
        if override:
            await self._override_repository.delete(override)
