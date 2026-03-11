from abc import abstractmethod
from enum import StrEnum
from typing import Protocol

from piaps.application.common.dto.base import dto


class ReportTemplate(StrEnum):
    EMPLOYEE_PAYROLL_REPORT  = "employee_payroll_report"
    DEPARTMENT_PAYROLL_REPORT  = "department_payroll_report"
    PAYROLL_SUMMARY_REPORT = "payroll_summary_report"


class ReportFormat(StrEnum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


@dto
class ReportDocument:
    content: bytes
    filename: str
    mime_type: str


class IReportRenderer(Protocol):
    @abstractmethod
    async def render[T](
        self,
        data: T, # pyright: ignore[reportInvalidTypeVarUse]
        template_name: ReportTemplate,
        format: ReportFormat,
    ) -> ReportDocument: ...
