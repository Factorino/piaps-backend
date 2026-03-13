from dishka import BaseScope, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.readers.payroll_item import IPayrollItemReader
from piaps.application.interfaces.readers.payroll_sheet import IPayrollSheetReader
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.readers.report import IPayrollReportReader
from piaps.application.interfaces.readers.user import IUserReader
from piaps.infrastructure.database.readers.department import SADepartmentReader
from piaps.infrastructure.database.readers.employee import SAEmployeeReader
from piaps.infrastructure.database.readers.payroll_item import SAPayrollItemReader
from piaps.infrastructure.database.readers.payroll_sheet import SAPayrollSheetReader
from piaps.infrastructure.database.readers.position import SAPositionReader
from piaps.infrastructure.database.readers.report import SAPayrollReportReader
from piaps.infrastructure.database.readers.user import SAUserReader


class ReadersProvider(Provider):
    scope: BaseScope | None = Scope.REQUEST

    @provide
    def department_reader(self, session: AsyncSession) -> IDepartmentReader:
        return SADepartmentReader(session)

    @provide
    def employee_reader(self, session: AsyncSession) -> IEmployeeReader:
        return SAEmployeeReader(session)

    @provide
    def payroll_item_reader(self, session: AsyncSession) -> IPayrollItemReader:
        return SAPayrollItemReader(session)

    @provide
    def payroll_sheet_reader(self, session: AsyncSession) -> IPayrollSheetReader:
        return SAPayrollSheetReader(session)

    @provide
    def position_reader(self, session: AsyncSession) -> IPositionReader:
        return SAPositionReader(session)

    @provide
    def report_reader(self, session: AsyncSession) -> IPayrollReportReader:
        return SAPayrollReportReader(session)

    @provide
    def user_reader(self, session: AsyncSession) -> IUserReader:
        return SAUserReader(session)
