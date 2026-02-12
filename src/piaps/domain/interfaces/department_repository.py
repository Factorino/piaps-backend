from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from piaps.domain.entities.department import Department


class IDepartmentRepository(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Department | None: ...

    @abstractmethod
    async def add(self, entity: Department) -> Department: ...

    @abstractmethod
    async def update(self, entity: Department) -> Department: ...

    @abstractmethod
    async def delete(self, entity: Department) -> None: ...
