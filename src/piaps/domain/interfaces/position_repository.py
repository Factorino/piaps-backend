from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from piaps.domain.entities.position import Position


class IPositionRepository(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Position | None: ...

    @abstractmethod
    async def add(self, entity: Position) -> Position: ...

    @abstractmethod
    async def update(self, entity: Position) -> Position: ...

    @abstractmethod
    async def delete(self, entity: Position) -> None: ...
