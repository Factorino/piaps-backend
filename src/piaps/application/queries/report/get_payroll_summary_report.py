from decimal import Decimal
from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.between import DateBetween
from piaps.application.common.dto.report.payroll_summary import (
    PayrollSummaryByDepartmentData,
    PayrollSummaryReportData,
)
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.readers.payroll_sheet import IPayrollSheetReader
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.reports.renderer import (
    IReportRenderer,
    ReportDocument,
    ReportFormat,
    ReportTemplate,
)
from piaps.domain.entities.department import Department
from piaps.domain.entities.user import User
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.enums.user_role import UserRole


if TYPE_CHECKING:
    from piaps.application.common.dto.query.pagination import PaginationResult
    from piaps.domain.entities.employee import Employee, EmployeeId
    from piaps.domain.entities.payroll_sheet import PayrollSheet
    from piaps.domain.entities.position import Position


@dto
class GetPayrollSummaryReportRequest:
    period: DateBetween
    status: PayrollStatus | None = None
    report_format: ReportFormat | None = None  # None => return only data


@dto
class GetPayrollSummaryReportResponse:
    data: PayrollSummaryReportData | None = None
    document: ReportDocument | None = None  # if report_format is specified


class GetPayrollSummaryReport(
    Interactor[GetPayrollSummaryReportRequest, GetPayrollSummaryReportResponse]
):
    def __init__(
        self,
        department_reader: IDepartmentReader,
        employee_reader: IEmployeeReader,
        position_reader: IPositionReader,
        payroll_sheet_reader: IPayrollSheetReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._department_reader: IDepartmentReader = department_reader
        self._employee_reader: IEmployeeReader = employee_reader
        self._position_reader: IPositionReader = position_reader
        self._payroll_sheet_reader: IPayrollSheetReader = payroll_sheet_reader
        self._report_renderer: IReportRenderer = report_renderer
        self._idp: IIdentityProvider = identity_provider

    async def execute(
        self, request: GetPayrollSummaryReportRequest
    ) -> GetPayrollSummaryReportResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        departments_result: PaginationResult[Department] = await self._department_reader.search(
            pagination=None
        )

        department_summaries: list[PayrollSummaryByDepartmentData] = []
        total_employee_count = 0
        grand_total_base_salary = Decimal(0)
        grand_total_accruals = Decimal(0)
        grand_total_deductions = Decimal(0)
        grand_total_net_salary = Decimal(0)

        for department in departments_result.data:
            summary: PayrollSummaryByDepartmentData = await self._build_department_summary(
                department=department,
                period=request.period,
                status=request.status,
            )
            department_summaries.append(summary)

            total_employee_count += summary.employee_count
            grand_total_base_salary += summary.total_base_salary
            grand_total_accruals += summary.total_accruals
            grand_total_deductions += summary.total_deductions
            grand_total_net_salary += summary.total_net_salary

        report_data = PayrollSummaryReportData(
            period_from=request.period.value_from,
            period_to=request.period.value_to,
            departments=department_summaries,
            total_employee_count=total_employee_count,
            grand_total_base_salary=grand_total_base_salary,
            grand_total_accruals=grand_total_accruals,
            grand_total_deductions=grand_total_deductions,
            grand_total_net_salary=grand_total_net_salary,
        )

        if request.report_format is not None:
            document: ReportDocument = await self._report_renderer.render(
                report_data, ReportTemplate.PAYROLL_SUMMARY_REPORT, request.report_format
            )
            return GetPayrollSummaryReportResponse(data=None, document=document)

        return GetPayrollSummaryReportResponse(data=report_data, document=None)

    async def _build_department_summary(
        self,
        department: Department,
        period: DateBetween,
        status: PayrollStatus | None,
    ) -> PayrollSummaryByDepartmentData:
        sheets_result: PaginationResult[
            PayrollSheet
        ] = await self._payroll_sheet_reader.search_by_department(
            department_id=department.id,
            period=period,
            status=status,
            sort=None,
            pagination=None,
        )

        employee_ids: set[EmployeeId] = {sheet.employee_id for sheet in sheets_result.data}
        total_base_salary = Decimal(0)
        total_accruals = Decimal(0)
        total_deductions = Decimal(0)
        total_net_salary = Decimal(0)

        for employee_id in employee_ids:
            employee: Employee | None = await self._employee_reader.find_by_id(employee_id)
            if employee is None:
                continue

            position: Position | None = await self._position_reader.find_by_id(
                employee.position_id
            )
            if position is not None:
                total_base_salary += position.base_salary.value

        for sheet in sheets_result.data:
            total_accruals += sheet.accruals_sum.value
            total_deductions += sheet.deductions_sum.value
            total_net_salary += sheet.net_salary.value

        return PayrollSummaryByDepartmentData(
            department_code=department.code.value,
            department_name=department.name.value,
            employee_count=len(employee_ids),
            total_base_salary=total_base_salary,
            total_accruals=total_accruals,
            total_deductions=total_deductions,
            total_net_salary=total_net_salary,
        )

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to view payroll summary reports")
