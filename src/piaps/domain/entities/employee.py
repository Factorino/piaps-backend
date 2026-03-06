from datetime import date
from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.position import PositionId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.full_name import FullName


EmployeeId = NewType("EmployeeId", UUID)


@entity
class Employee(Entity[EmployeeId]):
    code: Code
    full_name: FullName
    hire_date: date
    position_id: PositionId
    department_id: DepartmentId
