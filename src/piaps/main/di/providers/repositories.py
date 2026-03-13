from dishka import BaseScope, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.application.interfaces.repositories.employee import IEmployeeRepository
from piaps.application.interfaces.repositories.payroll_item import IPayrollItemRepository
from piaps.application.interfaces.repositories.payroll_sheet import IPayrollSheetRepository
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.infrastructure.database.repositories.department import SADepartmentRepository
from piaps.infrastructure.database.repositories.employee import SAEmployeeRepository
from piaps.infrastructure.database.repositories.payroll_item import SAPayrollItemRepository
from piaps.infrastructure.database.repositories.payroll_sheet import SAPayrollSheetRepository
from piaps.infrastructure.database.repositories.position import SAPositionRepository
from piaps.infrastructure.database.repositories.user import SAUserRepository


class RepositoriesProvider(Provider):
    scope: BaseScope | None = Scope.REQUEST

    @provide
    def department_repository(self, session: AsyncSession) -> IDepartmentRepository:
        return SADepartmentRepository(session)

    @provide
    def employee_repository(self, session: AsyncSession) -> IEmployeeRepository:
        return SAEmployeeRepository(session)

    @provide
    def payroll_item_repository(self, session: AsyncSession) -> IPayrollItemRepository:
        return SAPayrollItemRepository(session)

    @provide
    def payroll_sheet_repository(self, session: AsyncSession) -> IPayrollSheetRepository:
        return SAPayrollSheetRepository(session)

    @provide
    def position_repository(self, session: AsyncSession) -> IPositionRepository:
        return SAPositionRepository(session)

    @provide
    def user_repository(self, session: AsyncSession) -> IUserRepository:
        return SAUserRepository(session)
