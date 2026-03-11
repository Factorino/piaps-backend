from decimal import Decimal
from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.between import DateBetween
from piaps.application.common.dto.report.employee_payroll import (
    EmployeePayrollReportData,
    PayrollRecordData,
    PayrollSheetData,
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
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.payroll_sheet import PayrollSheet
from piaps.domain.entities.position import Position
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


if TYPE_CHECKING:
    from piaps.application.common.dto.query.pagination import PaginationResult


@dto
class GetEmployeePayrollReportRequest:
    employee_id: EmployeeId
    period: DateBetween
    report_format: ReportFormat | None = None  # None => return only data


@dto
class GetEmployeePayrollReportResponse:
    data: EmployeePayrollReportData | None = None
    document: ReportDocument | None = None  # if report_format is specified


class GetEmployeePayrollReport(
    Interactor[GetEmployeePayrollReportRequest, GetEmployeePayrollReportResponse]
):
    def __init__(
        self,
        employee_reader: IEmployeeReader,
        department_reader: IDepartmentReader,
        position_reader: IPositionReader,
        payroll_sheet_reader: IPayrollSheetReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._employee_reader: IEmployeeReader = employee_reader
        self._department_reader: IDepartmentReader = department_reader
        self._position_reader: IPositionReader = position_reader
        self._payroll_sheet_reader: IPayrollSheetReader = payroll_sheet_reader
        self._report_renderer: IReportRenderer = report_renderer
        self._idp: IIdentityProvider = identity_provider

    async def execute(
        self, request: GetEmployeePayrollReportRequest
    ) -> GetEmployeePayrollReportResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user, request.employee_id)

        employee: Employee | None = await self._employee_reader.find_by_id(request.employee_id)
        if employee is None:
            raise NotFoundError(f"Employee with id '{request.employee_id}' not found")

        department: Department | None = await self._department_reader.find_by_id(
            employee.department_id
        )
        if department is None:
            raise NotFoundError(f"Department with id '{employee.department_id}' not found")

        position: Position | None = await self._position_reader.find_by_id(employee.position_id)
        if position is None:
            raise NotFoundError(f"Position with id '{employee.position_id}' not found")

        sheets_result: PaginationResult[
            PayrollSheet
        ] = await self._payroll_sheet_reader.search_by_employee(
            employee_id=request.employee_id,
            period=request.period,
        )

        report_data: EmployeePayrollReportData = await self._build_report_data(
            employee, department, position, sheets_result.data
        )

        if request.report_format is not None:
            document: ReportDocument = await self._report_renderer.render(
                report_data, ReportTemplate.EMPLOYEE_PAYROLL_REPORT, request.report_format
            )
            return GetEmployeePayrollReportResponse(data=None, document=document)

        return GetEmployeePayrollReportResponse(data=report_data, document=None)

    async def _build_report_data(
        self,
        employee: Employee,
        department: Department,
        position: Position,
        sheets: list[PayrollSheet],
    ) -> EmployeePayrollReportData:
        sheet_dtos: list[PayrollSheetData] = []
        total_accruals = Decimal(0)
        total_deductions = Decimal(0)
        total_net_salary = Decimal(0)

        for sheet in sheets:
            records_dto: list[PayrollRecordData] = [
                PayrollRecordData(
                    payroll_item_code=record.payroll_item.code.value,
                    payroll_item_name=record.payroll_item.name.value,
                    payroll_type=record.payroll_item.payroll_type,
                    amount=record.amount.value,
                    comment=record.comment,
                )
                for record in sheet.records
            ]

            sheet_dto = PayrollSheetData(
                period=sheet.period,
                accruals_sum=sheet.accruals_sum.value,
                deductions_sum=sheet.deductions_sum.value,
                net_salary=sheet.net_salary.value,
                records=records_dto,
            )
            sheet_dtos.append(sheet_dto)

            total_accruals += sheet.accruals_sum.value
            total_deductions += sheet.deductions_sum.value
            total_net_salary += sheet.net_salary.value

        return EmployeePayrollReportData(
            employee_code=employee.code.value,
            employee_full_name=employee.full_name.full,
            department_name=department.name.value,
            position_name=position.name.value,
            base_salary=position.base_salary.value,
            sheets=sheet_dtos,
            total_accruals=total_accruals,
            total_deductions=total_deductions,
            total_net_salary=total_net_salary,
        )

    def _check_access(self, current_user: User, target_employee_id: EmployeeId) -> None:
        if current_user.role >= UserRole.ACCOUNTANT:
            return

        if current_user.employee_id is None or current_user.employee_id != target_employee_id:
            raise AccessDeniedError(
                "You don't have permission to view another employee's payroll report"
            )
