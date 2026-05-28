from pydantic import BaseModel

from src.enums.ai_enum import AiTaskTypeEnum


class AiCompletionRequest(BaseModel):
    prompt: str
    task_type: AiTaskTypeEnum
    temperature: float = 0.0
    max_tokens: int = 1024


class AiCompletionResponse(BaseModel):
    content: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: float | None = None
    duration_ms: int | None = None
