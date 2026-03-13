from collections.abc import Callable

from adaptix import P
from adaptix.conversion import link

from piaps.domain.entities.payroll_item import PayrollItem
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.payroll_item import PayrollItemORM
from piaps.infrastructure.database.repositories.base import SAAbstractRepository


_to_orm: Callable[[PayrollItem], PayrollItemORM] = get_mapper(
    PayrollItem,
    PayrollItemORM,
    recipe=[
        link(P[PayrollItem].code, P[PayrollItemORM].code, coercer=lambda c: c.value),
        link(P[PayrollItem].name, P[PayrollItemORM].name, coercer=lambda n: n.value),
    ],
)


class SAPayrollItemRepository(SAAbstractRepository[PayrollItem, PayrollItemORM]):
    def _to_orm(self, entity: PayrollItem) -> PayrollItemORM:
        return _to_orm(entity)
