import time

from src.dtos.ai_dtos import AiCompletionRequest, AiCompletionResponse
from src.entities.ai_interaction_entity import AiInteractionEntity
from src.enums.ai_enum import AiInteractionStatusEnum
from src.exceptions.base_exceptions import AiProviderException
from src.repositories.ai_interaction_repository import AiInteractionRepository
from src.services.ai.ai_provider import AiProvider


class AiService:
    def __init__(self, provider: AiProvider, repository: AiInteractionRepository):
        self._provider = provider
        self._repository = repository

    async def complete(self, request: AiCompletionRequest, user_id: int | None = None):
        start_time = time.monotonic()

        try:
            response = await self._provider.complete(request)
            duration_ms = int((time.monotonic() - start_time) * 1000)
            response = response.model_copy(update={'duration_ms': duration_ms})

            try:
                await self._log_interaction(
                    user_id=user_id,
                    request=request,
                    response=response,
                    duration_ms=duration_ms,
                    status=AiInteractionStatusEnum.COMPLETED,
                )
            except Exception:
                pass

            return response

        except Exception as exc:
            duration_ms = int((time.monotonic() - start_time) * 1000)

            try:
                await self._log_interaction(
                    user_id=user_id,
                    request=request,
                    response=None,
                    duration_ms=duration_ms,
                    status=AiInteractionStatusEnum.FAILED,
                    error_message=str(exc),
                )
            except Exception:
                pass

            if isinstance(exc, AiProviderException):
                raise
            raise AiProviderException(
                f'AI provider error: {exc}',
                details={
                    'provider': self._provider.provider_name,
                    'task_type': request.task_type,
                },
            ) from exc

    async def _log_interaction(
        self,
        user_id: int | None,
        request: AiCompletionRequest,
        response: AiCompletionResponse | None,
        duration_ms: int,
        status: AiInteractionStatusEnum,
        error_message: str | None = None,
    ) -> None:
        metadata = {
            'temperature': request.temperature,
            'system_prompt': request.system_prompt,
        }

        entity = AiInteractionEntity(
            user_id=user_id,
            provider=self._provider.provider_name,
            task_type=request.task_type,
            model=response.model if response else 'unknown',
            input_text=request.prompt,
            output_text=response.content if response else None,
            input_tokens=response.input_tokens if response else None,
            output_tokens=response.output_tokens if response else None,
            cost=response.cost if response else None,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message,
            metadata_json=metadata,
        )

        await self._repository.create(entity)
