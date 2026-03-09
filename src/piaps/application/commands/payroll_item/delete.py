from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.payroll_item import IPayrollItemReader
from piaps.application.interfaces.repositories.payroll_item import IPayrollItemRepository
from piaps.domain.entities.payroll_item import PayrollItemId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


if TYPE_CHECKING:
    from piaps.domain.entities.payroll_item import PayrollItem


@dto
class DeletePayrollItemRequest:
    id: PayrollItemId


class DeletePayrollItem(Interactor[DeletePayrollItemRequest, None]):
    def __init__(
        self,
        payroll_item_repository: IPayrollItemRepository,
        payroll_item_reader: IPayrollItemReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_item_repository: IPayrollItemRepository = payroll_item_repository
        self._payroll_item_reader: IPayrollItemReader = payroll_item_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: DeletePayrollItemRequest) -> None:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        payroll_item: PayrollItem | None = await self._payroll_item_reader.find_by_id(request.id)
        if payroll_item is None:
            raise NotFoundError(f"Payroll item with id '{request.id}' not found")

        await self._payroll_item_repository.delete(payroll_item)
        await self._uow.commit()

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to delete payroll items")
