from abc import ABC, abstractmethod

from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

from src.dtos.ai_dtos import AiCompletionRequest, AiCompletionResponse
from src.enums.ai_enum import AiProviderEnum
from src.exceptions.base_exceptions import AiProviderException
from src.settings import settings


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
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.AI_API_KEY)
        super().__init__()

    @property
    def provider_name(self) -> AiProviderEnum:
        return AiProviderEnum.GEMINI

    async def complete(self, request: AiCompletionRequest) -> AiCompletionResponse:
        config = self._build_config(request)
        response = await self._call_gemini_api(request, config)
        return self._process_response(request, response)

    def _get_safety_settings(self) -> list[types.SafetySetting]:
        return [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ]

    def _build_config(self, request: AiCompletionRequest) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=request.system_prompt,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
            safety_settings=self._get_safety_settings(),
        )

    async def _call_gemini_api(
        self, request: AiCompletionRequest, config: types.GenerateContentConfig
    ) -> types.GenerateContentResponse:
        try:
            return await self._client.aio.models.generate_content(
                model=settings.AI_MODEL,
                contents=request.prompt,
                config=config,
            )
        except ClientError as exc:
            raise AiProviderException(
                f'Gemini client error: {exc}',
                details={
                    'provider': self.provider_name,
                    'task_type': request.task_type,
                    'model': settings.AI_MODEL,
                },
            ) from exc
        except APIError as exc:
            raise AiProviderException(
                f'Gemini API error (status {exc.code}): {exc.message}',
                details={
                    'provider': self.provider_name,
                    'task_type': request.task_type,
                    'model': settings.AI_MODEL,
                    'status_code': exc.code,
                },
            ) from exc

    def _process_response(
        self, request: AiCompletionRequest, response: types.GenerateContentResponse
    ) -> AiCompletionResponse:
        if not response.text:
            raise AiProviderException(
                'Gemini returned empty response (possibly blocked by safety filters)',
                details={
                    'provider': self.provider_name,
                    'task_type': request.task_type,
                    'model': settings.AI_MODEL,
                    'finish_reason': str(response.candidates[0].finish_reason)
                    if response.candidates
                    else 'no_candidates',
                },
            )

        usage = response.usage_metadata

        return AiCompletionResponse(
            content=response.text,
            model=settings.AI_MODEL,
            input_tokens=usage.prompt_token_count if usage else None,
            output_tokens=usage.candidates_token_count if usage else None,
            cost=None,
        )
