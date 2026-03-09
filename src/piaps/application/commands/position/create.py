from decimal import Decimal
from typing import TYPE_CHECKING, Final
from uuid import uuid4

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.position import PositionDTO
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.errors.base import OperationFailedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.domain.entities.position import Position, PositionId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.services.code_generator import CodeGenerator
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.name import Name


if TYPE_CHECKING:
    from piaps.domain.entities.user import User


@dto
class CreatePositionRequest:
    name: str
    base_salary: Decimal
    description: str | None = None


@dto
class CreatePositionResponse:
    position: PositionDTO


class CreatePosition(Interactor[CreatePositionRequest, CreatePositionResponse]):
    _MAX_CODE_GEN_ATTEMPTS: Final[int] = 5

    def __init__(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        code_generator: CodeGenerator,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._position_repository: IPositionRepository = position_repository
        self._position_reader: IPositionReader = position_reader
        self._code_generator: CodeGenerator = code_generator
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: CreatePositionRequest) -> CreatePositionResponse:
        await self._check_access()

        id_: PositionId = PositionId(uuid4())
        code: Code = await self._generate_unique_code()
        name = Name(value=request.name)
        base_salary = Money(value=request.base_salary)
        description: str | None = request.description

        position = Position(
            id=id_,
            code=code,
            name=name,
            base_salary=base_salary,
            description=description,
        )

        await self._check_unique(position)
        await self._position_repository.add(position)
        await self._uow.commit()

        return CreatePositionResponse(position=PositionDTO.from_domain(position))

    async def _generate_unique_code(self) -> Code:
        for _ in range(self._MAX_CODE_GEN_ATTEMPTS):
            code: Code = self._code_generator.generate(Position)

            existing: Position | None = await self._position_reader.find_by_code(code)
            if existing is None:
                return code

        raise OperationFailedError(
            f"Failed to generate unique code for position "
            f"after {self._MAX_CODE_GEN_ATTEMPTS} attempts"
        )

    async def _check_unique(self, position: Position) -> None:
        existing: Position | None = await self._position_reader.find_by_name(position.name)
        if existing is not None and position.id != existing.id:
            raise AlreadyExistsError(f"Position with name '{position.name.value}' already exists")

    async def _check_access(self) -> None:
        user: User = await self._idp.get_user()
        if user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("Only administrators can create positions")
