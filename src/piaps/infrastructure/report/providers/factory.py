from pathlib import Path
from types import MappingProxyType
from typing import Final

from piaps.application.interfaces.reports.renderer import ReportFormat
from piaps.infrastructure.report.providers.base import IReportProvider
from piaps.infrastructure.report.providers.excel import ExcelReportProvider
from piaps.infrastructure.report.providers.pdf import PdfReportProvider


class ReportProviderFactory:
    def __init__(self, templates_dir: Path) -> None:
        self._providers: Final[MappingProxyType[ReportFormat, IReportProvider]] = MappingProxyType(
            {
                ReportFormat.PDF: PdfReportProvider(templates_dir),
                ReportFormat.EXCEL: ExcelReportProvider(templates_dir),
            }
        )

    def get_provider(self, format: ReportFormat) -> IReportProvider:
        provider: IReportProvider | None = self._providers.get(format)
        if not provider:
            raise ValueError(f"Unsupported report format: {format}")
        return provider
