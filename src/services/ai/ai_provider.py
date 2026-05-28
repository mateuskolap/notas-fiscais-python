from abc import ABC, abstractmethod

from src.dtos.ai_dtos import AiCompletionRequest, AiCompletionResponse
from src.enums.ai_enum import AiProviderEnum


class AiProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> AiProviderEnum:
        """
        Unique identifier for the provider.
        """
        pass

    @abstractmethod
    async def complete(self, request: AiCompletionRequest) -> AiCompletionResponse:
        """
        Send a prompt to the AI provider and return the response.
        """
        pass


class GeminiAiProvider(AiProvider):
    pass
