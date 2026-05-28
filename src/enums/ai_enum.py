from enum import StrEnum


class AiProviderEnum(StrEnum):
    GEMINI = 'gemini'


class AiTaskTypeEnum(StrEnum):
    PRODUCT_NORMALIZATION = 'product_normalization'


class AiInteractionStatusEnum(StrEnum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
