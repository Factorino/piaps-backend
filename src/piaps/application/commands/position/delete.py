from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.common.transaction_manager import ITransactionManager
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.domain.entities.position import PositionId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


if TYPE_CHECKING:
    from piaps.domain.entities.position import Position


@dto
class DeletePositionRequest:
    id: PositionId


class DeletePosition(Interactor[DeletePositionRequest, None]):
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

    async def execute(self, request: DeletePositionRequest) -> None:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        position: Position | None = await self._position_reader.find_by_id(request.id)
        if position is None:
            raise NotFoundError(f"Position with id '{request.id}' not found")

        await self._position_repository.delete(position)
        await self._uow.commit()

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to delete positions")
