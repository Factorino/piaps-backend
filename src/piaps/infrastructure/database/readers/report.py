from collections.abc import Iterable, Sequence
from decimal import Decimal
from typing import TYPE_CHECKING, NamedTuple

from sqlalchemy import Label, Result, Select, Subquery, case, func, select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.dto.query.between import Between, DateBetween
from piaps.application.common.dto.report.department_payroll import (
    DepartmentPayrollReportData,
    EmployeePayrollData,
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
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.errors.base import NotFoundError
from piaps.infrastructure.database.models.department import DepartmentORM
from piaps.infrastructure.database.models.employee import EmployeeORM
from piaps.infrastructure.database.models.payroll_item import PayrollItemORM
from piaps.infrastructure.database.models.payroll_record import PayrollRecordORM
from piaps.infrastructure.database.models.payroll_sheet import PayrollSheetORM
from piaps.infrastructure.database.models.position import PositionORM


if TYPE_CHECKING:
    from sqlalchemy.engine.row import Row


def _decimal_sum(values: Iterable[Decimal]) -> Decimal:
    return sum(values, start=Decimal(0))


class _EmployeeInfo(NamedTuple):
    employee_code: str
    employee_full_name: str
    department_name: str
    position_name: str
    base_salary: Decimal


class SAPayrollReportReader(IPayrollReportReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_employee_payroll_report(
        self,
        employee_id: EmployeeId,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> EmployeePayrollReportData:
        employee_info: _EmployeeInfo = await self._fetch_employee_info(employee_id)
        sheets: list[PayrollSheetData] = await self._fetch_employee_sheets(
            employee_id, period, status
        )

        total_accruals: Decimal = _decimal_sum(s.accruals_sum for s in sheets)
        total_deductions: Decimal = _decimal_sum(s.deductions_sum for s in sheets)

        return EmployeePayrollReportData(
            employee_code=employee_info.employee_code,
            employee_full_name=employee_info.employee_full_name,
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
        department: DepartmentORM = await self._fetch_department(department_id)
        employees: list[EmployeePayrollData] = await self._fetch_department_employees_payroll(
            department_id, period, status
        )

        total_base_salary: Decimal = _decimal_sum(e.base_salary for e in employees)
        total_accruals: Decimal = _decimal_sum(e.accruals_sum for e in employees)
        total_deductions: Decimal = _decimal_sum(e.deductions_sum for e in employees)

        return DepartmentPayrollReportData(
            department_code=department.code,
            department_name=department.name,
            period_from=period.value_from,
            period_to=period.value_to,
            employees=employees,
            total_base_salary=total_base_salary,
            total_accruals=total_accruals,
            total_deductions=total_deductions,
            total_net_salary=total_accruals - total_deductions,
            employee_count=len(employees),
        )

    async def get_payroll_summary_report(
        self,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> PayrollSummaryReportData:
        departments: list[
            PayrollSummaryByDepartmentData
        ] = await self._fetch_payroll_summary_by_departments(period, status)

        return PayrollSummaryReportData(
            period_from=period.value_from,
            period_to=period.value_to,
            departments=departments,
            total_employee_count=sum(d.employee_count for d in departments),
            grand_total_base_salary=_decimal_sum(d.total_base_salary for d in departments),
            grand_total_accruals=_decimal_sum(d.total_accruals for d in departments),
            grand_total_deductions=_decimal_sum(d.total_deductions for d in departments),
            grand_total_net_salary=_decimal_sum(d.total_net_salary for d in departments),
        )

    async def _fetch_employee_info(self, employee_id: EmployeeId) -> _EmployeeInfo:
        query: Select[tuple] = (
            select(
                EmployeeORM.code.label("employee_code"),
                EmployeeORM.full_name.label("employee_full_name"),
                DepartmentORM.name.label("department_name"),
                PositionORM.name.label("position_name"),
                PositionORM.base_salary,
            )
            .join(DepartmentORM, EmployeeORM.department_id == DepartmentORM.id)
            .join(PositionORM, EmployeeORM.position_id == PositionORM.id)
            .where(EmployeeORM.id == employee_id)
        )

        result: Result[tuple] = await self._execute(query)
        try:
            return _EmployeeInfo._make(result.one())
        except NoResultFound as e:
            raise NotFoundError(f"Employee with id '{employee_id}' not found") from e

    async def _fetch_employee_sheets(
        self,
        employee_id: EmployeeId,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> list[PayrollSheetData]:
        query: Select[tuple[PayrollSheetORM]] = select(PayrollSheetORM).where(
            PayrollSheetORM.employee_id == employee_id
        )
        query = self._apply_period_filter(query, PayrollSheetORM.period, period)
        query = self._apply_status_filter(query, PayrollSheetORM.status, status)

        result: Result[tuple[PayrollSheetORM]] = await self._execute(query)
        sheets_orm: Sequence[PayrollSheetORM] = result.scalars().all()
        return self._build_employee_sheets(sheets_orm)

    async def _fetch_department(self, department_id: DepartmentId) -> DepartmentORM:
        query: Select[tuple[DepartmentORM]] = select(DepartmentORM).where(
            DepartmentORM.id == department_id
        )
        result: Result[tuple[DepartmentORM]] = await self._execute(query)
        try:
            return result.scalars().one()
        except NoResultFound as e:
            raise NotFoundError(f"Department with id '{department_id}' not found") from e

    async def _fetch_department_employees_payroll(
        self,
        department_id: DepartmentId,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> list[EmployeePayrollData]:
        sheets_subquery: Subquery = self._get_sheets_subquery(period, status)

        query: Select[tuple[str, str, str, Decimal, Decimal, Decimal]] = (
            select(
                EmployeeORM.code.label("employee_code"),
                EmployeeORM.full_name.label("employee_full_name"),
                PositionORM.name.label("position_name"),
                PositionORM.base_salary,
                func.coalesce(sheets_subquery.c.accruals_sum, Decimal(0)).label("accruals_sum"),
                func.coalesce(sheets_subquery.c.deductions_sum, Decimal(0)).label(
                    "deductions_sum"
                ),
            )
            .join(PositionORM, EmployeeORM.position_id == PositionORM.id)
            .outerjoin(sheets_subquery, sheets_subquery.c.employee_id == EmployeeORM.id)
            .where(EmployeeORM.department_id == department_id)
            .order_by(EmployeeORM.full_name)
        )

        result: Result[tuple[str, str, str, Decimal, Decimal, Decimal]] = await self._execute(query)
        rows: Sequence[Row[tuple[str, str, str, Decimal, Decimal, Decimal]]] = result.all()

        return [
            EmployeePayrollData(
                employee_code=row.employee_code,
                employee_full_name=row.employee_full_name,
                position_name=row.position_name,
                base_salary=row.base_salary,
                accruals_sum=row.accruals_sum,
                deductions_sum=row.deductions_sum,
                net_salary=row.accruals_sum - row.deductions_sum,
            )
            for row in rows
        ]

    async def _fetch_payroll_summary_by_departments(
        self,
        period: DateBetween,
        status: PayrollStatus | None,
    ) -> list[PayrollSummaryByDepartmentData]:
        sheets_subquery: Subquery = self._get_sheets_subquery(period, status)

        query: Select[tuple[str, str, int, Decimal, Decimal, Decimal]] = (
            select(
                DepartmentORM.code.label("department_code"),
                DepartmentORM.name.label("department_name"),
                func.count(EmployeeORM.id).label("employee_count"),
                func.coalesce(func.sum(PositionORM.base_salary), Decimal(0)).label(
                    "total_base_salary"
                ),
                func.coalesce(func.sum(sheets_subquery.c.accruals_sum), Decimal(0)).label(
                    "total_accruals"
                ),
                func.coalesce(func.sum(sheets_subquery.c.deductions_sum), Decimal(0)).label(
                    "total_deductions"
                ),
            )
            .outerjoin(EmployeeORM, EmployeeORM.department_id == DepartmentORM.id)
            .outerjoin(PositionORM, EmployeeORM.position_id == PositionORM.id)
            .outerjoin(sheets_subquery, sheets_subquery.c.employee_id == EmployeeORM.id)
            .group_by(DepartmentORM.id, DepartmentORM.code, DepartmentORM.name)
            .order_by(DepartmentORM.name)
        )

        result: Result[tuple[str, str, int, Decimal, Decimal, Decimal]] = await self._execute(query)
        rows: Sequence[Row[tuple[str, str, int, Decimal, Decimal, Decimal]]] = result.all()

        return [
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

    async def _execute[T: tuple](self, query: Select[T]) -> Result[T]:
        try:
            return await self._session.execute(query)
        except SQLAlchemyError as e:
            raise OperationFailedError from e

    def _get_sheets_subquery(
        self,
        period: DateBetween,
        status: PayrollStatus | None,
    ) -> Subquery:
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

        sheets_query: Select[tuple[EmployeeId, Decimal, Decimal]] = (
            select(
                PayrollSheetORM.employee_id,
                accruals_sum,
                deductions_sum,
            )
            .join(PayrollRecordORM, PayrollRecordORM.payroll_sheet_id == PayrollSheetORM.id)
            .join(PayrollItemORM, PayrollRecordORM.payroll_item_id == PayrollItemORM.id)
            .group_by(PayrollSheetORM.employee_id)
        )

        sheets_query = self._apply_period_filter(sheets_query, PayrollSheetORM.period, period)
        sheets_query = self._apply_status_filter(sheets_query, PayrollSheetORM.status, status)
        return sheets_query.subquery()

    def _build_employee_sheets(
        self, sheets_orm: Iterable[PayrollSheetORM]
    ) -> list[PayrollSheetData]:
        sheets: list[PayrollSheetData] = []
        for sheet in sheets_orm:
            records: list[PayrollRecordData] = [
                PayrollRecordData(
                    payroll_item_code=record.payroll_item.code,
                    payroll_item_name=record.payroll_item.name,
                    payroll_type=record.payroll_item.payroll_type,
                    amount=record.amount,
                    comment=record.comment,
                )
                for record in sheet.records
            ]

            accruals_sum: Decimal = _decimal_sum(
                r.amount for r in records if r.payroll_type == PayrollItemType.ACCRUAL
            )
            deductions_sum: Decimal = _decimal_sum(
                r.amount for r in records if r.payroll_type == PayrollItemType.DEDUCTION
            )

            sheets.append(
                PayrollSheetData(
                    period=sheet.period,
                    accruals_sum=accruals_sum,
                    deductions_sum=deductions_sum,
                    net_salary=accruals_sum - deductions_sum,
                    records=records,
                )
            )

        return sheets

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
        column: InstrumentedAttribute,
        status: PayrollStatus | None,
    ) -> Select[T]:
        if status is None:
            return query
        return query.where(column == status)
