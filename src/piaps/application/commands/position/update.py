from decimal import Decimal

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.position import PositionView
from piaps.application.common.not_set import NOTSET, NotSet, is_set
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.domain.entities.position import Position, PositionId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import AlreadyExistsError, NotFoundError
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.name import Name


@dto
class UpdatePositionRequest:
    id: PositionId
    name: str | NotSet = NOTSET
    base_salary: Decimal | NotSet = NOTSET
    description: str | None | NotSet = NOTSET


@dto
class UpdatePositionResponse:
    position: PositionView


class UpdatePosition(Interactor[UpdatePositionRequest, UpdatePositionResponse]):
    def __init__(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        transaction_manager: ITransactionManager,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._position_repository: IPositionRepository = position_repository
        self._position_reader: IPositionReader = position_reader
        self._uow: ITransactionManager = transaction_manager
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: UpdatePositionRequest) -> UpdatePositionResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        position: Position | None = await self._position_reader.find_by_id(request.id)
        if position is None:
            raise NotFoundError(f"Position with id '{request.id}' not found")

        if is_set(request.name):
            position.name = Name(value=request.name)
        if is_set(request.base_salary):
            position.base_salary = Money(value=request.base_salary)
        if is_set(request.description):
            position.description = request.description

        await self._check_unique(position)
        await self._position_repository.update(position)
        await self._uow.commit()

        return UpdatePositionResponse(position=PositionView.from_domain(position))

    async def _check_unique(self, position: Position) -> None:
        existing: Position | None = await self._position_reader.find_by_name(position.name)
        if existing is not None and existing.id != position.id:
            raise AlreadyExistsError(f"Position with name '{position.name.value}' already exists")

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to update positions")
