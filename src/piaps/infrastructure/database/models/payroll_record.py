from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import UUID, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_item import PayrollItemId
from piaps.domain.entities.payroll_record import PayrollRecordId
from piaps.domain.entities.payroll_sheet import PayrollSheetId
from piaps.infrastructure.database.models.base import BaseORM
from piaps.infrastructure.database.models.payroll_item import PayrollItemORM


class PayrollRecordORM(BaseORM):
    __tablename__: Any = "payroll_records"

    id: Mapped[PayrollRecordId] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    employee_id: Mapped[EmployeeId] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    payroll_item_id: Mapped[PayrollItemId] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payroll_items.id"),
        nullable=False,
        index=True,
    )

    period: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    payroll_sheet_id: Mapped[PayrollSheetId] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payroll_sheets.id"),
        nullable=False,
        index=True,
    )

    payroll_item: Mapped[PayrollItemORM] = relationship(lazy="joined")
