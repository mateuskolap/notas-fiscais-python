from src.entities.ai_interaction_entity import AiInteractionEntity
from src.repositories.base_repository import BaseRepository


class AiInteractionRepository(
    BaseRepository[AiInteractionEntity], model=AiInteractionEntity
):
    pass
