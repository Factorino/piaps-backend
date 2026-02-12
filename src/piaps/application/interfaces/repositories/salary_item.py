from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.salary_item import SalaryItem


class ISalaryItemRepository(Protocol):
    @abstractmethod
    async def add(self, entity: SalaryItem) -> SalaryItem: ...

    @abstractmethod
    async def update(self, entity: SalaryItem) -> SalaryItem: ...

    @abstractmethod
    async def delete(self, entity: SalaryItem) -> None: ...
