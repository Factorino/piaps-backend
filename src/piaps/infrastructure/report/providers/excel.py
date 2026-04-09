import asyncio
from io import BytesIO
from pathlib import Path
from typing import Any, Final

from xlsxtpl.writerx import BookWriter

from piaps.application.errors.base import OperationFailedError
from piaps.application.interfaces.reports.renderer import ReportDocument, ReportTemplate
from piaps.infrastructure.report.providers.base import IReportProvider


class ExcelReportProvider(IReportProvider):
    _MIME_TYPE: Final[str] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def __init__(self, templates_dir: Path) -> None:
        self._templates_dir: Path = templates_dir / "excel"

    async def render(
        self,
        template_name: ReportTemplate,
        data: dict[str, Any],
    ) -> ReportDocument:
        template_path: Path = self._templates_dir / f"{template_name.value}.xlsx"

        writer = BookWriter(str(template_path))
        await asyncio.to_thread(writer.render_book, [data])

        output = BytesIO()
        writer.save(output)
        excel_bytes: bytes = output.getvalue()
        if not excel_bytes:
            raise OperationFailedError("Error occured while render Excel report")

        return ReportDocument(
            content=excel_bytes,
            filename=f"{template_name.value}.xlsx",
            mime_type=self._MIME_TYPE,
        )
