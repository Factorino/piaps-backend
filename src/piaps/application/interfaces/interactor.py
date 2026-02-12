from abc import abstractmethod
from typing import Protocol


class IInteractor[InputDTO, OutputDTO](Protocol):
    @abstractmethod
    async def execute(self, request: InputDTO) -> OutputDTO: ...
