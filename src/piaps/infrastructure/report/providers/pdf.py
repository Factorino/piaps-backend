from pathlib import Path
from typing import Any, Final, cast

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from weasyprint import HTML

from piaps.application.errors.base import OperationFailedError
from piaps.application.interfaces.reports.renderer import ReportDocument, ReportTemplate
from piaps.infrastructure.report.providers.base import IReportProvider


class PdfReportProvider(IReportProvider):
    _MIME_TYPE: Final[str] = "application/pdf"

    def __init__(self, templates_dir: Path) -> None:
        self._env = Environment(
            loader=FileSystemLoader(templates_dir / "pdf"),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=True,
        )

    async def render(
        self,
        template_name: ReportTemplate,
        data: dict[str, Any],
    ) -> ReportDocument:
        template_path: str = f"{template_name.value}.html.j2"
        template: Template = self._env.get_template(template_path)

        html_str: str = await template.render_async(**data)

        pdf_bytes: bytes | None = HTML(string=html_str).write_pdf()
        if not pdf_bytes:
            raise OperationFailedError("Error occured while render PDF report")

        return ReportDocument(
            content=cast("bytes", pdf_bytes),
            filename=f"{template_name.value}.pdf",
            mime_type=self._MIME_TYPE,
        )
