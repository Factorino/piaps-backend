from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.payroll_sheet import PayrollSheet


class IPayrollSheetRepository(Protocol):
    @abstractmethod
    async def add(self, entity: PayrollSheet) -> None: ...

    @abstractmethod
    async def update(self, entity: PayrollSheet) -> None: ...

    @abstractmethod
    async def delete(self, entity: PayrollSheet) -> None: ...
