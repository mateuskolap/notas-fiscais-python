import json
import logging
from decimal import Decimal

from src.dtos.ai_dtos import AiCompletionRequest
from src.dtos.product_dtos import NormalizedProductResult
from src.enums.ai_enum import AiTaskTypeEnum
from src.repositories.product_category_repository import ProductCategoryRepository
from src.services.ai.ai_service import AiService

logger = logging.getLogger(__name__)


class ProductNormalizationService:
    def __init__(self, ai_service: AiService, category_repo: ProductCategoryRepository):
        self._ai_service = ai_service
        self._category_repo = category_repo

    async def normalize_batch(
        self, descriptions: list[str]
    ) -> list[NormalizedProductResult]:
        if not descriptions:
            return []

        categories = await self._category_repo.find_tree()
        categories_text = self._format_categories(categories)

        descriptions_text = '\n'.join(
            f'[{i}] {desc}' for i, desc in enumerate(descriptions)
        )

        system_prompt = f"""
        You are an expert in Brazilian supermarket products.

        Given the list of raw product descriptions from invoices below,
        extract the following information for EACH product:

        1. normalized_name: Clean generic name (e.g., "Arroz Parboilizado")
        2. brand: Brand of the product (e.g., "Camil"). Null if not identifiable.
        3. quantity_label: Quantity with unit (e.g., "5kg", "1L", "6un"). Null if not identifiable.
        4. variant: Variant/type (e.g., "Tipo 1", "Integral", "Sem Lactose"). Null if not applicable.
        5. unit_of_measure: Normalized unit of measure: kg, g, l, ml, un. Null if not identifiable.
        6. measure_value: Numeric value of the quantity (e.g., 5.0, 1.0, 6.0). Null if not identifiable.
        7. category_slug: Slug of the most appropriate category from the provided list.
        8. confidence: Your confidence in the classification from 0.0 to 1.0 (Decimal)

        AVAILABLE CATEGORIES:
        {categories_text}

        Respond EXCLUSIVELY in valid JSON in the format of a list of objects:
        [
        {{
            "index": 0,
            "normalized_name": "Arroz Parboilizado",
            "brand": "Camil",
            "quantity_label": "5kg",
            "variant": "Tipo 1",
            "unit_of_measure": "kg",
            "measure_value": 5.0,
            "category_slug": "graos-e-cereais",
            "confidence": 0.95
        }}
        ]
        The 'index' property must correspond exactly to the product index provided in the input.
        Be extremely precise. Do not invent brands if the description does not contain a clear one.
        """

        prompt = f'PRODUCTS TO NORMALIZE:\n{descriptions_text}'

        request = AiCompletionRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type=AiTaskTypeEnum.PRODUCT_NORMALIZATION,
            temperature=0.1,
            max_tokens=8192,
        )

        logger.info(f'Sending {len(descriptions)} items to Gemini...')
        try:
            response = await self._ai_service.complete(request)
            logger.info(
                f'Received response from Gemini. Usage: {response.input_tokens} input, {response.output_tokens} output.'
            )
        except Exception as exc:
            logger.error(f'Gemini completion failed: {exc}')
            return []

        parsed = self._parse_response(response.content)
        logger.info(f'Parsed {len(parsed)} valid JSON items from Gemini response.')
        return parsed

    def _format_categories(self, categories) -> str:
        lines = []
        for cat in categories:
            lines.append(f'- {cat.name} (slug: {cat.slug})')
            if hasattr(cat, 'children') and cat.children:
                for child in cat.children:
                    lines.append(f'  - {child.name} (slug: {child.slug})')
        return '\n'.join(lines)

    def _parse_response(self, content: str) -> list[NormalizedProductResult]:
        try:
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
            elif content.startswith('```'):
                content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]

            data = json.loads(content)
            if not isinstance(data, list):
                logger.error('Parsed JSON is not a list.')
                return []

            results = []
            for item in data:
                results.append(
                    NormalizedProductResult(
                        index=item.get('index', 0),
                        normalized_name=item.get('normalized_name', ''),
                        brand=item.get('brand'),
                        quantity_label=item.get('quantity_label'),
                        variant=item.get('variant'),
                        unit_of_measure=item.get('unit_of_measure'),
                        measure_value=(
                            Decimal(str(item.get('measure_value')))
                            if item.get('measure_value') is not None
                            else None
                        ),
                        category_slug=item.get('category_slug'),
                        confidence=Decimal(str(item.get('confidence', 0.0))),
                    )
                )
            return results
        except Exception as exc:
            logger.error(f'Failed to parse AI response: {exc}. Content: {content}')
            return []
