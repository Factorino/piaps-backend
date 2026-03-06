from abc import abstractmethod
from typing import Protocol

from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId


class IPayrollSheetRepository(Protocol):
    @abstractmethod
    async def add(self, entity: PayrollSheet) -> None: ...

    @abstractmethod
    async def update(self, entity: PayrollSheet) -> None: ...

    @abstractmethod
    async def delete(self, id: PayrollSheetId) -> None: ...
