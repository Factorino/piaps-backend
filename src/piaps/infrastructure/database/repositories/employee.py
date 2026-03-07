from collections.abc import Callable

from adaptix import P
from adaptix.conversion import link
from sqlalchemy.ext.asyncio import AsyncSession

from piaps.application.interfaces.repositories.employee import IEmployeeRepository
from piaps.domain.entities.employee import Employee
from piaps.infrastructure.database.mapper import get_mapper
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


class SAEmployeeRepository(IEmployeeRepository, SAAbstractRepository[Employee, EmployeeORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _to_orm(self, entity: Employee) -> EmployeeORM:
        return _to_orm(entity)
