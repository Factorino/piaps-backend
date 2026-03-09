from decimal import Decimal
from typing import Self

from piaps.application.common.dto.base import dto
from piaps.domain.entities.position import Position, PositionId


@dto
class PositionDTO:
    id: PositionId
    code: str
    name: str
    base_salary: Decimal
    description: str | None = None

    @classmethod
    def from_domain(cls, entity: Position) -> Self:
        return cls(
            id=entity.id,
            code=entity.code.value,
            name=entity.name.value,
            base_salary=entity.base_salary.value,
            description=entity.description,
        )
