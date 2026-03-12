from pathlib import Path
from typing import TYPE_CHECKING, Any

from adaptix import Retort

from piaps.application.interfaces.reports.renderer import (
    IReportRenderer,
    ReportDocument,
    ReportFormat,
    ReportTemplate,
)
from piaps.infrastructure.report.providers.factory import ReportProviderFactory


if TYPE_CHECKING:
    from piaps.infrastructure.report.providers.base import IReportProvider


_retort = Retort()


class ReportRenderer(IReportRenderer):
    def __init__(self, templates_dir: Path) -> None:
        self._factory = ReportProviderFactory(templates_dir)

    async def render[T](
        self,
        data: T,  # pyright: ignore[reportInvalidTypeVarUse]
        template_name: ReportTemplate,
        format: ReportFormat,
    ) -> ReportDocument:
        dumped: dict[str, Any] = _retort.dump(data)
        provider: IReportProvider = self._factory.get_provider(format)
        return await provider.render(template_name, dumped)
