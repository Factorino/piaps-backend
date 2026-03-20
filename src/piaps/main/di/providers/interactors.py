from dishka import BaseScope, Provider, Scope, provide

from piaps.application.commands.auth.login_user import LoginUser
from piaps.application.commands.auth.refresh_token import RefreshToken
from piaps.application.commands.auth.register_user import RegisterUser
from piaps.application.commands.department.create import CreateDepartment
from piaps.application.commands.department.delete import DeleteDepartment
from piaps.application.commands.department.update import UpdateDepartment
from piaps.application.commands.employee.create import CreateEmployee
from piaps.application.commands.employee.delete import DeleteEmployee
from piaps.application.commands.employee.update import UpdateEmployee
from piaps.application.commands.payroll_item.create import CreatePayrollItem
from piaps.application.commands.payroll_item.delete import DeletePayrollItem
from piaps.application.commands.payroll_item.update import UpdatePayrollItem
from piaps.application.commands.payroll_sheet.add_record import AddPayrollRecord
from piaps.application.commands.payroll_sheet.cancel import CancelPayrollSheet
from piaps.application.commands.payroll_sheet.confirm import ConfirmPayrollSheet
from piaps.application.commands.payroll_sheet.create import CreatePayrollSheet
from piaps.application.commands.payroll_sheet.remove_record import RemovePayrollRecord
from piaps.application.commands.position.create import CreatePosition
from piaps.application.commands.position.delete import DeletePosition
from piaps.application.commands.position.update import UpdatePosition
from piaps.application.commands.user.bind_employee import BindEmployee
from piaps.application.commands.user.change_password import ChangePassword
from piaps.application.commands.user.change_role import ChangeUserRole
from piaps.application.commands.user.change_username import ChangeUsername
from piaps.application.commands.user.create import CreateUser
from piaps.application.commands.user.delete import DeleteUser
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.auth.jwt_provider import IJWTProvider
from piaps.application.interfaces.auth.password_hasher import IPasswordHasher
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.readers.payroll_item import IPayrollItemReader
from piaps.application.interfaces.readers.payroll_sheet import IPayrollSheetReader
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.readers.report import IPayrollReportReader
from piaps.application.interfaces.readers.user import IUserReader
from piaps.application.interfaces.reports.renderer import IReportRenderer
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.application.interfaces.repositories.employee import IEmployeeRepository
from piaps.application.interfaces.repositories.payroll_item import IPayrollItemRepository
from piaps.application.interfaces.repositories.payroll_sheet import IPayrollSheetRepository
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.application.interfaces.repositories.user import IUserRepository
from piaps.application.queries.department.get_by_id import GetDepartmentById
from piaps.application.queries.department.search import SearchDepartments
from piaps.application.queries.employee.get_by_id import GetEmployeeById
from piaps.application.queries.employee.search import SearchEmployees
from piaps.application.queries.payroll_item.get_by_id import GetPayrollItemById
from piaps.application.queries.payroll_item.search import SearchPayrollItems
from piaps.application.queries.payroll_sheet.get_by_id import GetPayrollSheetById
from piaps.application.queries.payroll_sheet.search import SearchPayrollSheets
from piaps.application.queries.position.get_by_id import GetPositionById
from piaps.application.queries.position.search import SearchPositions
from piaps.application.queries.report.department_payroll import GetDepartmentPayrollReport
from piaps.application.queries.report.employee_payroll import GetEmployeePayrollReport
from piaps.application.queries.report.payroll_summary import GetPayrollSummaryReport
from piaps.application.queries.user.get_by_id import GetUserById
from piaps.application.queries.user.get_current import GetCurrentUser
from piaps.application.queries.user.search import SearchUsers
from piaps.domain.services.code_generator import CodeGenerator
from piaps.domain.services.payroll_service import PayrollService


