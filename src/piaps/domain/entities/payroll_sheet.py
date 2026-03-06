from dataclasses import field
from datetime import date
from decimal import Decimal
from typing import NewType
from uuid import UUID

from piaps.domain.entities.base import Entity, entity
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_record import PayrollRecord, PayrollRecordId
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.domain.errors.base import NotFoundError
from piaps.domain.errors.payroll import InvalidPayrollRecordError, InvalidPayrollStatusError
from piaps.domain.value_objects.money import Money


PayrollSheetId = NewType("PayrollSheetId", UUID)


@entity
class PayrollSheet(Entity[PayrollSheetId]):
    employee_id: EmployeeId
    period: date
    status: PayrollStatus = PayrollStatus.DRAFT
    records: list[PayrollRecord] = field(default_factory=list)

    @property
    def accruals(self) -> list[PayrollRecord]:
        return self._get_by_type(PayrollItemType.ACCRUAL)

    @property
    def deductions(self) -> list[PayrollRecord]:
        return self._get_by_type(PayrollItemType.DEDUCTION)

    @property
    def accruals_sum(self) -> Money:
        return self._sum_by_type(PayrollItemType.ACCRUAL)

    @property
    def deductions_sum(self) -> Money:
        return self._sum_by_type(PayrollItemType.DEDUCTION)

    @property
    def net_salary(self) -> Money:
        return self.accruals_sum - self.deductions_sum

    def add_record(self, record: PayrollRecord) -> None:
        self._ensure_draft()
        if record.employee_id != self.employee_id:
            raise InvalidPayrollRecordError("Record employee_id does not match sheet employee_id")
        if record.period != self.period:
            raise InvalidPayrollRecordError("Record period does not match sheet period")
        self.records.append(record)

    def remove_record(self, record_id: PayrollRecordId) -> None:
        self._ensure_draft()
        record: PayrollRecord = self._get_record(record_id)
        self.records.remove(record)

    def confirm(self) -> None:
        self._set_status(PayrollStatus.CONFIRMED)

    def cancel(self) -> None:
        self._set_status(PayrollStatus.CANCELLED)

    def _get_record(self, record_id: PayrollRecordId) -> PayrollRecord:
        for record in self.records:
            if record.id == record_id:
                return record
        raise NotFoundError(f"Record with id {record_id} not found")

    def _get_by_type(self, payroll_type: PayrollItemType) -> list[PayrollRecord]:
        return [
            record for record in self.records if record.payroll_item.payroll_type == payroll_type
        ]

    def _sum_by_type(self, payroll_type: PayrollItemType) -> Money:
        return sum(
            (record.amount for record in self._get_by_type(payroll_type)),
            start=Money(value=Decimal(0)),
        )

    def _ensure_draft(self) -> None:
        if self.status != PayrollStatus.DRAFT:
            raise InvalidPayrollStatusError("Payroll sheet is not in draft status")

    def _set_status(self, new_status: PayrollStatus) -> None:
        self.status = new_status
