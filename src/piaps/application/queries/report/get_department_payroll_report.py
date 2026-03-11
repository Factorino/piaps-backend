from decimal import Decimal
from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.between import DateBetween
from piaps.application.common.dto.report.department_payroll import (
    DepartmentEmployeePayrollData,
    DepartmentPayrollReportData,
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
from piaps.domain.entities.department import Department, DepartmentId
from piaps.domain.entities.payroll_sheet import PayrollSheet
from piaps.domain.entities.user import User
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


if TYPE_CHECKING:
    from piaps.application.common.dto.query.pagination import PaginationResult
    from piaps.domain.entities.employee import Employee, EmployeeId
    from piaps.domain.entities.position import Position


@dto
class GetDepartmentPayrollReportRequest:
    department_id: DepartmentId
    period: DateBetween
    status: PayrollStatus | None = None
    report_format: ReportFormat | None = None  # None => return only data


@dto
class GetDepartmentPayrollReportResponse:
    data: DepartmentPayrollReportData | None = None
    document: ReportDocument | None = None  # if report_format is specified


class GetDepartmentPayrollReport(
    Interactor[GetDepartmentPayrollReportRequest, GetDepartmentPayrollReportResponse]
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
        self, request: GetDepartmentPayrollReportRequest
    ) -> GetDepartmentPayrollReportResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        department: Department | None = await self._department_reader.find_by_id(
            request.department_id
        )
        if department is None:
            raise NotFoundError(f"Department with id '{request.department_id}' not found")

        sheets_result: PaginationResult[
            PayrollSheet
        ] = await self._payroll_sheet_reader.search_by_department(
            department_id=request.department_id,
            period=request.period,
            status=request.status,
        )

        report_data: DepartmentPayrollReportData = await self._build_report_data(
            department=department,
            sheets=sheets_result.data,
            period=request.period,
        )

        if request.report_format is not None:
            document: ReportDocument = await self._report_renderer.render(
                report_data, ReportTemplate.DEPARTMENT_PAYROLL_REPORT, request.report_format
            )
            return GetDepartmentPayrollReportResponse(data=None, document=document)

        return GetDepartmentPayrollReportResponse(data=report_data, document=None)

    async def _build_report_data(
        self,
        department: Department,
        sheets: list[PayrollSheet],
        period: DateBetween,
    ) -> DepartmentPayrollReportData:
        employee_totals: dict[EmployeeId, dict[str, Decimal]] = {}

        for sheet in sheets:
            if sheet.employee_id not in employee_totals:
                employee_totals[sheet.employee_id] = {
                    "accruals": Decimal(0),
                    "deductions": Decimal(0),
                    "net_salary": Decimal(0),
                }

            employee_totals[sheet.employee_id]["accruals"] += sheet.accruals_sum.value
            employee_totals[sheet.employee_id]["deductions"] += sheet.deductions_sum.value
            employee_totals[sheet.employee_id]["net_salary"] += sheet.net_salary.value

        employees_dto: list[DepartmentEmployeePayrollData] = []
        total_base_salary = Decimal(0)
        total_accruals = Decimal(0)
        total_deductions = Decimal(0)
        total_net_salary = Decimal(0)

        for employee_id, totals in employee_totals.items():
            employee: Employee | None = await self._employee_reader.find_by_id(employee_id)
            if employee is None:
                continue

            position: Position | None = await self._position_reader.find_by_id(
                employee.position_id
            )
            if position is None:
                continue

            employee_dto = DepartmentEmployeePayrollData(
                employee_code=employee.code.value,
                employee_full_name=employee.full_name.full,
                position_name=position.name.value,
                base_salary=position.base_salary.value,
                accruals_sum=totals["accruals"],
                deductions_sum=totals["deductions"],
                net_salary=totals["net_salary"],
            )
            employees_dto.append(employee_dto)

            total_base_salary += position.base_salary.value
            total_accruals += totals["accruals"]
            total_deductions += totals["deductions"]
            total_net_salary += totals["net_salary"]

        return DepartmentPayrollReportData(
            department_code=department.code.value,
            department_name=department.name.value,
            period_from=period.value_from,
            period_to=period.value_to,
            employees=employees_dto,
            total_base_salary=total_base_salary,
            total_accruals=total_accruals,
            total_deductions=total_deductions,
            total_net_salary=total_net_salary,
            employee_count=len(employees_dto),
        )

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to view department payroll reports")
