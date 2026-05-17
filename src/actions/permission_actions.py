from src.actions.base_actions import BaseActions
from src.entities.permission_entity import PermissionEntity
from src.repositories.base_repository import BaseRepository


class PermissionActions(BaseActions[PermissionEntity]):
    def __init__(self, repository: BaseRepository[PermissionEntity]):
        super().__init__(repository, entity_name='Permission')
        self.repository = repository
