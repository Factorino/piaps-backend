from decimal import Decimal
from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.payroll_item import PayrollItemDTO
from piaps.application.common.not_set import NOTSET, NotSet, is_set
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.payroll_item import IPayrollItemReader
from piaps.application.interfaces.repositories.payroll_item import IPayrollItemRepository
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError, NotFoundError
from piaps.domain.value_objects.name import Name


if TYPE_CHECKING:
    from piaps.domain.entities.user import User


@dto
class UpdatePayrollItemRequest:
    id: PayrollItemId
    name: str | NotSet = NOTSET
    payroll_type: PayrollItemType | NotSet = NOTSET
    calc_type: PayrollCalculationType | NotSet = NOTSET
    value: Decimal | None | NotSet = NOTSET


@dto
class UpdatePayrollItemResponse:
    payroll_item: PayrollItemDTO


class UpdatePayrollItem(Interactor[UpdatePayrollItemRequest, UpdatePayrollItemResponse]):
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

    async def execute(self, request: UpdatePayrollItemRequest) -> UpdatePayrollItemResponse:
        await self._check_access()

        payroll_item: PayrollItem | None = await self._payroll_item_reader.find_by_id(request.id)
        if payroll_item is None:
            raise NotFoundError(f"Payroll item with id '{request.id}' not found")

        if is_set(request.name):
            payroll_item.name = Name(value=request.name)
        if is_set(request.payroll_type):
            payroll_item.payroll_type = request.payroll_type
        if is_set(request.calc_type):
            payroll_item.calc_type = request.calc_type
        if is_set(request.value):
            payroll_item.value = request.value

        await self._check_unique(payroll_item)
        await self._payroll_item_repository.update(payroll_item)
        await self._uow.commit()

        return UpdatePayrollItemResponse(payroll_item=PayrollItemDTO.from_domain(payroll_item))

    async def _check_unique(self, payroll_item: PayrollItem) -> None:
        existing: PayrollItem | None = await self._payroll_item_reader.find_by_name(
            payroll_item.name
        )
        if existing is not None and payroll_item.id != existing.id:
            raise AlreadyExistsError(
                f"Payroll item with name '{payroll_item.name.value}' already exists"
            )

    async def _check_access(self) -> None:
        user: User = await self._idp.get_user()
        if user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("Only accountants and administrators can delete payroll items")
