from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from piaps.domain.entities.salary_item import SalaryItem


class ISalaryItemRepository(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> SalaryItem | None: ...

    @abstractmethod
    async def add(self, entity: SalaryItem) -> SalaryItem: ...

    @abstractmethod
    async def update(self, entity: SalaryItem) -> SalaryItem: ...

    @abstractmethod
    async def delete(self, entity: SalaryItem) -> None: ...
