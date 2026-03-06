from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.name import Name


PositionId = NewType("PositionId", UUID)


@entity
class Position(Entity[PositionId]):
    code: Code
    name: Name
    base_salary: Money
    description: str | None = None
