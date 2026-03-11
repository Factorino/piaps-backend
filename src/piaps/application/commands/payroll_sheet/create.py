from datetime import date
from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.payroll_sheet import PayrollSheetDTO
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.readers.payroll_sheet import IPayrollSheetReader
from piaps.application.interfaces.repositories.payroll_sheet import IPayrollSheetRepository
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError, NotFoundError


@dto
class CreatePayrollSheetRequest:
    employee_id: EmployeeId
    period: date


@dto
class CreatePayrollSheetResponse:
    payroll_sheet: PayrollSheetDTO


class CreatePayrollSheet(Interactor[CreatePayrollSheetRequest, CreatePayrollSheetResponse]):
    def __init__(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        employee_reader: IEmployeeReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_sheet_repository: IPayrollSheetRepository = payroll_sheet_repository
        self._payroll_sheet_reader: IPayrollSheetReader = payroll_sheet_reader
        self._employee_reader: IEmployeeReader = employee_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: CreatePayrollSheetRequest) -> CreatePayrollSheetResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        employee: Employee | None = await self._employee_reader.find_by_id(request.employee_id)
        if employee is None:
            raise NotFoundError(f"Employee with id '{request.employee_id}' not found")

        await self._check_unique(request.employee_id, request.period)

        payroll_sheet = PayrollSheet(
            id=PayrollSheetId(uuid4()),
            employee_id=request.employee_id,
            period=request.period,
        )

        await self._payroll_sheet_repository.add(payroll_sheet)
        await self._uow.commit()

        return CreatePayrollSheetResponse(payroll_sheet=PayrollSheetDTO.from_domain(payroll_sheet))

    async def _check_unique(self, employee_id: EmployeeId, period: date) -> None:
        existing: (
            PayrollSheet | None
        ) = await self._payroll_sheet_reader.find_by_employee_and_period(employee_id, period)
        if existing is not None:
            raise AlreadyExistsError(
                f"Payroll sheet for employee '{employee_id}' for period '{period}' already exists"
            )

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to create payroll sheets")
