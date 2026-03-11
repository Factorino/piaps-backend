from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.payroll_sheet import PayrollSheetView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.employee import IEmployeeReader
from piaps.application.interfaces.readers.payroll_item import IPayrollItemReader
from piaps.application.interfaces.readers.payroll_sheet import IPayrollSheetReader
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.payroll_sheet import IPayrollSheetRepository
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.entities.payroll_record import PayrollRecord, PayrollRecordId
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError
from piaps.domain.services.payroll_service import PayrollService
from piaps.domain.value_objects.money import Money


if TYPE_CHECKING:
    from piaps.domain.entities.position import Position


@dto
class AddPayrollRecordRequest:
    payroll_sheet_id: PayrollSheetId
    payroll_item_id: PayrollItemId
    amount: Decimal | None = None  # None => calculated by the service
    comment: str | None = None


@dto
class AddPayrollRecordResponse:
    payroll_sheet: PayrollSheetView


class AddPayrollRecord(Interactor[AddPayrollRecordRequest, AddPayrollRecordResponse]):
    def __init__(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        payroll_item_reader: IPayrollItemReader,
        position_reader: IPositionReader,
        employee_reader: IEmployeeReader,
        payroll_service: PayrollService,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_sheet_repository: IPayrollSheetRepository = payroll_sheet_repository
        self._payroll_sheet_reader: IPayrollSheetReader = payroll_sheet_reader
        self._payroll_item_reader: IPayrollItemReader = payroll_item_reader
        self._position_reader: IPositionReader = position_reader
        self._employee_reader: IEmployeeReader = employee_reader
        self._payroll_service: PayrollService = payroll_service
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: AddPayrollRecordRequest) -> AddPayrollRecordResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        payroll_sheet: PayrollSheet | None = await self._payroll_sheet_reader.find_by_id(
            request.payroll_sheet_id
        )
        if payroll_sheet is None:
            raise NotFoundError(f"Payroll sheet with id '{request.payroll_sheet_id}' not found")

        payroll_item: PayrollItem | None = await self._payroll_item_reader.find_by_id(
            request.payroll_item_id
        )
        if payroll_item is None:
            raise NotFoundError(f"Payroll item with id '{request.payroll_item_id}' not found")

        base_salary: Money = await self._resolve_base_salary(payroll_sheet.employee_id)
        override: Money | None = (
            Money(value=request.amount) if request.amount is not None else None
        )
        amount: Money = self._payroll_service.calculate(
            payroll_item=payroll_item,
            base_salary=base_salary,
            amount=override,
        )

        record = PayrollRecord(
            id=PayrollRecordId(uuid4()),
            employee_id=payroll_sheet.employee_id,
            payroll_item=payroll_item,
            period=payroll_sheet.period,
            amount=amount,
            comment=request.comment,
        )

        payroll_sheet.add_record(record)

        await self._payroll_sheet_repository.update(payroll_sheet)
        await self._uow.commit()

        return AddPayrollRecordResponse(payroll_sheet=PayrollSheetView.from_domain(payroll_sheet))

    async def _resolve_base_salary(self, employee_id: EmployeeId) -> Money:
        employee: Employee | None = await self._employee_reader.find_by_id(employee_id)
        if employee is None:
            raise NotFoundError(f"Employee with id '{employee_id}' not found")

        position: Position | None = await self._position_reader.find_by_id(employee.position_id)
        if position is None:
            raise NotFoundError(f"Position with id '{employee.position_id}' not found")

        return position.base_salary

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to add payroll records")
