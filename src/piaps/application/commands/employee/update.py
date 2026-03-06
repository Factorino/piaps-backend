from uuid import UUID

from piaps.application.common.dto import dto
from piaps.application.errors.base import NotFoundError
from piaps.application.interfaces.interactor import IInteractor
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.application.interfaces.transaction_manager import TransactionManager
from piaps.domain.entities.position import Position


@dto
class UpdatePositionRequest:
    id: UUID
    name: str | None = None
    description: str | None = None


@dto
class UpdatePositionResponse:
    position: Position


class UpdatePosition(IInteractor[UpdatePositionRequest, UpdatePositionResponse]):
    def __init__(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        uow: TransactionManager,
    ) -> None:
        self._repository: IPositionRepository = position_repository
        self._reader: IPositionReader = position_reader
        self._uow: TransactionManager = uow

    async def execute(self, request: UpdatePositionRequest) -> UpdatePositionResponse:
        existing: Position | None = await self._reader.find_by_id(request.id)
        if existing is None:
            raise NotFoundError

        updated = Position(
            id=existing.id,
            code=existing.code,
            name=request.name if request.name is not None else existing.name,
            description=request.description
            if request.description is not None
            else existing.description,
        )

        saved: Position = await self._repository.update(updated)
        await self._uow.commit()

        return UpdatePositionResponse(position=saved)
