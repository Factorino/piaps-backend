from datetime import date
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.full_name import FullName


@entity
class Employee(Entity[UUID]):
    code: Code
    full_name: FullName
    hire_date: date

    position_id: UUID
    department_id: UUID
