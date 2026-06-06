import asyncio
import logging

from src.actions.product_normalization_actions import ProductNormalizationActions
from src.dependencies import _get_ai_provider  # noqa: PLC2701
from src.repositories.ai_interaction_repository import AiInteractionRepository
from src.repositories.canonical_product_repository import CanonicalProductRepository
from src.repositories.database import get_session
from src.repositories.product_category_repository import ProductCategoryRepository
from src.repositories.product_match_repository import ProductMatchRepository
from src.repositories.user_product_override_repository import (
    UserProductOverrideRepository,
)
from src.services.ai.ai_service import AiService
from src.services.ai.product_normalization_service import ProductNormalizationService
from src.worker import celery_app

logger = logging.getLogger(__name__)


async def run_normalization_batch():
    session_generator = get_session()
    session = await anext(session_generator)

    try:
        match_repo = ProductMatchRepository(session)
        canonical_repo = CanonicalProductRepository(session)
        category_repo = ProductCategoryRepository(session)
        override_repo = UserProductOverrideRepository(session)
        ai_interaction_repo = AiInteractionRepository(session)

        ai_provider = _get_ai_provider()
        ai_service = AiService(ai_provider, ai_interaction_repo)
        normalization_service = ProductNormalizationService(ai_service, category_repo)

        actions = ProductNormalizationActions(
            match_repo,
            canonical_repo,
            category_repo,
            override_repo,
            normalization_service,
        )

        logger.info('Starting AI product normalization task...')
        created_count = await actions.normalize_unmatched_products(batch_size=15)
        logger.info(
            f'Finished AI product normalization task. Created {created_count} canonical products.'
        )

        return created_count

    finally:
        await session.close()


async def run_matching_batch():
    session_generator = get_session()
    session = await anext(session_generator)

    try:
        match_repo = ProductMatchRepository(session)
        canonical_repo = CanonicalProductRepository(session)
        category_repo = ProductCategoryRepository(session)
        override_repo = UserProductOverrideRepository(session)

        actions = ProductNormalizationActions(
            match_repo,
            canonical_repo,
            category_repo,
            override_repo,
            None,  # type: ignore
        )

        logger.info('Starting database product matching task...')
        matched_count = await actions.match_unmatched_items(batch_size=100)
        logger.info(
            f'Finished database product matching task. Linked {matched_count} items.'
        )

        return matched_count

    finally:
        await session.close()


@celery_app.task(
    bind=True,
    name='normalize_pending_products',
    max_retries=3,
    default_retry_delay=60,
    rate_limit='10/m',
)
def normalize_pending_products(self):
    try:
        return asyncio.run(run_normalization_batch())
    except Exception as exc:
        logger.error(f'Error running AI normalization task: {exc}')
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name='match_pending_items',
    max_retries=3,
    default_retry_delay=30,
)
def match_pending_items(self):
    try:
        return asyncio.run(run_matching_batch())
    except Exception as exc:
        logger.error(f'Error running database matching task: {exc}')
        raise self.retry(exc=exc)
