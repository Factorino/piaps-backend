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
    PayrollSheetFilterField,
    PayrollSheetSortField,
)
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_item import PayrollItem
from piaps.domain.entities.payroll_record import PayrollRecord
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.name import Name
from piaps.infrastructure.database.models.payroll_record import PayrollRecordORM
from piaps.infrastructure.database.models.payroll_sheet import PayrollSheetORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


def _record_orm_to_domain(record: PayrollRecordORM) -> PayrollRecord:
    return PayrollRecord(
        id=record.id,
        employee_id=record.employee_id,
        payroll_item=PayrollItem(
            id=record.payroll_item.id,
            code=Code.from_str(record.payroll_item.code),
            name=Name(value=record.payroll_item.name),
            payroll_type=record.payroll_item.payroll_type,
            calc_type=record.payroll_item.calc_type,
            value=record.payroll_item.value,
        ),
        period=record.period,
        amount=Money(value=record.amount),
        comment=record.comment,
    )


def _sheet_orm_to_domain(sheet: PayrollSheetORM) -> PayrollSheet:
    return PayrollSheet(
        id=sheet.id,
        employee_id=sheet.employee_id,
        period=sheet.period,
        status=sheet.status,
        records=[_record_orm_to_domain(r) for r in sheet.records],
    )


class SAPayrollSheetReader(SAAbstractReader[PayrollSheet, PayrollSheetORM]):
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
        return _sheet_orm_to_domain(orm_obj)
