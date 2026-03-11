from datetime import date
from typing import Self

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.payroll_record import PayrollRecordView
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.domain.enums.payroll_status import PayrollStatus


@dto
class PayrollSheetView:
    id: PayrollSheetId
    period: date
    status: PayrollStatus
    records: list[PayrollRecordView]

    @classmethod
    def from_domain(cls, entity: PayrollSheet) -> Self:
        records: list[PayrollRecordView] = [
            PayrollRecordView.from_domain(rec) for rec in entity.records
        ]

        return cls(
            id=entity.id,
            period=entity.period,
            status=entity.status,
            records=records,
        )
