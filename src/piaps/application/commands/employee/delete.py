from typing import TYPE_CHECKING
from uuid import UUID

from piaps.application.common.dto import dto
from piaps.application.errors.base import NotFoundError
from piaps.application.interfaces.interactor import IInteractor
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.application.interfaces.transaction_manager import TransactionManager


if TYPE_CHECKING:
    from piaps.domain.entities.position import Position


@dto
class DeletePositionRequest:
    id: UUID


@dto
class DeletePositionResponse:
    success: bool


class DeletePosition(IInteractor[DeletePositionRequest, DeletePositionResponse]):
    def __init__(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        uow: TransactionManager,
    ) -> None:
        self._repository: IPositionRepository = position_repository
        self._reader: IPositionReader = position_reader
        self._uow: TransactionManager = uow

    async def execute(self, request: DeletePositionRequest) -> DeletePositionResponse:
        position: Position | None = await self._reader.find_by_id(request.id)
        if position is None:
            raise NotFoundError

        await self._repository.delete(position)
        await self._uow.commit()

        return DeletePositionResponse(success=True)
