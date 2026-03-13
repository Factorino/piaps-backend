from dishka import BaseScope, Provider, Scope, provide

from piaps.application.interfaces.reports.renderer import IReportRenderer
from piaps.infrastructure.report.renderer import ReportRenderer
from piaps.main.config.renderer import RendererConfig


class ReportRenderersProvider(Provider):
    scope: BaseScope | None = Scope.REQUEST

    @provide(provides=IReportRenderer)
    def report_renderer(self, config: RendererConfig) -> IReportRenderer:
        return ReportRenderer(config.templates_path)
