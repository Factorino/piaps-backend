from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar

from sqlalchemy import Result, Select, select
from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.query.sort import Sort
from piaps.application.interfaces.readers.position import (
    IPositionReader,
    PositionFilterField,
    PositionSortField,
)
from piaps.domain.entities.position import Position, PositionId
from piaps.domain.value_objects.code import Code
from piaps.infrastructure.database.models.position import PositionORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


class SAPositionReader(IPositionReader, SAAbstractReader[Position, PositionORM]):
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
        query: Select[tuple[PositionORM]] = select(PositionORM).where(PositionORM.id == id)
        result: Result[tuple[PositionORM]] = await self._execute(query)
        row: PositionORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def find_by_code(self, code: Code) -> Position | None:
        query: Select[tuple[PositionORM]] = select(PositionORM).where(
            PositionORM.code == code.value
        )
        result: Result[tuple[PositionORM]] = await self._execute(query)
        row: PositionORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def search(
        self,
        filter: Filter[PositionFilterField] | None = None,
        sort: Sort[PositionSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Position]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: PositionORM) -> Position:
        raise NotImplementedError  # TODO: adaptix converter
