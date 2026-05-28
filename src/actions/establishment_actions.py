from src.actions.base_actions import BaseActions
from src.dtos.establishment_dtos import EstablishmentCreate, EstablishmentUpdate
from src.entities.establishment_entity import EstablishmentEntity
from src.exceptions.base_exceptions import ConflictException
from src.repositories.establishment_repository import EstablishmentRepository


class EstablishmentActions(BaseActions[EstablishmentEntity]):
    def __init__(self, repository: EstablishmentRepository):
        super().__init__(repository, entity_name='Establishment')
        self.repository = repository

    async def create(self, data: EstablishmentCreate) -> EstablishmentEntity:
        existing = await self.repository.find_by_tin(data.business_tin)
        if existing:
            raise ConflictException(
                'CNPJ already registered',
                details={'field': 'business_tin', 'value': data.business_tin},
            )

        establishment = EstablishmentEntity(
            name=data.name,
            business_tin=data.business_tin,
            address=data.address,
        )

        return await self.repository.create(establishment)

    async def update(
        self, establishment_id: int, data: EstablishmentUpdate
    ) -> EstablishmentEntity:
        establishment = await self._get_or_raise(establishment_id)

        update_data = data.model_dump(exclude_unset=True)

        if (
            'business_tin' in update_data
            and update_data['business_tin'] != establishment.business_tin
        ):
            existing = await self.repository.find_by_tin(update_data['business_tin'])
            if existing:
                raise ConflictException(
                    'CNPJ already registered',
                    details={
                        'field': 'business_tin',
                        'value': update_data['business_tin'],
                    },
                )

        for field, value in update_data.items():
            setattr(establishment, field, value)

        return await self.repository.update(establishment)
