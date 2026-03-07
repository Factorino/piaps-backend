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
from piaps.application.interfaces.readers.employee import (
    EmployeeFilterField,
    EmployeeSortField,
    IEmployeeReader,
)
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.position import PositionId
from piaps.domain.value_objects.code import Code
from piaps.infrastructure.database.models.employee import EmployeeORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


class SAEmployeeReader(IEmployeeReader, SAAbstractReader[Employee, EmployeeORM]):
    _model = EmployeeORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            EmployeeFilterField.CODE: EmployeeORM.code,
            EmployeeFilterField.FULL_NAME: EmployeeORM.full_name,
            EmployeeFilterField.HIRE_DATE: EmployeeORM.hire_date,
            EmployeeFilterField.DEPARTMENT_ID: EmployeeORM.department_id,
            EmployeeFilterField.POSITION_ID: EmployeeORM.position_id,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            EmployeeSortField.CODE: EmployeeORM.code,
            EmployeeSortField.FULL_NAME: EmployeeORM.full_name,
            EmployeeSortField.HIRE_DATE: EmployeeORM.hire_date,
        }
    )

    async def find_by_id(self, id: EmployeeId) -> Employee | None:
        query: Select[tuple[EmployeeORM]] = select(EmployeeORM).where(EmployeeORM.id == id)
        result: Result[tuple[EmployeeORM]] = await self._execute(query)
        row: EmployeeORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def find_by_code(self, code: Code) -> Employee | None:
        query: Select[tuple[EmployeeORM]] = select(EmployeeORM).where(
            EmployeeORM.code == code.value
        )
        result: Result[tuple[EmployeeORM]] = await self._execute(query)
        row: EmployeeORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def search(
        self,
        filter: Filter[EmployeeFilterField] | None = None,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Employee]:
        return await self._search(filter, sort, pagination)

    async def search_by_department(
        self,
        department_id: DepartmentId,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Employee]:
        base_query: Select = select(EmployeeORM).where(EmployeeORM.department_id == department_id)
        return await self._search(sort=sort, pagination=pagination, base_query=base_query)

    async def search_by_position(
        self,
        position_id: PositionId,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Employee]:
        base_query: Select = select(EmployeeORM).where(EmployeeORM.position_id == position_id)
        return await self._search(sort=sort, pagination=pagination, base_query=base_query)

    def _to_domain(self, orm_obj: EmployeeORM) -> Employee:
        raise NotImplementedError  # TODO: adaptix converter
