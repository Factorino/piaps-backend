from datetime import date
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
from piaps.application.interfaces.readers.payroll_sheet import (
    IPayrollSheetReader,
    PayrollSheetFilterField,
    PayrollSheetSortField,
)
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.infrastructure.database.models.employee import EmployeeORM
from piaps.infrastructure.database.models.payroll_sheet import PayrollSheetORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


class SAPayrollSheetReader(IPayrollSheetReader, SAAbstractReader[PayrollSheet, PayrollSheetORM]):
    _model = PayrollSheetORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            PayrollSheetFilterField.EMPLOYEE_ID: PayrollSheetORM.employee_id,
            PayrollSheetFilterField.PERIOD: PayrollSheetORM.period,
            PayrollSheetFilterField.STATUS: PayrollSheetORM.status,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            PayrollSheetSortField.PERIOD: PayrollSheetORM.period,
            PayrollSheetSortField.STATUS: PayrollSheetORM.status,
        }
    )

    async def find_by_id(self, id: PayrollSheetId) -> PayrollSheet | None:
        query: Select[tuple[PayrollSheetORM]] = select(PayrollSheetORM).where(
            PayrollSheetORM.id == id
        )
        result: Result[tuple[PayrollSheetORM]] = await self._execute(query)
        row: PayrollSheetORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def find_by_employee_and_period(
        self,
        employee_id: EmployeeId,
        period: date,
    ) -> PayrollSheet | None:
        query: Select[tuple[PayrollSheetORM]] = select(PayrollSheetORM).where(
            PayrollSheetORM.employee_id == employee_id,
            PayrollSheetORM.period == period,
        )
        result: Result[tuple[PayrollSheetORM]] = await self._execute(query)
        row: PayrollSheetORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def search(
        self,
        filter: Filter[PayrollSheetFilterField] | None = None,
        sort: Sort[PayrollSheetSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollSheet]:
        return await self._search(filter, sort, pagination)

    async def search_by_employee(
        self,
        employee_id: EmployeeId,
        period: date | None = None,
        status: PayrollStatus | None = None,
        sort: Sort[PayrollSheetSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollSheet]:
        base_query: Select = select(PayrollSheetORM).where(
            PayrollSheetORM.employee_id == employee_id
        )
        if period is not None:
            base_query = base_query.where(PayrollSheetORM.period == period)
        if status is not None:
            base_query = base_query.where(PayrollSheetORM.status == status)
        return await self._search(sort=sort, pagination=pagination, base_query=base_query)

    async def search_by_department(
        self,
        department_id: DepartmentId,
        period: date | None = None,
        status: PayrollStatus | None = None,
        sort: Sort[PayrollSheetSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollSheet]:
        base_query: Select = (
            select(PayrollSheetORM)
            .join(EmployeeORM, PayrollSheetORM.employee_id == EmployeeORM.id)
            .where(EmployeeORM.department_id == department_id)
        )
        if period is not None:
            base_query = base_query.where(PayrollSheetORM.period == period)
        if status is not None:
            base_query = base_query.where(PayrollSheetORM.status == status)
        return await self._search(sort=sort, pagination=pagination, base_query=base_query)

    def _to_domain(self, orm_obj: PayrollSheetORM) -> PayrollSheet:
        raise NotImplementedError  # TODO: adaptix converter
