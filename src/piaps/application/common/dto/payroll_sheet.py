from datetime import date
from typing import Self

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.payroll_record import PayrollRecordDTO
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.enums.payroll_status import PayrollStatus


@dto
class PayrollSheetDTO:
    id: PayrollSheetId
    period: date
    status: PayrollStatus
    records: list[PayrollRecordDTO]

    @classmethod
    def from_domain(cls, entity: PayrollSheet) -> Self:
        records: list[PayrollRecordDTO] = [
            PayrollRecordDTO.from_domain(rec) for rec in entity.records
        ]

        return cls(
            id=entity.id,
            period=entity.period,
            status=entity.status,
            records=records,
        )
