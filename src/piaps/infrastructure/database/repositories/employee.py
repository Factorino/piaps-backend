from collections.abc import Callable

from adaptix import P
from adaptix.conversion import link

from piaps.domain.entities.employee import Employee
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.employee import EmployeeORM
from piaps.infrastructure.database.repositories.base import SAAbstractRepository


_to_orm: Callable[[Employee], EmployeeORM] = get_mapper(
    Employee,
    EmployeeORM,
    recipe=[
        link(P[Employee].code, P[EmployeeORM].code, coercer=lambda c: c.value),
        link(P[Employee].full_name, P[EmployeeORM].full_name, coercer=lambda fn: fn.full),
    ],
)


class SAEmployeeRepository(SAAbstractRepository[Employee, EmployeeORM]):
    def _to_orm(self, entity: Employee) -> EmployeeORM:
        return _to_orm(entity)
