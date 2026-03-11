from datetime import date
from typing import Self

from piaps.application.common.dto.base import dto
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.position import PositionId


@dto
class EmployeeView:
    id: EmployeeId
    code: str
    last_name: str
    first_name: str
    middle_name: str | None = None
    hire_date: date
    department_id: DepartmentId
    position_id: PositionId

    @classmethod
    def from_domain(cls, entity: Employee) -> Self:
        return cls(
            id=entity.id,
            code=entity.code.value,
            last_name=entity.full_name.last_name,
            first_name=entity.full_name.first_name,
            middle_name=entity.full_name.middle_name,
            hire_date=entity.hire_date,
            department_id=entity.department_id,
            position_id=entity.position_id,
        )
