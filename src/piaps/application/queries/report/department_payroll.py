from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.between import DateBetween
from piaps.application.common.dto.report.department_payroll import (
    DepartmentPayrollReportData,
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
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.user import User
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.enums.user_role import UserRole


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
        report_reader: IPayrollReportReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._report_reader: IPayrollReportReader = report_reader
        self._report_renderer: IReportRenderer = report_renderer
        self._idp: IIdentityProvider = identity_provider

    async def execute(
        self, request: GetDepartmentPayrollReportRequest
    ) -> GetDepartmentPayrollReportResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        report_data: DepartmentPayrollReportData = (
            await self._report_reader.get_department_payroll_report(
                request.department_id, request.period, request.status
            )
        )

        if request.report_format is not None:
            document: ReportDocument = await self._report_renderer.render(
                report_data, ReportTemplate.DEPARTMENT_PAYROLL_REPORT, request.report_format
            )
            return GetDepartmentPayrollReportResponse(data=None, document=document)

        return GetDepartmentPayrollReportResponse(data=report_data, document=None)

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to view department payroll reports")
