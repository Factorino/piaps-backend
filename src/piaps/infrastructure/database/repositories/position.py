from collections.abc import Callable

from adaptix import P
from adaptix.conversion import link

from piaps.domain.entities.position import Position
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.position import PositionORM
from piaps.infrastructure.database.repositories.base import SAAbstractRepository


_to_orm: Callable[[Position], PositionORM] = get_mapper(
    Position,
    PositionORM,
    recipe=[
        link(P[Position].code, P[PositionORM].code, coercer=lambda c: c.value),
        link(P[Position].name, P[PositionORM].name, coercer=lambda n: n.value),
        link(P[Position].base_salary, P[PositionORM].base_salary, coercer=lambda m: m.value),
    ],
)


class SAPositionRepository(SAAbstractRepository[Position, PositionORM]):
    def _to_orm(self, entity: Position) -> PositionORM:
        return _to_orm(entity)
