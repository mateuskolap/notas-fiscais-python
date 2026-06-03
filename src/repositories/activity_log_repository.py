from src.dtos.activity_log_dtos import ActivityLogFilterParams
from src.entities.activity_log_entity import ActivityLogEntity
from src.repositories.base_repository import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLogEntity], model=ActivityLogEntity):
    _loggable = False

    def _apply_filters(self, query, filters: ActivityLogFilterParams | None):
        if not filters:
            return query

        if filters.subject_type is not None:
            query = query.where(ActivityLogEntity.subject_type == filters.subject_type)
        if filters.subject_id is not None:
            query = query.where(ActivityLogEntity.subject_id == filters.subject_id)
        if filters.causer_id is not None:
            query = query.where(ActivityLogEntity.causer_id == filters.causer_id)
        if filters.event is not None:
            query = query.where(ActivityLogEntity.event == filters.event)
        if filters.date_from is not None:
            query = query.where(ActivityLogEntity.created_at >= filters.date_from)
        if filters.date_to is not None:
            query = query.where(ActivityLogEntity.created_at <= filters.date_to)

        return query
