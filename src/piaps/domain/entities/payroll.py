from dataclasses import field
from typing import TYPE_CHECKING
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.value_objects.period import Period


if TYPE_CHECKING:
    from piaps.domain.value_objects.payroll_line_item import PayrollLineItem


@entity
class Payroll(Entity[UUID]):
    employee_id: UUID
    period: Period
    status: PayrollStatus
    accruals: list["PayrollLineItem"] = field(default_factory=list)
    deductions: list["PayrollLineItem"] = field(default_factory=list)
