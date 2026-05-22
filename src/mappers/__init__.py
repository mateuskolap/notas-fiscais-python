class EntityMapper:
    @staticmethod
    def to_entity(dto, entity_class, **extra_fields):
        data = dto.model_dump()
        data.update(extra_fields)
        return entity_class(**data)

    @staticmethod
    def to_entities(dtos, entity_class, description_transform=None, **extra_fields):
        entities = []
        for dto in dtos:
            data = dto.model_dump()
            data.update(extra_fields)
            if description_transform and 'description' in data:
                data['description'] = description_transform(data['description'])
            entities.append(entity_class(**data))
        return entities
