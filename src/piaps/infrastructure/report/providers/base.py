from abc import abstractmethod
from typing import Any, Protocol

from piaps.application.interfaces.reports.renderer import ReportDocument, ReportTemplate


class IReportProvider(Protocol):
    @abstractmethod
    async def render(
        self, template_name: ReportTemplate, data: dict[str, Any]
    ) -> ReportDocument: ...
