from dishka import BaseScope, Provider, Scope, provide

from piaps.domain.services.code_generator import CodeGenerator
from piaps.domain.services.payroll_service import PayrollService


class DomainServicesProvider(Provider):
    scope: BaseScope | None = Scope.APP

    @provide
    def code_generator(self) -> CodeGenerator:
        return CodeGenerator()

    @provide
    def payroll_service(self) -> PayrollService:
        return PayrollService()
