from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


DepartmentId = NewType("DepartmentId", UUID)


@entity
class Department(Entity[DepartmentId]):
    code: Code
    name: Name
    description: str | None = None
