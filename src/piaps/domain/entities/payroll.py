from dataclasses import field
from decimal import Decimal
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.errors.base import ValidationError
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.period import Period


if TYPE_CHECKING:
    from piaps.domain.value_objects.payroll_line_item import PayrollLineItem


@entity
class Payroll(Entity[UUID]):
    employee_id: UUID
    period: Period
    status: PayrollStatus = PayrollStatus.DRAFT
    base_salary: Money
    accruals: list["PayrollLineItem"] = field(default_factory=list)
    deductions: list["PayrollLineItem"] = field(default_factory=list)

    @property
    def net_salary(self) -> Money:
        gross: Decimal = self.base_salary.value + sum(item.amount.value for item in self.accruals)
        total_deductions: Decimal | Literal[0] = sum(item.amount.value for item in self.deductions)
        net: Decimal = gross - total_deductions
        return Money(value=Decimal(net))

    def set_status(self, status: PayrollStatus) -> None:
        if status != self.status + 1:
            raise ValidationError
        self.status = status

    def add_accrual(self, line_item: "PayrollLineItem") -> None:
        if self.status >= PayrollStatus.CALCULATED:
            raise ValidationError
        self.accruals.append(line_item)

    def add_deduction(self, line_item: "PayrollLineItem") -> None:
        if self.status >= PayrollStatus.CALCULATED:
            raise ValidationError
        self.deductions.append(line_item)
