from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.payroll_item import PayrollItemView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.payroll_item import IPayrollItemReader
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class GetPayrollItemByIdRequest:
    id: PayrollItemId


@dto
class GetPayrollItemByIdResponse:
    payroll_item: PayrollItemView


class GetPayrollItemById(Interactor[GetPayrollItemByIdRequest, GetPayrollItemByIdResponse]):
    def __init__(
        self,
        payroll_item_reader: IPayrollItemReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_item_reader: IPayrollItemReader = payroll_item_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: GetPayrollItemByIdRequest) -> GetPayrollItemByIdResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        payroll_item: PayrollItem | None = await self._payroll_item_reader.find_by_id(request.id)
        if payroll_item is None:
            raise NotFoundError(f"Payroll item with id '{request.id}' not found")

        return GetPayrollItemByIdResponse(payroll_item=PayrollItemView.from_domain(payroll_item))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read payroll items")
