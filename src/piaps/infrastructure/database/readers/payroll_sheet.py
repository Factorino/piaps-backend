from datetime import date
from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar

from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.interfaces.readers.payroll_sheet import (
    IPayrollSheetReader,
    PayrollSheetFilterField,
    PayrollSheetSortField,
)
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
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
        return await self._find(PayrollSheetORM.id == id)

    async def find_by_employee_and_period(
        self,
        employee_id: EmployeeId,
        period: date,
    ) -> PayrollSheet | None:
        return await self._find(
            PayrollSheetORM.employee_id == employee_id,
            PayrollSheetORM.period == period,
        )

    async def search(
        self,
        filter: Filter[PayrollSheetFilterField] | None = None,
        sort: Sort[PayrollSheetSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollSheet]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: PayrollSheetORM) -> PayrollSheet:
        raise NotImplementedError  # TODO: adaptix converter
