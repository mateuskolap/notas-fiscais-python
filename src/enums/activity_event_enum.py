from enum import Enum


class ActivityEventEnum(str, Enum):
    CREATED = 'created'
    UPDATED = 'updated'
    DELETED = 'deleted'
