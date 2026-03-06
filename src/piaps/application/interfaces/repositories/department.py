from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.department import Department, DepartmentId


class IDepartmentRepository(Protocol):
    @abstractmethod
    async def add(self, entity: Department) -> None: ...

    @abstractmethod
    async def update(self, entity: Department) -> None: ...

    @abstractmethod
    async def delete(self, id: DepartmentId) -> None: ...
