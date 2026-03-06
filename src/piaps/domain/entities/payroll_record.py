from datetime import date
from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_item import PayrollItem
from piaps.domain.value_objects.money import Money


PayrollRecordId = NewType("PayrollRecordId", UUID)


@entity
class PayrollRecord(Entity[PayrollRecordId]):
    employee_id: EmployeeId
    payroll_item: PayrollItem
    period: date
    amount: Money
    comment: str | None = None
