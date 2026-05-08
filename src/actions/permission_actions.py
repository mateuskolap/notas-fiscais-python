from src.actions.base_actions import BaseActions
from src.entities.permission_entity import PermissionModel
from src.repositories.base_repository import BaseRepository


class PermissionActions(BaseActions[PermissionModel]):
    def __init__(self, repository: BaseRepository[PermissionModel]):
        super().__init__(repository, entity_name='Permission')
        self.repository = repository
