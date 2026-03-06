from typing import TYPE_CHECKING
from uuid import uuid4

from piaps.application.common.dto import dto
from piaps.application.interfaces.interactor import IInteractor
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.application.interfaces.repositories.position import IPositionRepository
from piaps.application.interfaces.transaction_manager import TransactionManager
from piaps.domain.entities.position import Position
from piaps.domain.errors.base import AlreadyExistsError
from piaps.domain.services.code_generator import CodeGenerator


if TYPE_CHECKING:
    from piaps.domain.value_objects.code import Code


@dto
class CreatePositionRequest:
    name: str
    description: str | None = None


@dto
class CreatePositionResponse:
    position: Position


class CreatePosition(IInteractor[CreatePositionRequest, CreatePositionResponse]):
    def __init__(
        self,
        position_repository: IPositionRepository,
        position_reader: IPositionReader,
        code_generator: CodeGenerator,
        uow: TransactionManager,
    ) -> None:
        self._repository: IPositionRepository = position_repository
        self._reader: IPositionReader = position_reader
        self._code_generator: CodeGenerator = code_generator
        self._uow: TransactionManager = uow

    async def execute(self, request: CreatePositionRequest) -> CreatePositionResponse:
        code: Code = self._code_generator.generate(Position)

        existing: Position | None = await self._reader.find_by_code(code)
        if existing is not None:
            raise AlreadyExistsError

        position = Position(
            id=uuid4(),
            code=code,
            name=request.name,
            description=request.description,
        )

        saved: Position = await self._repository.add(position)
        await self._uow.commit()

        return CreatePositionResponse(position=saved)
