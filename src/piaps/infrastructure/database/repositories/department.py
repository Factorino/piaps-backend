from collections.abc import Callable

from adaptix import P
from adaptix.conversion import link
from sqlalchemy.ext.asyncio import AsyncSession

from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.domain.entities.department import Department
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.department import DepartmentORM
from piaps.infrastructure.database.repositories.base import SAAbstractRepository


_to_orm: Callable[[Department], DepartmentORM] = get_mapper(
    Department,
    DepartmentORM,
    recipe=[
        link(P[Department].code, P[DepartmentORM].code, coercer=lambda c: c.value),
        link(P[Department].name, P[DepartmentORM].name, coercer=lambda n: n.value),
    ],
)


class SADepartmentRepository(
    IDepartmentRepository, SAAbstractRepository[Department, DepartmentORM]
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _to_orm(self, entity: Department) -> DepartmentORM:
        return _to_orm(entity)
