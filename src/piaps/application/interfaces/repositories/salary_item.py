from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId


class IPayrollItemRepository(Protocol):
    @abstractmethod
    async def add(self, entity: PayrollItem) -> None: ...

    @abstractmethod
    async def update(self, entity: PayrollItem) -> None: ...

    @abstractmethod
    async def delete(self, id: PayrollItemId) -> None: ...
