from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.employee import Employee


class IEmployeeRepository(Protocol):
    @abstractmethod
    async def add(self, entity: Employee) -> None: ...

    @abstractmethod
    async def update(self, entity: Employee) -> None: ...

    @abstractmethod
    async def delete(self, entity: Employee) -> None: ...
