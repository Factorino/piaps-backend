from piaps.application.common.dto.base import dto
from piaps.application.common.dto.payroll_sheet import PayrollSheetDTO
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.payroll_sheet import IPayrollSheetReader
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class GetPayrollSheetByIdRequest:
    id: PayrollSheetId


@dto
class GetPayrollSheetByIdResponse:
    payroll_sheet: PayrollSheetDTO


class GetPayrollByIdSheet(Interactor[GetPayrollSheetByIdRequest, GetPayrollSheetByIdResponse]):
    def __init__(
        self,
        payroll_sheet_reader: IPayrollSheetReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_sheet_reader: IPayrollSheetReader = payroll_sheet_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: GetPayrollSheetByIdRequest) -> GetPayrollSheetByIdResponse:
        current_user: User = await self._idp.get_user()

        payroll_sheet: PayrollSheet | None = await self._payroll_sheet_reader.find_by_id(
            request.id
        )
        if payroll_sheet is None:
            raise NotFoundError(f"Payroll sheet with id '{request.id}' not found")

        self._check_access(current_user, payroll_sheet)

        return GetPayrollSheetByIdResponse(
            payroll_sheet=PayrollSheetDTO.from_domain(payroll_sheet)
        )

    def _check_access(self, current_user: User, payroll_sheet: PayrollSheet) -> None:
        if current_user.role >= UserRole.ACCOUNTANT:
            return

        if (
            current_user.employee_id is None
            or current_user.employee_id != payroll_sheet.employee_id
        ):
            raise NotFoundError(f"Payroll sheet with id '{payroll_sheet.id}' not found")
