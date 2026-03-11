from typing import Self

from piaps.application.common.dto.base import dto
from piaps.domain.entities.department import Department, DepartmentId


@dto
class DepartmentView:
    id: DepartmentId
    code: str
    name: str
    description: str | None = None

    @classmethod
    def from_domain(cls, entity: Department) -> Self:
        return cls(
            id=entity.id,
            code=entity.code.value,
            name=entity.name.value,
            description=entity.description,
        )
