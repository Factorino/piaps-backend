from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.payroll import Payroll


class IPayrollRepository(Protocol):
    @abstractmethod
    async def add(self, entity: Payroll) -> Payroll: ...

    @abstractmethod
    async def update(self, entity: Payroll) -> Payroll: ...

    @abstractmethod
    async def delete(self, entity: Payroll) -> None: ...
