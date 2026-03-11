from datetime import date
from decimal import Decimal
from typing import NamedTuple

from sqlalchemy import Label, Result, Select, Subquery, case, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.dto.query.between import Between, DateBetween
from piaps.application.common.dto.report.department_payroll import (
    DepartmentEmployeePayrollData,
    DepartmentPayrollReportData,
)
from piaps.application.common.dto.report.employee_payroll import (
    EmployeePayrollReportData,
    PayrollRecordData,
    PayrollSheetData,
)
from piaps.application.common.dto.report.payroll_summary import (
    PayrollSummaryByDepartmentData,
    PayrollSummaryReportData,
)
from piaps.application.errors.base import OperationFailedError
from piaps.application.interfaces.readers.report import IPayrollReportReader
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_sheet import PayrollSheetId
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.infrastructure.database.models.department import DepartmentORM
from piaps.infrastructure.database.models.employee import EmployeeORM
from piaps.infrastructure.database.models.payroll_item import PayrollItemORM
from piaps.infrastructure.database.models.payroll_record import PayrollRecordORM
from piaps.infrastructure.database.models.payroll_sheet import PayrollSheetORM
from piaps.infrastructure.database.models.position import PositionORM


class _EmployeeInfo(NamedTuple):
    code: str
    full_name: str
    department_name: str
    position_name: str
    base_salary: Decimal


class _PayrollRecordInfo(NamedTuple):
    sheet_id: PayrollSheetId
    period: date
    amount: Decimal
    comment: str | None
    payroll_item_code: str
    payroll_item_name: str
    payroll_type: PayrollItemType


class _DepartmentInfo(NamedTuple):
    code: str
    name: str


class _EmployeeAggregateInfo(NamedTuple):
    employee_code: str
    employee_full_name: str
    position_name: str
    base_salary: Decimal
    accruals_sum: Decimal
    deductions_sum: Decimal


class _DepartmentPayrollSummary(NamedTuple):
    department_code: str
    department_name: str
    employee_count: int
    total_base_salary: Decimal
    total_accruals: Decimal
    total_deductions: Decimal


