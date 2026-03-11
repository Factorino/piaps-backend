from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.payroll_sheet import PayrollSheetView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.payroll_sheet import IPayrollSheetReader
from piaps.application.interfaces.repositories.payroll_sheet import IPayrollSheetRepository
from piaps.domain.entities.payroll_record import PayrollRecordId
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class RemovePayrollRecordRequest:
    payroll_sheet_id: PayrollSheetId
    record_id: PayrollRecordId


@dto
class RemovePayrollRecordResponse:
    payroll_sheet: PayrollSheetView


class RemovePayrollRecord(Interactor[RemovePayrollRecordRequest, RemovePayrollRecordResponse]):
    def __init__(
        self,
        payroll_sheet_repository: IPayrollSheetRepository,
        payroll_sheet_reader: IPayrollSheetReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_sheet_repository: IPayrollSheetRepository = payroll_sheet_repository
        self._payroll_sheet_reader: IPayrollSheetReader = payroll_sheet_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: RemovePayrollRecordRequest) -> RemovePayrollRecordResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        payroll_sheet: PayrollSheet | None = await self._payroll_sheet_reader.find_by_id(
            request.payroll_sheet_id
        )
        if payroll_sheet is None:
            raise NotFoundError(f"Payroll sheet with id '{request.payroll_sheet_id}' not found")

        payroll_sheet.remove_record(request.record_id)

        await self._payroll_sheet_repository.update(payroll_sheet)
        await self._uow.commit()

        return RemovePayrollRecordResponse(
            payroll_sheet=PayrollSheetView.from_domain(payroll_sheet)
        )

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to remove payroll records")
