from src.actions.base_actions import BaseActions
from src.dtos.category_dtos import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from src.entities.product_category_entity import ProductCategoryEntity
from src.entities.user_product_category_entity import UserProductCategoryEntity
from src.exceptions.base_exceptions import ConflictException, NotFoundException
from src.repositories.product_category_repository import ProductCategoryRepository
from src.repositories.user_product_category_repository import (
    UserProductCategoryRepository,
)
from src.utils.slug import generate_slug


class ProductCategoryActions(BaseActions[ProductCategoryEntity]):
    def __init__(
        self,
        repository: ProductCategoryRepository,
        user_category_repo: UserProductCategoryRepository,
    ):
        super().__init__(repository, entity_name='ProductCategory')
        self.repository = repository
        self.user_category_repo = user_category_repo

    async def list_all_for_user(self, user_id: int) -> list[CategoryResponse]:
        global_cats = await self.repository.find_all_by(is_default=True)
        user_cats_all = await self.user_category_repo.find_all_by(user_id=user_id)

        override_map = {
            uc.category_id: uc for uc in user_cats_all if uc.category_id is not None
        }

        response = []
        for gc in global_cats:
            override = override_map.get(gc.id)
            is_active = override.is_active if override else True
            response.append(
                CategoryResponse(
                    id=gc.id,
                    name=gc.name,
                    slug=gc.slug,
                    parent_id=gc.parent_id,
                    is_global=True,
                    is_active=is_active,
                )
            )

        for uc in user_cats_all:
            if uc.category_id is None:
                response.append(
                    CategoryResponse(
                        id=uc.id,
                        name=uc.custom_name,
                        slug=uc.custom_slug,
                        parent_id=uc.custom_parent_id,
                        is_global=False,
                        is_active=uc.is_active,
                    )
                )

        return response

    async def find_user_category(
        self, user_id: int, category_id: int, is_global: bool
    ) -> CategoryResponse:
        if is_global:
            global_cat = await self.repository.find_by_id(category_id)
            if not global_cat:
                raise NotFoundException('Global category not found')

            override = await self.user_category_repo.find_one_by(
                user_id=user_id, category_id=category_id
            )
            is_active = override.is_active if override else True

            return CategoryResponse(
                id=global_cat.id,
                name=global_cat.name,
                slug=global_cat.slug,
                parent_id=global_cat.parent_id,
                is_global=True,
                is_active=is_active,
            )
        else:
            custom_cat = await self.user_category_repo.find_by_user_and_id(
                user_id, category_id
            )
            if not custom_cat or custom_cat.category_id is not None:
                raise NotFoundException('Custom category not found')

            return CategoryResponse(
                id=custom_cat.id,
                name=custom_cat.custom_name,
                slug=custom_cat.custom_slug,
                parent_id=custom_cat.custom_parent_id,
                is_global=False,
                is_active=custom_cat.is_active,
            )

    async def create_user_category(
        self, user_id: int, data: CategoryCreateRequest
    ) -> CategoryResponse:
        slug = generate_slug(data.name)
        existing = await self.user_category_repo.find_by_user_and_slug(user_id, slug)
        if existing:
            raise ConflictException('User category with this name already exists')

        if data.parent_id is not None:
            parent = await self.user_category_repo.find_by_user_and_id(
                user_id, data.parent_id
            )
            if not parent or parent.category_id is not None:
                raise NotFoundException('Parent custom category not found')

        entity = UserProductCategoryEntity(
            user_id=user_id,
            category_id=None,
            custom_name=data.name,
            custom_slug=slug,
            custom_parent_id=data.parent_id,
            is_active=True,
        )
        entity = await self.user_category_repo.create(entity)
        return CategoryResponse(
            id=entity.id,
            name=entity.custom_name,
            slug=entity.custom_slug,
            parent_id=entity.custom_parent_id,
            is_global=False,
            is_active=True,
        )

    async def update_user_category(
        self,
        user_id: int,
        category_id: int,
        is_global: bool,
        data: CategoryUpdateRequest,
    ) -> CategoryResponse:
        if is_global:
            override = await self.user_category_repo.find_one_by(
                user_id=user_id, category_id=category_id
            )
            if not override:
                global_cat = await self.repository.find_by_id(category_id)
                if not global_cat:
                    raise NotFoundException('Global category not found')
                override = UserProductCategoryEntity(
                    user_id=user_id,
                    category_id=category_id,
                    is_active=data.is_active if data.is_active is not None else True,
                )
                override = await self.user_category_repo.create(override)
            elif data.is_active is not None:
                override.is_active = data.is_active
                override = await self.user_category_repo.update(override)

            global_cat = await self.repository.find_by_id(category_id)
            return CategoryResponse(
                id=global_cat.id,
                name=global_cat.name,
                slug=global_cat.slug,
                parent_id=global_cat.parent_id,
                is_global=True,
                is_active=override.is_active,
            )
        else:
            custom_cat = await self.user_category_repo.find_by_user_and_id(
                user_id, category_id
            )
            if not custom_cat or custom_cat.category_id is not None:
                raise NotFoundException('Custom category not found')

            if data.name is not None:
                custom_cat.custom_name = data.name
                new_slug = generate_slug(data.name)
                if new_slug != custom_cat.custom_slug:
                    existing = await self.user_category_repo.find_by_user_and_slug(
                        user_id, new_slug
                    )
                    if existing and existing.id != custom_cat.id:
                        raise ConflictException(
                            'Category with this name already exists'
                        )
                    custom_cat.custom_slug = new_slug
            if data.parent_id is not None:
                parent = await self.user_category_repo.find_by_user_and_id(
                    user_id, data.parent_id
                )
                if not parent or parent.category_id is not None:
                    raise NotFoundException('Parent custom category not found')
                custom_cat.custom_parent_id = data.parent_id
            if data.is_active is not None:
                custom_cat.is_active = data.is_active

            custom_cat = await self.user_category_repo.update(custom_cat)
            return CategoryResponse(
                id=custom_cat.id,
                name=custom_cat.custom_name,
                slug=custom_cat.custom_slug,
                parent_id=custom_cat.custom_parent_id,
                is_global=False,
                is_active=custom_cat.is_active,
            )

    async def delete_user_category(
        self, user_id: int, category_id: int, is_global: bool
    ) -> None:
        if is_global:
            override = await self.user_category_repo.find_one_by(
                user_id=user_id, category_id=category_id
            )
            if override:
                override.is_active = False
                await self.user_category_repo.update(override)
            else:
                global_cat = await self.repository.find_by_id(category_id)
                if not global_cat:
                    raise NotFoundException('Global category not found')
                override = UserProductCategoryEntity(
                    user_id=user_id, category_id=category_id, is_active=False
                )
                await self.user_category_repo.create(override)
        else:
            custom_cat = await self.user_category_repo.find_by_user_and_id(
                user_id, category_id
            )
            if not custom_cat or custom_cat.category_id is not None:
                raise NotFoundException('Custom category not found')
            await self.user_category_repo.delete(custom_cat)
