from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.between import DateBetween
from piaps.application.common.dto.report.employee_payroll import (
    EmployeePayrollReportData,
)
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.report import IPayrollReportReader
from piaps.application.interfaces.reports.renderer import (
    IReportRenderer,
    ReportDocument,
    ReportFormat,
    ReportTemplate,
)
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.user import User
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.enums.user_role import UserRole


@dto
class GetEmployeePayrollReportRequest:
    employee_id: EmployeeId
    period: DateBetween
    status: PayrollStatus | None = None
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
        report_reader: IPayrollReportReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._report_reader: IPayrollReportReader = report_reader
        self._report_renderer: IReportRenderer = report_renderer
        self._idp: IIdentityProvider = identity_provider

    async def execute(
        self, request: GetEmployeePayrollReportRequest
    ) -> GetEmployeePayrollReportResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user, request.employee_id)

        report_data: EmployeePayrollReportData = (
            await self._report_reader.get_employee_payroll_report(
                request.employee_id, request.period, request.status
            )
        )

        if request.report_format is not None:
            document: ReportDocument = await self._report_renderer.render(
                report_data, ReportTemplate.EMPLOYEE_PAYROLL_REPORT, request.report_format
            )
            return GetEmployeePayrollReportResponse(data=None, document=document)

        return GetEmployeePayrollReportResponse(data=report_data, document=None)

    def _check_access(self, current_user: User, target_employee_id: EmployeeId) -> None:
        if current_user.role >= UserRole.ACCOUNTANT:
            return

        if current_user.employee_id is None or current_user.employee_id != target_employee_id:
            raise AccessDeniedError(
                "You don't have permission to view another employee's payroll report"
            )
