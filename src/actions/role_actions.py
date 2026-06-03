from sqlalchemy.orm import selectinload

from src.actions.base_actions import BaseActions
from src.dtos.role_dtos import RoleCreate, RoleUpdate
from src.entities.role_entity import RoleEntity
from src.entities.user_entity import UserEntity
from src.exceptions.base_exceptions import ConflictException, NotFoundException
from src.repositories.permission_repository import PermissionRepository
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository


class RoleActions(BaseActions[RoleEntity]):
    def __init__(
        self,
        repository: RoleRepository,
        permission_repo: PermissionRepository,
        user_repo: UserRepository,
    ):
        super().__init__(repository, entity_name='Role')
        self.repository = repository
        self.permission_repo = permission_repo
        self.user_repo = user_repo

    async def find(self, id: int) -> RoleEntity:
        return await self._get_or_raise(
            finder=lambda: self.repository.find_by_id_with_permissions(id)
        )

    async def create(self, data: RoleCreate) -> RoleEntity:
        existing = await self.repository.find_by_name(data.name)
        if existing:
            raise ConflictException(
                f'{self._entity_name} already exists',
                details={'field': 'name', 'value': data.name},
            )

        permissions_list = [p.value for p in data.permissions]
        db_permissions = await self.permission_repo.find_by_names(permissions_list)

        found_names = {p.name for p in db_permissions}
        for p in data.permissions:
            if p.value not in found_names:
                raise NotFoundException(
                    f'Permission {p.value} not found in database',
                    details={'resource': 'Permission', 'name': p.value},
                )

        role = RoleEntity(
            name=data.name,
            description=data.description,
        )
        role.permissions = list(db_permissions)

        return await self.repository.create(role)

    async def update(self, role_id: int, data: RoleUpdate) -> RoleEntity:
        role = await self.find(role_id)  # This fetches with permissions

        if data.name and data.name != role.name:
            existing = await self.repository.find_by_name(data.name)
            if existing:
                raise ConflictException(
                    f'{self._entity_name} already exists',
                    details={'field': 'name', 'value': data.name},
                )
            role.name = data.name

        if data.description is not None:
            role.description = data.description

        if data.permissions is not None:
            permissions_list = [p.value for p in data.permissions]
            db_permissions = await self.permission_repo.find_by_names(permissions_list)

            found_names = {p.name for p in db_permissions}
            for p in data.permissions:
                if p.value not in found_names:
                    raise NotFoundException(
                        f'Permission {p.value} not found in database',
                        details={'resource': 'Permission', 'name': p.value},
                    )

            role.permissions = list(db_permissions)

        return await self.repository.update(role)

    async def assign_roles_to_user(
        self, user_id: int, role_ids: list[int]
    ) -> list[RoleEntity]:
        async def find_user_with_roles():
            res = await self.user_repo.session.execute(
                self.user_repo
                ._base_query()
                .options(selectinload(UserEntity.roles))
                .where(UserEntity.id == user_id)
                .execution_options(populate_existing=True)
            )
            return res.unique().scalar_one_or_none()

        user = await self._get_or_raise(
            id=user_id,
            finder=find_user_with_roles,
            message='User not found',
            resource_name='User',
        )

        roles = []
        for rid in role_ids:
            role = await self._get_or_raise(
                rid, message=f'Role {rid} not found', resource_name='Role'
            )
            roles.append(role)

        user.roles = roles
        await self.user_repo.update(user)
        return roles

    async def get_user_permissions(self, user_id: int) -> set[str]:
        async def find_user():
            res = await self.user_repo.session.execute(
                self.user_repo
                ._base_query()
                .options(
                    selectinload(UserEntity.roles).selectinload(RoleEntity.permissions)
                )
                .where(UserEntity.id == user_id)
                .execution_options(populate_existing=True)
            )
            return res.unique().scalar_one_or_none()

        user = await self._get_or_raise(
            id=user_id, finder=find_user, message='User not found', resource_name='User'
        )

        permissions_set = set()
        for role in user.roles:
            for perm in role.permissions:
                permissions_set.add(perm.name)

        return permissions_set
