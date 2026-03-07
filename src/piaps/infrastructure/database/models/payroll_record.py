from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import UUID as SAUUID, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from piaps.infrastructure.database.models.base import BaseORM
from piaps.infrastructure.database.models.payroll_item import PayrollItemORM


class PayrollRecordORM(BaseORM):
    __tablename__: Any = "payroll_records"

    id: Mapped[UUID] = mapped_column(
        SAUUID(as_uuid=True),
        primary_key=True,
    )

    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    payroll_item_id: Mapped[UUID] = mapped_column(
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

    payroll_sheet_id: Mapped[UUID] = mapped_column(
        ForeignKey("payroll_sheets.id"),
        nullable=False,
        index=True,
    )

    payroll_item: Mapped[PayrollItemORM] = relationship(lazy="joined")
