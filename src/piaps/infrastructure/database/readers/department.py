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
from piaps.application.interfaces.readers.department import (
    DepartmentFilterField,
    DepartmentSortField,
    IDepartmentReader,
)
from piaps.domain.entities.department import Department, DepartmentId
from piaps.domain.value_objects.code import Code
from piaps.infrastructure.database.models.department import DepartmentORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


class SADepartmentReader(IDepartmentReader, SAAbstractReader[Department, DepartmentORM]):
    _model = DepartmentORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            DepartmentFilterField.CODE: DepartmentORM.code,
            DepartmentFilterField.NAME: DepartmentORM.name,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            DepartmentSortField.CODE: DepartmentORM.code,
            DepartmentSortField.NAME: DepartmentORM.name,
        }
    )

    async def find_by_id(self, id: DepartmentId) -> Department | None:
        query: Select[tuple[DepartmentORM]] = select(DepartmentORM).where(DepartmentORM.id == id)
        result: Result[tuple[DepartmentORM]] = await self._execute(query)
        row: DepartmentORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def find_by_code(self, code: Code) -> Department | None:
        query: Select[tuple[DepartmentORM]] = select(DepartmentORM).where(
            DepartmentORM.code == code.value
        )
        result: Result[tuple[DepartmentORM]] = await self._execute(query)
        row: DepartmentORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def search(
        self,
        filter: Filter[DepartmentFilterField] | None = None,
        sort: Sort[DepartmentSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Department]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: DepartmentORM) -> Department:
        raise NotImplementedError  # TODO: adaptix converter
