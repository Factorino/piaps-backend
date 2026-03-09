from decimal import Decimal
from typing import Final
from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.payroll_item import PayrollItemDTO
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.errors.base import OperationFailedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.payroll_item import IPayrollItemReader
from piaps.application.interfaces.repositories.payroll_item import IPayrollItemRepository
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.entities.user import User
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.services.code_generator import CodeGenerator
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


@dto
class CreatePayrollItemRequest:
    name: str
    payroll_type: PayrollItemType
    calc_type: PayrollCalculationType
    value: Decimal | None = None


@dto
class CreatePayrollItemResponse:
    payroll_item: PayrollItemDTO


class CreatePayrollItem(Interactor[CreatePayrollItemRequest, CreatePayrollItemResponse]):
    _MAX_CODE_GEN_ATTEMPTS: Final[int] = 5

    def __init__(
        self,
        payroll_item_repository: IPayrollItemRepository,
        payroll_item_reader: IPayrollItemReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_item_repository: IPayrollItemRepository = payroll_item_repository
        self._payroll_item_reader: IPayrollItemReader = payroll_item_reader
        self._code_generator: CodeGenerator = code_generator
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: CreatePayrollItemRequest) -> CreatePayrollItemResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        id_: PayrollItemId = PayrollItemId(uuid4())
        code: Code = await self._generate_unique_code()
        name = Name(value=request.name)
        payroll_type: PayrollItemType = request.payroll_type
        calc_type: PayrollCalculationType = request.calc_type
        value: Decimal | None = request.value

        payroll_item = PayrollItem(
            id=id_,
            code=code,
            name=name,
            payroll_type=payroll_type,
            calc_type=calc_type,
            value=value,
        )

        await self._check_unique(payroll_item)
        await self._payroll_item_repository.add(payroll_item)
        await self._uow.commit()

        return CreatePayrollItemResponse(payroll_item=PayrollItemDTO.from_domain(payroll_item))

    async def _generate_unique_code(self) -> Code:
        for _ in range(self._MAX_CODE_GEN_ATTEMPTS):
            code: Code = self._code_generator.generate(PayrollItem)

            existing: PayrollItem | None = await self._payroll_item_reader.find_by_code(code)
            if existing is None:
                return code

        raise OperationFailedError(
            f"Failed to generate unique code for payroll item "
            f"after {self._MAX_CODE_GEN_ATTEMPTS} attempts"
        )

    async def _check_unique(self, payroll_item: PayrollItem) -> None:
        existing: PayrollItem | None = await self._payroll_item_reader.find_by_name(
            payroll_item.name
        )
        if existing is not None and existing.id != payroll_item.id:
            raise AlreadyExistsError(
                f"Payroll item with name '{payroll_item.name.value}' already exists"
            )

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to create payroll items")
