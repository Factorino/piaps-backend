from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.value_objects.code import Code


@entity
class Department(Entity[UUID]):
    code: Code
    name: str
    description: str | None = None
