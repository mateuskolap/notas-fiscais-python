import logging

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.permission_entity import PermissionEntity
from src.entities.product_category_entity import ProductCategoryEntity
from src.entities.role_entity import RoleEntity
from src.entities.role_permission_entity import RolePermissionEntity
from src.entities.user_entity import UserEntity
from src.entities.user_role_entity import UserRoleEntity
from src.enums.permission_enum import PermissionEnum
from src.repositories.database import engine
from src.services.password_service import hash_password

logger = logging.getLogger(__name__)


async def seed_permissions(session: AsyncSession) -> None:
    logger.info('Seeding permissions...')
    permissions = [p.value for p in PermissionEnum]

    await session.execute(
        delete(PermissionEntity).where(PermissionEntity.name.not_in(permissions))
    )

    for p in permissions:
        result = await session.execute(
            select(PermissionEntity).where(PermissionEntity.name == p)
        )
        if not result.scalar_one_or_none():
            session.add(PermissionEntity(name=p))

    await session.flush()


async def seed_roles(session: AsyncSession) -> None:
    logger.info('Seeding roles...')
    result = await session.execute(select(RoleEntity).where(RoleEntity.name == 'Admin'))
    admin_role = result.scalar_one_or_none()

    if not admin_role:
        admin_role = RoleEntity(name='Admin', description='Administrator role')
        session.add(admin_role)
        await session.flush()
        await session.refresh(admin_role)

    result = await session.execute(select(RoleEntity).where(RoleEntity.name == 'User'))
    user_role = result.scalar_one_or_none()

    if not user_role:
        user_role = RoleEntity(name='User', description='Default user role')
        session.add(user_role)
        await session.flush()
        await session.refresh(user_role)

    result = await session.execute(select(PermissionEntity))
    all_perms = result.scalars().all()

    for p in all_perms:
        result = await session.execute(
            select(RolePermissionEntity)
            .where(RolePermissionEntity.role_id == admin_role.id)
            .where(RolePermissionEntity.permission_id == p.id)
        )
        if not result.scalar_one_or_none():
            session.add(RolePermissionEntity(role_id=admin_role.id, permission_id=p.id))

    await session.flush()


async def seed_admin_user(session: AsyncSession) -> None:
    logger.info('Seeding admin user...')
    result = await session.execute(
        select(UserEntity).where(UserEntity.email == 'admin@notei.com')
    )
    admin_user = result.scalar_one_or_none()

    if not admin_user:
        admin_user = UserEntity(
            name='Admin',
            email='admin@notei.com',
            password=hash_password('Change@123'),
        )
        session.add(admin_user)
        await session.flush()
        await session.refresh(admin_user)

    result = await session.execute(select(RoleEntity).where(RoleEntity.name == 'Admin'))
    admin_role = result.scalar_one()

    result = await session.execute(
        select(UserRoleEntity)
        .where(UserRoleEntity.user_id == admin_user.id)
        .where(UserRoleEntity.role_id == admin_role.id)
    )
    if not result.scalar_one_or_none():
        session.add(UserRoleEntity(user_id=admin_user.id, role_id=admin_role.id))

    await session.flush()


async def seed_product_categories(session: AsyncSession) -> None:
    logger.info('Seeding product categories...')

    categories_tree = {
        'alimentos': ('Alimentos', {
            'graos-e-cereais': 'Grãos e Cereais',
            'carnes-e-aves': 'Carnes e Aves',
            'laticinios': 'Laticínios',
            'frutas-e-verduras': 'Frutas e Verduras',
            'padaria-e-confeitaria': 'Padaria e Confeitaria',
            'congelados': 'Congelados',
            'enlatados-e-conservas': 'Enlatados e Conservas',
            'massas-e-molhos': 'Massas e Molhos',
            'temperos-e-condimentos': 'Temperos e Condimentos',
            'doces-e-sobremesas': 'Doces e Sobremesas',
            'oleos-e-azeites': 'Óleos e Azeites',
        }),
        'bebidas': ('Bebidas', {
            'agua-e-sucos': 'Água e Sucos',
            'refrigerantes': 'Refrigerantes',
            'bebidas-alcoolicas': 'Bebidas Alcoólicas',
            'cafe-e-cha': 'Café e Chá',
            'bebidas-lacteas': 'Bebidas Lácteas',
        }),
        'limpeza': ('Limpeza', {
            'detergentes-e-saboes': 'Detergentes e Sabões',
            'desinfetantes': 'Desinfetantes',
            'limpeza-de-roupas': 'Limpeza de Roupas',
            'acessorios-de-limpeza': 'Acessórios de Limpeza',
        }),
        'higiene-pessoal': ('Higiene Pessoal', {
            'banho-e-corpo': 'Banho e Corpo',
            'bucal': 'Bucal',
            'cabelos': 'Cabelos',
            'desodorantes': 'Desodorantes',
            'papel-higienico-e-lencos': 'Papel Higiênico e Lenços',
        }),
        'bebes-e-criancas': ('Bebês e Crianças', {
            'fraldas': 'Fraldas',
            'alimentacao-infantil': 'Alimentação Infantil',
            'higiene-infantil': 'Higiene Infantil',
        }),
        'pet': ('Pet', {
            'racao': 'Ração',
            'acessorios-pet': 'Acessórios Pet',
        }),
        'outros': ('Outros', {
            'utensilios-domesticos': 'Utensílios Domésticos',
            'descartaveis': 'Descartáveis',
            'diversos': 'Diversos',
        })
    }

    pos = 0
    for parent_slug, (parent_name, children) in categories_tree.items():
        result = await session.execute(
            select(ProductCategoryEntity).where(ProductCategoryEntity.slug == parent_slug).where(ProductCategoryEntity.parent_id.is_(None))
        )
        parent = result.scalar_one_or_none()
        if not parent:
            parent = ProductCategoryEntity(
                name=parent_name,
                slug=parent_slug,
                position=pos,
                is_default=True
            )
            session.add(parent)
            await session.flush()
            await session.refresh(parent)

        pos += 1

        child_pos = 0
        for child_slug, child_name in children.items():
            result = await session.execute(
                select(ProductCategoryEntity)
                .where(ProductCategoryEntity.slug == child_slug)
                .where(ProductCategoryEntity.parent_id == parent.id)
            )
            child = result.scalar_one_or_none()
            if not child:
                child = ProductCategoryEntity(
                    name=child_name,
                    slug=child_slug,
                    parent_id=parent.id,
                    position=child_pos,
                    is_default=True
                )
                session.add(child)
            child_pos += 1

    await session.flush()


async def run_seeders() -> None:
    logger.info('Starting DB Seeders...')
    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            await seed_permissions(session)
            await seed_roles(session)
            await seed_admin_user(session)
            await seed_product_categories(session)
    logger.info('DB Seeders completed successfully!')


if __name__ == '__main__':
    import asyncio

    asyncio.run(run_seeders())
