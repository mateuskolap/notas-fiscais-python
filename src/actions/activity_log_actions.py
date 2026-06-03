from typing import Sequence

from src.actions.base_actions import BaseActions
from src.entities.activity_log_entity import ActivityLogEntity
from src.repositories.activity_log_repository import ActivityLogRepository


class ActivityLogActions(BaseActions[ActivityLogEntity]):
    def __init__(self, repository: ActivityLogRepository):
        super().__init__(repository, entity_name='ActivityLog')
        self.repository = repository

    async def find_by_subject(
        self, subject_type: str, subject_id: int
    ) -> Sequence[ActivityLogEntity]:
        return await self.repository.find_all_by(
            subject_type=subject_type, subject_id=subject_id
        )
