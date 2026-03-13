from collections.abc import Callable
from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar

from adaptix import P
from adaptix.conversion import link
from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.interfaces.readers.position import (
    PositionFilterField,
    PositionSortField,
)
from piaps.domain.entities.position import Position, PositionId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.name import Name
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.position import PositionORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


_to_domain: Callable[[PositionORM], Position] = get_mapper(
    PositionORM,
    Position,
    recipe=[
        link(P[PositionORM].code, P[Position].code, coercer=Code.from_str),
        link(P[PositionORM].name, P[Position].name, coercer=lambda n: Name(value=n)),
        link(
            P[PositionORM].base_salary, P[Position].base_salary, coercer=lambda m: Money(value=m)
        ),
    ],
)


class SAPositionReader(SAAbstractReader[Position, PositionORM]):
    _model = PositionORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            PositionFilterField.CODE: PositionORM.code,
            PositionFilterField.NAME: PositionORM.name,
            PositionFilterField.BASE_SALARY: PositionORM.base_salary,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            PositionSortField.CODE: PositionORM.code,
            PositionSortField.NAME: PositionORM.name,
            PositionSortField.BASE_SALARY: PositionORM.base_salary,
        }
    )

    async def find_by_id(self, id: PositionId) -> Position | None:
        return await self._find(PositionORM.id == id)

    async def find_by_code(self, code: Code) -> Position | None:
        return await self._find(PositionORM.code == code.value)

    async def find_by_name(self, name: Name) -> Position | None:
        return await self._find(PositionORM.name == name.value)

    async def search(
        self,
        filter: Filter[PositionFilterField] | None = None,
        sort: Sort[PositionSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Position]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: PositionORM) -> Position:
        return _to_domain(orm_obj)