class InteractorsProvider(Provider):
    scope: BaseScope | None = Scope.REQUEST

    # Auth

    @provide
    def register_user(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        employee_reader: IEmployeeReader,
        password_hasher: IPasswordHasher,
        transaction_manager: ITransactionManager,
    ) -> RegisterUser:
        return RegisterUser(
            user_repository,
            user_reader,
            employee_reader,
            password_hasher,
            transaction_manager,
        )

    @provide
    def login_user(
        self,
        user_reader: IUserReader,
        password_hasher: IPasswordHasher,
        jwt_provider: IJWTProvider,
    ) -> LoginUser:
        return LoginUser(user_reader, password_hasher, jwt_provider)

    @provide
    def refresh_token(
        self,
        user_reader: IUserReader,
        jwt_provider: IJWTProvider,
    ) -> RefreshToken:
        return RefreshToken(user_reader, jwt_provider)

    # User management

    @provide
    def create_user(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        password_hasher: IPasswordHasher,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> CreateUser:
        return CreateUser(
            user_repository, user_reader, password_hasher, transaction_manager, identity_provider
        )

    @provide
    def delete_user(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> DeleteUser:
        return DeleteUser(user_repository, user_reader, transaction_manager, identity_provider)

    @provide
    def change_username(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> ChangeUsername:
        return ChangeUsername(user_repository, user_reader, transaction_manager, identity_provider)

    @provide
    def change_password(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        password_hasher: IPasswordHasher,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> ChangePassword:
        return ChangePassword(
            user_repository, user_reader, password_hasher, transaction_manager, identity_provider
        )

    @provide
    def change_user_role(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> ChangeUserRole:
        return ChangeUserRole(user_repository, user_reader, transaction_manager, identity_provider)

    @provide
    def bind_employee(
        self,
        user_repository: IUserRepository,
        user_reader: IUserReader,
        employee_reader: IEmployeeReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> BindEmployee:
        return BindEmployee(
            user_repository, user_reader, employee_reader, transaction_manager, identity_provider
        )

    @provide
    def get_current_user(self, identity_provider: IIdentityProvider) -> GetCurrentUser:
        return GetCurrentUser(identity_provider)

    @provide
    def get_user_by_id(
        self,
        user_reader: IUserReader,
        identity_provider: IIdentityProvider,
    ) -> GetUserById:
        return GetUserById(user_reader, identity_provider)

    @provide
    def search_users(
        self,
        user_reader: IUserReader,
        identity_provider: IIdentityProvider,
    ) -> SearchUsers:
        return SearchUsers(user_reader, identity_provider)

    # Departments

    @provide
    def create_department(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> CreateDepartment:
        return CreateDepartment(
            department_repository,
            department_reader,
            code_generator,
            transaction_manager,
            identity_provider,
        )

    @provide
    def update_department(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> UpdateDepartment:
        return UpdateDepartment(
            department_repository, department_reader, transaction_manager, identity_provider
        )

    @provide
    def delete_department(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> DeleteDepartment:
        return DeleteDepartment(
            department_repository, department_reader, transaction_manager, identity_provider
        )

    @provide
    def get_department_by_id(
        self,
        department_reader: IDepartmentReader,
        identity_provider: IIdentityProvider,
    ) -> GetDepartmentById:
        return GetDepartmentById(department_reader, identity_provider)

    @provide
    def search_departments(
        self,
        department_reader: IDepartmentReader,
        identity_provider: IIdentityProvider,
    ) -> SearchDepartments:
        return SearchDepartments(department_reader, identity_provider)

    # Positions

    @provide
    def create_position(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> CreatePosition:
        return CreatePosition(
            position_repository,
            position_reader,
            code_generator,
            transaction_manager,
            identity_provider,
        )

    @provide
    def update_position(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> UpdatePosition:
        return UpdatePosition(
            position_repository, position_reader, transaction_manager, identity_provider
        )

    @provide
    def delete_position(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> DeletePosition:
        return DeletePosition(
            position_repository, position_reader, transaction_manager, identity_provider
        )

    @provide
    def get_position_by_id(
        self,
        position_reader: IPositionReader,
        identity_provider: IIdentityProvider,
    ) -> GetPositionById:
        return GetPositionById(position_reader, identity_provider)

    @provide
    def search_positions(
        self,
        position_reader: IPositionReader,
        identity_provider: IIdentityProvider,
    ) -> SearchPositions:
        return SearchPositions(position_reader, identity_provider)

    # Payroll Items

    @provide
    def create_payroll_item(
        self,
        payroll_item_repository: IPayrollItemRepository,
        payroll_item_reader: IPayrollItemReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> CreatePayrollItem:
        return CreatePayrollItem(
            payroll_item_repository,
            payroll_item_reader,
            code_generator,
            transaction_manager,
            identity_provider,
        )

    @provide
    def update_payroll_item(
        self,
        payroll_item_repository: IPayrollItemRepository,
        payroll_item_reader: IPayrollItemReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> UpdatePayrollItem:
        return UpdatePayrollItem(
            payroll_item_repository, payroll_item_reader, transaction_manager, identity_provider
        )

    @provide
    def delete_payroll_item(
        self,
        payroll_item_repository: IPayrollItemRepository,
        payroll_item_reader: IPayrollItemReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> DeletePayrollItem:
        return DeletePayrollItem(
            payroll_item_repository, payroll_item_reader, transaction_manager, identity_provider
        )

    @provide
    def get_payroll_item_by_id(
        self,
        payroll_item_reader: IPayrollItemReader,
        identity_provider: IIdentityProvider,
    ) -> GetPayrollItemById:
        return GetPayrollItemById(payroll_item_reader, identity_provider)

    @provide
    def search_payroll_items(
        self,
        payroll_item_reader: IPayrollItemReader,
        identity_provider: IIdentityProvider,
    ) -> SearchPayrollItems:
        return SearchPayrollItems(payroll_item_reader, identity_provider)

    # Employees

    @provide
    def create_employee(
        self,
        employee_repository: IEmployeeRepository,
        employee_reader: IEmployeeReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> CreateEmployee:
        return CreateEmployee(
            employee_repository,
            employee_reader,
            code_generator,
            transaction_manager,
            identity_provider,
        )

    @provide
    def update_employee(
        self,
        employee_repository: IEmployeeRepository,
        employee_reader: IEmployeeReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> UpdateEmployee:
        return UpdateEmployee(
            employee_repository, employee_reader, transaction_manager, identity_provider
        )

    @provide
    def delete_employee(
        self,
        employee_repository: IEmployeeRepository,
        employee_reader: IEmployeeReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> DeleteEmployee:
        return DeleteEmployee(
            employee_repository, employee_reader, transaction_manager, identity_provider
        )

    @provide
    def get_employee_by_id(
        self,
        employee_reader: IEmployeeReader,
        identity_provider: IIdentityProvider,
    ) -> GetEmployeeById:
        return GetEmployeeById(employee_reader, identity_provider)

    @provide
    def search_employees(
        self,
        employee_reader: IEmployeeReader,
        identity_provider: IIdentityProvider,
    ) -> SearchEmployees:
        return SearchEmployees(employee_reader, identity_provider)

    # Payroll Sheets

    @provide
    def create_payroll_sheet(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        employee_reader: IEmployeeReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> CreatePayrollSheet:
        return CreatePayrollSheet(
            payroll_sheet_repository,
            payroll_sheet_reader,
            employee_reader,
            transaction_manager,
            identity_provider,
        )

    @provide
    def add_payroll_record(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        payroll_item_reader: IPayrollItemReader,
        position_reader: IPositionReader,
        employee_reader: IEmployeeReader,
        payroll_service: PayrollService,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> AddPayrollRecord:
        return AddPayrollRecord(
            payroll_sheet_repository,
            payroll_sheet_reader,
            payroll_item_reader,
            position_reader,
            employee_reader,
            payroll_service,
            transaction_manager,
            identity_provider,
        )

    @provide
    def remove_payroll_record(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> RemovePayrollRecord:
        return RemovePayrollRecord(
            payroll_sheet_repository, payroll_sheet_reader, transaction_manager, identity_provider
        )

    @provide
    def cancel_payroll_sheet(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> CancelPayrollSheet:
        return CancelPayrollSheet(
            payroll_sheet_repository, payroll_sheet_reader, transaction_manager, identity_provider
        )

    @provide
    def confirm_payroll_sheet(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> ConfirmPayrollSheet:
        return ConfirmPayrollSheet(
            payroll_sheet_repository, payroll_sheet_reader, transaction_manager, identity_provider
        )

    @provide
    def get_payroll_sheet_by_id(
        self,
        payroll_sheet_reader: IPayrollSheetReader,
        identity_provider: IIdentityProvider,
    ) -> GetPayrollSheetById:
        return GetPayrollSheetById(payroll_sheet_reader, identity_provider)

    @provide
    def search_payroll_sheets(
        self,
        payroll_sheet_reader: IPayrollSheetReader,
        identity_provider: IIdentityProvider,
    ) -> SearchPayrollSheets:
        return SearchPayrollSheets(payroll_sheet_reader, identity_provider)

    # Reports

    @provide
    def get_employee_payroll_report(
        self,
        report_reader: IPayrollReportReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> GetEmployeePayrollReport:
        return GetEmployeePayrollReport(report_reader, report_renderer, identity_provider)

    @provide
    def get_department_payroll_report(
        self,
        report_reader: IPayrollReportReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> GetDepartmentPayrollReport:
        return GetDepartmentPayrollReport(report_reader, report_renderer, identity_provider)

    @provide
    def get_payroll_summary_report(
        self,
        report_reader: IPayrollReportReader,
        report_renderer: IReportRenderer,
        identity_provider: IIdentityProvider,
    ) -> GetPayrollSummaryReport:
        return GetPayrollSummaryReport(report_reader, report_renderer, identity_provider)