class SAPayrollReportReader(IPayrollReportReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_employee_payroll_report(
        self,
        employee_id: EmployeeId,
        period: DateBetween,
    ) -> EmployeePayrollReportData:
        employee_info: _EmployeeInfo = await self._fetch_employee_info(employee_id)
        sheet_records: list[_PayrollRecordInfo] = await self._fetch_employee_sheets_records(
            employee_id, period
        )

        sheets: list[PayrollSheetData] = self._build_payroll_sheet_data(sheet_records)

        total_accruals: Decimal = sum(
            (sheet.accruals_sum for sheet in sheets),
            start=Decimal(0),
        )
        total_deductions: Decimal = sum(
            (sheet.deductions_sum for sheet in sheets),
            start=Decimal(0),
        )

        return EmployeePayrollReportData(
            employee_code=employee_info.code,
            employee_full_name=employee_info.full_name,
            department_name=employee_info.department_name,
            position_name=employee_info.position_name,
            base_salary=employee_info.base_salary,
            sheets=sheets,
            total_accruals=total_accruals,
            total_deductions=total_deductions,
            total_net_salary=total_accruals - total_deductions,
        )

    async def get_department_payroll_report(
        self,
        department_id: DepartmentId,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> DepartmentPayrollReportData:
        department_info: _DepartmentInfo = await self._fetch_department_info(department_id)
        employees_info: list[_EmployeeAggregateInfo] = await self._fetch_employees_aggregate_info(
            department_id, period, status
        )

        employees: list[DepartmentEmployeePayrollData] = [
            DepartmentEmployeePayrollData(
                employee_code=row.employee_code,
                employee_full_name=row.employee_full_name,
                position_name=row.position_name,
                base_salary=row.base_salary,
                accruals_sum=row.accruals_sum,
                deductions_sum=row.deductions_sum,
                net_salary=row.accruals_sum - row.deductions_sum,
            )
            for row in employees_info
        ]

        return DepartmentPayrollReportData(
            department_code=department_info.code,
            department_name=department_info.name,
            period_from=period.value_from,
            period_to=period.value_to,
            employees=employees,
            total_base_salary=sum((empl.base_salary for empl in employees), start=Decimal(0)),
            total_accruals=sum((empl.accruals_sum for empl in employees), start=Decimal(0)),
            total_deductions=sum((empl.deductions_sum for empl in employees), start=Decimal(0)),
            total_net_salary=sum((empl.net_salary for empl in employees), start=Decimal(0)),
            employee_count=len(employees),
        )

    async def get_payroll_summary_report(
        self,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> PayrollSummaryReportData:
        rows: list[_DepartmentPayrollSummary] = await self._fetch_summary_aggregates(
            period, status
        )

        departments: list[PayrollSummaryByDepartmentData] = [
            PayrollSummaryByDepartmentData(
                department_code=row.department_code,
                department_name=row.department_name,
                employee_count=row.employee_count,
                total_base_salary=row.total_base_salary,
                total_accruals=row.total_accruals,
                total_deductions=row.total_deductions,
                total_net_salary=row.total_accruals - row.total_deductions,
            )
            for row in rows
        ]

        return PayrollSummaryReportData(
            period_from=period.value_from,
            period_to=period.value_to,
            departments=departments,
            total_employee_count=sum(dep.employee_count for dep in departments),
            grand_total_base_salary=sum(
                (dep.total_base_salary for dep in departments), start=Decimal(0)
            ),
            grand_total_accruals=sum(
                (dep.total_accruals for dep in departments), start=Decimal(0)
            ),
            grand_total_deductions=sum(
                (dep.total_deductions for dep in departments), start=Decimal(0)
            ),
            grand_total_net_salary=sum(
                (dep.total_net_salary for dep in departments), start=Decimal(0)
            ),
        )

    async def _fetch_employee_info(self, employee_id: EmployeeId) -> _EmployeeInfo:
        query: Select[tuple] = (
            select(
                EmployeeORM.code,
                EmployeeORM.full_name,
                DepartmentORM.name.label("department_name"),
                PositionORM.name.label("position_name"),
                PositionORM.base_salary,
            )
            .join(DepartmentORM, EmployeeORM.department_id == DepartmentORM.id)
            .join(PositionORM, EmployeeORM.position_id == PositionORM.id)
            .where(EmployeeORM.id == employee_id)
        )

        result: Result[tuple] = await self._execute(query)
        return _EmployeeInfo._make(result.one())

    async def _fetch_employee_sheets_records(
        self,
        employee_id: EmployeeId,
        period: DateBetween,
    ) -> list[_PayrollRecordInfo]:
        query: Select[tuple] = (
            select(
                PayrollSheetORM.id.label("sheet_id"),
                PayrollSheetORM.period,
                PayrollRecordORM.amount,
                PayrollRecordORM.comment,
                PayrollItemORM.code.label("payroll_item_code"),
                PayrollItemORM.name.label("payroll_item_name"),
                PayrollItemORM.payroll_type,
            )
            .join(PayrollRecordORM, PayrollRecordORM.payroll_sheet_id == PayrollSheetORM.id)
            .join(PayrollItemORM, PayrollRecordORM.payroll_item_id == PayrollItemORM.id)
            .where(PayrollSheetORM.employee_id == employee_id)
            .order_by(PayrollSheetORM.period)
        )
        query = self._apply_period_filter(query, PayrollSheetORM.period, period)

        result: Result[tuple] = await self._execute(query)
        return [_PayrollRecordInfo._make(rec) for rec in result.all()]

    async def _fetch_department_info(self, department_id: DepartmentId) -> _DepartmentInfo:
        query: Select[tuple] = select(
            DepartmentORM.code,
            DepartmentORM.name,
        ).where(DepartmentORM.id == department_id)

        result: Result[tuple] = await self._execute(query)
        return _DepartmentInfo._make(result.one())

    async def _fetch_employees_aggregate_info(
        self,
        department_id: DepartmentId,
        period: DateBetween,
        status: PayrollStatus | None,
    ) -> list[_EmployeeAggregateInfo]:
        accruals_sum: Label[Decimal] = func.sum(
            case(
                (
                    PayrollItemORM.payroll_type == PayrollItemType.ACCRUAL,
                    PayrollRecordORM.amount,
                ),
                else_=Decimal(0),
            )
        ).label("accruals_sum")

        deductions_sum: Label[Decimal] = func.sum(
            case(
                (
                    PayrollItemORM.payroll_type == PayrollItemType.DEDUCTION,
                    PayrollRecordORM.amount,
                ),
                else_=Decimal(0),
            )
        ).label("deductions_sum")

        query: Select[tuple] = (
            select(
                EmployeeORM.code.label("employee_code"),
                EmployeeORM.full_name.label("employee_full_name"),
                PositionORM.name.label("position_name"),
                PositionORM.base_salary,
                accruals_sum,
                deductions_sum,
            )
            .join(PayrollSheetORM, PayrollSheetORM.employee_id == EmployeeORM.id)
            .join(PayrollRecordORM, PayrollRecordORM.payroll_sheet_id == PayrollSheetORM.id)
            .join(PayrollItemORM, PayrollRecordORM.payroll_item_id == PayrollItemORM.id)
            .join(PositionORM, EmployeeORM.position_id == PositionORM.id)
            .where(EmployeeORM.department_id == department_id)
            .group_by(
                EmployeeORM.id,
                EmployeeORM.code,
                EmployeeORM.full_name,
                PositionORM.name,
                PositionORM.base_salary,
            )
            .order_by(EmployeeORM.full_name)
        )
        query = self._apply_period_filter(query, PayrollSheetORM.period, period)
        query = self._apply_status_filter(query, status)

        result: Result[tuple] = await self._execute(query)
        return [_EmployeeAggregateInfo._make(row) for row in result.all()]

    async def _fetch_summary_aggregates(
        self,
        period: DateBetween,
        status: PayrollStatus | None,
    ) -> list[_DepartmentPayrollSummary]:
        dept_salary_subq: Subquery = (
            select(
                EmployeeORM.department_id,
                func.sum(PositionORM.base_salary).label("total_base_salary"),
                func.count(EmployeeORM.id).label("employee_count"),
            )
            .join(PositionORM, EmployeeORM.position_id == PositionORM.id)
            .group_by(EmployeeORM.department_id)
            .subquery()
        )

        accruals_sum: Label[Decimal] = func.sum(
            case(
                (
                    PayrollItemORM.payroll_type == PayrollItemType.ACCRUAL,
                    PayrollRecordORM.amount,
                ),
                else_=Decimal(0),
            )
        ).label("total_accruals")

        deductions_sum: Label[Decimal] = func.sum(
            case(
                (
                    PayrollItemORM.payroll_type == PayrollItemType.DEDUCTION,
                    PayrollRecordORM.amount,
                ),
                else_=Decimal(0),
            )
        ).label("total_deductions")

        query: Select[tuple] = (
            select(
                DepartmentORM.code.label("department_code"),
                DepartmentORM.name.label("department_name"),
                dept_salary_subq.c.employee_count,
                dept_salary_subq.c.total_base_salary,
                accruals_sum,
                deductions_sum,
            )
            .join(dept_salary_subq, dept_salary_subq.c.department_id == DepartmentORM.id)
            .join(EmployeeORM, EmployeeORM.department_id == DepartmentORM.id)
            .join(PayrollSheetORM, PayrollSheetORM.employee_id == EmployeeORM.id)
            .join(PayrollRecordORM, PayrollRecordORM.payroll_sheet_id == PayrollSheetORM.id)
            .join(PayrollItemORM, PayrollRecordORM.payroll_item_id == PayrollItemORM.id)
            .group_by(
                DepartmentORM.id,
                DepartmentORM.code,
                DepartmentORM.name,
                dept_salary_subq.c.employee_count,
                dept_salary_subq.c.total_base_salary,
            )
            .order_by(DepartmentORM.name)
        )
        query = self._apply_period_filter(query, PayrollSheetORM.period, period)
        query = self._apply_status_filter(query, status)

        result: Result[tuple] = await self._execute(query)
        return [_DepartmentPayrollSummary._make(row) for row in result.all()]

    def _apply_period_filter[T: tuple](
        self,
        query: Select[T],
        column: InstrumentedAttribute,
        between: Between | None,
    ) -> Select[T]:
        if between is None:
            return query
        if between.value_from is not None:
            query = query.where(column >= between.value_from)
        if between.value_to is not None:
            query = query.where(column <= between.value_to)
        return query

    def _apply_status_filter[T: tuple](
        self,
        query: Select[T],
        status: PayrollStatus | None,
    ) -> Select[T]:
        if status is None:
            return query
        return query.where(PayrollSheetORM.status == status)

    def _build_payroll_sheet_data(
        self, records: list[_PayrollRecordInfo]
    ) -> list[PayrollSheetData]:
        sheets: dict[PayrollSheetId, list[PayrollRecordData]] = {}
        sheet_periods: dict[PayrollSheetId, date] = {}

        for record in records:
            sheet_id: PayrollSheetId = record.sheet_id
            sheet_periods[sheet_id] = record.period
            sheets.setdefault(sheet_id, []).append(
                PayrollRecordData(
                    payroll_item_code=record.payroll_item_code,
                    payroll_item_name=record.payroll_item_name,
                    payroll_type=record.payroll_type,
                    amount=record.amount,
                    comment=record.comment,
                )
            )

        result: list[PayrollSheetData] = []
        for sheet_id, sheet_records in sheets.items():
            accruals: Decimal = sum(
                (
                    rec.amount
                    for rec in sheet_records
                    if rec.payroll_type == PayrollItemType.ACCRUAL
                ),
                start=Decimal(0),
            )

            deductions: Decimal = sum(
                (
                    rec.amount
                    for rec in sheet_records
                    if rec.payroll_type == PayrollItemType.DEDUCTION
                ),
                start=Decimal(0),
            )

            result.append(
                PayrollSheetData(
                    period=sheet_periods[sheet_id],
                    accruals_sum=accruals,
                    deductions_sum=deductions,
                    net_salary=accruals - deductions,
                    records=sheet_records,
                )
            )

        return result

    async def _execute[T: tuple](self, query: Select[T]) -> Result[T]:
        try:
            return await self._session.execute(query)
        except SQLAlchemyError as e:
            raise OperationFailedError from e
