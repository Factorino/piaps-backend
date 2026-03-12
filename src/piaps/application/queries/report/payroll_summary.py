from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.between import DateBetween
from piaps.application.common.dto.report.payroll_summary import (
    PayrollSummaryReportData,
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
from piaps.domain.entities.user import User
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.enums.user_role import UserRole


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
        report_reader: IPayrollReportReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._report_reader: IPayrollReportReader = report_reader
        self._report_renderer: IReportRenderer = report_renderer
        self._idp: IIdentityProvider = identity_provider

    async def execute(
        self, request: GetPayrollSummaryReportRequest
    ) -> GetPayrollSummaryReportResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        report_data: PayrollSummaryReportData = (
            await self._report_reader.get_payroll_summary_report(request.period, request.status)
        )

        if request.report_format is not None:
            document: ReportDocument = await self._report_renderer.render(
                report_data, ReportTemplate.PAYROLL_SUMMARY_REPORT, request.report_format
            )
            return GetPayrollSummaryReportResponse(data=None, document=document)

        return GetPayrollSummaryReportResponse(data=report_data, document=None)

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to view payroll summary reports")
