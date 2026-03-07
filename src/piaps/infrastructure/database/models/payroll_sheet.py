from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import UUID as SAUUID, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from piaps.domain.enums.payroll_status import PayrollStatus
from piaps.infrastructure.database.models.base import BaseORM
from piaps.infrastructure.database.models.payroll_record import PayrollRecordORM


class PayrollSheetORM(BaseORM):
    __tablename__: Any = "payroll_sheets"

    id: Mapped[UUID] = mapped_column(
        SAUUID(as_uuid=True),
        primary_key=True,
    )

    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    period: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    status: Mapped[PayrollStatus] = mapped_column(
        Enum(PayrollStatus),
        default=PayrollStatus.DRAFT,
        nullable=False,
    )

    records: Mapped[list[PayrollRecordORM]] = relationship(
        lazy="selectin",
        cascade="all, delete-orphan",
    )
