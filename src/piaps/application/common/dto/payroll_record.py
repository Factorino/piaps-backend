from datetime import date
from decimal import Decimal
from typing import Self

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.payroll_item import PayrollItemDTO
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_record import PayrollRecord, PayrollRecordId


@dto
class PayrollRecordDTO:
    id: PayrollRecordId
    employee_id: EmployeeId
    payroll_item: PayrollItemDTO
    period: date
    amount: Decimal
    comment: str | None = None

    @classmethod
    def from_domain(cls, entity: PayrollRecord) -> Self:
        return cls(
            id=entity.id,
            employee_id=entity.employee_id,
            payroll_item=PayrollItemDTO.from_domain(entity.payroll_item),
            period=entity.period,
            amount=entity.amount.value,
            comment=entity.comment,
        )
