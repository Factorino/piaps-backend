from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.position import Position, PositionId


class IPositionRepository(Protocol):
    @abstractmethod
    async def add(self, entity: Position) -> None: ...

    @abstractmethod
    async def update(self, entity: Position) -> None: ...

    @abstractmethod
    async def delete(self, id: PositionId) -> None: ...
